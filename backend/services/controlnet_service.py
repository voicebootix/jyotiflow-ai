"""
🎨 CONTROLNET SERVICE: Background & Clothing Transformation

This service handles the second step of the multi-API approach:
1. RunWare IP-Adapter preserves face identity
2. ControlNet transforms background and clothing while preserving pose/structure

Integrates with multiple ControlNet providers:
- Hugging Face Inference API
- Replicate API  
- Local ControlNet deployment
"""

import logging
import httpx
import base64
import io
from PIL import Image
from typing import Optional, Tuple
from fastapi import HTTPException
import os

logger = logging.getLogger(__name__)

class ControlNetService:
    """
    🎨 ControlNet Service for background and clothing transformation
    
    Designed to work as Step 2 after RunWare IP-Adapter face preservation.
    Uses pose/structure preservation while allowing complete background/clothing changes.
    """
    
    def __init__(self):
        # Hugging Face API for ControlNet
        self.hf_api_key = os.getenv("HUGGING_FACE_API_KEY")
        self.hf_base_url = "https://api-inference.huggingface.co/models"
        
        # Replicate API as backup
        self.replicate_api_key = os.getenv("REPLICATE_API_TOKEN")
        
        # ControlNet model endpoints
        self.controlnet_models = {
            "pose": "lllyasviel/sd-controlnet-openpose",
            "depth": "lllyasviel/sd-controlnet-depth", 
            "canny": "lllyasviel/sd-controlnet-canny",
            "inpaint": "runwayml/stable-diffusion-inpainting"
        }
        
        if not self.hf_api_key:
            logger.warning("⚠️ Hugging Face API key not found - ControlNet service limited")
        else:
            logger.info("✅ ControlNet Service initialized with Hugging Face API")
    
    async def transform_background_clothing(
        self,
        input_image_bytes: bytes,
        clothing_prompt: str,
        background_prompt: str,
        control_type: str = "pose",
        strength: float = 0.85  # High strength for background/clothing transformation (0.85)
    ) -> bytes:
        """
        Transform background and clothing while preserving face and pose
        
        Args:
            input_image_bytes: Face-preserved image from RunWare IP-Adapter
            clothing_prompt: Description of desired clothing transformation
            background_prompt: Description of desired background
            control_type: Type of control (pose, depth, canny)
            strength: Transformation strength (0.0-1.0)
            
        Returns:
            bytes: Final transformed image with new background and clothing
        """
        try:
            # Combine prompts for complete transformation
            full_prompt = f"{clothing_prompt}, {background_prompt}, photorealistic, high quality, detailed"
            
            # Negative prompts to avoid face changes
            negative_prompt = "different face, changed face, face swap, face replacement, wrong identity, mutated face, distorted face, blurry face, artificial face"
            
            logger.info(f"🎨 Starting ControlNet transformation with {control_type} control")
            logger.info(f"📝 Clothing: {clothing_prompt}")
            logger.info(f"🏞️ Background: {background_prompt}")
            
            # Try providers in order: Hugging Face -> Replicate -> Local
            last_error = None
            
            # 1. Try Hugging Face API first
            if self.hf_api_key:
                try:
                    return await self._transform_with_huggingface(
                        input_image_bytes, full_prompt, negative_prompt, control_type, strength
                    )
                except HTTPException as e:
                    logger.warning(f"⚠️ Hugging Face API failed: {e.detail}")
                    last_error = e
                except Exception as e:
                    logger.warning(f"⚠️ Hugging Face API error: {e}")
                    last_error = HTTPException(status_code=503, detail=f"Hugging Face API error: {str(e)}")
            
            # 2. Fallback to Replicate API
            if self.replicate_api_key:
                try:
                    return await self._transform_with_replicate(
                        input_image_bytes, full_prompt, negative_prompt, control_type, strength
                    )
                except HTTPException as e:
                    logger.warning(f"⚠️ Replicate API failed: {e.detail}")
                    last_error = e
                except Exception as e:
                    logger.warning(f"⚠️ Replicate API error: {e}")
                    last_error = HTTPException(status_code=503, detail=f"Replicate API error: {str(e)}")
            
            # 3. Fallback to local deployment
            try:
                return await self._transform_with_local(
                    input_image_bytes, full_prompt, negative_prompt, control_type, strength
                )
            except HTTPException as e:
                logger.warning(f"⚠️ Local deployment failed: {e.detail}")
                last_error = e
            except Exception as e:
                logger.warning(f"⚠️ Local deployment error: {e}")
                last_error = HTTPException(status_code=503, detail=f"Local deployment error: {str(e)}")
            
            # All providers failed
            if last_error:
                raise last_error
            else:
                raise HTTPException(
                    status_code=503,
                    detail="ControlNet service not available - no API keys configured"
                )
                
        except Exception as e:
            logger.error(f"❌ ControlNet transformation failed: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"ControlNet transformation failed: {str(e)}"
            ) from e
    
    async def _transform_with_huggingface(
        self,
        image_bytes: bytes,
        prompt: str,
        negative_prompt: str,
        control_type: str,
        strength: float
    ) -> bytes:
        """Transform using Hugging Face Inference API"""
        
        model_name = self.controlnet_models.get(control_type, self.controlnet_models["pose"])
        api_url = f"{self.hf_base_url}/{model_name}"
        
        # Convert image to base64 for API
        image_b64 = base64.b64encode(image_bytes).decode()
        
        payload = {
            "inputs": {
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "image": image_b64,
                "num_inference_steps": 20,
                "guidance_scale": 7.5,
                "strength": strength
            }
        }
        
        headers = {
            "Authorization": f"Bearer {self.hf_api_key}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            logger.info(f"🔄 Calling Hugging Face ControlNet API: {model_name}")
            
            response = await client.post(api_url, json=payload, headers=headers)
            
            if response.status_code == 200:
                # HF returns image bytes directly
                result_bytes = response.content
                logger.info("✅ Hugging Face ControlNet transformation completed")
                return result_bytes
            else:
                error_msg = f"Hugging Face API error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise HTTPException(status_code=503, detail=error_msg)
    
    async def _transform_with_replicate(
        self,
        image_bytes: bytes,
        prompt: str,
        negative_prompt: str,
        control_type: str,
        strength: float
    ) -> bytes:
        """Transform using Replicate API (fallback provider)"""
        
        # TODO: Implement Replicate ControlNet integration
        # Would use replicate.run() with ControlNet models
        logger.info("🔄 Attempting Replicate API transformation...")
        raise HTTPException(
            status_code=501, 
            detail="Replicate ControlNet integration not yet implemented"
        )
    
    async def _transform_with_local(
        self,
        image_bytes: bytes,
        prompt: str,
        negative_prompt: str,
        control_type: str,
        strength: float
    ) -> bytes:
        """Transform using local ControlNet deployment (final fallback)"""
        
        # TODO: Implement local ControlNet deployment integration
        # Would connect to local Stable Diffusion + ControlNet setup
        logger.info("🔄 Attempting local deployment transformation...")
        raise HTTPException(
            status_code=501, 
            detail="Local ControlNet deployment not yet implemented"
        )
    
    async def extract_pose_from_image(self, image_bytes: bytes) -> dict:
        """Extract pose information for ControlNet pose control"""
        # This would integrate with OpenPose or similar
        # For now, return basic structure
        return {
            "pose_detected": True,
            "keypoints": [],  # Would contain actual pose keypoints
            "confidence": 0.9
        }

# Dependency injection
_controlnet_service = None

def get_controlnet_service() -> ControlNetService:
    """Get ControlNet service instance"""
    global _controlnet_service
    if _controlnet_service is None:
        _controlnet_service = ControlNetService()
    return _controlnet_service
