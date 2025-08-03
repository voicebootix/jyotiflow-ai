"""
🎨 STABILITY AI SERVICE
This service provides a centralized interface for interacting with the Stability.ai API
for both text-to-image generation and image inpainting.

It follows CORE.MD and REFRESH.MD principles.

ENVIRONMENT VARIABLES:
- STABILITY_API_KEY: Required for all Stability.ai services.
"""

import os
import base64
import logging
import httpx
import binascii
import json
from typing import AsyncGenerator, Optional
import asyncio

from fastapi import HTTPException
from PIL import Image
import io

# Initialize logger
logger = logging.getLogger(__name__)

# --- Constants ---
STABILITY_AI_HOST = "https://api.stability.ai"
TEXT_TO_IMAGE_ENGINE_ID = "stable-diffusion-xl-1024-v1-0" 

# API Keys
STABILITY_API_KEY = os.getenv("STABILITY_API_KEY")


class StabilityAiService:
    def __init__(self):
        self.api_key = STABILITY_API_KEY
        self.is_configured = bool(self.api_key)

        self._async_client: Optional[httpx.AsyncClient] = None
        self._client_lock = asyncio.Lock()

        if not self.is_configured:
            logger.warning("STABILITY_API_KEY not configured. All Stability.ai services will be disabled.")

    async def get_client(self) -> httpx.AsyncClient:
        if self._async_client is None or self._async_client.is_closed:
            async with self._client_lock:
                if self._async_client is None or self._async_client.is_closed:
                    # Set a longer timeout for potentially slow AI operations
                    self._async_client = httpx.AsyncClient(timeout=180.0)
        return self._async_client

    async def close_client(self):
        if self._async_client and not self._async_client.is_closed:
            await self._async_client.aclose()
            logger.info("Shared Stability AI service client closed.")
    
    async def generate_image_with_mask(
        self, 
        init_image_bytes: bytes, 
        mask_image_bytes: bytes, 
        text_prompt: str, 
        negative_prompt: Optional[str] = None
    ) -> bytes:
        """
        Generates an image using the Stability.ai v2beta inpainting endpoint.
        This method sends image and mask data as binary content in a multipart/form-data request.
        """
        if not self.is_configured:
            raise HTTPException(status_code=501, detail="Image inpainting service is not configured (missing STABILITY_API_KEY).")

        if not text_prompt or not isinstance(text_prompt, str) or len(text_prompt.strip()) == 0:
            raise HTTPException(status_code=400, detail="Text prompt cannot be empty.")

        # v2beta inpainting endpoint
        url = f"{STABILITY_AI_HOST}/v2beta/stable-image/edit/inpaint"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "image/*, application/json" # Request images on success, JSON on errors
        }

        # CORE.MD: DEBUG - Log file sizes before sending to API
        init_size_kb = len(init_image_bytes) / 1024
        mask_size_kb = len(mask_image_bytes) / 1024
        logger.info(f"Sending to Stability.ai - Init image: {init_size_kb:.1f}KB | Mask: {mask_size_kb:.1f}KB")
        
        # REFRESH.MD: FIX - Correctly format the files for httpx multipart/form-data.
        files = {
            'image': ('init_image.png', init_image_bytes, 'image/png'),
            'mask': ('mask_image.png', mask_image_bytes, 'image/png')
        }
        
        data = {
            "prompt": text_prompt,
            "output_format": "png",
        }
        
        if negative_prompt:
            data["negative_prompt"] = negative_prompt

        max_retries = 3
        base_delay = 2

        for attempt in range(max_retries):
            try:
                client = await self.get_client()
                logger.info(f"Posting to Stability.ai inpainting API, attempt {attempt + 1}")
                
                response = await client.post(url, headers=headers, files=files, data=data)
                
                # REFRESH.MD: FIX - Check for any 2xx success status code, not just 200.
                if 200 <= response.status_code < 300:
                    result_size_kb = len(response.content) / 1024
                    logger.info(f"✅ Inpainting generation successful with status {response.status_code}.")
                    logger.info(f"✅ Generated image size: {result_size_kb:.1f}KB | Content-Type: {response.headers.get('content-type', 'unknown')}")
                    return response.content

                # For any other status, raise an exception to be handled below.
                response.raise_for_status()

            except httpx.HTTPStatusError as e:
                # Try to parse the error response as JSON, otherwise use the raw text
                try:
                    error_details = e.response.json()
                    error_message = error_details.get("message", json.dumps(error_details))
                except json.JSONDecodeError:
                    error_message = e.response.text

                logger.error(f"Inpainting API HTTP error - Status: {e.response.status_code}, Response: {error_message}")

                if e.response.status_code == 429 and attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)
                    logger.warning(f"Rate limit exceeded (429). Retrying in {delay}s...")
                    await asyncio.sleep(delay)
                    continue
                else:
                    raise HTTPException(status_code=e.response.status_code, detail=f"Inpainting API Call Failed: {error_message}") from e
            
            except Exception as e:
                logger.error(f"Unexpected error during inpainting: {e}", exc_info=True)
                raise HTTPException(status_code=500, detail="An unexpected error occurred during inpainting.") from e
        
        raise HTTPException(status_code=500, detail="Failed to generate inpainted image after all retries.")

    async def generate_image_to_image(
        self, 
        init_image_bytes: bytes, 
        text_prompt: str, 
        negative_prompt: Optional[str] = None,
        strength: float = 0.35
    ) -> bytes:
        """
        Generates an image using the Stability.ai v2beta image-to-image endpoint.
        This method preserves the identity/structure of the init image while applying theme changes.
        
        Args:
            init_image_bytes: The base image to transform
            text_prompt: The prompt describing desired changes
            negative_prompt: What to avoid in the generation
            strength: Denoising strength (0.0-1.0). Lower values preserve more of original image.
                     0.3-0.4 recommended for identity preservation with theme changes.
        """
        if not self.is_configured:
            raise HTTPException(status_code=501, detail="Image-to-image service is not configured (missing STABILITY_API_KEY).")

        if not text_prompt or not isinstance(text_prompt, str) or len(text_prompt.strip()) == 0:
            raise HTTPException(status_code=400, detail="Text prompt cannot be empty.")

        if not (0.0 <= strength <= 1.0):
            raise HTTPException(status_code=400, detail="Strength must be between 0.0 and 1.0.")

        # v2beta image-to-image endpoint (using Ultra for img2img)
        url = f"{STABILITY_AI_HOST}/v2beta/stable-image/generate/ultra"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "image/*, application/json"
        }

        # CORE.MD: DEBUG - Log parameters for img2img
        init_size_kb = len(init_image_bytes) / 1024
        logger.info(f"Img2img - Init image: {init_size_kb:.1f}KB | Strength: {strength} | Prompt: {text_prompt[:100]}...")
        
        # Format files for httpx multipart/form-data
        files = {
            'image': ('init_image.png', init_image_bytes, 'image/png')
        }
        
        data = {
            "prompt": text_prompt,
            "strength": strength,
            "output_format": "png"
        }
        
        if negative_prompt:
            data["negative_prompt"] = negative_prompt

        max_retries = 3
        base_delay = 2

        for attempt in range(max_retries):
            try:
                client = await self.get_client()
                logger.info(f"Posting to Stability.ai img2img API, attempt {attempt + 1}")
                
                response = await client.post(url, headers=headers, files=files, data=data)
                
                if 200 <= response.status_code < 300:
                    result_size_kb = len(response.content) / 1024
                    logger.info(f"✅ Img2img generation successful with status {response.status_code}.")
                    logger.info(f"✅ Generated image size: {result_size_kb:.1f}KB | Content-Type: {response.headers.get('content-type', 'unknown')}")
                    return response.content

                response.raise_for_status()

            except httpx.HTTPStatusError as e:
                try:
                    error_details = e.response.json()
                    error_message = error_details.get("message", json.dumps(error_details))
                except json.JSONDecodeError:
                    error_message = e.response.text

                logger.error(f"Img2img API HTTP error - Status: {e.response.status_code}, Response: {error_message}")

                if e.response.status_code == 429 and attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)
                    logger.warning(f"Rate limit exceeded (429). Retrying in {delay}s...")
                    await asyncio.sleep(delay)
                    continue
                else:
                    raise HTTPException(status_code=e.response.status_code, detail=f"Img2img API Call Failed: {error_message}") from e
            
            except Exception as e:
                logger.error(f"Unexpected error during img2img: {e}", exc_info=True)
                raise HTTPException(status_code=500, detail="An unexpected error occurred during image-to-image generation.") from e
        
        raise HTTPException(status_code=500, detail="Failed to generate img2img image after all retries.")

    async def generate_image_from_text(self, text_prompt: str, negative_prompt: Optional[str] = None) -> bytes:
        """
        Generates an image using the Stability.ai v1 text-to-image endpoint.
        """
        if not self.is_configured:
            raise HTTPException(status_code=501, detail="Text-to-image service is not configured (missing STABILITY_API_KEY).")

        if not text_prompt or not isinstance(text_prompt, str) or len(text_prompt.strip()) == 0:
            raise HTTPException(status_code=400, detail="Text prompt cannot be empty.")

        url = f"{STABILITY_AI_HOST}/v1/generation/{TEXT_TO_IMAGE_ENGINE_ID}/text-to-image"
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        payload = {
            "text_prompts": [{"text": text_prompt, "weight": 1.0}],
            "cfg_scale": 10, "height": 1024, "width": 1024,
            "samples": 1, "steps": 30,
        }
        
        if negative_prompt:
            payload["text_prompts"].append({"text": negative_prompt, "weight": -1.0})

        max_retries = 3
        base_delay = 1

        for attempt in range(max_retries):
            try:
                client = await self.get_client()
                response = await client.post(url, headers=headers, json=payload)
                
                # REFRESH.MD: FIX - Also check for any 2xx success status code here.
                if 200 <= response.status_code < 300:
                    response_data = response.json()
                    artifacts = response_data.get("artifacts")
                    if not artifacts or not isinstance(artifacts, list):
                        raise HTTPException(status_code=500, detail="Invalid artifacts from Stability.ai text2image")
                    
                    image_base64 = artifacts[0]["base64"]
                    
                    try:
                        return base64.b64decode(image_base64)
                    except (binascii.Error, TypeError) as e:
                        raise HTTPException(status_code=500, detail="Could not decode image data from Stability.ai text2image") from e
                
                # For any other status, raise an exception.
                response.raise_for_status()

            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429 and attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)
                    await asyncio.sleep(delay)
                    continue
                else:
                    error_response = e.response.text
                    raise HTTPException(status_code=e.response.status_code, detail=f"Text-to-image API Error: {error_response}") from e
            except Exception as e:
                logger.error(f"Unexpected error during text-to-image generation: {e}", exc_info=True)
                raise HTTPException(status_code=500, detail="An unexpected error occurred during image generation.") from e
        
        raise HTTPException(status_code=500, detail="Failed to generate image from text after all retries.")

# --- FastAPI Dependency Injection ---
async def get_stability_service() -> AsyncGenerator['StabilityAiService', None]:
    """FastAPI dependency provider for StabilityAiService."""
    service = StabilityAiService()
    try:
        yield service
    finally:
        await service.close_client()
