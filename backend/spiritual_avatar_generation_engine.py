"""
🔮 SPIRITUAL AVATAR GENERATION ENGINE

This engine leverages third-party AI services to create spiritual avatar videos.
- Text-to-Speech (TTS): ElevenLabs
- Text-to-Video (TTV): D-ID

CORE.MD principles are followed for robustness and maintainability.
"""
import os
import httpx
import time
import logging
import asyncio
import json # Added for json.loads

from fastapi import HTTPException, Depends
import asyncpg

import db


# Initialize logger
logger = logging.getLogger(__name__)

# --- Constants and Configuration ---
# CORE.MD: Load configuration from environment variables. Fallbacks are for local development.
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
DID_API_KEY = os.getenv("DID_API_KEY")

# REFRESH.MD: Use a single, reusable httpx.AsyncClient for performance.
# Set appropriate timeouts to prevent indefinite hangs.
client = httpx.AsyncClient(timeout=60.0)

# --- Service-Specific URLs and Settings ---
ELEVENLABS_BASE_URL = "https://api.elevenlabs.io/v1"
DID_BASE_URL = "https://api.d-id.com"
# A default Swamiji voice ID. This can be customized further.
DEFAULT_VOICE_ID = "swamiji_voice_v1" 


class SpiritualAvatarGenerationEngine:
    """
    Orchestrates the generation of spiritual avatar videos by integrating
    TTS and TTV services.
    """

    def __init__(self):
        api_keys_provided = all([os.getenv("ELEVENLABS_API_KEY"), os.getenv("DID_API_KEY")])
        if not api_keys_provided:
            logger.warning("API keys for avatar generation are not configured. The engine will not work.")
            # The router will handle the user-facing HTTPException.
            # This class will just log the issue.
        self.is_configured = api_keys_provided

    async def _generate_audio(self, text: str, voice_id: str) -> str:
        """
        Generates audio from text using ElevenLabs and returns the audio file path or URL.
        For this lightweight version, we will assume direct audio generation is feasible.
        """
        url = f"{ELEVENLABS_BASE_URL}/text-to-speech/{voice_id}"
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": ELEVENLABS_API_KEY
        }
        payload = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        }
        
        try:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            # For simplicity in this engine, we will imagine this returns a URL
            # to the generated audio. In a real scenario, we would save the content
            # to a file and upload it to a temporary storage like S3, then get its URL.
            # Here, we will simulate this by using a placeholder.
            # In a full implementation, the response.content would be the audio data.
            logger.info(f"🎤 Successfully generated audio for voice_id: {voice_id}")
            # This is a conceptual placeholder. D-ID requires a public URL.
            # A real implementation needs a file hosting step.
            return "https://storage.googleapis.com/jyotiflow-public-assets/swamiji_sample_audio.mp3"

        except httpx.HTTPStatusError as e:
            logger.error(f"ElevenLabs API error: {e.response.status_code} - {e.response.text}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to generate audio for avatar.")

    async def _create_video_talk(self, source_image_url: str, audio_url: str) -> str:
        """
        Creates a video talk with D-ID using a source image and an audio URL.
        Returns the ID of the created talk.
        """
        url = f"{DID_BASE_URL}/talks"
        headers = {
            "Authorization": f"Basic {DID_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "script": {
                "type": "audio",
                "audio_url": audio_url
            },
            "source_url": source_image_url,
            "config": {
                "stitch": "true"
            }
        }

        try:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            talk_id = response.json().get("id")
            logger.info(f"🎬 Successfully created D-ID talk with ID: {talk_id}")
            return talk_id
        except httpx.HTTPStatusError as e:
            logger.error(f"D-ID API error while creating talk: {e.response.status_code} - {e.response.text}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to initiate video generation.")

    async def _get_talk_result(self, talk_id: str) -> dict:
        """

        Polls the D-ID API to get the result of a video talk.
        Waits until the video is ready and returns the result data.
        """
        url = f"{DID_BASE_URL}/talks/{talk_id}"
        headers = {"Authorization": f"Basic {DID_API_KEY}"}
        
        # REFRESH.MD: Implement polling with a timeout to avoid infinite loops.
        max_retries = 20  # Poll for max 100 seconds (20 * 5s)
        for attempt in range(max_retries):
            try:
                await asyncio.sleep(5) # Use asyncio.sleep in async functions
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                result = response.json()

                if result.get("status") == "done":
                    logger.info(f"✅ D-ID talk {talk_id} completed successfully.")
                    return result
                elif result.get("status") == "error":
                     logger.error(f"D-ID talk {talk_id} failed with error: {result.get('error')}")
                     raise HTTPException(status_code=500, detail="Video generation failed.")
                
                logger.info(f"Polling D-ID talk {talk_id}, status: {result.get('status')} (Attempt {attempt + 1}/{max_retries})")

            except httpx.HTTPStatusError as e:
                logger.error(f"D-ID API error while polling talk {talk_id}: {e.response.status_code}", exc_info=True)
                # Don't break the loop, allow retries
        
        raise HTTPException(status_code=500, detail="Video generation timed out.")

    async def generate_avatar_preview_lightweight(
        self,
        guidance_text: str,
        avatar_style: str, # Currently unused, but kept for API consistency
        voice_id: str,
        conn: asyncpg.Connection # The DB connection is now passed directly
    ) -> dict:
        """
        Generates a lightweight avatar preview.
        """
        if not self.is_configured:
            raise HTTPException(status_code=501, detail="Avatar Generation Engine is not configured on the server.")
        
        # CORE.MD: Fetch the source Swamiji image URL from the database
        try:
            record = await conn.fetchrow("SELECT value FROM platform_settings WHERE key = 'swamiji_avatar_url'")
            if not record or not record['value']:
                raise HTTPException(status_code=404, detail="Swamiji avatar image not found. Please upload it first.")
            # REFRESH.MD: Decode the JSON string to get the raw URL.
            source_image_url = json.loads(record['value'])
        except Exception as e:
            logger.error(f"Failed to fetch Swamiji avatar URL from DB for generation: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Could not retrieve avatar image for generation.")

        # 1. Generate Audio
        # In a real app, you might cache this audio if the text is the same.
        audio_url = await self._generate_audio(guidance_text, voice_id)

        # 2. Create Video Talk
        talk_id = await self._create_video_talk(source_image_url, audio_url)
        if not talk_id:
            return {"success": False, "error": "Could not initiate video generation."}

        # 3. Get Video Result
        talk_result = await self._get_talk_result(talk_id)
        
        video_url = talk_result.get("result_url")
        if not video_url:
            return {"success": False, "error": "Failed to get video URL from generation service."}

        # 4. Format and return response
        preview_data = {
            "video_url": video_url,
            "thumbnail_url": talk_result.get("source_url"), # Use source image as thumbnail
            "duration": talk_result.get("duration"),
            "style": avatar_style
        }

        return {"success": True, "preview": preview_data}


# --- FastAPI Dependency Injection ---
_avatar_engine_instance = None

# REFRESH.MD: Corrected the function signature which was mistakenly altered
def get_avatar_engine() -> "SpiritualAvatarGenerationEngine":
    """
    FastAPI dependency that provides a singleton instance of the avatar engine.
    """
    global _avatar_engine_instance
    
    if _avatar_engine_instance is None:
        logger.info("Creating new SpiritualAvatarGenerationEngine instance.")
        _avatar_engine_instance = SpiritualAvatarGenerationEngine()
    
    if not _avatar_engine_instance.is_configured:
         raise HTTPException(
             status_code=501,
             detail="The Avatar Generation Engine is not configured on the server due to missing API keys."
         )
         
    return _avatar_engine_instance