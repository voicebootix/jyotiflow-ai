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

from fastapi import HTTPException

# Initialize logger
logger = logging.getLogger(__name__)

# --- Constants ---
# REFRESH.MD: Centralize API configuration constants.
API_HOST = os.getenv("STABILITY_API_HOST", "https://api.stability.ai")
ENGINE_ID = "stable-diffusion-v1-6" # Using the latest stable version

class StabilityAiService:
    def __init__(self):
        self.api_key = os.getenv("STABILITY_API_KEY")
        self.api_host = API_HOST
        self.engine_id = ENGINE_ID
        self.is_configured = bool(self.api_key)
        self._async_client: Optional[httpx.AsyncClient] = None

        if not self.is_configured:
            logger.warning("Stability.ai API key is not configured. Image generation service is disabled.")

    async def get_client(self) -> httpx.AsyncClient:
        """Provides a lazily initialized httpx.AsyncClient instance."""
        if self._async_client is None or self._async_client.is_closed:
            self._async_client = httpx.AsyncClient(timeout=90.0)
        return self._async_client

    async def close_client(self):
        """Closes the client if it's open."""
        if self._async_client and not self._async_client.is_closed:
            await self._async_client.aclose()
            logger.info("Stability.ai service client closed.")
    
    async def inpaint_image(self, image_bytes: bytes, mask_bytes: bytes, text_prompt: str) -> bytes:
        """
        Inpaints an image using the Stability.ai API's masking endpoint.
        """
        if not self.is_configured:
            raise HTTPException(status_code=501, detail="Image generation service is not configured.")

        # --- Input Validation ---
        if not all(isinstance(arg, bytes) for arg in [image_bytes, mask_bytes]):
            raise HTTPException(status_code=400, detail="Image and mask must be provided as bytes.")
        if not text_prompt or not isinstance(text_prompt, str) or len(text_prompt.strip()) == 0:
            raise HTTPException(status_code=400, detail="Text prompt cannot be empty.")

        # --- API Request ---
        url = f"{self.api_host}/v1/generation/{self.engine_id}/image-to-image/masking"
        
        headers = {
            "Accept": "image/png",
            "Authorization": f"Bearer {self.api_key}"
        }

        # CORE.MD: Correctly structure the multipart form data for httpx.
        files = {
            'init_image': ('init_image.png', image_bytes, 'image/png'),
            'mask_image': ('mask_image.png', mask_bytes, 'image/png')
        }
        data = {
            'mask_source': 'MASK_IMAGE_BLACK',
            'text_prompts[0][text]': text_prompt,
            'cfg_scale': '7',
            'samples': '1',
            'steps': '30',
        }
        
        try:
            client = await self.get_client()
            response = await client.post(url, headers=headers, data=data, files=files)
            response.raise_for_status()
            logger.info("✅ Successfully inpainted image.")
            return response.content

        except httpx.HTTPStatusError as e:
            logger.error(f"Stability.ai API error during inpainting: {e.response.status_code} - {e.response.text}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Failed to inpaint image: {e.response.text}") from e
        except Exception as e:
            logger.error(f"An unexpected error occurred during inpainting: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="An unexpected error occurred during inpainting.") from e


# --- FastAPI Dependency Injection ---
# REFRESH.MD: Refactored to a generator-based dependency to manage the client lifecycle.
async def get_stability_service() -> AsyncGenerator[StabilityAiService, None]:
    """
    FastAPI dependency that provides a request-scoped instance of the StabilityAiService
    and ensures its resources are properly cleaned up.
    """
    service = StabilityAiService()
    try:
        yield service
    finally:
        # Ensures the client is closed even if errors occur.
        if service._async_client and not service._async_client.is_closed:
            await service._async_client.aclose() 