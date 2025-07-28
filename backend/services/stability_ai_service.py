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

# CORE.MD: Load configuration from environment variables.
STABILITY_API_KEY = os.getenv("STABILITY_API_KEY")
API_HOST = os.getenv("STABILITY_API_HOST", "https://api.stability.ai")
ENGINE_ID = "stable-diffusion-xl-1024-v1-0"

class StabilityAiService:
    """
    A service class to manage text-to-image generation with Stability.ai.
    Manages the lifecycle of the httpx.AsyncClient.
    """

    def __init__(self):
        self.is_configured = bool(STABILITY_API_KEY)
        if not self.is_configured:
            logger.warning("Stability.ai API key is not configured. Image generation service is disabled.")
        # REFRESH.MD: Lazy initialization of the client.
        self._client: httpx.AsyncClient | None = None

    @property
    def client(self) -> httpx.AsyncClient:
        """Provides a lazily initialized httpx.AsyncClient instance."""
        if self._client is None:
            # CORE.MD: The client is instantiated on first use.
            self._client = httpx.AsyncClient(timeout=90.0)
        return self._client

    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit. Ensures the client is closed."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            logger.info("Stability.ai service client closed.")

    async def generate_image(self, text_prompt: str) -> bytes:
        """
        Generates an image from a text prompt using the Stability.ai API.
        """
        if not self.is_configured:
            raise HTTPException(status_code=501, detail="Image generation service is not configured.")

        # CORE.MD: Add input validation for the text prompt.
        if not text_prompt or not isinstance(text_prompt, str) or len(text_prompt.strip()) == 0:
            raise HTTPException(status_code=400, detail="Text prompt cannot be empty.")
        if len(text_prompt) > 2000: # Stability API has a limit
            raise HTTPException(status_code=400, detail="Text prompt is too long.")

        url = f"{API_HOST}/v1/generation/{ENGINE_ID}/text-to-image"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {STABILITY_API_KEY}",
        }
        payload = {
            "steps": 40,
            "width": 1024,
            "height": 1024,
            "seed": 0,
            "cfg_scale": 5,
            "samples": 1,
            # CORE.MD: Removed style_preset from the payload as it might not be supported by all models
            # and could be the cause of the 400 Bad Request error. The prompt is descriptive enough.
            "text_prompts": [
                {"text": text_prompt, "weight": 1},
                {"text": "blurry, bad, disfigured, poor quality, distorted", "weight": -1}
            ],
        }

        try:
            response = await self.client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            response_data = response.json()
            artifacts = response_data.get("artifacts")
            
            if not artifacts or not isinstance(artifacts, list) or "base64" not in artifacts[0]:
                raise HTTPException(status_code=500, detail="Invalid response from image generation service.")
            
            image_base64 = artifacts[0]["base64"]
            
            # CORE.MD: Add robust error handling for base64 decoding.
            try:
                image_bytes = base64.b64decode(image_base64)
            except (binascii.Error, TypeError) as e:
                logger.error(f"Failed to decode base64 image from Stability.ai: {e}", exc_info=True)
                raise HTTPException(status_code=500, detail="Could not decode image data from generation service.") from e

            logger.info("✅ Successfully generated image from text prompt.")
            return image_bytes

        except httpx.HTTPStatusError as e:
            logger.error(f"Stability.ai API error: {e.response.status_code} - {e.response.text}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to generate image from Stability.ai.") from e
        except Exception as e:
            logger.error(f"An unexpected error occurred during image generation: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="An unexpected error occurred while generating the image.") from e

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
        engine_id = "stable-diffusion-v1-6"
        url = f"{self.api_host}/v1/generation/{engine_id}/image-to-image/masking"
        
        headers = {
            "Accept": "image/png",
            "Authorization": f"Bearer {self.api_key}"
        }

        form_data = {
            'init_image': image_bytes,
            'mask_image': mask_bytes,
            'mask_source': 'MASK_IMAGE_BLACK',
            'text_prompts[0][text]': text_prompt,
            'cfg_scale': '7',
            'samples': '1',
            'steps': '30',
        }
        
        try:
            client = await self.get_client()
            response = await client.post(url, headers=headers, files=form_data)
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
        if service._client and not service._client.is_closed:
            await service._client.aclose() 