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
        
        # Local ControlNet deployment (optional)
        self.local_controlnet_url = os.getenv("LOCAL_CONTROLNET_URL")
        
        # ControlNet model endpoints
        self.controlnet_models = {
            "pose": "lllyasviel/sd-controlnet-openpose",
            "depth": "lllyasviel/sd-controlnet-depth", 
            "canny": "lllyasviel/sd-controlnet-canny"
        }
        
        if not self.hf_api_key:
            logger.warning("⚠️ Hugging Face API key not found - ControlNet service limited")
        else:
            logger.info("✅ ControlNet Service initialized with Hugging Face API")
    
    @staticmethod
    def _sanitize_prompt(text: str, max_len: int = 1500) -> str:
        """
        Sanitize prompt text for safe logging and API usage
        
        Args:
            text: Input prompt text
            max_len: Maximum length for truncation
            
        Returns:
            str: Sanitized and truncated prompt text
        """
        if not isinstance(text, str):
            return ""
        
        # Collapse whitespace and strip
        sanitized = " ".join(text.split())
        
        # Truncate if too long
        if len(sanitized) > max_len:
            sanitized = sanitized[:max_len].rsplit(' ', 1)[0] + "..."
            
        return sanitized
    
    async def transform_background_clothing(
        self,
        input_image_bytes: bytes,
        clothing_prompt: str,
        background_prompt: str,
        control_type: str = "pose",
        strength: float = 0.85,  # High strength for background/clothing transformation (0.85)
        init_image_bytes: bytes | None = None,
        img2img_strength: float = 0.45  # Identity preservation strength for img2img
    ) -> bytes:
        """
        Transform background and clothing while preserving face and pose
        
        Args:
            input_image_bytes: Face-preserved image from RunWare IP-Adapter
            clothing_prompt: Description of desired clothing transformation
            background_prompt: Description of desired background
            control_type: Type of control (pose, depth, canny)
            strength: ControlNet conditioning strength (0.0-1.0)
            init_image_bytes: Optional init image for img2img identity preservation
            img2img_strength: Denoising strength for img2img (0.0-1.0)
            
        Returns:
            bytes: Final transformed image with new background and clothing
        """
        try:
            # Sanitize prompts for safe processing
            clean_clothing = self._sanitize_prompt(clothing_prompt)
            clean_background = self._sanitize_prompt(background_prompt)
            
            # Combine prompts for complete transformation
            full_prompt = f"{clean_clothing}, {clean_background}, photorealistic, high quality, detailed"
            
            # Enhanced negative prompts with camera/framing negatives
            negative_prompt = ("different face, changed face, face swap, face replacement, wrong identity, "
                             "mutated face, distorted face, blurry face, artificial face, "
                             "bad framing, camera occlusion, awkward crop, poor composition, "
                             "distorted perspective, unnatural viewpoint")
            
            logger.info(f"🎨 Starting ControlNet transformation with {control_type} control")
            logger.info(f"📝 Prompt lengths - Clothing: {len(clothing_prompt)} chars, Background: {len(background_prompt)} chars")
            logger.debug(f"🔍 Clothing preview: {clean_clothing[:50]}{'...' if len(clean_clothing) > 50 else ''}")
            logger.debug(f"🔍 Background preview: {clean_background[:50]}{'...' if len(clean_background) > 50 else ''}")
            
            # Try providers in order: Hugging Face -> Replicate -> Local
            last_error = None
            
            # 1. Try Hugging Face API first
            original_error = None
            if self.hf_api_key:
                try:
                    return await self._transform_with_huggingface(
                        input_image_bytes, full_prompt, negative_prompt, control_type, strength,
                        init_image_bytes, img2img_strength
                    )
                except HTTPException as e:
                    logger.warning(f"⚠️ Hugging Face API failed: {e.detail}")
                    original_error = e
                    last_error = e
                except Exception as e:
                    logger.warning(f"⚠️ Hugging Face API error: {e}")
                    original_error = e
                    last_error = HTTPException(status_code=503, detail=f"Hugging Face API error: {str(e)}")
            
            # 2. Fallback to Replicate API
            if self.replicate_api_key:
                try:
                    return await self._transform_with_replicate(
                        input_image_bytes, full_prompt, negative_prompt, control_type, strength
                    )
                except HTTPException as e:
                    logger.warning(f"⚠️ Replicate API failed: {e.detail}")
                    if not original_error:
                        original_error = e
                    last_error = e
                except Exception as e:
                    logger.warning(f"⚠️ Replicate API error: {e}")
                    if not original_error:
                        original_error = e
                    last_error = HTTPException(status_code=503, detail=f"Replicate API error: {str(e)}")
            
            # 3. Fallback to local deployment (only if configured)
            if self.local_controlnet_url:
                try:
                    return await self._transform_with_local(
                        input_image_bytes, full_prompt, negative_prompt, control_type, strength
                    )
                except HTTPException as e:
                    logger.warning(f"⚠️ Local deployment failed: {e.detail}")
                    # Keep original upstream error as primary cause
                    if original_error:
                        logger.info(f"💡 Raising original upstream error instead of local fallback error")
                        last_error = original_error
                    else:
                        last_error = e
                except Exception as e:
                    logger.warning(f"⚠️ Local deployment error: {e}")
                    # Keep original upstream error as primary cause
                    if original_error:
                        logger.info(f"💡 Raising original upstream error instead of local fallback error")
                        last_error = HTTPException(
                            status_code=503, 
                            detail=f"Primary: {getattr(original_error, 'detail', str(original_error))}. Local fallback also failed: {str(e)}"
                        )
                    else:
                        last_error = HTTPException(status_code=503, detail=f"Local deployment error: {str(e)}")
            else:
                logger.info("🔧 Local ControlNet deployment not configured (LOCAL_CONTROLNET_URL not set)")
            
            # All providers failed
            if last_error:
                raise last_error
            else:
                raise HTTPException(
                    status_code=503,
                    detail="ControlNet service not available - no API keys configured"
                )
                
        except HTTPException:
            # Re-raise HTTPException with original status code
            raise
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
        strength: float,
        init_image_bytes: bytes | None = None,
        img2img_strength: float = 0.45
    ) -> bytes:
        """Transform using Hugging Face Inference API"""
        
        model_name = self.controlnet_models.get(control_type, self.controlnet_models["pose"])
        api_url = f"{self.hf_base_url}/{model_name}"
        
        # Convert control image to base64 for API
        control_image_b64 = base64.b64encode(image_bytes).decode()
        
        # Updated HF ControlNet API format with optional init_image support
        payload = {
            "inputs": prompt,
            "control_image": control_image_b64,
            "parameters": {
                "negative_prompt": negative_prompt,
                "num_inference_steps": 20,
                "guidance_scale": 7.5,
                "controlnet_conditioning_scale": strength,
                "controlnet_type": control_type
            }
        }
        
        # Add init_image support for identity preservation
        if init_image_bytes:
            init_image_b64 = base64.b64encode(init_image_bytes).decode()
            payload["init_image"] = init_image_b64
            payload["parameters"]["strength"] = img2img_strength  # img2img denoising strength
        
        headers = {
            "Authorization": f"Bearer {self.hf_api_key}",
            "Content-Type": "application/json",
            "Accept": "image/png"
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
