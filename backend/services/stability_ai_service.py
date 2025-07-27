"""
🎨 STABILITY AI SERVICE

This service provides a centralized interface for interacting with the Stability.ai API
for text-to-image generation. It follows CORE.MD and REFRESH.MD principles.
"""

import os
import base64
import logging
import httpx

from fastapi import HTTPException

# Initialize logger
logger = logging.getLogger(__name__)

# CORE.MD: Load configuration from environment variables.
STABILITY_API_KEY = os.getenv("STABILITY_API_KEY")
API_HOST = os.getenv("STABILITY_API_HOST", "https://api.stability.ai")
ENGINE_ID = "stable-diffusion-xl-1024-v1-0"

# REFRESH.MD: Use a single, reusable httpx.AsyncClient for performance.
client = httpx.AsyncClient(timeout=90.0)

class StabilityAiService:
    """A service class to manage text-to-image generation with Stability.ai."""

    def __init__(self):
        self.is_configured = bool(STABILITY_API_KEY)
        if not self.is_configured:
            logger.warning("Stability.ai API key is not configured. Image generation service is disabled.")

    async def generate_image(self, text_prompt: str, style_preset: str = "photorealistic") -> bytes:
        """
        Generates an image from a text prompt using the Stability.ai API.

        Args:
            text_prompt: The descriptive text prompt for the image.
            style_preset: The style to apply (e.g., 'photorealistic', 'digital-art').

        Returns:
            The generated image content in bytes.
        
        Raises:
            HTTPException: If the image generation fails or the service is not configured.
        """
        if not self.is_configured:
            raise HTTPException(status_code=501, detail="Image generation service is not configured.")

        url = f"{API_HOST}/v1/generation/{ENGINE_ID}/text-to-image"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {STABILITY_API_KEY}",
        }
        payload = {
            "text_prompts": [{"text": text_prompt}],
            "cfg_scale": 7,
            "height": 1024,
            "width": 1024,
            "samples": 1,
            "steps": 40,
            "style_preset": style_preset,
        }

        try:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            response_data = response.json()
            artifacts = response_data.get("artifacts")
            
            if not artifacts or not isinstance(artifacts, list) or "base64" not in artifacts[0]:
                raise HTTPException(status_code=500, detail="Invalid response from image generation service.")
            
            image_base64 = artifacts[0]["base64"]
            image_bytes = base64.b64decode(image_base64)
            
            logger.info("✅ Successfully generated image from text prompt.")
            return image_bytes

        except httpx.HTTPStatusError as e:
            logger.error(f"Stability.ai API error: {e.response.status_code} - {e.response.text}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to generate image from Stability.ai.") from e
        except Exception as e:
            logger.error(f"An unexpected error occurred during image generation: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="An unexpected error occurred while generating the image.") from e

# --- FastAPI Dependency Injection ---
_stability_service_instance = None

def get_stability_service() -> StabilityAiService:
    """
    FastAPI dependency that provides a singleton instance of the StabilityAiService.
    """
    global _stability_service_instance
    if _stability_service_instance is None:
        _stability_service_instance = StabilityAiService()
    return _stability_service_instance 