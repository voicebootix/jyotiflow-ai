"""
🎨 STABILITY AI SERVICE & STABLE DIFFUSION API

This service provides a centralized interface for interacting with two distinct APIs:
1. Stability.ai API for text-to-image generation.
2. StableDiffusionAPI.com for image inpainting.

It follows CORE.MD and REFRESH.MD principles.

ENVIRONMENT VARIABLES:
- STABILITY_API_KEY: Required for the original text-to-image endpoint.
- STABLE_DIFFUSION_API_KEY: Recommended for the inpainting endpoint. Falls back to STABILITY_API_KEY if not set.

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
# REFRESH.MD: FIX - Unified hosts and added a dedicated key for the new API with a fallback.
STABILITY_AI_HOST = "https://api.stability.ai"
STABLE_DIFFUSION_API_HOST = "https://stablediffusionapi.com/api/v3"

# Used for the text-to-image endpoint via Stability.ai
ENGINE_ID = "stable-diffusion-xl-1024-v1-0" 

# API Keys
STABILITY_API_KEY = os.getenv("STABILITY_API_KEY")
STABLE_DIFFUSION_API_KEY = os.getenv("STABLE_DIFFUSION_API_KEY", STABILITY_API_KEY)


class StabilityAiService:
    def __init__(self):
        # REFRESH.MD: FIX - Validate presence of API keys for each service.
        self.stability_api_key = STABILITY_API_KEY
        self.stable_diffusion_api_key = STABLE_DIFFUSION_API_KEY
        
        self.is_text_to_image_configured = bool(self.stability_api_key)
        self.is_inpainting_configured = bool(self.stable_diffusion_api_key)

        self._async_client: Optional[httpx.AsyncClient] = None
        self._client_lock = asyncio.Lock()

        if not self.is_text_to_image_configured:
            logger.warning("STABILITY_API_KEY not configured. Text-to-image service will be disabled.")
        if not self.is_inpainting_configured:
            logger.warning("STABLE_DIFFUSION_API_KEY not configured. Inpainting service will be disabled.")

    async def get_client(self) -> httpx.AsyncClient:
        if self._async_client is None or self._async_client.is_closed:
            async with self._client_lock:
                if self._async_client is None or self._async_client.is_closed:
                    self._async_client = httpx.AsyncClient(timeout=180.0)
        return self._async_client

    async def close_client(self):
        if self._async_client and not self._async_client.is_closed:
            await self._async_client.aclose()
            logger.info("Shared AI service client closed.")
    
    async def generate_image_with_mask(
        self, 
        init_image_url: str, 
        mask_image_url: str, 
        text_prompt: str, 
        negative_prompt: Optional[str] = None
    ) -> bytes:
        """
        REFRESH.MD: FIX - Migrated to use image URLs instead of base64 data for the inpainting endpoint.
        """
        if not self.is_inpainting_configured:
            raise HTTPException(status_code=501, detail="Image inpainting service is not configured.")

        if not text_prompt or not isinstance(text_prompt, str) or len(text_prompt.strip()) == 0:
            raise HTTPException(status_code=400, detail="Text prompt cannot be empty.")

        url = f"{STABLE_DIFFUSION_API_HOST}/inpaint"
        
        payload = {
            "key": self.stable_diffusion_api_key,
            "prompt": text_prompt,
            "negative_prompt": negative_prompt,
            "init_image": init_image_url,
            "mask_image": mask_image_url,
            "width": "1024", # The API works best with standard sizes
            "height": "1024",
            "samples": "1",
            "num_inference_steps": "21",
            "safety_checker": "no",
            "enhance_prompt": "yes",
            "guidance_scale": 7.5,
            "strength": 0.7,
            "base64": "no", # We will fetch the URL, so no base64 needed in response
            "webhook": None,
            "track_id": None,
        }
        
        headers = {"Content-Type": "application/json"}
        max_retries = 3
        base_delay = 2

        for attempt in range(max_retries):
            try:
                client = await self.get_client()
                logger.info(f"Posting to inpainting API with URLs, attempt {attempt + 1}")
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                response_data = response.json()

                if response_data.get("status") == "success":
                    logger.info("✅ Inpainting generation successful.")
                    if response_data.get("output") and isinstance(response_data["output"], list) and len(response_data["output"]) > 0:
                        image_url = response_data["output"][0]
                        logger.info(f"Fetching generated image from URL: {image_url}")
                        image_response = await client.get(image_url)
                        image_response.raise_for_status()
                        return image_response.content
                    else:
                        raise HTTPException(status_code=500, detail="API response missing image output URL.")

                elif response_data.get("status") == "processing":
                    # Handle async processing by polling
                    processing_id = response_data.get("id")
                    logger.warning(f"Inpainting is processing (ID: {processing_id}). Will poll for result.")
                    fetch_url = f"{STABLE_DIFFUSION_API_HOST}/fetch/{processing_id}"
                    for _ in range(20): # Poll for up to 100 seconds
                        await asyncio.sleep(5)
                        fetch_response = await client.post(fetch_url, json={"key": self.stable_diffusion_api_key})
                        fetch_data = fetch_response.json()
                        if fetch_data.get("status") == "success":
                            logger.info("✅ Polling successful, image generated.")
                            if fetch_data.get("output"):
                                image_url = fetch_data["output"][0]
                                image_response = await client.get(image_url)
                                image_response.raise_for_status()
                                return image_response.content
                            else:
                                raise HTTPException(status_code=500, detail="Polling response missing image URL.")
                    raise HTTPException(status_code=504, detail="Inpainting timed out after polling.")
                
                else:
                    error_detail = response_data.get("message", "Unknown API error")
                    logger.error(f"Inpainting API returned status '{response_data.get('status')}': {error_detail}")
                    raise HTTPException(status_code=500, detail=f"Inpainting API Error: {error_detail}")

            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429 and attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)
                    logger.warning(f"Rate limit exceeded (429). Retrying in {delay}s...")
                    await asyncio.sleep(delay)
                    continue
                else:
                    error_response = e.response.text
                    logger.error(f"Inpainting API HTTP error - Status: {e.response.status_code}, Response: {error_response}")
                    raise HTTPException(status_code=500, detail=f"Inpainting API Call Failed: {error_response}") from e
            
            except Exception as e:
                logger.error(f"Unexpected error during inpainting: {e}", exc_info=True)
                raise HTTPException(status_code=500, detail="An unexpected error occurred during inpainting.") from e
        
        raise HTTPException(status_code=500, detail="Failed to generate inpainted image after all retries.")

    async def generate_image_from_text(self, text_prompt: str, negative_prompt: Optional[str] = None) -> bytes:
        """
        Generates an image using the original Stability.ai text-to-image endpoint.
        """
        if not self.is_text_to_image_configured:
            raise HTTPException(status_code=501, detail="Text-to-image service is not configured.")

        if not text_prompt or not isinstance(text_prompt, str) or len(text_prompt.strip()) == 0:
            raise HTTPException(status_code=400, detail="Text prompt cannot be empty.")

        url = f"{STABILITY_AI_HOST}/v1/generation/{ENGINE_ID}/text-to-image"
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {self.stability_api_key}"
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
                response.raise_for_status()
                response_data = response.json()
                
                artifacts = response_data.get("artifacts")
                if not artifacts or not isinstance(artifacts, list):
                    raise HTTPException(status_code=500, detail="Invalid artifacts from Stability.ai text2image")
                
                image_base64 = artifacts[0]["base64"]
                
                try:
                    return base64.b64decode(image_base64)
                except (binascii.Error, TypeError) as e:
                    raise HTTPException(status_code=500, detail="Could not decode image data from Stability.ai text2image") from e

            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429 and attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)
                    await asyncio.sleep(delay)
                    continue
                else:
                    error_response = e.response.text
                    raise HTTPException(status_code=500, detail=f"Text-to-image API Error: {error_response}") from e
            except Exception as e:
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
