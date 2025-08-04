"""
🎯 DEEP IMAGE AI SERVICE

This service provides advanced face-preserving background transformation using Deep-Image.ai API.
Perfect for maintaining Swamiji's exact facial features while completely transforming backgrounds and attire.

Key features:
- adapter_type: "face" for exact face preservation
- face_id: true for detailed facial feature retention
- Complete background transformation capability
- Realistic model for high-quality portraits
"""

import logging
import os
import httpx
from fastapi import HTTPException
from typing import Optional
import json

logger = logging.getLogger(__name__)

# Environment variable for Deep Image AI API key
DEEP_IMAGE_API_KEY = os.getenv("DEEP_IMAGE_API_KEY")

class DeepImageAiService:
    """Service for Deep Image AI face-preserving image generation."""
    
    def __init__(self):
        self.api_key = DEEP_IMAGE_API_KEY
        self.base_url = "https://deep-image.ai/rest_api"
        self.is_configured = bool(self.api_key)
        
        if not self.is_configured:
            logger.warning("DEEP_IMAGE_API_KEY not configured. Deep Image AI services will be disabled.")
        else:
            logger.info("Deep Image AI service initialized successfully")

    async def generate_themed_avatar(
        self,
        image_url: str,
        theme_description: str,
        width: int = 1024,
        height: int = 1024,
        model_type: str = "realistic"
    ) -> bytes:
        """
        Generate a themed avatar with perfect face preservation and complete background transformation.
        
        Args:
            image_url: URL of the source Swamiji image
            theme_description: Description of the desired background/scene
            width: Output image width (default: 1024)
            height: Output image height (default: 1024)
            model_type: Deep Image model type ("realistic", "fantasy", "premium")
            
        Returns:
            bytes: Generated image as bytes
            
        Raises:
            HTTPException: If service not configured or API call fails
        """
        if not self.is_configured:
            raise HTTPException(
                status_code=501, 
                detail="Deep Image AI service is not configured (missing DEEP_IMAGE_API_KEY)."
            )
        
        try:
            headers = {
                "X-API-KEY": self.api_key,
                "Content-Type": "application/json"
            }
            
            # Deep Image AI payload for face-preserving background transformation
            payload = {
                "url": image_url,
                "width": width,
                "height": height,
                "background": {
                    "generate": {
                        "description": theme_description,
                        "adapter_type": "face",  # Use face from input image
                        "face_id": True,         # Preserve detailed facial features
                        "model_type": model_type # Realistic model for portraits
                    }
                },
                "output_format": "png"
            }
            
            logger.info(f"Deep Image AI request: {theme_description}, model: {model_type}")
            logger.debug(f"Payload: {json.dumps(payload, indent=2)}")
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                # Use process_result endpoint for immediate results (up to 25s processing)
                response = await client.post(
                    f"{self.base_url}/process_result",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code != 200:
                    error_detail = f"Deep Image AI API error: {response.status_code}"
                    if response.content:
                        try:
                            error_data = response.json()
                            error_detail += f" - {error_data}"
                        except:
                            error_detail += f" - {response.text}"
                    
                    logger.error(error_detail)
                    raise HTTPException(status_code=502, detail=error_detail)
                
                result = response.json()
                logger.debug(f"Deep Image AI response: {result}")
                
                # Check if processing is complete
                if result.get("status") == "complete" and result.get("result_url"):
                    # Download the generated image
                    image_url = result["result_url"]
                    logger.info(f"Deep Image AI processing complete: {image_url}")
                    
                    async with httpx.AsyncClient() as download_client:
                        download_response = await download_client.get(image_url)
                        download_response.raise_for_status()
                        return download_response.content
                        
                elif result.get("job"):
                    # Processing is taking longer, would need to poll for results
                    job_id = result["job"]
                    logger.warning(f"Deep Image AI job queued: {job_id}. Polling not implemented yet.")
                    raise HTTPException(
                        status_code=503, 
                        detail="Image processing is taking longer than expected. Please try again."
                    )
                else:
                    logger.error(f"Unexpected Deep Image AI response: {result}")
                    raise HTTPException(
                        status_code=502, 
                        detail="Unexpected response from Deep Image AI service"
                    )
                    
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error calling Deep Image AI: {e}", exc_info=True)
            raise HTTPException(status_code=502, detail="Failed to call Deep Image AI service") from e
        except httpx.RequestError as e:
            logger.error(f"Request error calling Deep Image AI: {e}", exc_info=True)
            raise HTTPException(status_code=503, detail="Deep Image AI service is currently unavailable") from e
        except Exception as e:
            logger.error(f"Unexpected error in Deep Image AI service: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="An unexpected error occurred") from e

    async def check_service_status(self) -> dict:
        """
        Check if Deep Image AI service is available and configured.
        
        Returns:
            dict: Service status information
        """
        if not self.is_configured:
            return {
                "available": False,
                "reason": "DEEP_IMAGE_API_KEY not configured"
            }
        
        try:
            headers = {"X-API-KEY": self.api_key}
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/me", headers=headers)
                
                if response.status_code == 200:
                    user_info = response.json()
                    return {
                        "available": True,
                        "credits": user_info.get("credits", "unknown"),
                        "username": user_info.get("username", "unknown")
                    }
                else:
                    return {
                        "available": False,
                        "reason": f"API authentication failed: {response.status_code}"
                    }
                    
        except Exception as e:
            logger.error(f"Failed to check Deep Image AI service status: {e}")
            return {
                "available": False,
                "reason": f"Service check failed: {str(e)}"
            }


# --- FastAPI Dependency Injection ---
def get_deep_image_service() -> DeepImageAiService:
    """Creates an instance of the DeepImageAiService."""
    return DeepImageAiService()