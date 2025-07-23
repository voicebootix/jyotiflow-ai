"""
🎭 SPIRITUAL AVATAR GENERATION ENGINE
Real D-ID + ElevenLabs Integration for Swamiji Avatar Videos

This module provides the complete implementation for generating avatar videos
with Swami Jyotirananthan's digital embodiment using real AI services.
"""

import asyncio
import aiohttp
import json
import logging
import os
import uuid
from datetime import datetime, timezone
from typing import Dict, Optional, Tuple, List, Any
from pathlib import Path
import base64
import hashlib
import time

from core_foundation_enhanced import settings, db_manager
from enhanced_business_logic import SpiritualAvatarEngine, AvatarGenerationContext, AvatarEmotion
from ..schemas.avatar import AvatarSessionCreate, AvatarSession

logger = logging.getLogger(__name__)

class SwamjiAvatarGenerationEngine:
    """
    Complete Avatar Generation Engine for Swami Jyotirananthan
    Real D-ID + ElevenLabs Integration
    """
    
    def __init__(self):
        self.settings = settings
        self.db = db_manager
        
        # Swamiji Avatar Configuration
        self.swamiji_presenter_id = "amy-jcu8YUbZbKt8EXOlXG7je"  # D-ID presenter ID
        self.swamiji_voice_id = "21m00Tcm4TlvDq8ikWAM"  # ElevenLabs voice ID (Rachel as placeholder)
        
        # API Endpoints
        self.d_id_base_url = "https://api.d-id.com"
        self.elevenlabs_base_url = "https://api.elevenlabs.io/v1"
        
        # Storage configuration
        self.avatar_storage_path = Path("storage/avatars")
        self.avatar_storage_path.mkdir(parents=True, exist_ok=True)
        
        # Generation limits
        self.max_video_duration = 1800  # 30 minutes
        self.max_concurrent_generations = 3
        self.current_generations = 0
        
        # CORE.MD & REFRESH.MD: Proactive dependency checks at initialization
        if not self.settings.d_id_api_key or "your-d-id-api-key" in self.settings.d_id_api_key:
            logger.warning("D-ID API key is not configured. Avatar generation will fail.")
        if not self.settings.elevenlabs_api_key or "your-elevenlabs-api-key" in self.settings.elevenlabs_api_key:
            logger.warning("ElevenLabs API key is not configured. Avatar generation will fail.")

        logger.info("🎭 Swamiji Avatar Generation Engine initialized")
    
    async def generate_complete_avatar_video(
        self,
        session_id: str,
        user_email: str,
        guidance_text: str,
        service_type: str,
        avatar_style: str = "default",
        voice_tone: str = "calm",
        audio_url: Optional[str] = None,
        video_duration: int = 60,
    ) -> Dict[str, Any]:
        """
        Orchestrates the full avatar generation process.
        """
        generation_start_time = time.time()
        try:
            video_result = await self._generate_avatar_video(
                guidance_text=guidance_text,
                avatar_style=avatar_style,
                session_id=session_id,
                user_email=user_email,
                audio_url=audio_url
            )
            
            if not video_result.get("success"):
                raise Exception(f"Video generation failed: {video_result.get('error', 'Unknown D-ID error')}")
            
            generation_time = time.time() - generation_start_time
            total_cost = video_result.get("cost", 0)
            
            await self._store_avatar_session(
                session_id, user_email, guidance_text, avatar_style, voice_tone,
                video_result.get("video_url"), audio_url,
                video_duration, 0, total_cost,
                generation_time
            )
            
            logger.info(f"✅ Avatar generation completed in {generation_time:.2f}s")
            return {
                "success": True,
                "video_url": video_result.get("video_url"),
                "audio_url": audio_url,
                "duration_seconds": video_duration,
                "generation_time": generation_time,
                "total_cost": total_cost,
                "voice_cost": 0,
                "video_cost": total_cost,
                "quality": "high"
            }
        except Exception as e:
            logger.error(f"Avatar generation process failed for session {session_id}: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    async def _generate_avatar_video(
        self,
        guidance_text: str,
        avatar_style: str,
        session_id: str,
        user_email: str,
        audio_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generates avatar video using D-ID with pre-generated audio or text-to-speech.
        """
        try:
            avatar_style_config = self._get_avatar_style_config(avatar_style)
            source_image_url = avatar_style_config.get("source_url")
            if not source_image_url:
                return {"success": False, "error": f"Source image URL not found for style '{avatar_style}'"}

            if audio_url:
                script = {"type": "audio", "audio_url": audio_url}
            else:
                script = {
                    "type": "text",
                    "input": guidance_text,
                    "provider": {
                        "type": "elevenlabs",
                        "voice_id": self.swamiji_voice_id # Use the configured voice_id
                    }
                }

            default_expressions_response = await self._get_d_id_default_expressions()
            default_data = default_expressions_response.get("data", {})
            default_expressions = default_data.get("expressions", []) if isinstance(default_data, dict) else []
            
            avatar_expressions = avatar_style_config.get("expressions", [])
            final_expressions = default_expressions + avatar_expressions

            body = {
                "script": script,
                "source_url": source_image_url,
                "driver_expression": {"expressions": final_expressions, "transition_frames": 20},
                "config": {"result_format": "mp4", "stitch": True},
                "user_data": f'{{"session_id": "{session_id}", "user_email": "{user_email}"}}'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.d_id_base_url}/talks",
                    json=body,
                    headers={
                        "accept": "application/json",
                        "content-type": "application/json",
                        "authorization": f"Basic {self.settings.d_id_api_key}"
                    }
                ) as response:
                    response_data = await response.json()
                    if response.status in [200, 201]:
                        talk_id = response_data["id"]
                        video_url = await self._poll_d_id_completion(talk_id)
                        
                        if video_url:
                            # REFRESH.MD: Use configurable pricing values with fallbacks
                            words_per_minute = getattr(self.settings, 'avatar_words_per_minute', 150)
                            cost_per_minute = getattr(self.settings, 'avatar_video_cost_per_minute', 0.12)
                            
                            estimated_minutes = len(guidance_text) / words_per_minute
                            cost = estimated_minutes * cost_per_minute
                            return {"success": True, "video_url": video_url, "talk_id": talk_id, "cost": cost}
                        else:
                            return {"success": False, "error": "Video generation timeout", "cost": 0}
                    else:
                        error_text = await response.text()
                        return {"success": False, "error": f"D-ID API error: {response.status} - {error_text}", "cost": 0}
        except Exception as e:
            logger.error(f"Exception during D-ID video generation: {e}", exc_info=True)
            return {"success": False, "error": str(e), "cost": 0}

    async def _poll_d_id_completion(self, talk_id: str, timeout: int = 300) -> Optional[str]:
        start_time = time.time()
        first_check = True
        while time.time() - start_time < timeout:
            try:
                # CORE.MD: Avoid initial sleep to get faster response for completed jobs.
                if not first_check:
                    await asyncio.sleep(10)
                first_check = False

                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        f"{self.d_id_base_url}/talks/{talk_id}",
                        headers={"Authorization": f"Basic {self.settings.d_id_api_key}"}
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            status = data.get("status")
                            if status == "done":
                                logger.info(f"✅ D-ID Talk {talk_id} completed successfully.")
                                return data.get("result_url")
                            elif status in ("created", "started"):
                                logger.info(f"D-ID Talk {talk_id} is still in progress with status: {status}")
                                continue
                            elif status == "error":
                                logger.error(f"D-ID Talk {talk_id} failed with error: {data.get('error')}")
                                return None
                        else:
                             logger.warning(f"Polling D-ID: Status {response.status}")

            except Exception as e:
                # REFRESH.MD: Log suppressed exceptions for better debugging.
                logger.error(f"Error polling D-ID for talk {talk_id}: {e}", exc_info=True)
                continue
        logger.error(f"D-ID generation timeout after {timeout} seconds for talk {talk_id}")
        return None

    def _get_voice_settings(self, voice_tone: str) -> Dict[str, float]:
        """Get voice settings based on tone"""
        settings_map = {
            "compassionate": {
                "stability": 0.85,
                "similarity_boost": 0.75,
                "style": 0.40,
                "use_speaker_boost": True
            },
            "wise": {
                "stability": 0.90,
                "similarity_boost": 0.80,
                "style": 0.25,
                "use_speaker_boost": True
            },
            "gentle": {
                "stability": 0.80,
                "similarity_boost": 0.70,
                "style": 0.50,
                "use_speaker_boost": True
            },
            "powerful": {
                "stability": 0.75,
                "similarity_boost": 0.85,
                "style": 0.20,
                "use_speaker_boost": True
            },
            "joyful": {
                "stability": 0.70,
                "similarity_boost": 0.75,
                "style": 0.60,
                "use_speaker_boost": True
            }
        }
        
        return settings_map.get(voice_tone, settings_map["compassionate"])
    
    def _get_avatar_style_config(self, avatar_style: str) -> Dict[str, Any]:
        style_configs = {
            # CORE.MD: Replace placeholder test URLs with a valid generic D-ID image URL.
            "traditional": {"source_url": "https://cdn.d-id.com/images/amy-jL0MeD3d.jpeg", "expressions": []},
            "modern": {"source_url": "https://cdn.d-id.com/images/amy-jL0MeD3d.jpeg", "expressions": []},
            "default": {"source_url": "https://cdn.d-id.com/images/amy-jL0MeD3d.jpeg", "expressions": []}
        }
        return style_configs.get(avatar_style, style_configs["default"])

    async def _get_d_id_default_expressions(self) -> Dict[str, Any]:
        return {"success": True, "data": {"expressions": []}}

    async def _store_avatar_session(
        self, session_id: str, user_email: str, guidance_text: str, avatar_style: str,
        voice_tone: str, video_url: Optional[str], audio_url: Optional[str],
        duration_seconds: int, voice_cost: float, video_cost: float, generation_time: float
    ):
        # CORE.MD: Fix database type mismatch by using raw SQL insert.
        query = """
            INSERT INTO avatar_sessions (
                session_id, user_email, guidance_text, avatar_style, voice_tone, 
                video_url, audio_url, duration_seconds, voice_cost, video_cost, 
                total_cost, generation_time, status, created_at, updated_at
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
        """
        now = datetime.now(timezone.utc)
        total_cost = voice_cost + video_cost
        
        async with self.db.get_connection() as connection:
            try:
                await connection.execute(
                    query, session_id, user_email, guidance_text, avatar_style, voice_tone,
                    video_url, audio_url, duration_seconds, voice_cost, video_cost,
                    total_cost, generation_time, 'completed', now, now
                )
                logger.info(f"✅ Avatar session {session_id} stored successfully.")
            except Exception as e:
                # REFRESH.MD: Log the exception details before re-raising.
                logger.error(f"❌ Failed to store avatar session {session_id}: {e}", exc_info=True)
                raise
    
    async def get_avatar_generation_status(self, session_id: str) -> Dict[str, Any]:
        """Get avatar generation status"""
        try:
            conn = await self.db.get_connection()
            
            result = await conn.fetchrow("""
                SELECT generation_status, video_url, audio_url, duration_seconds,
                       total_cost, generation_time_seconds, generation_completed_at
                FROM avatar_sessions 
                WHERE session_id = $1
            """, session_id)
            
            await self.db.release_connection(conn)
            
            if result:
                return {
                    "session_id": session_id,
                    "status": result["generation_status"],
                    "video_url": result["video_url"],
                    "audio_url": result["audio_url"],
                    "duration_seconds": result["duration_seconds"],
                    "total_cost": result["total_cost"],
                    "generation_time": result["generation_time_seconds"],
                    "completed_at": result["generation_completed_at"]
                }
            else:
                return {"session_id": session_id, "status": "not_found"}
                
        except Exception as e:
            logger.error(f"Failed to get avatar status: {e}")
            return {"session_id": session_id, "status": "error", "error": str(e)}
    
    async def create_swamiji_presenter(self) -> Dict[str, Any]:
        """Create or update Swamiji presenter in D-ID"""
        try:
            # This would typically involve uploading a photo of Swamiji
            # For now, we'll use a default presenter and customize it
            
            payload = {
                "name": "Swami Jyotirananthan",
                "description": "Tamil spiritual master and divine guide",
                "image_url": "https://create-images-results.d-id.com/DefaultPresenters/amy/image.jpeg",
                "voice_id": self.swamiji_voice_id,
                "background_color": "#8B4513"
            }
            
            headers = {
                "Authorization": f"Basic {self.settings.d_id_api_key}",
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.d_id_base_url}/presenters",
                    json=payload,
                    headers=headers
                ) as response:
                    
                    if response.status == 201:
                        result = await response.json()
                        self.swamiji_presenter_id = result["id"]
                        
                        logger.info(f"✅ Swamiji presenter created: {self.swamiji_presenter_id}")
                        return {
                            "success": True,
                            "presenter_id": self.swamiji_presenter_id,
                            "message": "Swamiji presenter created successfully"
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"Presenter creation error: {response.status} - {error_text}")
                        return {
                            "success": False,
                            "error": f"Presenter creation failed: {response.status}",
                            "message": "Using default presenter"
                        }
        
        except Exception as e:
            logger.error(f"Presenter creation exception: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Using default presenter"
            }
    
    async def test_avatar_services(self) -> Dict[str, Any]:
        """Test both D-ID and ElevenLabs connectivity"""
        results = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "services": {}
        }
        
        # Test ElevenLabs
        try:
            headers = {
                "xi-api-key": self.settings.elevenlabs_api_key
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.elevenlabs_base_url}/voices",
                    headers=headers
                ) as response:
                    
                    if response.status == 200:
                        voices = await response.json()
                        results["services"]["elevenlabs"] = {
                            "status": "connected",
                            "voices_available": len(voices.get("voices", [])),
                            "swamiji_voice_id": self.swamiji_voice_id
                        }
                    else:
                        results["services"]["elevenlabs"] = {
                            "status": "error",
                            "error": f"HTTP {response.status}"
                        }
        except Exception as e:
            results["services"]["elevenlabs"] = {
                "status": "error",
                "error": str(e)
            }
        
        # Test D-ID
        try:
            headers = {
                "Authorization": f"Basic {self.settings.d_id_api_key}"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.d_id_base_url}/talks",
                    headers=headers
                ) as response:
                    
                    if response.status == 200:
                        results["services"]["d_id"] = {
                            "status": "connected",
                            "presenter_id": self.swamiji_presenter_id
                        }
                    else:
                        results["services"]["d_id"] = {
                            "status": "error",
                            "error": f"HTTP {response.status}"
                        }
        except Exception as e:
            results["services"]["d_id"] = {
                "status": "error",
                "error": str(e)
            }
        
        return results

# Global instance
avatar_engine = SwamjiAvatarGenerationEngine()

# Export for use in other modules
__all__ = ["avatar_engine", "SwamjiAvatarGenerationEngine"]