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
        avatar_style: str = "traditional",
        voice_tone: str = "compassionate",
        video_duration: int = 300
    ) -> Dict[str, Any]:
        """
        Generate complete avatar video with voice synthesis
        This is the main entry point for avatar generation
        """
        try:
            # Validate inputs
            if not guidance_text or len(guidance_text.strip()) < 10:
                raise ValueError("Guidance text too short")
            
            if video_duration > self.max_video_duration:
                raise ValueError(f"Duration exceeds maximum of {self.max_video_duration} seconds")
            
            # Check generation limits
            if self.current_generations >= self.max_concurrent_generations:
                raise ValueError("Maximum concurrent generations reached")
            
            self.current_generations += 1
            generation_start_time = time.time()
            
            logger.info(f"🎭 Starting avatar generation for session {session_id}")
            
            avatar_style_config = self._get_avatar_style_config(avatar_style)
            source_image_url = avatar_style_config.get("source_url")
            if not source_image_url:
                return {"success": False, "error": f"Source image URL not found for style '{avatar_style}'"}

            # CORE.MD: Restore text-to-speech fallback logic.
            # Use audio_url if present, otherwise fall back to generating audio from text.
            if audio_url:
                logger.info(f"🎵 Using provided audio URL: {audio_url}")
                script = {
                    "type": "audio",
                    "audio_url": audio_url
                }
            else:
                logger.info(f"🎵 Generating voice audio for text: '{guidance_text[:30]}...'")
                script = {
                    "type": "text",
                    "input": guidance_text,
                    "provider": {
                        "type": "elevenlabs",
                        "voice_id": self.settings.elevenlabs_voice_id or "onelab-voice-id"
                    }
                }
            
            # Get the default expressions for a talk
            default_expressions_response = await self._get_d_id_default_expressions()
            if not default_expressions_response.get("success"):
                return {"success": False, "error": "Could not retrieve D-ID default expressions."}
            
            # REFRESH.MD: Add validation to prevent KeyError/TypeError before accessing nested keys.
            default_data = default_expressions_response.get("data", {})
            if not isinstance(default_data, dict):
                default_data = {}
            
            default_expressions = default_data.get("expressions", [])
            if not isinstance(default_expressions, list):
                default_expressions = []

            avatar_expressions = avatar_style_config.get("expressions", [])
            if not isinstance(avatar_expressions, list):
                avatar_expressions = []

            final_expressions = default_expressions + avatar_expressions

            body = {
                "script": script,
                "source_url": source_image_url,
                "driver_expression": {
                    "expressions": final_expressions,
                    "transition_frames": 20
                },
                "config": {
                    "result_format": "mp4",
                    "stitch": True,
                },
                "user_data": f'{{"session_id": "{session_id}", "user_email": "{user_email}"}}'
            }
            
            logger.info("🎬 Generating avatar video...")
            # Make the API call to D-ID
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
                        # Video generation started successfully
                        talk_id = response_data["id"]
                        logger.info(f"🎬 Video generation started. Talk ID: {talk_id}")
                        
                        # Poll for completion
                        video_url = await self._poll_d_id_completion(talk_id)
                        
                        if video_url:
                            # Calculate cost (D-ID pricing: ~$0.12/minute)
                            estimated_minutes = len(text) / 150
                            cost = estimated_minutes * 0.12
                            
                            return {
                                "success": True,
                                "video_url": video_url,
                                "talk_id": talk_id,
                                "cost": cost
                            }
                        else:
                            return {
                                "success": False,
                                "error": "Video generation timeout",
                                "cost": 0
                            }
                    else:
                        error_text = await response.text()
                        logger.error(f"D-ID API error: {response.status} - {error_text}")
                        return {
                            "success": False,
                            "error": f"D-ID API error: {response.status}",
                            "cost": 0
                        }
        
        except Exception as e:
            logger.error(f"❌ Avatar generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "video_url": None,
                "audio_url": None,
                "generation_time": time.time() - generation_start_time if 'generation_start_time' in locals() else 0
            }
        
        finally:
            self.current_generations -= 1
    
    async def _generate_voice_audio(
        self, 
        text: str, 
        voice_tone: str, 
        session_id: str
    ) -> Dict[str, Any]:
        """Generate voice audio using ElevenLabs API"""
        try:
            # Voice settings based on tone
            voice_settings = self._get_voice_settings(voice_tone)
            
            # Prepare request payload
            payload = {
                "text": text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": voice_settings
            }
            
            # API headers
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.settings.elevenlabs_api_key
            }
            
            # Make API call
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.elevenlabs_base_url}/text-to-speech/{self.swamiji_voice_id}",
                    json=payload,
                    headers=headers
                ) as response:
                    
                    if response.status == 200:
                        # Save audio file
                        audio_content = await response.read()
                        audio_filename = f"voice_{session_id}_{uuid.uuid4().hex[:8]}.mp3"
                        audio_path = self.avatar_storage_path / audio_filename
                        
                        with open(audio_path, 'wb') as f:
                            f.write(audio_content)
                        
                        # Calculate cost (ElevenLabs pricing: ~$0.18/minute)
                        estimated_minutes = len(text) / 150  # ~150 chars per minute
                        cost = estimated_minutes * 0.18
                        
                        return {
                            "success": True,
                            "audio_url": f"/storage/avatars/{audio_filename}",
                            "audio_path": str(audio_path),
                            "cost": cost,
                            "duration_estimate": estimated_minutes * 60
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"ElevenLabs API error: {response.status} - {error_text}")
                        return {
                            "success": False,
                            "error": f"ElevenLabs API error: {response.status}",
                            "cost": 0
                        }
        
        except Exception as e:
            logger.error(f"Voice generation error: {e}")
            return {
                "success": False,
                "error": str(e),
                "cost": 0
            }

    async def _get_d_id_default_expressions(self) -> Dict[str, Any]:
        """
        Fetches the default expressions from D-ID API.
        REFRESH.MD: Implemented this missing method to prevent AttributeError.
        """
        url = f"{self.d_id_base_url}/expressions"
        headers = {
            "accept": "application/json",
            "authorization": f"Basic {self.settings.d_id_api_key}"
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info("Successfully fetched D-ID default expressions.")
                        return {"success": True, "data": data}
                    else:
                        error_text = await response.text()
                        logger.error(f"Failed to get D-ID default expressions. Status: {response.status}, Response: {error_text}")
                        return {"success": False, "error": f"D-ID API error: {response.status}"}
        except Exception as e:
            logger.error(f"Exception while fetching D-ID default expressions: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    async def _generate_avatar_video(
        self,
        text: str,
        audio_url: str,
        avatar_style: str,
        session_id: str
    ) -> Dict[str, Any]:
        """Generate avatar video using D-ID API"""
        try:
            # Prepare avatar configuration
            avatar_config = self._get_avatar_config(avatar_style)
            
            # Get the default expressions for a talk
            default_expressions_response = await self._get_d_id_default_expressions()
            if not default_expressions_response.get("success"):
                return {"success": False, "error": "Could not retrieve D-ID default expressions."}
            
            default_data = default_expressions_response.get("data", {})
            if not isinstance(default_data, dict):
                default_data = {}
            
            default_expressions = default_data.get("expressions", [])
            if not isinstance(default_expressions, list):
                default_expressions = []

            avatar_expressions = avatar_config.get("expressions", [])
            if not isinstance(avatar_expressions, list):
                avatar_expressions = []

            final_expressions = default_expressions + avatar_expressions

            body = {
                "script": {
                    "type": "audio",
                    "audio_url": audio_url
                },
                "source_url": avatar_config["presenter_image"],
                "driver_expression": {
                    "expressions": final_expressions,
                    "transition_frames": 20
                },
                "config": {
                    "result_format": "mp4",
                    "stitch": True,
                },
                "presenter_id": self.swamiji_presenter_id,
                "background": {
                    "type": "color",
                    "color": avatar_config["background_color"]
                }
            }
            
            # If we have custom audio, use it
            if audio_url and Path(audio_url).exists():
                body["script"] = {
                    "type": "audio",
                    "audio_url": audio_url
                }
            
            # API headers
            headers = {
                "Authorization": f"Basic {self.settings.d_id_api_key}",
                "Content-Type": "application/json"
            }
            
            # Create video generation job
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.d_id_base_url}/talks",
                    json=body,
                    headers=headers
                ) as response:
                    
                    if response.status == 201:
                        result = await response.json()
                        talk_id = result["id"]
                        
                        # Poll for completion
                        video_url = await self._poll_d_id_completion(talk_id)
                        
                        if video_url:
                            # Calculate cost (D-ID pricing: ~$0.12/minute)
                            estimated_minutes = len(text) / 150
                            cost = estimated_minutes * 0.12
                            
                            return {
                                "success": True,
                                "video_url": video_url,
                                "talk_id": talk_id,
                                "cost": cost
                            }
                        else:
                            return {
                                "success": False,
                                "error": "Video generation timeout",
                                "cost": 0
                            }
                    else:
                        error_text = await response.text()
                        logger.error(f"D-ID API error: {response.status} - {error_text}")
                        return {
                            "success": False,
                            "error": f"D-ID API error: {response.status}",
                            "cost": 0
                        }
        
        except Exception as e:
            logger.error(f"Video generation error: {e}")
            return {
                "success": False,
                "error": str(e),
                "cost": 0
            }
    
    async def _poll_d_id_completion(self, talk_id: str, max_wait: int = 300) -> Optional[str]:
        """Poll D-ID API for video completion"""
        headers = {
            "Authorization": f"Basic {self.settings.d_id_api_key}",
        }
        
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        f"{self.d_id_base_url}/talks/{talk_id}",
                        headers=headers
                    ) as response:
                        
                        if response.status == 200:
                            result = await response.json()
                            status = result.get("status")
                            
                            if status == "done":
                                return result.get("result_url")
                            elif status == "error":
                                logger.error(f"D-ID generation error: {result.get('error')}")
                                return None
                            elif status in ["created", "started"]:
                                # Still processing, wait and retry
                                await asyncio.sleep(10)
                                continue
                        else:
                            logger.error(f"D-ID polling error: {response.status}")
                            await asyncio.sleep(10)
                            continue
                            
            except Exception as e:
                logger.error(f"D-ID polling exception: {e}")
                await asyncio.sleep(10)
                continue
        
        logger.error(f"D-ID generation timeout after {max_wait} seconds")
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
    
    def _get_avatar_config(self, avatar_style: str) -> Dict[str, str]:
        """Get avatar configuration based on style"""
        config_map = {
            "traditional": {
                "presenter_image": "https://create-images-results.d-id.com/DefaultPresenters/amy/image.jpeg",
                "background_color": "#8B4513",  # Saddle brown
                "clothing_style": "traditional_robes"
            },
            "modern": {
                "presenter_image": "https://create-images-results.d-id.com/DefaultPresenters/amy/image.jpeg",
                "background_color": "#2F4F4F",  # Dark slate gray
                "clothing_style": "modern_spiritual"
            },
            "festival": {
                "presenter_image": "https://create-images-results.d-id.com/DefaultPresenters/amy/image.jpeg",
                "background_color": "#FF6347",  # Tomato
                "clothing_style": "festival_attire"
            },
            "meditation": {
                "presenter_image": "https://create-images-results.d-id.com/DefaultPresenters/amy/image.jpeg",
                "background_color": "#4682B4",  # Steel blue
                "clothing_style": "meditation_robes"
            }
        }
        
        return config_map.get(avatar_style, config_map["traditional"])
    
    async def _store_avatar_session(
        self,
        session_id: str,
        user_email: str,
        guidance_text: str,
        avatar_style: str,
        voice_tone: str,
        video_url: str,
        audio_url: str,
        duration_seconds: int,
        voice_cost: float,
        video_cost: float,
        generation_time: float
    ):
        """Store avatar generation session in database"""
        try:
            conn = await self.db.get_connection()
            
            await conn.execute("""
                INSERT INTO avatar_sessions 
                (session_id, user_email, avatar_prompt, voice_script, avatar_style, voice_tone,
                 generation_status, video_url, audio_url, duration_seconds, 
                 d_id_cost, elevenlabs_cost, total_cost, generation_time_seconds,
                 generation_completed_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
            """, 
                session_id, user_email, f"Avatar style: {avatar_style}", guidance_text,
                avatar_style, voice_tone, "completed", video_url, audio_url, duration_seconds,
                video_cost, voice_cost, voice_cost + video_cost, generation_time,
                datetime.now(timezone.utc)
            )
            
            await self.db.release_connection(conn)
            logger.info(f"📊 Avatar session stored: {session_id}")
            
        except Exception as e:
            logger.error(f"Failed to store avatar session: {e}")
    
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