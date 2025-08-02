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
# RESTORED: Original Stability.ai setup with user's existing API key
API_HOST = "https://api.stability.ai"
ENGINE_ID = "stable-diffusion-xl-1024-v1-0"  # Try working SDXL engine
INPAINTING_ENGINE_ID = "stable-diffusion-xl-1024-v1-0"  # Same engine for inpainting  
API_KEY = os.getenv("STABILITY_API_KEY")  # User's original environment variable


def _resize_image_if_needed(image_bytes: bytes, max_pixels: int = 1048576) -> bytes:
    """
    Resize image if it exceeds the maximum pixel count for StabilityAI API.
    Max pixels: 1,048,576 (typically 1024x1024)
    
    CORE.MD: Robust handling of edge cases and format preservation
    REFRESH.MD: Exception chaining for better debugging
    """
    try:
        # Open image from bytes
        image = Image.open(io.BytesIO(image_bytes))
        width, height = image.size
        current_pixels = width * height
        original_format = image.format or 'PNG'  # Preserve original format
        
        # Check if resize is needed
        if current_pixels <= max_pixels:
            logger.info(f"Image size OK: {width}x{height} = {current_pixels} pixels")
            return image_bytes
        
        # Calculate new dimensions while maintaining aspect ratio
        ratio = (max_pixels / current_pixels) ** 0.5
        new_width = int(width * ratio)
        new_height = int(height * ratio)
        
        # CORE.MD: Prevent zero dimensions but maintain pixel limit compliance
        new_width = max(new_width, 1)
        new_height = max(new_height, 1)
        
        # REFRESH.MD: Re-check pixel limit after minimum enforcement
        adjusted_pixels = new_width * new_height
        if adjusted_pixels > max_pixels:
            # If minimum dimensions exceed limit, recalculate with stricter constraints
            logger.warning(f"Minimum dimensions ({new_width}x{new_height}={adjusted_pixels}) exceed pixel limit {max_pixels}")
            # Use the largest square that fits within the limit
            max_dimension = int(max_pixels ** 0.5)
            if width >= height:
                new_width = max_dimension
                new_height = max(1, int(max_dimension * height / width))
            else:
                new_height = max_dimension
                new_width = max(1, int(max_dimension * width / height))
            logger.info(f"Adjusted to square-based dimensions: {new_width}x{new_height}")
        
        # Ensure dimensions are even numbers (some APIs prefer this)
        # Only adjust if it doesn't violate pixel limit
        temp_width = new_width - (new_width % 2) if new_width > 1 else new_width
        temp_height = new_height - (new_height % 2) if new_height > 1 else new_height
        
        # Final validation: ensure even adjustment doesn't exceed pixel limit
        if temp_width * temp_height <= max_pixels and temp_width > 0 and temp_height > 0:
            new_width = temp_width
            new_height = temp_height
        
        logger.info(f"Resizing image from {width}x{height} ({current_pixels}) to {new_width}x{new_height} ({new_width*new_height})")
        
        # Resize image
        resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Convert back to bytes with original format preservation
        output_bytes = io.BytesIO()
        # Use original format if supported, fallback to PNG
        save_format = original_format if original_format in ['JPEG', 'PNG', 'WEBP'] else 'PNG'
        resized_image.save(output_bytes, format=save_format)
        
        logger.info(f"Image resized and saved in {save_format} format")
        return output_bytes.getvalue()
        
    except Exception as e:
        logger.error(f"Failed to resize image: {e}", exc_info=True)
        # REFRESH.MD: Exception chaining to preserve original traceback
        raise HTTPException(status_code=400, detail=f"Failed to process image: {e}") from e


