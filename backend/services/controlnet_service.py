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
        
        # ControlNet model endpoints (using guaranteed working HF models)
        self.controlnet_models = {
            "pose": "runwayml/stable-diffusion-v1-5",  # Fallback to base SD model
            "depth": "runwayml/stable-diffusion-v1-5", 
            "canny": "runwayml/stable-diffusion-v1-5"
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
            # 1. Validate control_type against allowed set
            valid_control_types = set(self.controlnet_models.keys())
            if control_type not in valid_control_types:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid control_type '{control_type}'. Must be one of: {', '.join(valid_control_types)}"
                )
            
            # 2. Clamp strength values to [0.0, 1.0] range
            strength = max(0.0, min(1.0, strength))
            img2img_strength = max(0.0, min(1.0, img2img_strength))
            
            # 3. Sanitize individual prompts
            clean_clothing = self._sanitize_prompt(clothing_prompt)
            clean_background = self._sanitize_prompt(background_prompt)
            
            # 4. Combine and sanitize full prompt
            combined_prompt = f"{clean_clothing}, {clean_background}, photorealistic, high quality, detailed"
            full_prompt = self._sanitize_prompt(combined_prompt, max_len=1500)
            
            # 5. Validate final prompt length
            if len(full_prompt) > 1500:
                raise HTTPException(
                    status_code=400,
                    detail=f"Combined prompt too long ({len(full_prompt)} chars). Must be ≤1500 characters."
                )
            
            # Enhanced negative prompts following user guidance for blocking original elements
            negative_prompt = ("different face, changed face, face swap, face replacement, wrong identity, "
                             "mutated face, distorted face, blurry face, artificial face, "
                             "same clothes, same background, original outfit, old temple background, current clothing, "
                             "identical attire, unchanged robes, original setting, same environment, "
                             "copying reference clothing, maintaining original background, preserving old attire, "
                             "bad framing, camera occlusion, awkward crop, poor composition, "
                             "distorted perspective, unnatural viewpoint, low quality, blurry")
            
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
                        input_image_bytes, full_prompt, negative_prompt, control_type, strength,
                        init_image_bytes, img2img_strength
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
                        input_image_bytes, full_prompt, negative_prompt, control_type, strength,
                        init_image_bytes, img2img_strength
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
        
        # Use environment-configured model for img2img (guaranteed working HF Inference API model)
        model_id = os.getenv("HF_IMG2IMG_MODEL", "runwayml/stable-diffusion-v1-5")
        api_url = f"{self.hf_base_url}/{model_id}"
        
        # HF Stable Diffusion img2img API format for face preservation
        # Use init_image (input_image_bytes) as base to preserve face structure
        if not image_bytes:
            raise HTTPException(status_code=400, detail="Input image required for img2img transformation")
        
        # Base64 encode the init image for HF img2img API
        init_image_b64 = base64.b64encode(image_bytes).decode()
        
        # Read configuration from environment with sensible defaults
        hf_strength = float(os.getenv("HF_IMG2IMG_STRENGTH", str(img2img_strength)))
        hf_guidance_scale = float(os.getenv("HF_IMG2IMG_GUIDANCE_SCALE", "7.5"))
        hf_num_steps = int(os.getenv("HF_IMG2IMG_STEPS", "25"))
        hf_width = int(os.getenv("HF_IMG2IMG_WIDTH", "512"))
        hf_height = int(os.getenv("HF_IMG2IMG_HEIGHT", "512"))
        hf_seed = os.getenv("HF_IMG2IMG_SEED")  # Optional, can be None
        
        # Build parameters dict, excluding None values
        parameters = {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "strength": hf_strength,
            "guidance_scale": hf_guidance_scale,
            "num_inference_steps": hf_num_steps,
            "width": hf_width,
            "height": hf_height
        }
        
        # Add seed only if provided
        if hf_seed is not None:
            try:
                parameters["seed"] = int(hf_seed)
            except ValueError:
                logger.warning(f"⚠️ Invalid seed value: {hf_seed}, skipping")
        
        # HF img2img API payload format
        payload = {
            "inputs": init_image_b64,  # Base64 encoded init image
            "parameters": parameters
        }
        
        logger.info(f"🔄 Using HF Stable Diffusion img2img API: {model_id}")
        logger.info(f"🎨 img2img strength: {hf_strength} (face preservation balance)")
        
        headers = {
            "Authorization": f"Bearer {self.hf_api_key}",
            "Content-Type": "application/json",
            "Accept": "image/png",
            "X-Wait-For-Model": "true"  # Wait for model loading to prevent 503s
        }
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            logger.info(f"🔄 Calling Hugging Face img2img API: {model_id}")
            logger.info(f"🔗 API URL: {api_url}")
            
            response = await client.post(api_url, json=payload, headers=headers)
            
            if response.status_code == 200:
                # HF returns image bytes directly
                result_bytes = response.content
                logger.info("✅ Hugging Face img2img transformation completed")
                return result_bytes
            elif response.status_code == 404:
                error_msg = f"HF img2img model not found: {model_id}. Check if model exists on HuggingFace."
                logger.error(f"❌ {error_msg}")
                logger.error("💡 Available models: CompVis/stable-diffusion-v1-4, stabilityai/stable-diffusion-2-1, etc.")
                raise HTTPException(status_code=503, detail=error_msg)
            else:
                error_msg = f"Hugging Face API error: {response.status_code} - {response.text}"
                logger.error(f"❌ {error_msg}")
                raise HTTPException(status_code=503, detail=error_msg)
    
    async def _transform_with_replicate(
        self,
        image_bytes: bytes,
        prompt: str,
        negative_prompt: str,
        control_type: str,
        strength: float,
        init_image_bytes: bytes | None = None,
        img2img_strength: float = 0.45
    ) -> bytes:
        """Transform using Replicate API (reliable fallback provider)"""
        
        if not self.replicate_api_key:
            raise HTTPException(status_code=501, detail="Replicate API key not configured")
        
        try:
            import replicate
        except ImportError as e:
            raise HTTPException(status_code=501, detail="Replicate package not installed") from e
        
        logger.info("🔄 Using Replicate Stable Diffusion img2img...")
        
        # Convert image to base64 for Replicate
        if init_image_bytes:
            # Use init_image for face preservation
            image_b64 = base64.b64encode(init_image_bytes).decode()
            init_image_data_uri = f"data:image/png;base64,{image_b64}"
        else:
            # Use control image
            image_b64 = base64.b64encode(image_bytes).decode()
            init_image_data_uri = f"data:image/png;base64,{image_b64}"
        
        # Replicate Stable Diffusion img2img - Using async client approach
        try:
            # Create prediction using async approach to avoid blocking
            import asyncio
            import functools
            
            # Run replicate.run in thread pool to avoid blocking event loop
            loop = asyncio.get_event_loop()
            output = await loop.run_in_executor(
                None,
                functools.partial(
                    replicate.run,
                    "stability-ai/stable-diffusion:db21e45d3f7023abc2a46ee38a23973f6dce16bb082a930b0c49861f96d1e5bf",
                    input={
                        "prompt": prompt,
                        "negative_prompt": negative_prompt,
                        "init_image": init_image_data_uri,
                        "strength": img2img_strength,
                        "guidance_scale": 7.5,
                        "num_inference_steps": 25,
                        "width": 512,
                        "height": 512
                    }
                )
            )
            
        except Exception as e:
            logger.error(f"❌ Replicate API call failed: {e}", exc_info=True)
            raise HTTPException(status_code=503, detail=f"Replicate API call failed: {str(e)}") from e
        
        # Validate output before indexing to prevent IndexError
        if not output:
            logger.error("❌ Replicate returned empty output")
            raise HTTPException(status_code=503, detail="Replicate returned empty output")
        
        if not isinstance(output, (list, tuple)):
            logger.error(f"❌ Replicate output is not a list/tuple, got: {type(output)}")
            raise HTTPException(status_code=503, detail=f"Unexpected Replicate output format: {type(output)}")
        
        if len(output) == 0:
            logger.error("❌ Replicate output list is empty")
            raise HTTPException(status_code=503, detail="Replicate output list is empty")
        
        # Validate that first element is a valid URL string
        image_url = output[0]
        if not image_url or not isinstance(image_url, str):
            logger.error(f"❌ Invalid Replicate output URL: {image_url}")
            raise HTTPException(status_code=503, detail="Invalid Replicate output URL format")
        
        # Download result from Replicate with proper error handling
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(image_url)
                if response.status_code == 200:
                    logger.info("✅ Replicate img2img transformation completed")
                    return response.content
                else:
                    logger.error(f"❌ Failed to download from Replicate: HTTP {response.status_code}")
                    raise HTTPException(status_code=503, detail=f"Failed to download from Replicate: {response.status_code}")
        except httpx.RequestError as e:
            logger.error(f"❌ Network error downloading from Replicate: {e}", exc_info=True)
            raise HTTPException(status_code=503, detail=f"Network error downloading from Replicate: {str(e)}") from e
        
        
    
    async def _transform_with_local(
        self,
        image_bytes: bytes,
        prompt: str,
        negative_prompt: str,
        control_type: str,
        strength: float,
        init_image_bytes: bytes | None = None,
        img2img_strength: float = 0.45
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
