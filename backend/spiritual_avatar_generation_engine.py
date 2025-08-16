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
import uuid # REFRESH.MD: Added to generate unique filenames for audio
from typing import List, Dict, Optional # Added for List and Dict type hints

from fastapi import HTTPException, Depends
import asyncpg

# Import the new LoRA Avatar Service
from .lora_avatar_service import LoraAvatarService, get_lora_avatar_service

# REFRESH.MD: Removed unused 'db' import for code cleanup.

# REFRESH.MD: Import storage service to handle audio uploads dynamically.
try:
    from services.supabase_storage_service import SupabaseStorageService, get_storage_service
    STORAGE_SERVICE_AVAILABLE = True
except ImportError:
    STORAGE_SERVICE_AVAILABLE = False
    class SupabaseStorageService: pass
    def get_storage_service():
        raise HTTPException(status_code=501, detail="Storage service is not available.")


# Initialize logger
logger = logging.getLogger(__name__)

# --- Constants and Configuration ---
# CORE.MD: Load configuration from environment variables. Fallbacks are for local development.
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
DID_API_KEY = os.getenv("D_ID_API_KEY")

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

    def __init__(self, storage_service: "SupabaseStorageService", lora_avatar_service: "LoraAvatarService"):
        self.did_configured = all([os.getenv("ELEVENLABS_API_KEY"), os.getenv("D_ID_API_KEY")])
        self.lora_configured = lora_avatar_service.is_configured
        
        if not self.did_configured:
            logger.warning("D-ID/ElevenLabs API keys are not configured. Standard avatar generation will not work.")
        if not self.lora_configured:
            logger.warning("LoRA Avatar Service is not configured. LoRA-based avatar generation will not work.")

        self.is_configured = self.did_configured or self.lora_configured
        self.storage_service = storage_service
        self.lora_avatar_service = lora_avatar_service

    async def _generate_lora_avatar_image(self, prompt: str, negative_prompt: str) -> bytes:
        """Generates an avatar image using the LoRA service."""
        # For now, we use a static base image. This could be made dynamic later.
        base_image_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'swamiji_base_image.png')
        try:
            with open(base_image_path, "rb") as f:
                image_bytes = f.read()
        except FileNotFoundError:
            logger.error(f"Base image for LoRA not found at {base_image_path}")
            raise HTTPException(status_code=500, detail="Base image for LoRA avatar not found.")

        return await self.lora_avatar_service.generate_avatar_image(
            prompt=prompt,
            negative_prompt=negative_prompt,
            input_image_bytes=image_bytes
        )

    async def _generate_audio(self, text: str, voice_id: str) -> str:
        """
        Generates audio from text using ElevenLabs, uploads it to storage,
        and returns the public URL.
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
            
            # REFRESH.MD: Instead of returning a hardcoded URL, upload the real audio data.
            audio_content = response.content
            # CORE.MD: Use uuid to ensure unique filenames and prevent overwrites.
            file_name_in_bucket = f"public/generated_audio_{uuid.uuid4()}.mp3"
            bucket_name = "avatars"

            # CORE.MD: Removed 'await' as the underlying Supabase client library's
            # upload method is synchronous, not asynchronous.
            public_url = self.storage_service.upload_file(
                bucket_name=bucket_name,
                file_path_in_bucket=file_name_in_bucket,
                file=audio_content,
                content_type="audio/mpeg"
            )
            
            logger.info(f"🎤 Successfully generated and uploaded audio to: {public_url}")
            return public_url

        except httpx.HTTPStatusError as e:
            logger.error(f"ElevenLabs API error: {e.response.status_code} - {e.response.text}", exc_info=True)
            # CORE.MD: Use 'from e' for proper exception chaining and improved debugging.
            raise HTTPException(status_code=500, detail="Failed to generate audio for avatar.") from e
        except Exception as e:
            logger.error(f"Failed to upload generated audio: {e}", exc_info=True)
            # CORE.MD: Use 'from e' for proper exception chaining.
            raise HTTPException(status_code=500, detail="Failed to store generated audio.") from e

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
            # CORE.MD: Use 'from e' for proper exception chaining.
            raise HTTPException(status_code=500, detail="Failed to initiate video generation.") from e

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

    async def get_available_voices(self) -> List[Dict[str, str]]:
        """
        Retrieves the list of available voices from the ElevenLabs API.
        """
        if not self.is_configured:
            logger.warning("Cannot fetch voices, avatar engine is not configured.")
            return []

        url = f"{ELEVENLABS_BASE_URL}/voices"
        headers = {"xi-api-key": ELEVENLABS_API_KEY}

        try:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            voices_data = response.json().get("voices", [])
            
            # REFRESH.MD: Refactored to a for-loop for robust and readable parsing of voice data.
            formatted_voices = []
            for voice in voices_data:
                labels = voice.get("labels")
                gender_raw = "unknown"
                # CORE.MD: Check if 'labels' is a dictionary to prevent AttributeErrors.
                if isinstance(labels, dict):
                    gender_raw = labels.get("gender")

                # CORE.MD: Check if the final gender value is a string before calling .lower().
                gender_str = "unknown"
                if isinstance(gender_raw, str):
                    gender_str = gender_raw

                formatted_voices.append({
                    "id": voice["voice_id"],
                    "name": voice["name"],
                    # This is now safe from all identified edge cases (None, non-dict, non-str).
                    "gender": gender_str.lower()
                })

            logger.info(f"Successfully fetched {len(formatted_voices)} voices from ElevenLabs.")
            return formatted_voices

        except httpx.HTTPStatusError as e:
            logger.error(f"ElevenLabs API error while fetching voices: {e.response.status_code}", exc_info=True)
            # Return empty list on failure, so the frontend doesn't break.
            return []
        except Exception as e:
            logger.error(f"An unexpected error occurred while fetching voices: {e}", exc_info=True)
            return []

    async def generate_avatar_preview_lightweight(
        self,
        guidance_text: str,
        # REFRESH.MD: The avatar_style parameter is no longer used and has been removed.
        voice_id: str,
        source_image_url: str 
    ) -> dict:
        """
        Generates a lightweight avatar preview.
        """
        if not self.is_configured:
            raise HTTPException(status_code=501, detail="Avatar Generation Engine is not configured on the server.")
        
        # CORE.MD: The source Swamiji image URL is now a direct parameter.
        # This decouples the engine from the database and makes it more flexible.
        if not source_image_url:
            raise HTTPException(status_code=400, detail="A source image URL must be provided.")

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
            "style": "daily_theme" # REFRESH.MD: Hardcode the style as it's now always dynamic.
        }

        return {"success": True, "preview": preview_data}


    async def generate_complete_avatar_video(
        self,
        session_id: str,
        user_email: str,
        guidance_text: str,
        service_type: str,
        avatar_style: str,
        voice_tone: str,
        video_duration: int,
        source_image_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Orchestrates the full avatar generation process, choosing the correct engine.
        """
        if not self.is_configured:
            raise HTTPException(status_code=501, detail="Avatar Generation Engine is not configured.")

        start_time = time.time()

        # Decide which generation path to take
        if avatar_style == "lora_spiritual":
            if not self.lora_configured:
                raise HTTPException(status_code=501, detail="LoRA avatar generation is not configured on the server.")
            
            # This path is currently image-only. Video generation would be a separate step.
            # For now, we return the image URL in place of a video URL.
            logger.info(f"Starting LoRA-based avatar generation for session {session_id}")
            prompt = f"A spiritual master {voice_tone}, in a {service_type} setting. {guidance_text[:100]}"
            negative_prompt = "cartoon, unrealistic, blurry, low quality"
            
            image_bytes = await self._generate_lora_avatar_image(prompt, negative_prompt)
            
            # Upload the generated image to storage
            file_name_in_bucket = f"public/generated_lora_avatars/{session_id}.png"
            image_url = self.storage_service.upload_file(
                bucket_name="avatars",
                file_path_in_bucket=file_name_in_bucket,
                file=image_bytes,
                content_type="image/png"
            )
            
            processing_time = time.time() - start_time
            logger.info(f"✅ LoRA avatar generation for {session_id} complete in {processing_time:.2f}s. Image at: {image_url}")

            return {
                "success": True,
                "video_url": image_url, # Returning image URL as video_url for now
                "processing_time": processing_time
            }
        else:
            # Default to D-ID video generation
            if not self.did_configured:
                raise HTTPException(status_code=501, detail="Standard avatar generation is not configured on the server.")
            if not source_image_url:
                raise HTTPException(status_code=400, detail="A source image URL is required for standard avatar generation.")

            logger.info(f"Starting D-ID based avatar generation for session {session_id}")
            audio_url = await self._generate_audio(guidance_text, voice_id=DEFAULT_VOICE_ID)
            talk_id = await self._create_video_talk(source_image_url, audio_url)
            talk_result = await self._get_talk_result(talk_id)
            
            video_url = talk_result.get("result_url")
            if not video_url:
                raise HTTPException(status_code=500, detail="Failed to get final video URL.")

            processing_time = time.time() - start_time
            logger.info(f"✅ D-ID avatar generation for {session_id} complete in {processing_time:.2f}s.")

            return {
                "success": True,
                "video_url": video_url,
                "processing_time": processing_time
            }


# --- FastAPI Dependency Injection ---

# REFRESH.MD: Refactored to remove the flawed singleton pattern.
# A new instance is created per request, which is FastAPI's recommended approach
# for handling dependencies, avoiding state-related issues and static analysis warnings.
def get_avatar_engine(
    storage_service: SupabaseStorageService = Depends(get_storage_service),
    lora_avatar_service: LoraAvatarService = Depends(get_lora_avatar_service)
) -> "SpiritualAvatarGenerationEngine":
    """
    FastAPI dependency that provides a request-scoped instance of the avatar engine.
    This ensures each request gets a fresh instance with its own dependencies.
    """
    engine = SpiritualAvatarGenerationEngine(
        storage_service=storage_service,
        lora_avatar_service=lora_avatar_service
    )
    
    if not engine.is_configured:
         raise HTTPException(
             status_code=501,
             detail="The Avatar Generation Engine is not configured on the server due to missing API keys."
         )
         
    return engine