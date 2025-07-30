"""
🎨 STABILITY AI SERVICE

This service provides a centralized interface for interacting with the Stability.ai API
for text-to-image generation. It follows CORE.MD and REFRESH.MD principles.
"""

import os
import base64
import logging
import httpx
import binascii # REFRESH.MD: Import for specific exception handling on base64 decoding.
from typing import AsyncGenerator, Optional
import asyncio

from fastapi import HTTPException

# Initialize logger
logger = logging.getLogger(__name__)

# --- Constants ---
# REFRESH.MD: Centralize API configuration constants.
API_HOST = os.getenv("STABILITY_API_HOST", "https://api.stability.ai")
# CORE.MD: Use a masking-capable engine ID.
ENGINE_ID = "stable-diffusion-xl-1024-v1-0"

class StabilityAiService:
    def __init__(self):
        self.api_key = os.getenv("STABILITY_API_KEY")
        self.api_host = os.getenv("STABILITY_API_HOST", "https://api.stability.ai")
        # REFRESH.MD: Use the correct engine ID for image inpainting/masking.
        self.engine_id = "stable-diffusion-xl-1024-v1-0"
        self.is_configured = bool(self.api_key)
        self._async_client: Optional[httpx.AsyncClient] = None
        # REFRESH.MD: Add a lock to prevent race conditions during client initialization.
        self._client_lock = asyncio.Lock()

        if not self.is_configured:
            logger.warning("Stability.ai API key is not configured. Image generation service is disabled.")

    async def get_client(self) -> httpx.AsyncClient:
        """Provides a lazily initialized, thread-safe httpx.AsyncClient instance."""
        if self._async_client is None or self._async_client.is_closed:
            async with self._client_lock:
                # Double-check locking pattern
                if self._async_client is None or self._async_client.is_closed:
                    self._async_client = httpx.AsyncClient(timeout=90.0)
        return self._async_client

    async def close_client(self):
        """Closes the client if it's open."""
        if self._async_client and not self._async_client.is_closed:
            await self._async_client.aclose()
            logger.info("Stability.ai service client closed.")
    
    # CORE.MD: Refactored from inpainting to a more suitable image-to-image generation.
    async def generate_image_from_image(self, image_bytes: bytes, text_prompt: str, negative_prompt: Optional[str] = None, image_strength: float = 0.6) -> bytes:
        """
        Generates an image using the Stability.ai image-to-image endpoint,
        which is better suited for theme generation than masking.
        """
        if not self.is_configured:
            raise HTTPException(status_code=501, detail="Image generation service is not configured.")

        # --- Input Validation ---
        if not isinstance(image_bytes, bytes):
            raise HTTPException(status_code=400, detail="Image must be provided as bytes.")
        if not text_prompt or not isinstance(text_prompt, str) or len(text_prompt.strip()) == 0:
            raise HTTPException(status_code=400, detail="Text prompt cannot be empty.")
        if not 0.0 <= image_strength <= 1.0:
            raise HTTPException(status_code=400, detail="Image strength must be between 0.0 and 1.0.")

        # --- API Request ---
        # CORE.MD: Switched to the more appropriate image-to-image endpoint.
        url = f"{self.api_host}/v1/generation/{self.engine_id}/image-to-image"
        
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        # REFRESH.MD: Correctly structure the multipart/form-data request for image-to-image.
        files = {
            'init_image': ('init_image.png', image_bytes, 'image/png'),
        }
        
        data = {
            "image_strength": str(image_strength),
            "init_image_mode": "IMAGE_STRENGTH",
            "text_prompts[0][text]": text_prompt,
            "text_prompts[0][weight]": 1.0,
            "cfg_scale": 7,
            "style_preset": "photographic",
            "samples": 1,
            "steps": 30,
        }
        
        # REFRESH.MD: Add negative prompt to the request if provided.
        if negative_prompt:
            data["text_prompts[1][text]"] = negative_prompt
            data["text_prompts[1][weight]"] = -1.0


        max_retries = 3
        base_delay = 1  # in seconds

        for attempt in range(max_retries):
            try:
                client = await self.get_client()
                # REFRESH.MD: Pass files and data correctly to the httpx client.
                response = await client.post(url, headers=headers, files=files, data=data)

                # REFRESH.MD: Log the response text on error for better debugging.
                if response.status_code == 429 and attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)
                    logger.warning(f"Rate limit exceeded. Retrying in {delay} seconds... (Attempt {attempt + 1}/{max_retries})")
                    await asyncio.sleep(delay)
                    continue

                if response.status_code != 200:
                    logger.error(f"Stability.ai API error: {response.status_code} - {response.text}")
                response.raise_for_status()

                # REFRESH.MD: Correctly parse the JSON response and decode the base64 image.
                response_data = response.json()
                artifacts = response_data.get("artifacts")
                
                # CORE.MD: Add type checking to prevent TypeError if the artifact is not a dict.
                if not artifacts or not isinstance(artifacts, list) or not isinstance(artifacts[0], dict) or "base64" not in artifacts[0]:
                    raise HTTPException(status_code=500, detail="Invalid response from image generation service.")
                
                image_base64 = artifacts[0]["base64"]
                
                try:
                    image_bytes = base64.b64decode(image_base64)
                except (binascii.Error, TypeError) as e:
                    logger.error(f"Failed to decode base64 image from Stability.ai: {e}", exc_info=True)
                    raise HTTPException(status_code=500, detail="Could not decode image data from generation service.") from e

                logger.info("✅ Successfully generated image from image.")
                return image_bytes

            except HTTPException:
                # CORE.MD: Re-raise HTTPException to preserve specific error messages.
                raise
            except httpx.HTTPStatusError as e:
                # CORE.MD: Only retry on 429 (Too Many Requests). For other client/server errors, fail immediately.
                if e.response.status_code == 429 and attempt < max_retries - 1:
                    # This is the expected path for rate limiting, no need to log an error, just a warning.
                    pass
                else:
                    # For non-429 errors or if it's the last attempt, log and re-raise.
                    logger.error(f"Stability.ai API error: {e.response.status_code} - {e.response.text}", exc_info=True)
                    raise HTTPException(status_code=500, detail=f"Failed to generate image: {e.response.text}") from e
            
            except httpx.RequestError as e:
                # REFRESH.MD: Handle specific network errors.
                logger.error(f"Network error while contacting Stability.ai for image generation: {e}", exc_info=True)
                raise HTTPException(status_code=502, detail="A network error occurred while generating the image.") from e
            except Exception as e:
                logger.error(f"An unexpected error occurred during image generation: {e}", exc_info=True)
                raise HTTPException(status_code=500, detail="An unexpected error occurred during image generation.") from e
        
        # This part will be reached only if all retries fail with a non-HTTPStatusError that we didn't re-raise
        raise HTTPException(status_code=500, detail="Failed to generate image after multiple attempts.")


# --- FastAPI Dependency Injection ---
# REFRESH.MD: Refactored to a generator-based dependency to manage the client lifecycle.
async def get_stability_service() -> AsyncGenerator['StabilityAiService', None]:
    """FastAPI dependency provider for StabilityAiService."""
    service = StabilityAiService()
    try:
        yield service
    finally:
        # REFRESH.MD: Use the dedicated close_client method for proper encapsulation.
        await service.close_client() 