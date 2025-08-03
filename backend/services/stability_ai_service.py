"""
🎨 STABILITY AI SERVICE

RESTORED: This service provides a centralized interface for interacting with the Stability.ai API
for text-to-image and image-to-image generation, including masking/inpainting.
It follows CORE.MD and REFRESH.MD principles.

ENVIRONMENT VARIABLES:
- STABILITY_API_KEY: Required API key for Stability.ai
  Get your API key from: https://platform.stability.ai/

FACE PRESERVATION:
- Black mask areas (0) = Preserved (Swamiji's face protected)
- White mask areas (255) = Modified (background changed)
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
# REFRESH.MD: Migrated to new StableDiffusionAPI.com endpoint
API_HOST = "https://stablediffusionapi.com/api/v3"
ENGINE_ID = "stable-diffusion-xl-1024-v1-0"  # This might be for a different API now
INPAINTING_ENGINE_ID = "stable-diffusion-xl-1024-v1-0" # Legacy, not used by new inpaint API
API_KEY = os.getenv("STABILITY_API_KEY")

def _resize_image_if_needed(image_bytes: bytes, max_pixels: int = 1048576) -> bytes:
    """
    Resize image if it exceeds the maximum pixel count for StabilityAI API.
    Max pixels: 1,048,576 (typically 1024x1024)
    
    CORE.MD: Robust handling of edge cases and format preservation
    REFRESH.MD: Exception chaining for better debugging
    """
    try:
        image = Image.open(io.BytesIO(image_bytes))
        width, height = image.size
        current_pixels = width * height
        original_format = image.format or 'PNG'
        
        if current_pixels <= max_pixels:
            logger.info(f"Image size OK: {width}x{height} = {current_pixels} pixels")
            return image_bytes
        
        ratio = (max_pixels / current_pixels) ** 0.5
        new_width = int(width * ratio)
        new_height = int(height * ratio)
        
        new_width = max(new_width, 1)
        new_height = max(new_height, 1)
        
        adjusted_pixels = new_width * new_height
        if adjusted_pixels > max_pixels:
            logger.warning(f"Minimum dimensions ({new_width}x{new_height}={adjusted_pixels}) exceed pixel limit {max_pixels}")
            max_dimension = int(max_pixels ** 0.5)
            if width >= height:
                new_width = max_dimension
                new_height = max(1, int(max_dimension * height / width))
            else:
                new_height = max_dimension
                new_width = max(1, int(max_dimension * width / height))
            logger.info(f"Adjusted to square-based dimensions: {new_width}x{new_height}")
        
        temp_width = new_width - (new_width % 2) if new_width > 1 else new_width
        temp_height = new_height - (new_height % 2) if new_height > 1 else new_height
        
        if temp_width * temp_height <= max_pixels and temp_width > 0 and temp_height > 0:
            new_width = temp_width
            new_height = temp_height
        
        logger.info(f"Resizing image from {width}x{height} ({current_pixels}) to {new_width}x{new_height} ({new_width*new_height})")
        
        resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        output_bytes = io.BytesIO()
        save_format = original_format if original_format in ['JPEG', 'PNG', 'WEBP'] else 'PNG'
        resized_image.save(output_bytes, format=save_format)
        
        logger.info(f"Image resized and saved in {save_format} format")
        return output_bytes.getvalue()
        
    except Exception as e:
        logger.error(f"Failed to resize image: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=f"Failed to process image: {e}") from e

def _resize_image_and_mask_synchronized(image_bytes: bytes, mask_bytes: bytes, max_pixels: int = 1048576) -> tuple[bytes, bytes]:
    """
    Resize image and mask to identical dimensions ensuring perfect synchronization.
    CORE.MD: Prevents dimension mismatch that causes API rejections
    REFRESH.MD: Synchronized processing for spatial correspondence
    """
    try:
        image = Image.open(io.BytesIO(image_bytes))
        mask = Image.open(io.BytesIO(mask_bytes))
        
        original_image_format = image.format or 'PNG'
        original_mask_format = mask.format or 'PNG'
        logger.info(f"Original formats - Image: {original_image_format}, Mask: {original_mask_format}")
        
        image_width, image_height = image.size
        mask_width, mask_height = mask.size
        image_pixels = image_width * image_height
        mask_pixels = mask_width * mask_height
        
        if image_pixels >= mask_pixels:
            ref_width, ref_height = image_width, image_height
            ref_pixels = image_pixels
            logger.info(f"Using image dimensions as reference: {ref_width}x{ref_height}")
        else:
            ref_width, ref_height = mask_width, mask_height
            ref_pixels = mask_pixels
            logger.info(f"Using mask dimensions as reference: {ref_width}x{ref_height}")
        
        if ref_pixels <= max_pixels:
            if image_width != ref_width or image_height != ref_height:
                logger.info(f"Resizing image to match reference: {ref_width}x{ref_height}")
                image = image.resize((ref_width, ref_height), Image.Resampling.LANCZOS)
            if mask_width != ref_width or mask_height != ref_height:
                logger.info(f"Resizing mask to match reference: {ref_width}x{ref_height}")
                mask = mask.resize((ref_width, ref_height), Image.Resampling.LANCZOS)
            
            image_output = io.BytesIO()
            mask_output = io.BytesIO()
            
            save_format_image = original_image_format if original_image_format in ['JPEG', 'PNG', 'WEBP'] else 'PNG'
            save_format_mask = original_mask_format if original_mask_format in ['JPEG', 'PNG', 'WEBP'] else 'PNG'
            
            image.save(image_output, format=save_format_image)
            mask.save(mask_output, format=save_format_mask)
            
            return image_output.getvalue(), mask_output.getvalue()
        
        ratio = (max_pixels / ref_pixels) ** 0.5
        new_width = int(ref_width * ratio)
        new_height = int(ref_height * ratio)
        
        new_width = max(new_width, 1)
        new_height = max(new_height, 1)
        
        adjusted_pixels = new_width * new_height
        if adjusted_pixels > max_pixels:
            logger.warning(f"Synchronized dimensions ({new_width}x{new_height}={adjusted_pixels}) exceed limit {max_pixels}")
            max_dimension = int(max_pixels ** 0.5)
            if ref_width >= ref_height:
                new_width = max_dimension
                new_height = max(1, int(max_dimension * ref_height / ref_width))
            else:
                new_height = max_dimension
                new_width = max(1, int(max_dimension * ref_width / ref_height))
        
        temp_width = new_width - (new_width % 2) if new_width > 1 else new_width
        temp_height = new_height - (new_height % 2) if new_height > 1 else new_height
        
        if temp_width * temp_height <= max_pixels and temp_width > 0 and temp_height > 0:
            new_width = temp_width
            new_height = temp_height
        
        logger.info(f"Synchronizing both image and mask to: {new_width}x{new_height} ({new_width*new_height} pixels)")
        
        resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        resized_mask = mask.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        image_output = io.BytesIO()
        mask_output = io.BytesIO()
        
        save_format_image = original_image_format if original_image_format in ['JPEG', 'PNG', 'WEBP'] else 'PNG'
        save_format_mask = original_mask_format if original_mask_format in ['JPEG', 'PNG', 'WEBP'] else 'PNG'
        
        resized_image.save(image_output, format=save_format_image)
        resized_mask.save(mask_output, format=save_format_mask)
        
        logger.info(f"Synchronized resize complete - Image: {save_format_image}, Mask: {save_format_mask}")
        return image_output.getvalue(), mask_output.getvalue()
        
    except Exception as e:
        logger.error(f"Failed to synchronize image and mask resize: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=f"Failed to synchronize image processing: {e}") from e

class StabilityAiService:
    def __init__(self):
        self.api_key = API_KEY
        self.api_host = API_HOST
        self.is_configured = bool(self.api_key)
        self._async_client: Optional[httpx.AsyncClient] = None
        self._client_lock = asyncio.Lock()

        if not self.is_configured:
            logger.warning("STABILITY_API_KEY not configured. Service will be disabled.")

    async def get_client(self) -> httpx.AsyncClient:
        if self._async_client is None or self._async_client.is_closed:
            async with self._client_lock:
                if self._async_client is None or self._async_client.is_closed:
                    self._async_client = httpx.AsyncClient(timeout=180.0) # Increased timeout for image fetching
        return self._async_client

    async def close_client(self):
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
        REFRESH.MD: Migrated to new StableDiffusionAPI.com inpainting endpoint.
        This preserves the masked area (face) while regenerating the rest.
        """
        if not self.is_configured:
            raise HTTPException(status_code=501, detail="Image generation service is not configured.")

        if not isinstance(image_bytes, bytes) or not isinstance(mask_bytes, bytes):
            raise HTTPException(status_code=400, detail="Initial image and mask must be provided as bytes.")
        if not text_prompt or not isinstance(text_prompt, str) or len(text_prompt.strip()) == 0:
            raise HTTPException(status_code=400, detail="Text prompt cannot be empty.")

        image_bytes, mask_bytes = _resize_image_and_mask_synchronized(image_bytes, mask_bytes)

        try:
            image_pil = Image.open(io.BytesIO(image_bytes))
            actual_width, actual_height = image_pil.size
            logger.info(f"Using actual image dimensions for API call: {actual_width}x{actual_height}")
        except Exception as e:
            logger.error(f"Failed to extract image dimensions after resize: {e}", exc_info=True)
            raise HTTPException(status_code=400, detail="Failed to process image dimensions") from e
            
        init_image_b64 = base64.b64encode(image_bytes).decode('utf-8')
        mask_image_b64 = base64.b64encode(mask_bytes).decode('utf-8')

        # REFRESH.MD: New API endpoint and payload structure
        url = f"{self.api_host}/inpaint"
        
        payload = {
            "key": self.api_key,
            "prompt": text_prompt,
            "negative_prompt": negative_prompt,
            "init_image": f"data:image/png;base64,{init_image_b64}",
            "mask_image": f"data:image/png;base64,{mask_image_b64}",
            "width": str(actual_width),
            "height": str(actual_height),
            "samples": "1",
            "num_inference_steps": "21",
            "safety_checker": "no",
            "enhance_prompt": "yes",
            "guidance_scale": 7.5,
            "strength": 0.7,
            "base64": "yes", # Request base64 response directly
            "webhook": None,
            "track_id": None,
        }
        
        headers = {"Content-Type": "application/json"}
        max_retries = 3
        base_delay = 2

        for attempt in range(max_retries):
            try:
                client = await self.get_client()
                logger.info(f"Posting to inpainting API, attempt {attempt + 1}")
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()

                response_data = response.json()

                if response_data.get("status") == "success":
                    logger.info("✅ Inpainting generation successful (status: success).")
                    if response_data.get("base64"):
                        image_base64 = response_data["base64"]
                    elif response_data.get("output"):
                        # Fallback to fetching URL if base64 is not provided
                        image_url = response_data["output"][0]
                        logger.info(f"Fetching generated image from URL: {image_url}")
                        image_response = await client.get(image_url)
                        image_response.raise_for_status()
                        return image_response.content
                    else:
                        raise HTTPException(status_code=500, detail="API response missing image data.")
                    
                    try:
                        return base64.b64decode(image_base64)
                    except (binascii.Error, TypeError) as e:
                        logger.error(f"Failed to decode base64 image from API: {e}", exc_info=True)
                        raise HTTPException(status_code=500, detail="Could not decode image data from API.") from e

                elif response_data.get("status") == "processing":
                    processing_id = response_data.get("id")
                    logger.warning(f"Inpainting is processing (ID: {processing_id}). Will poll for result.")
                    # Poll for the result
                    fetch_url = f"{self.api_host}/fetch/{processing_id}"
                    for _ in range(20): # Poll for up to 100 seconds
                        await asyncio.sleep(5)
                        logger.info(f"Polling for result at: {fetch_url}")
                        fetch_response = await client.post(fetch_url, json={"key": self.api_key})
                        fetch_data = fetch_response.json()
                        if fetch_data.get("status") == "success":
                            logger.info("✅ Polling successful, image generated.")
                            if fetch_data.get("output"):
                                image_url = fetch_data["output"][0]
                                logger.info(f"Fetching generated image from URL: {image_url}")
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
            
            except httpx.RequestError as e:
                logger.error(f"Network error on inpainting: {e}", exc_info=True)
                raise HTTPException(status_code=502, detail="A network error occurred during inpainting.") from e
            except Exception as e:
                logger.error(f"Unexpected error during inpainting: {e}", exc_info=True)
                raise HTTPException(status_code=500, detail="An unexpected error occurred during inpainting.") from e
        
        raise HTTPException(status_code=500, detail="Failed to generate inpainted image after all retries.")

    async def generate_image_from_text(self, text_prompt: str, negative_prompt: Optional[str] = None) -> bytes:
        """
        Generates an image using the original Stability.ai text-to-image endpoint.
        NOTE: This might need updating if the API key is for StableDiffusionAPI.com
        """
        if not self.is_configured:
            raise HTTPException(status_code=501, detail="Image generation service is not configured.")

        if not text_prompt or not isinstance(text_prompt, str) or len(text_prompt.strip()) == 0:
            raise HTTPException(status_code=400, detail="Text prompt cannot be empty.")

        # This part still uses the old stability.ai endpoint.
        # It may fail if the API key is only for stablediffusionapi.com
        # Using a different API host for this function for now.
        original_api_host = "https://api.stability.ai"
        url = f"{original_api_host}/v1/generation/{ENGINE_ID}/text-to-image"
        
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
                response.raise_for_status()

                response_data = response.json()
                
                artifacts = response_data.get("artifacts")
                if not artifacts or not isinstance(artifacts, list):
                    raise HTTPException(status_code=500, detail="Invalid artifacts from Stability.ai text2image")
                
                if not isinstance(artifacts[0], dict) or "base64" not in artifacts[0]:
                    raise HTTPException(status_code=500, detail="Invalid artifact structure in Stability.ai text2image response")
                
                image_base64 = artifacts[0]["base64"]
                
                try:
                    return base64.b64decode(image_base64)
                except (binascii.Error, TypeError) as e:
                    logger.error(f"Failed to decode base64 image from Stability.ai text2image: {e}", exc_info=True)
                    raise HTTPException(status_code=500, detail="Could not decode image data from Stability.ai text2image") from e

            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429 and attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)
                    await asyncio.sleep(delay)
                    continue
                else:
                    error_response = e.response.text
                    logger.error(f"Text-to-image API error - Status: {e.response.status_code}, Response: {error_response}")
                    raise HTTPException(status_code=500, detail=f"Text-to-image API Error: {error_response}") from e
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
