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
from app_settings import AppSettings
from ..database.database_manager import DatabaseManager
from ..core.dependencies import get_app_settings, get_database_manager

logger = logging.getLogger(__name__)

class SpiritualAvatarGenerationEngine:
    """
    Complete Avatar Generation Engine for Swami Jyotirananthan
    Real D-ID + ElevenLabs Integration
    """
    
    def __init__(self, settings: AppSettings, db_session_manager: DatabaseManager):
        self.settings = settings
        self.db = db_session_manager
        self.d_id_base_url = "https://api.d-id.com"
        
        # REFRESH.MD: Consolidate all configuration assignments into the constructor.
        self.max_concurrent_generations = getattr(self.settings, 'avatar_max_concurrent_generations', 5)
        self.current_generations = 0
        self.max_video_duration = getattr(self.settings, 'avatar_max_video_duration', 300)
        self.swamiji_voice_id = getattr(self.settings, 'elevenlabs_voice_id', 'onelab-voice-id')
        self.swamiji_presenter_id = "amy-jcu8YUbZbKt8EXOlXG7je"
        
        if not self.settings.d_id_api_key or "your-did-api-key" in self.settings.d_id_api_key:
            logger.warning("D-ID API key is not configured.")
        if not self.settings.elevenlabs_api_key or "your-elevenlabs-api-key" in self.settings.elevenlabs_api_key:
            logger.warning("ElevenLabs API key is not configured.")

        # Swamiji Avatar Configuration
        # self.swamiji_presenter_id = "amy-jcu8YUbZbKt8EXOlXG7je"  # D-ID presenter ID
        
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
        # CORE.MD: Restore input validation.
        if not guidance_text or len(guidance_text.strip()) < 10:
            return {"success": False, "error": "Guidance text must be at least 10 characters long."}
        if video_duration > self.max_video_duration:
            return {"success": False, "error": f"Video duration cannot exceed {self.max_video_duration} seconds."}

        # CORE.MD: Restore concurrency limiting.
        if self.current_generations >= self.max_concurrent_generations:
            logger.warning("Max concurrent avatar generations reached. Request queued/rejected.")
            return {"success": False, "error": "Maximum concurrent generations reached. Please try again later."}

        generation_start_time = time.time()
        try:
            self.current_generations += 1
            logger.info(f"🎭 Starting avatar generation for session {session_id}. Current generations: {self.current_generations}")

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
        finally:
            # REFRESH.MD: Ensure concurrency counter is always decremented.
            self.current_generations -= 1
            logger.info(f"Avatar generation process finished for session {session_id}. Current generations: {self.current_generations}")

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
                        # CORE.MD: Use the initialized attribute for consistency.
                        "voice_id": self.swamiji_voice_id
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
            # CORE.MD: Update with unique and valid source URLs for visual variety.
            "traditional": {"source_url": "https://clips-presenters.d-id.com/jane/image.jpeg", "expressions": []},
            "modern": {"source_url": "https://clips-presenters.d-id.com/christopher/image.jpeg", "expressions": []},
            "default": {"source_url": "https://clips-presenters.d-id.com/amy/image.jpeg", "expressions": []}
        }
        return style_configs.get(avatar_style, style_configs["default"])

    async def _get_d_id_default_expressions(self) -> Dict[str, Any]:
        return {"success": True, "data": {"expressions": []}}

    async def _store_avatar_session(
        self, session_id: str, user_email: str, guidance_text: str, avatar_style: str,
        voice_tone: str, video_url: Optional[str], audio_url: Optional[str],
        duration_seconds: int, voice_cost: float, video_cost: float, generation_time: float
    ):
        # CORE.MD: Align query with database schema and fix connection management.
        query = """
            INSERT INTO avatar_sessions (
                session_id, user_email, voice_script, avatar_style, voice_tone, 
                video_url, audio_url, duration_seconds, elevenlabs_cost, d_id_cost, 
                total_cost, generation_time, generation_status, created_at, updated_at
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
        """
        now = datetime.now(timezone.utc)
        total_cost = voice_cost + video_cost
        
        connection = None
        try:
            connection = await self.db.get_connection()
            await connection.execute(
                query, session_id, user_email, guidance_text, avatar_style, voice_tone,
                video_url, audio_url, duration_seconds, voice_cost, video_cost,
                total_cost, generation_time, 'completed', now, now
            )
            logger.info(f"✅ Avatar session {session_id} stored successfully.")
        except Exception as e:
            logger.error(f"❌ Failed to store avatar session {session_id}: {e}", exc_info=True)
            raise
        finally:
            if connection:
                await self.db.release_connection(connection)
    
    async def get_avatar_generation_status(self, session_id: str) -> Dict[str, Any]:
        """
        Retrieves the status of an avatar generation task from the database.
        """
        # CORE.MD: Fix column name mismatch and standardize connection management.
        query = "SELECT generation_status, video_url FROM avatar_sessions WHERE session_id = $1"
        connection = None
        try:
            connection = await self.db.get_connection()
            row = await connection.fetchrow(query, session_id)
            if row:
                return {"success": True, "status": row['generation_status'], "video_url": row['video_url']}
            else:
                return {"success": False, "error": "Session not found."}
        except Exception as e:
            logger.error(f"Error fetching avatar status for session {session_id}: {e}", exc_info=True)
            return {"success": False, "error": "Database error."}
        finally:
            if connection:
                await self.db.release_connection(connection)
    
    async def create_swamiji_presenter(self) -> Dict[str, Any]:
        """
        Creates a new D-ID presenter for Swamiji using a source image URL.
        This is typically a one-time setup operation.
        """
        source_url = "https://your-image-hosting.com/swamiji-presenter-image.jpeg"
        
        headers = {
            "Authorization": f"Basic {self.settings.d_id_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "source_url": source_url,
            "name": "Swamiji"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.d_id_base_url}/presenters", json=payload, headers=headers) as response:
                if response.status == 201:
                    presenter_data = await response.json()
                    self.swamiji_presenter_id = presenter_data["id"]
                    logger.info(f"✅ Swamiji presenter created with ID: {self.swamiji_presenter_id}")
                    return {"success": True, "presenter_id": self.swamiji_presenter_id}
                else:
                    error_text = await response.text()
                    logger.error(f"Failed to create Swamiji presenter: {response.status} - {error_text}")
                    return {"success": False, "error": f"D-ID API error: {response.status}"}
    
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

def get_avatar_engine(
    settings: AppSettings = Depends(get_app_settings),
    db_manager: DatabaseManager = Depends(get_database_manager)
) -> SpiritualAvatarGenerationEngine:
    """
    Dependency injector for the SpiritualAvatarGenerationEngine.
    Creates a single instance and caches it for the application's lifespan.
    """
    # This is a simple way to cache the engine instance.
    # For a more robust solution in a larger app, you might use a more
    # sophisticated caching mechanism tied to the app's lifecycle.
    if not hasattr(get_avatar_engine, "engine_instance"):
        logger.info("Initializing SpiritualAvatarGenerationEngine instance...")
        get_avatar_engine.engine_instance = SpiritualAvatarGenerationEngine(settings, db_manager)
    return get_avatar_engine.engine_instance

# Export for use in other modules
__all__ = ["SpiritualAvatarGenerationEngine", "get_avatar_engine"]