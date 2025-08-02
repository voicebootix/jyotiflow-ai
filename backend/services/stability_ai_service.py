"""
🎨 STABILITY AI SERVICE

This service provides a centralized interface for interacting with the Stability.ai API
for text-to-image and image-to-image generation, including masking. 
It follows CORE.MD and REFRESH.MD principles.
"""

import os
import base64
import logging
import httpx
import binascii
from typing import AsyncGenerator, Optional
import asyncio

from fastapi import HTTPException

# Initialize logger
logger = logging.getLogger(__name__)

# --- Constants ---
API_HOST = os.getenv("STABILITY_API_HOST", "https://api.stability.ai")
# REFRESH.MD: Use the engine ID that supports inpainting/masking.
ENGINE_ID = "stable-diffusion-xl-1024-v1-0"
MASKING_ENGINE_ID = "stable-diffusion-v2-2-2-inpainting" # A dedicated engine for masking

class StabilityAiService:
    def __init__(self):
        self.api_key = os.getenv("STABILITY_API_KEY")
        self.api_host = os.getenv("STABILITY_API_HOST", "https://api.stability.ai")
        self.engine_id = ENGINE_ID
        self.masking_engine_id = MASKING_ENGINE_ID
        self.is_configured = bool(self.api_key)
        self._async_client: Optional[httpx.AsyncClient] = None
        self._client_lock = asyncio.Lock()

        if not self.is_configured:
            logger.warning("Stability.ai API key is not configured. Image generation service is disabled.")

    async def get_client(self) -> httpx.AsyncClient:
        """Provides a lazily initialized, thread-safe httpx.AsyncClient instance."""
        if self._async_client is None or self._async_client.is_closed:
            async with self._client_lock:
                if self._async_client is None or self._async_client.is_closed:
                    self._async_client = httpx.AsyncClient(timeout=90.0)
        return self._async_client

    async def close_client(self):
        """Closes the client if it's open."""
        if self._async_client and not self._async_client.is_closed:
            await self._async_client.aclose()
            logger.info("Stability.ai service client closed.")
    
    async def generate_image_with_mask(
        self, 
        image_bytes: bytes, 
        mask_bytes: bytes, 
        text_prompt: str, 
        negative_prompt: Optional[str] = None
    ) -> bytes:
        """
        Generates an image using the Stability.ai image-to-image masking endpoint.
        This preserves the masked (black) area of the image while regenerating the rest.
        """
        if not self.is_configured:
            raise HTTPException(status_code=501, detail="Image generation service is not configured.")

        # --- Input Validation (CORE.MD) ---
        if not isinstance(image_bytes, bytes) or not isinstance(mask_bytes, bytes):
            raise HTTPException(status_code=400, detail="Initial image and mask must be provided as bytes.")
        if not text_prompt or not isinstance(text_prompt, str) or len(text_prompt.strip()) == 0:
            raise HTTPException(status_code=400, detail="Text prompt cannot be empty.")

        # --- API Request ---
        url = f"{self.api_host}/v1/generation/{self.masking_engine_id}/image-to-image/masking"
        
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        files = {
            'init_image': ('init_image.png', image_bytes, 'image/png'),
            'mask_image': ('mask_image.png', mask_bytes, 'image/png'),
        }
        
        data = {
            "mask_source": "MASK_IMAGE_BLACK",
            "text_prompts[0][text]": text_prompt,
            "text_prompts[0][weight]": 1.0,
            "cfg_scale": 10,
            "samples": 1,
            "steps": 40,
        }
        
        if negative_prompt:
            data["text_prompts[1][text]"] = negative_prompt
            data["text_prompts[1][weight]"] = -1.0

        max_retries = 3
        base_delay = 1

        for attempt in range(max_retries):
            try:
                client = await self.get_client()
                response = await client.post(url, headers=headers, files=files, data=data)
                response.raise_for_status()

                response_data = response.json()
                artifacts = response_data.get("artifacts")
                
                if not artifacts or not isinstance(artifacts, list):
                    raise HTTPException(status_code=500, detail="Invalid artifacts from masking service.")
                
                if not isinstance(artifacts[0], dict) or "base64" not in artifacts[0]:
                    raise HTTPException(status_code=500, detail="Invalid artifact structure in masking response.")
                
                image_base64 = artifacts[0]["base64"]
                
                try:
                    decoded_image_bytes = base64.b64decode(image_base64)
                except (binascii.Error, TypeError) as e:
                    logger.error(f"Failed to decode base64 image from Stability.ai masking: {e}", exc_info=True)
                    raise HTTPException(status_code=500, detail="Could not decode masked image data.") from e

                logger.info("✅ Successfully generated image with masking.")
                return decoded_image_bytes

            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429 and attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)
                    logger.warning(f"Rate limit exceeded (429) on masking. Retrying in {delay}s...")
                    await asyncio.sleep(delay)
                    continue
                else:
                    logger.error(f"Stability.ai masking API failed: {e.response.status_code} - {e.response.text}", exc_info=True)
                    raise HTTPException(status_code=500, detail=f"Failed to generate masked image: {e.response.text}") from e
            
            except HTTPException:
                raise
            except httpx.RequestError as e:
                logger.error(f"Network error on masking: {e}", exc_info=True)
                raise HTTPException(status_code=502, detail="A network error occurred during masking.") from e
            except Exception as e:
                logger.error(f"Unexpected error during masking: {e}", exc_info=True)
                raise HTTPException(status_code=500, detail="An unexpected error occurred during masking.") from e
        
        raise HTTPException(status_code=500, detail="Failed to generate masked image after all retries.")

    async def generate_image_from_text(self, text_prompt: str, negative_prompt: Optional[str] = None) -> bytes:
        """
        Generates an image using the Stability.ai text-to-image endpoint.
        """
        if not self.is_configured:
            raise HTTPException(status_code=501, detail="Image generation service is not configured.")

        if not text_prompt or not isinstance(text_prompt, str) or len(text_prompt.strip()) == 0:
            raise HTTPException(status_code=400, detail="Text prompt cannot be empty.")

        url = f"{self.api_host}/v1/generation/{self.engine_id}/text-to-image"
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        payload = {
            "text_prompts": [
                {"text": text_prompt, "weight": 1.0}
            ],
            "cfg_scale": 10,
            "height": 1024,
            "width": 1024,
            "samples": 1,
            "steps": 30,
        }
        
        if negative_prompt:
            payload["text_prompts"].append({"text": negative_prompt, "weight": -1.0})

        max_retries = 3
        base_delay = 1

        for attempt in range(max_retries):
            try:
                client = await self.get_client()
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()

                response_data = response.json()
                artifacts = response_data.get("artifacts")
                
                if not artifacts or not isinstance(artifacts, list):
                    raise HTTPException(status_code=500, detail="Invalid or empty artifacts received from image generation service.")
                
                if not isinstance(artifacts[0], dict) or "base64" not in artifacts[0]:
                    raise HTTPException(status_code=500, detail="Invalid artifact structure in response.")
                
                image_base64 = artifacts[0]["base64"]
                
                try:
                    image_bytes = base64.b64decode(image_base64)
                except (binascii.Error, TypeError) as e:
                    logger.error(f"Failed to decode base64 image from Stability.ai: {e}", exc_info=True)
                    raise HTTPException(status_code=500, detail="Could not decode image data from generation service.") from e

                logger.info("✅ Successfully generated image from text.")
                return image_bytes

            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429 and attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)
                    logger.warning(f"Rate limit exceeded (429). Retrying in {delay} seconds... (Attempt {attempt + 1}/{max_retries})")
                    await asyncio.sleep(delay)
                    continue
                else:
                    logger.error(f"Stability.ai API request failed: {e.response.status_code} - {e.response.text}", exc_info=True)
                    raise HTTPException(status_code=500, detail=f"Failed to generate image: {e.response.text}") from e
            
            except HTTPException:
                raise
            except httpx.RequestError as e:
                logger.error(f"Network error while contacting Stability.ai: {e}", exc_info=True)
                raise HTTPException(status_code=502, detail="A network error occurred while generating the image.") from e

            except Exception as e:
                logger.error(f"An unexpected error occurred during text-to-image generation: {e}", exc_info=True)
                raise HTTPException(status_code=500, detail="An unexpected error occurred during image generation.") from e
        
        raise HTTPException(status_code=500, detail="Failed to generate image after all retries.")


# --- FastAPI Dependency Injection ---
async def get_stability_service() -> AsyncGenerator['StabilityAiService', None]:
    """FastAPI dependency provider for StabilityAiService."""
    service = StabilityAiService()
    try:
        yield service
    finally:
        await service.close_client()