def _resize_image_and_mask_synchronized(image_bytes: bytes, mask_bytes: bytes, max_pixels: int = 1048576) -> tuple[bytes, bytes]:
    """
    Resize image and mask to identical dimensions ensuring perfect synchronization.
    CORE.MD: Prevents dimension mismatch that causes API rejections
    REFRESH.MD: Synchronized processing for spatial correspondence
    """
    try:
        # Open both images
        image = Image.open(io.BytesIO(image_bytes))
        mask = Image.open(io.BytesIO(mask_bytes))
        
        # CORE.MD: Capture original formats BEFORE any resize operations
        original_image_format = image.format or 'PNG'
        original_mask_format = mask.format or 'PNG'
        logger.info(f"Original formats - Image: {original_image_format}, Mask: {original_mask_format}")
        
        # Get dimensions - use the larger image as reference for pixel calculation
        image_width, image_height = image.size
        mask_width, mask_height = mask.size
        image_pixels = image_width * image_height
        mask_pixels = mask_width * mask_height
        
        # Use the image with larger pixel count as the reference for dimension calculation
        if image_pixels >= mask_pixels:
            ref_width, ref_height = image_width, image_height
            ref_pixels = image_pixels
            logger.info(f"Using image dimensions as reference: {ref_width}x{ref_height}")
        else:
            ref_width, ref_height = mask_width, mask_height
            ref_pixels = mask_pixels
            logger.info(f"Using mask dimensions as reference: {ref_width}x{ref_height}")
        
        # Check if resize is needed
        if ref_pixels <= max_pixels:
            # No resize needed, but ensure both have same dimensions as reference
            if image_width != ref_width or image_height != ref_height:
                logger.info(f"Resizing image to match reference: {ref_width}x{ref_height}")
                image = image.resize((ref_width, ref_height), Image.Resampling.LANCZOS)
            if mask_width != ref_width or mask_height != ref_height:
                logger.info(f"Resizing mask to match reference: {ref_width}x{ref_height}")
                mask = mask.resize((ref_width, ref_height), Image.Resampling.LANCZOS)
            
            # Convert back to bytes with original formats preserved
            image_output = io.BytesIO()
            mask_output = io.BytesIO()
            
            # REFRESH.MD: Use captured original formats instead of post-resize formats
            save_format_image = original_image_format if original_image_format in ['JPEG', 'PNG', 'WEBP'] else 'PNG'
            save_format_mask = original_mask_format if original_mask_format in ['JPEG', 'PNG', 'WEBP'] else 'PNG'
            
            image.save(image_output, format=save_format_image)
            mask.save(mask_output, format=save_format_mask)
            
            return image_output.getvalue(), mask_output.getvalue()
        
        # Calculate synchronized new dimensions
        ratio = (max_pixels / ref_pixels) ** 0.5
        new_width = int(ref_width * ratio)
        new_height = int(ref_height * ratio)
        
        # CORE.MD: Prevent zero dimensions with consistent minimums
        new_width = max(new_width, 1)
        new_height = max(new_height, 1)
        
        # REFRESH.MD: Re-validate pixel limit after minimum enforcement
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
        
        # Try even number adjustment if safe
        temp_width = new_width - (new_width % 2) if new_width > 1 else new_width
        temp_height = new_height - (new_height % 2) if new_height > 1 else new_height
        
        if temp_width * temp_height <= max_pixels and temp_width > 0 and temp_height > 0:
            new_width = temp_width
            new_height = temp_height
        
        logger.info(f"Synchronizing both image and mask to: {new_width}x{new_height} ({new_width*new_height} pixels)")
        
        # Resize both to IDENTICAL dimensions
        resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        resized_mask = mask.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Convert back to bytes with original format preservation
        image_output = io.BytesIO()
        mask_output = io.BytesIO()
        
        # REFRESH.MD: Use captured original formats (resized images lose format info)
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
        self.engine_id = ENGINE_ID
        self.inpainting_engine_id = INPAINTING_ENGINE_ID
        self.is_configured = bool(self.api_key)
        self._async_client: Optional[httpx.AsyncClient] = None
        self._client_lock = asyncio.Lock()

        if not self.is_configured:
            logger.warning("RESTORED: Stability.ai API key not configured. Set STABILITY_API_KEY environment variable.")

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
            logger.info("Inpainting service client closed.")
    
    async def generate_image_with_mask(
        self, 
        image_bytes: bytes, 
        mask_bytes: bytes, 
        text_prompt: str, 
        negative_prompt: Optional[str] = None
    ) -> bytes:
        """
        Generates an image using StableDiffusionAPI.com inpainting endpoint.
        This preserves the masked (black) area of the image (Swamiji's face) while regenerating the rest.
        CORE.MD: Face preservation logic maintained for spiritual avatar generation.
        """
        if not self.is_configured:
            raise HTTPException(status_code=501, detail="Image generation service is not configured.")

        # --- Input Validation (CORE.MD) ---
        if not isinstance(image_bytes, bytes) or not isinstance(mask_bytes, bytes):
            raise HTTPException(status_code=400, detail="Initial image and mask must be provided as bytes.")
        if not text_prompt or not isinstance(text_prompt, str) or len(text_prompt.strip()) == 0:
            raise HTTPException(status_code=400, detail="Text prompt cannot be empty.")

        # --- Synchronized Image & Mask Resizing (FIX: Dimension mismatch + pixel limit) ---
        image_bytes, mask_bytes = _resize_image_and_mask_synchronized(image_bytes, mask_bytes)

        # --- Extract Actual Dimensions (CORE.MD: Prevent dimension mismatch) ---
        try:
            from PIL import Image as PILImage
            import io
            
            # Get actual dimensions from resized image
            image_pil = PILImage.open(io.BytesIO(image_bytes))
            actual_width, actual_height = image_pil.size
            logger.info(f"Using actual image dimensions: {actual_width}x{actual_height}")
            
        except Exception as e:
            logger.error(f"Failed to extract image dimensions: {e}", exc_info=True)
            raise HTTPException(status_code=400, detail="Failed to process image dimensions") from e

        # --- OPTIMIZED: Detect MIME types and use original bytes directly ---
        def _detect_image_format(image_bytes: bytes) -> tuple[str, str]:
            """Detect image format from bytes and return (extension, mime_type)"""
            if image_bytes.startswith(b'\xff\xd8\xff'):
                return "jpg", "image/jpeg"
            elif image_bytes.startswith(b'\x89PNG\r\n\x1a\n'):
                return "png", "image/png"
            elif image_bytes.startswith(b'RIFF') and b'WEBP' in image_bytes[:12]:
                return "webp", "image/webp"
            else:
                # Default to PNG if detection fails
                return "png", "image/png"

        # Detect actual image formats
        init_ext, init_mime = _detect_image_format(image_bytes)
        mask_ext, mask_mime = _detect_image_format(mask_bytes)
        
        logger.info(f"Detected formats - Init: {init_mime}, Mask: {mask_mime}")

        # --- FIXED: Stability.ai API with multipart/form-data ---
        url = f"{self.api_host}/v1/generation/{self.inpainting_engine_id}/image-to-image/masking"
        
        headers = {
            "Accept": "application/json", 
            "Authorization": f"Bearer {self.api_key}"
            # No Content-Type - httpx sets multipart/form-data automatically
        }

        # Prepare text_prompts JSON string
        text_prompts = [{"text": text_prompt, "weight": 1.0}]
        if negative_prompt:
            text_prompts.append({"text": negative_prompt, "weight": -1.0})
        
        # CORE.MD: Use original bytes directly with proper MIME types (no base64 roundtrip)
        files = {
            "init_image": (f"init_image.{init_ext}", image_bytes, init_mime),
            "mask_image": (f"mask_image.{mask_ext}", mask_bytes, mask_mime),
        }
        
        data = {
            "text_prompts": json.dumps(text_prompts),  # Proper JSON formatting
            "cfg_scale": "7",
            "samples": "1", 
            "steps": "25",
            "mask_source": "MASK_IMAGE_BLACK"
        }

        max_retries = 3
        base_delay = 2

        for attempt in range(max_retries):
            try:
                client = await self.get_client()
                response = await client.post(url, headers=headers, files=files, data=data)
                response.raise_for_status()

                response_data = response.json()
                
                # RESTORED: Original Stability.ai API response format
                artifacts = response_data.get("artifacts")
                if not artifacts or not isinstance(artifacts, list):
                    raise HTTPException(status_code=500, detail="Invalid or empty artifacts received from Stability.ai")
                
                if not isinstance(artifacts[0], dict) or "base64" not in artifacts[0]:
                    raise HTTPException(status_code=500, detail="Invalid artifact structure in Stability.ai response")
                
                image_base64 = artifacts[0]["base64"]
                
                try:
                    generated_image_bytes = base64.b64decode(image_base64)
                except (binascii.Error, TypeError) as e:
                    logger.error(f"Failed to decode base64 image from Stability.ai: {e}", exc_info=True)
                    raise HTTPException(status_code=500, detail="Could not decode image data from Stability.ai") from e

                logger.info("✅ Successfully generated image with inpainting (face preserved).")
                return generated_image_bytes

            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429 and attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)
                    logger.warning(f"Rate limit exceeded (429) on inpainting. Retrying in {delay}s...")
                    await asyncio.sleep(delay)
                    continue
                else:
                    error_response = e.response.text
                    logger.error(f"Inpainting API error - Status: {e.response.status_code}")
                    logger.error(f"Error response: {error_response}")
                    logger.error(f"Request URL: {e.request.url}")
                    raise HTTPException(status_code=500, detail=f"Inpainting API Error: {error_response}") from e
            
            except HTTPException:
                raise
            except httpx.RequestError as e:
                logger.error(f"Network error on inpainting: {e}", exc_info=True)
                raise HTTPException(status_code=502, detail="A network error occurred during inpainting.") from e
            except Exception as e:
                logger.error(f"Unexpected error during inpainting: {e}", exc_info=True)
                raise HTTPException(status_code=500, detail="An unexpected error occurred during inpainting.") from e
        
        raise HTTPException(status_code=500, detail="Failed to generate inpainted image after all retries.")

    async def generate_image_from_text(self, text_prompt: str, negative_prompt: Optional[str] = None) -> bytes:
        """
        Generates an image using StableDiffusionAPI.com text-to-image endpoint.
        REFRESH.MD: Complete migration from deprecated Stability.ai API.
        """
        if not self.is_configured:
            raise HTTPException(status_code=501, detail="Image generation service is not configured.")

        if not text_prompt or not isinstance(text_prompt, str) or len(text_prompt.strip()) == 0:
            raise HTTPException(status_code=400, detail="Text prompt cannot be empty.")

        # RESTORED: Original Stability.ai text-to-image endpoint
        url = f"{self.api_host}/v1/generation/{self.engine_id}/text-to-image"
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        # RESTORED: Original Stability.ai payload format  
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
        
        # Add negative prompt if provided
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
                
                # RESTORED: Original Stability.ai artifacts response format
                artifacts = response_data.get("artifacts")
                if not artifacts or not isinstance(artifacts, list):
                    raise HTTPException(status_code=500, detail="Invalid or empty artifacts received from Stability.ai")
                
                if not isinstance(artifacts[0], dict) or "base64" not in artifacts[0]:
                    raise HTTPException(status_code=500, detail="Invalid artifact structure in Stability.ai response")
                
                image_base64 = artifacts[0]["base64"]
                
                try:
                    generated_image_bytes = base64.b64decode(image_base64)
                except (binascii.Error, TypeError) as e:
                    logger.error(f"Failed to decode base64 image from Stability.ai: {e}", exc_info=True)
                    raise HTTPException(status_code=500, detail="Could not decode image data from Stability.ai") from e

                logger.info("✅ Successfully generated image from text.")
                return generated_image_bytes

            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429 and attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)
                    logger.warning(f"Rate limit exceeded (429). Retrying in {delay} seconds... (Attempt {attempt + 1}/{max_retries})")
                    await asyncio.sleep(delay)
                    continue
                else:
                    error_response = e.response.text
                    logger.error(f"Text-to-image API error - Status: {e.response.status_code}")
                    logger.error(f"Error response: {error_response}")
                    raise HTTPException(status_code=500, detail=f"Text-to-image API Error: {error_response}") from e
            
            except HTTPException:
                raise
            except httpx.RequestError as e:
                logger.error(f"Network error on text-to-image: {e}", exc_info=True)
                raise HTTPException(status_code=502, detail="A network error occurred during text-to-image generation.") from e

            except Exception as e:
                logger.error(f"An unexpected error occurred during text-to-image generation: {e}", exc_info=True)
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
