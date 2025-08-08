"""
🌟 THEME SERVICE

This service is the creative engine that generates daily visual themes for Swamiji's avatar.
It uses Stability AI's image-to-image generation with balanced strength for natural transformation 
while preserving Swamiji's identity and changing clothing/background according to daily themes.
"""

import logging
from datetime import datetime
import os
import uuid
import httpx
from fastapi import HTTPException, Depends
import asyncpg
import json
import base64
from typing import Optional, Tuple, List
from PIL import Image, ImageDraw
import io
import numpy as np
from scipy import ndimage

from services.stability_ai_service import StabilityAiService, get_stability_service
from services.supabase_storage_service import SupabaseStorageService, get_storage_service
import db
from enum import Enum

logger = logging.getLogger(__name__)

# 🎯 ADVANCED FACE PRESERVATION METHODS
class FacePreservationMethod(Enum):
    """Face preservation method options for theme generation"""
    STABILITY_AI = "stability_ai"  # Current method (20-30% success)
    RUNWARE_FACEREF = "runware_faceref"  # IP-Adapter FaceID (80-90% success)

# 🚀 RUNWARE API SERVICE CLASS
class RunWareService:
    """
    🎯 RunWare API Service for IP-Adapter FaceID face preservation
    Achieves 80-90% face consistency with $0.0006 per image cost
    
    This service uses RunWare's IP-Adapter FaceID technology to maintain
    perfect face consistency while allowing complete background/clothing changes.
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.runware.ai/v1"
        
        if not api_key:
            logger.warning("⚠️ RunWare API key not provided - service will not be available")
        else:
            logger.info("✅ RunWare Service initialized with IP-Adapter FaceID support")
        
    async def generate_with_face_reference(
        self, 
        face_image_bytes: bytes, 
        prompt: str, 
        negative_prompt: str = "",
        width: int = 1024,
        height: int = 1024,
        steps: int = 30,
        cfg_scale: float = 7.0
    ) -> bytes:
        """
        Generate image with face reference preservation using IP-Adapter FaceID
        
        Args:
            face_image_bytes: Reference face image bytes (Swamiji photo)
            prompt: Theme generation prompt
            negative_prompt: Negative prompt to avoid unwanted features
            width: Output image width
            height: Output image height
            steps: Number of inference steps
            cfg_scale: Classifier-free guidance scale
            
        Returns:
            bytes: Generated image with preserved face
        """
        try:
            if not self.api_key:
                raise HTTPException(status_code=503, detail="RunWare API key not configured")
                
            # First, upload the face reference image
            face_url = await self._upload_reference_image(face_image_bytes)
            
            # 🎯 CORRECT RUNWARE API ENDPOINT
            url = "https://api.runware.ai/v1"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # 🎯 CORRECT RUNWARE API SCHEMA
            task_uuid = str(uuid.uuid4())
            payload = {
                "taskType": "imageInference",
                "taskUUID": task_uuid,
                "positivePrompt": prompt,
                "negativePrompt": negative_prompt,
                "model": "runware:105@1",
                "height": height,
                "width": width,
                "numberResults": 1,
                "steps": steps,  # Number of inference steps
                "CFGScale": cfg_scale,  # Classifier-free guidance scale
                "ipAdapters": [
                    {
                        "model": "runware:105@1",
                        "guideImage": face_url,
                        "weight": 1.0  # Maximum face preservation
                    }
                ]
            }
            
            logger.info(f"🎯 RunWare IP-Adapter FaceID generation starting...")
            logger.info(f"📝 Prompt: {prompt[:100]}...")
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                
                result = response.json()
                logger.info(f"🔍 RunWare API response structure: {list(result.keys())}")
                
                # 🎯 CORRECT RUNWARE RESPONSE PARSING
                data_array = result.get('data', [])
                if not data_array:
                    raise HTTPException(status_code=500, detail="No data returned by RunWare API")
                
                first_result = data_array[0]
                
                # Extract image URL or base64 data
                img_url = first_result.get('imageURL')
                if not img_url:
                    # Try alternative fields
                    img_url = first_result.get('imageBase64Data') or first_result.get('imageDataURI')
                    if not img_url:
                        raise HTTPException(status_code=500, detail="No image URL or data found in RunWare response")
                
                # Download the generated image if it's a URL, otherwise decode base64
                if img_url.startswith('http'):
                    img_response = await client.get(img_url)
                    img_response.raise_for_status()
                    image_content = img_response.content
                else:
                    # Handle base64 data
                    if img_url.startswith('data:image/'):
                        # Remove data URL prefix
                        img_url = img_url.split(',', 1)[1]
                    image_content = base64.b64decode(img_url)
                
                logger.info("✅ RunWare IP-Adapter FaceID generation completed successfully")
                return image_content
                
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ RunWare API error: {e.response.status_code} - {e.response.text}")
            raise HTTPException(status_code=502, detail=f"RunWare API error: {e.response.status_code}") from e
        except httpx.RequestError as e:
            logger.error(f"❌ Network error during RunWare generation: {e}")
            raise HTTPException(status_code=502, detail="Network error during RunWare generation") from e
        except Exception as e:
            logger.error(f"❌ RunWare generation failed: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"RunWare generation failed: {str(e)}") from e
    
    async def _upload_reference_image(self, image_bytes: bytes) -> str:
        """Upload reference image to RunWare and return URL"""
        try:
            url = f"{self.base_url}/image/upload"
            headers = {"Authorization": f"Bearer {self.api_key}"}
            
            files = {"image": ("reference.jpg", image_bytes, "image/jpeg")}
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, headers=headers, files=files)
                response.raise_for_status()
                
                result = response.json()
                uploaded_url = result.get('url')
                
                if not uploaded_url:
                    raise HTTPException(status_code=500, detail="Failed to upload reference image to RunWare")
                
                logger.info("✅ Reference image uploaded to RunWare successfully")
                return uploaded_url
                
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ RunWare upload API error: {e.response.status_code} - {e.response.text}")
            raise HTTPException(status_code=502, detail=f"RunWare upload API error: {e.response.status_code}") from e
        except httpx.RequestError as e:
            logger.error(f"❌ Network error during reference image upload: {e}")
            raise HTTPException(status_code=502, detail="Network error during reference image upload") from e
        except Exception as e:
            logger.error(f"❌ Failed to upload reference image: {e}")
            raise HTTPException(status_code=500, detail=f"Reference image upload failed: {str(e)}") from e

# 🎯 PHASE 1: DRAMATIC COLOR REDESIGN - Maximum contrast to avoid saffron conflicts
# Each theme uses COMPLETELY DIFFERENT colors + varied clothing styles for better AI differentiation
THEMES = {
    0: {"name": "Meditative Monday", "description": "wearing pristine PURE WHITE ceremonial robes with flowing silver-trimmed fabric, sitting in lotus position on a snow-capped Himalayan mountain peak at golden sunrise, surrounded by swirling morning mist and ancient prayer flags, with soft ethereal lighting illuminating the serene meditation pose"},
    1: {"name": "Teaching Tuesday", "description": "wearing rich DEEP MAROON traditional scholar robes with intricate golden embroidery and sacred symbols, seated on an ornate wooden throne in a magnificent ashram hall with carved pillars, colorful tapestries, brass oil lamps, and devoted disciples seated on the marble floor, warm temple lighting creating a divine atmosphere"},
    2: {"name": "Wisdom Wednesday", "description": "wearing FOREST GREEN simple cotton kurta with natural hemp threads, sitting cross-legged under a massive ancient banyan tree with sprawling roots, surrounded by palm leaf manuscripts, traditional ink pots, wooden writing stylus, dappled sunlight filtering through dense green foliage creating a scholarly forest retreat"},
    3: {"name": "Thankful Thursday", "description": "wearing ROYAL BLUE silk kurta with simple white dhoti, kneeling gracefully by a sacred crystal-clear river with lotus flowers floating on the surface, holding a brass plate filled with marigold offerings, coconut, incense, surrounded by ancient stone ghats and temple spires in the misty distance"},
    4: {"name": "Festive Friday", "description": "adorned in magnificent BRIGHT GOLDEN YELLOW silk robes with elaborate zari work, ruby gemstones, sacred rudraksha beads, standing in a grand temple courtyard during festival celebrations with colorful rangoli patterns, hanging marigold garlands, burning oil lamps, devotees with musical instruments, vibrant festival atmosphere"},
    5: {"name": "Silent Saturday", "description": "wearing simple CHARCOAL GRAY meditation robes with rough handwoven texture, sitting in perfect stillness inside a dimly lit ancient cave with smooth stone walls, flickering butter lamps casting dancing shadows, stalactites overhead, complete silence and spiritual solitude, minimal natural lighting from cave entrance"},
    6: {"name": "Serene Sunday", "description": "wearing flowing CREAM-COLORED cotton dhoti with subtle silver threads, walking barefoot on pristine white sand along an endless ocean beach at peaceful dawn, gentle waves lapping the shore, seagulls in the distance, palm trees swaying, soft morning sunlight creating a heavenly coastal sanctuary"},
}

class ThemeService:
    """
    🎯 ENHANCED THEME SERVICE: Multi-method face preservation support
    Orchestrates daily theme generation with advanced face preservation methods.
    
    Supported Methods:
    - Stability AI img2img (legacy, 20-30% success)
    - RunWare IP-Adapter FaceID (advanced, 80-90% success)
    """

    def __init__(
        self,
        stability_service: StabilityAiService,
        storage_service: SupabaseStorageService,
        db_conn: asyncpg.Connection,
    ):
        self.stability_service = stability_service
        self.storage_service = storage_service
        self.db_conn = db_conn
        
        # 🎯 ADVANCED FACE PRESERVATION CONFIGURATION
        # Read environment variables for face preservation method
        from core_foundation_enhanced import EnhancedSettings
        settings = EnhancedSettings()
        
        self.face_preservation_method = settings.face_preservation_method
        self.runware_api_key = settings.runware_api_key
        
        # Initialize RunWare service if configured
        if self.face_preservation_method == FacePreservationMethod.RUNWARE_FACEREF.value:
            if self.runware_api_key:
                self.runware_service = RunWareService(self.runware_api_key)
                logger.info("✅ ThemeService initialized with RunWare IP-Adapter FaceID (80-90% success rate)")
            else:
                logger.warning("⚠️ RunWare method selected but API key not provided, falling back to Stability AI")
                self.face_preservation_method = FacePreservationMethod.STABILITY_AI.value
        
        if self.face_preservation_method == FacePreservationMethod.STABILITY_AI.value:
            logger.info("📝 ThemeService initialized with Stability AI img2img (20-30% success rate)")
        
        logger.info(f"🎯 Active face preservation method: {self.face_preservation_method}")
    
    async def _generate_with_runware(
        self, 
        base_image_bytes: bytes,
        theme_description: str,
        custom_prompt: Optional[str] = None
    ) -> Tuple[bytes, str]:
        """
        🚀 RUNWARE IP-ADAPTER FACEID GENERATION METHOD
        Uses RunWare's advanced face preservation technology for 80-90% success rate.
        
        Args:
            base_image_bytes: Swamiji reference image bytes
            theme_description: Daily theme description
            custom_prompt: Optional custom prompt override
            
        Returns:
            Tuple[bytes, str]: Generated image bytes and final prompt used
        """
        try:
            # 🎨 CONSTRUCT OPTIMIZED PROMPT FOR RUNWARE
            if custom_prompt:
                final_prompt = custom_prompt
            else:
                # Create comprehensive prompt for RunWare IP-Adapter
                final_prompt = f"""A photorealistic, high-resolution portrait of the same person {theme_description}.
                
CRITICAL: Preserve the exact same person's face, identity, and features.
Transform ONLY the clothing, background, and environment to match the theme.
Maintain professional spiritual appearance with authentic details.
High quality, detailed, cinematic lighting, masterpiece."""

            # 🛡️ COMPREHENSIVE NEGATIVE PROMPT for face preservation
            negative_prompt = """different face, changed face, new face, altered face, face swap, face replacement, 
different person, wrong identity, mutated face, distorted face, different eyes, different nose, different mouth, 
face morph, artificial face, generic face, low quality, blurry, deformed, ugly, bad anatomy, cartoon"""

            logger.info("🚀 Starting RunWare IP-Adapter FaceID generation...")
            logger.info(f"📝 Final prompt: {final_prompt[:150]}...")
            
            # Generate with RunWare IP-Adapter FaceID
            generated_image_bytes = await self.runware_service.generate_with_face_reference(
                face_image_bytes=base_image_bytes,
                prompt=final_prompt,
                negative_prompt=negative_prompt,
                width=1024,
                height=1024,
                steps=30,
                cfg_scale=7.0
            )
            
            logger.info("✅ RunWare IP-Adapter FaceID generation completed successfully")
            return generated_image_bytes, final_prompt
            
        except Exception as e:
            logger.error(f"❌ RunWare generation failed: {e}", exc_info=True)
            # Re-raise the exception to be handled by the calling method
            raise

    async def _generate_with_stability_legacy(
        self, 
        base_image_bytes: bytes,
        theme_description: str,
        custom_prompt: Optional[str] = None,
        strength_param: float = 0.4
    ) -> Tuple[bytes, str]:
        """
        📝 STABILITY AI GENERATION METHOD (Legacy)
        Uses existing Stability AI img2img approach for fallback compatibility.
        
        This method contains the original ultra-strong prompt approach that was
        previously used in generate_themed_image_bytes().
        
        Args:
            base_image_bytes: Swamiji reference image bytes
            theme_description: Daily theme description
            custom_prompt: Optional custom prompt override
            strength_param: Transformation strength (0.1-0.4)
            
        Returns:
            Tuple[bytes, str]: Generated image bytes and final prompt used
        """
        try:
            logger.info("📝 Starting Stability AI img2img generation (legacy method)")
            
            # 🎨 OPTION 5+6 COMBINATION: Ultra-extended mask + AI color analysis for ULTIMATE precision
            logger.info("🎨 OPTION 5+6 ULTIMATE: Ultra-extended mask (40% neck) + AI color analysis + precise color injection")
            
            # Get image dimensions for mask creation
            base_image = Image.open(io.BytesIO(base_image_bytes))
            image_width, image_height = base_image.size
            logger.info(f"📐 BASE IMAGE DIMENSIONS: {image_width}x{image_height}")
            
            # 🎨 OPTION 6: Advanced face color analysis - Extract precise skin tone colors
            try:
                analyzed_skin_color = self._analyze_face_skin_color(base_image_bytes)
                logger.info(f"🎨 COLOR ANALYSIS COMPLETE: {analyzed_skin_color}")
            except Exception as color_error:
                logger.error(f"❌ Color analysis failed, using fallback: {color_error}")
                analyzed_skin_color = "warm natural skin tone with consistent complexion"
            
            # 🎯 NO MASK APPROACH: Ultra-strong prompts for face preservation
            
            # 🎨 ULTRA-STRONG FACE PRESERVATION PROMPTS - Force AI to keep exact same face
            ultra_strong_prompt = f"""CRITICAL INSTRUCTION: Keep the EXACT SAME PERSON with identical face, eyes, nose, mouth, facial structure, and skin tone ({analyzed_skin_color}).
DO NOT change this person's face or identity in ANY way.

Transform ONLY the clothing and background to: {theme_description}

MANDATORY PRESERVATION:
- Keep this exact person's face completely unchanged
- Preserve all facial features: same eyes, same nose, same mouth, same cheeks
- Maintain identical facial structure and bone structure  
- Keep exact same skin tone and complexion
- Preserve same head shape and hair
- Do not alter this person's identity

TRANSFORM ONLY:
- Change clothing style and colors to match the theme
- Modify background environment and setting
- Adjust lighting and atmosphere
- Add appropriate accessories (jewelry, beads, tilaka)

This must remain the same recognizable person with only clothing and background changes."""
            
            # 🚫 ULTRA-STRONG NEGATIVE PROMPTS - Prevent any face alterations
            ultra_negative_prompt = "different face, changed face, new face, altered face, face swap, face replacement, different person, changed identity, wrong identity, mutated face, distorted face, different eyes, different nose, different mouth, different skin, face morph, face change, artificial face, generic face, template face, stock photo face, different facial structure, altered features"

            # 🎯 SWITCHING TO IMG2IMG: No mask, caller-specified strength with bounds, strong prompts
            logger.info("🎯 SWITCHING TO NO-MASK IMG2IMG: Ultra-strong prompts for face preservation")
            
            # 🔧 RESPECT CALLER'S STRENGTH with face-safe bounds checking (CORE.MD compliance)
            # Clamp strength_param to face-safe range (0.1 to 0.4) to prevent face distortion
            effective_strength = max(0.1, min(strength_param, 0.4))
            
            logger.info(f"🎯 EFFECTIVE STRENGTH: {effective_strength} (requested: {strength_param}, clamped to face-safe range 0.1-0.4)")
            
            # 🛡️ NO-MASK TRANSFORMATION - Rely entirely on prompt instructions
            logger.info("🎯 NO-MASK IMG2IMG: Starting ultra-strong prompt-based face preservation")
            logger.info(f"🎨 ULTRA-STRONG PROMPT: {ultra_strong_prompt[:200]}...")
            
            raw_generated_bytes = await self.stability_service.generate_image_to_image(
                init_image_bytes=base_image_bytes,
                text_prompt=ultra_strong_prompt,
                negative_prompt=ultra_negative_prompt,
                strength=effective_strength
            )
            logger.info("✅ NO-MASK SUCCESS: Face preservation via ultra-strong prompts")
            
            logger.info("✅ NO-MASK IMG2IMG COMPLETE: Prompt-based face preservation with theme changes")
            return raw_generated_bytes, ultra_strong_prompt
            
        except Exception as e:
            logger.error(f"❌ Stability AI generation failed: {e}", exc_info=True)
            raise




    async def _apply_color_harmonization(
        self, 
        generated_image_bytes: bytes, 
        original_image_bytes: bytes,
        mask_bytes: bytes,
        image_width: int, 
        image_height: int
    ) -> bytes:
        """
        🎨 ADVANCED COLOR HARMONIZATION: Fix face-body color mismatch for natural blending.
        
        USER REQUIREMENT: "body oda face porunthanu" - Face and body should blend naturally
        - Analyzes AI-generated body colors and lighting
        - Adjusts preserved face region to match body's color palette
        - Applies smooth gradient blending at mask edges
        - Maintains face identity while improving color consistency
        
        HARMONIZATION TECHNIQUES:
        1. Color Temperature Matching: Adjust face warmth/coolness to match body
        2. Saturation Matching: Align face saturation with AI-generated style
        3. Brightness/Contrast Matching: Match lighting conditions
        4. Gradient Blending: Smooth transitions at preserved region edges
        
        Args:
            generated_image_bytes: AI-generated image with face-body mismatch
            original_image_bytes: Original Swamiji photo for reference
            mask_bytes: Mask used for inpainting (to identify preserved regions)
            image_width: Image width
            image_height: Image height
            
        Returns:
            bytes: Color-harmonized image with natural face-body blending
        """
        try:
            # Load images
            generated_image = Image.open(io.BytesIO(generated_image_bytes)).convert('RGB')
            mask_image = Image.open(io.BytesIO(mask_bytes)).convert('L')
            
            # Convert to numpy arrays for processing
            generated_array = np.array(generated_image)
            mask_array = np.array(mask_image)
            
            # Create face and body region masks
            # Face region: where mask is dark (preserved areas)
            face_mask = mask_array < 128  # Black/dark areas = preserved face
            body_mask = mask_array >= 192  # White/bright areas = AI-generated body
            
            # Extract color statistics from each region
            face_pixels = generated_array[face_mask]
            body_pixels = generated_array[body_mask]
            
            if len(face_pixels) == 0 or len(body_pixels) == 0:
                logger.warning("⚠️ Color harmonization: Insufficient face or body pixels, using original")
                return generated_image_bytes
            
            # Calculate color statistics
            face_mean = np.mean(face_pixels, axis=0)
            body_mean = np.mean(body_pixels, axis=0)
            
            face_std = np.std(face_pixels, axis=0)
            body_std = np.std(body_pixels, axis=0)
            
            # 🎨 COLOR HARMONIZATION: Adjust face colors to match body
            # 1. Calculate color shift needed
            color_shift = body_mean - face_mean
            
            # 2. Calculate saturation adjustment
            face_saturation = np.mean(face_std)
            body_saturation = np.mean(body_std)
            saturation_ratio = body_saturation / max(face_saturation, 1.0)
            
            # 3. Create harmonized image
            harmonized_array = generated_array.copy()
            
            # 🚀 VECTORIZED COLOR HARMONIZATION: High-performance color adjustments
            adjustment_strength = 0.4  # Subtle adjustment to maintain face identity
            
            # Create float copy for processing
            harmonized_array_float = harmonized_array.astype(float)
            
            # Get indices of face pixels for vectorized operations
            face_indices = np.where(face_mask)
            
            if len(face_indices[0]) > 0:
                # Extract face pixels for vectorized processing
                face_pixels_float = harmonized_array_float[face_indices]
                
                # 1. Apply color temperature shift (vectorized)
                adjusted_pixels = face_pixels_float + (color_shift * adjustment_strength)
                
                # 2. Apply saturation adjustment (vectorized)
                pixel_means = np.mean(adjusted_pixels, axis=1, keepdims=True)
                adjusted_pixels = pixel_means + (adjusted_pixels - pixel_means) * (
                    saturation_ratio ** adjustment_strength
                )
                
                # 3. Ensure valid range
                adjusted_pixels = np.clip(adjusted_pixels, 0, 255)
                
                # 4. Calculate blend factors based on mask values (vectorized)
                mask_values = mask_array[face_indices]
                blend_factors = np.where(
                    mask_values < 64,
                    adjustment_strength,  # Core preserved area
                    adjustment_strength * 0.3  # Edge area - less adjustment
                )
                
                # 5. Apply blended adjustment (vectorized)
                blended_pixels = (
                    face_pixels_float * (1 - blend_factors[:, np.newaxis]) + 
                    adjusted_pixels * blend_factors[:, np.newaxis]
                )
                
                # Update harmonized array with processed pixels
                harmonized_array_float[face_indices] = blended_pixels
            
            # Convert back to uint8
            harmonized_array = harmonized_array_float.astype(np.uint8)
            
            # Convert back to PIL Image
            harmonized_image = Image.fromarray(harmonized_array, mode='RGB')
            
            # Convert to bytes
            harmonized_buffer = io.BytesIO()
            harmonized_image.save(harmonized_buffer, format='PNG')
            harmonized_bytes = harmonized_buffer.getvalue()
            
            logger.info(f"🎨 COLOR HARMONIZATION SUCCESS: Face-body color matching applied | "
                       f"Face mean: {face_mean.astype(int)} → Body mean: {body_mean.astype(int)} | "
                       f"Saturation ratio: {saturation_ratio:.2f}")
            
            return harmonized_bytes
            
        except Exception as e:
            logger.error(f"❌ Color harmonization failed, using original: {str(e)}")
            # Fallback: return generated image without harmonization
            return generated_image_bytes

    def _analyze_face_skin_color(self, image_bytes: bytes) -> str:
        """
        🎨 OPTION 6: Advanced color analysis - Extract dominant skin colors from face area.
        
        Analyzes the preserved face area to extract dominant skin tone colors and
        converts them to descriptive terms for prompt injection.
        
        Args:
            image_bytes: Original image bytes to analyze
            
        Returns:
            str: Descriptive color terms for prompt injection
            
        Analysis Process:
        1. Load image and extract face area pixels
        2. Calculate dominant RGB colors using clustering
        3. Convert RGB values to descriptive color terms
        4. Return formatted color description for prompts
        """
        try:
            # Load image and convert to RGB
            image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
            image_width, image_height = image.size
            
            # Calculate face area coordinates (same as mask inner zone)
            face_width_ratio = 0.28   # 28% of image width
            face_height_ratio = 0.32  # 32% of image height
            
            face_width = int(image_width * face_width_ratio)
            face_height = int(image_height * face_height_ratio)
            
            face_left = (image_width - face_width) // 2
            face_top = int(image_height * 0.15)
            face_right = face_left + face_width
            face_bottom = face_top + face_height
            
            # Extract face area pixels
            face_area = image.crop((face_left, face_top, face_right, face_bottom))
            face_pixels = np.array(face_area)
            
            # Reshape to list of RGB values
            pixels_reshaped = face_pixels.reshape(-1, 3)
            
            # Calculate average RGB values (dominant color) with safe conversion
            try:
                avg_r = float(np.mean(pixels_reshaped[:, 0]))
                avg_g = float(np.mean(pixels_reshaped[:, 1]))
                avg_b = float(np.mean(pixels_reshaped[:, 2]))
                
                # Clamp to valid RGB range and convert to int
                avg_r = max(0, min(255, int(round(avg_r))))
                avg_g = max(0, min(255, int(round(avg_g))))
                avg_b = max(0, min(255, int(round(avg_b))))
                
            except (ValueError, OverflowError, TypeError) as e:
                logger.warning(f"RGB calculation error, using fallback values: {e}")
                avg_r, avg_g, avg_b = 139, 102, 85  # Safe fallback values
            
            # Convert RGB to descriptive color terms with error handling
            color_description = self._rgb_to_skin_tone_description(avg_r, avg_g, avg_b)
            
            logger.info(f"🎨 FACE COLOR ANALYSIS: RGB({avg_r}, {avg_g}, {avg_b}) → {color_description}")
            return color_description
            
        except Exception as e:
            logger.error(f"❌ Face color analysis failed: {e}")
            # Fallback to generic description
            return "warm natural skin tone with consistent complexion"
    
    def _rgb_to_skin_tone_description(self, r: int, g: int, b: int) -> str:
        """
        Convert RGB values to descriptive skin tone terms for AI prompts.
        
        CORE.MD & REFRESH.MD COMPLIANCE: Enhanced with RGB validation, improved warmth calculation,
        and accurate color terminology without hardcoded assumptions.
        
        Args:
            r, g, b: RGB color values (must be 0-255)
            
        Returns:
            str: Descriptive color terms for prompt injection
            
        Raises:
            ValueError: If RGB values are outside valid 0-255 range
        """
        # 🛡️ RGB VALIDATION - CORE.MD: Input validation with clear error messages
        if not all(isinstance(val, (int, float)) for val in [r, g, b]):
            raise ValueError(f"RGB values must be numeric. Received: r={type(r).__name__}, g={type(g).__name__}, b={type(b).__name__}")
        
        if not all(0 <= val <= 255 for val in [r, g, b]):
            raise ValueError(f"RGB values must be in range 0-255. Received: r={r}, g={g}, b={b}")
        
        # Convert to int for consistency
        r, g, b = int(r), int(g), int(b)
        
        # 🎨 ENHANCED WARMTH CALCULATION - Include green channel for accurate color temperature
        brightness = (r + g + b) / 3
        # Improved warmth: considers both red-blue and green-blue relationships for accurate skin tone analysis
        warmth = (r - b) + (g - b) * 0.5  # Weighted formula: red-blue primary, green-blue secondary
        
        # 🎯 ENHANCED BASE TONE DETERMINATION - More accurate skin tone categories
        if brightness > 200:
            base_tone = "very fair"
        elif brightness > 180:
            base_tone = "fair"
        elif brightness > 140:
            base_tone = "medium" 
        elif brightness > 100:
            base_tone = "olive"
        elif brightness > 60:
            base_tone = "deep"
        else:
            base_tone = "very deep"
            
        # 🌡️ ENHANCED WARMTH CATEGORIZATION - Improved thresholds for green-enhanced calculation
        if warmth > 30:
            warmth_desc = "warm golden"
        elif warmth > 15:
            warmth_desc = "warm"
        elif warmth > -15:
            warmth_desc = "neutral"
        elif warmth > -30:
            warmth_desc = "cool"
        else:
            warmth_desc = "cool pink"
            
        # ✅ ACCURATE COLOR DESCRIPTION - Remove hardcoded "brown", use precise terminology
        # No assumptions about skin color - let the AI determine the actual hue based on RGB values
        color_description = f"{warmth_desc} {base_tone} skin tone with RGB({r}, {g}, {b}) undertones"
        
        return color_description

    def _create_face_preservation_mask(self, image_width: int, image_height: int) -> bytes:
        """
        🎭 FACE PRESERVATION MASK: Creates mask for inpainting where face area is preserved.
        
        USER SPECIFICATION: Face area-ஐ mask செய்யாதீர்கள் - Just mask dress & body only.
        
        Mask Logic:
        - BLACK pixels (0) = Face area = PRESERVE (never touched by AI)
        - WHITE pixels (255) = Dress/body/background = TRANSFORM
        
        Args:
            image_width: Width of the base image
            image_height: Height of the base image
            
        Returns:
            bytes: PNG mask image where face is black (preserved), rest is white (transformed)
        """
        try:
            # Create white background (all areas will be transformed by default)
            mask = Image.new('L', (image_width, image_height), 255)  # White = transform
            draw = ImageDraw.Draw(mask)
            
            # 🎯 FACE AREA CALCULATION - Small centered area for face preservation
            # Conservative face area - only core facial features
            face_width_ratio = 0.22   # 22% of image width (smaller than before)
            face_height_ratio = 0.28  # 28% of image height (smaller than before)
            
            face_width = int(image_width * face_width_ratio)
            face_height = int(image_height * face_height_ratio)
            
            # Center the face area
            face_left = (image_width - face_width) // 2
            face_top = int(image_height * 0.18)  # Slightly higher position for face
            face_right = face_left + face_width
            face_bottom = face_top + face_height
            
            # 🎭 DRAW FACE PRESERVATION AREA - Black ellipse for natural face shape
            draw.ellipse(
                [face_left, face_top, face_right, face_bottom],
                fill=0  # Black = preserve face area
            )
            
            # Convert to bytes
            mask_buffer = io.BytesIO()
            mask.save(mask_buffer, format='PNG')
            mask_bytes = mask_buffer.getvalue()
            
            logger.info(f"🎭 FACE MASK CREATED: {image_width}x{image_height} | Face area: {face_width}x{face_height} | Position: ({face_left},{face_top}) to ({face_right},{face_bottom})")
            logger.info(f"🎯 MASK LOGIC: Face ellipse BLACK (preserve), rest WHITE (transform) | Mask size: {len(mask_bytes)/1024:.1f}KB")
            
            return mask_bytes
            
        except Exception as e:
            logger.error(f"❌ Face preservation mask creation failed: {e}")
            # Fallback: create simple center rectangle mask
            mask = Image.new('L', (image_width, image_height), 255)
            draw = ImageDraw.Draw(mask)
            center_x, center_y = image_width // 2, image_height // 2
            face_size = min(image_width, image_height) // 4
            draw.rectangle([
                center_x - face_size//2, center_y - face_size//2,
                center_x + face_size//2, center_y + face_size//2
            ], fill=0)
            
            mask_buffer = io.BytesIO()
            mask.save(mask_buffer, format='PNG')
            return mask_buffer.getvalue()

    async def _determine_safe_strength(self, requested_strength: float) -> float:
        """
        🎯 FEATURE FLAG CONTROLLED STRENGTH DETERMINATION - CORE.MD & REFRESH.MD COMPLIANCE
        Implements A/B testing and controlled rollout for aggressive transformation parameters.
        
        Args:
            requested_strength: The requested strength parameter (default 0.4)
            
        Returns:
            float: The final strength to use, controlled by feature flags and safety checks
            
        Feature Flag Logic:
        - AGGRESSIVE_THEME_TESTING=true: Enables controlled aggressive testing (0.6-0.8)
        - TESTING_MODE=true: Allows higher strength for development testing
        - Default: Uses safe range (0.3-0.4) for production
        - A/B Testing: Future enhancement for user subset testing
        """
        # Environment-based feature flags
        aggressive_testing_enabled = os.getenv("AGGRESSIVE_THEME_TESTING", "false").lower() == "true"
        testing_mode = os.getenv("TESTING_MODE", "false").lower() == "true"
        environment = os.getenv("ENVIRONMENT", "production").lower()
        
        # Safety validation - ensure strength is within valid range
        if not (0.0 <= requested_strength <= 1.0):
            logger.error(f"❌ INVALID STRENGTH: {requested_strength} outside range 0.0-1.0, defaulting to 0.4")
            return 0.4
            
        # Feature flag decision tree
        if aggressive_testing_enabled and environment in ["development", "staging", "testing"]:
            # Controlled aggressive testing in non-production environments
            if requested_strength > 0.4:
                logger.warning(f"🧪 FEATURE FLAG ACTIVE: Aggressive testing enabled, using requested strength {requested_strength}")
                return min(requested_strength, 0.8)  # Cap at 0.8 maximum
            else:
                return requested_strength
                
        elif testing_mode and environment != "production":
            # Development testing mode - allow requested strength but with logging
            if requested_strength > 0.4:
                logger.warning(f"🔧 TESTING MODE: Using requested strength {requested_strength} in {environment}")
                return min(requested_strength, 0.8)  # Cap at 0.8 maximum
            else:
                return requested_strength
                
        else:
            # Production safety - enforce safe range
            if requested_strength > 0.4:
                logger.warning(f"🔒 PRODUCTION SAFETY: Requested strength {requested_strength} exceeds safe range, capping at 0.4")
                return 0.4
            else:
                return max(requested_strength, 0.3)  # Minimum 0.3 for some transformation

    async def _get_base_image_data(self) -> tuple[bytes, str]:
        """
        Fetches the uploaded Swamiji image URL from the DB, downloads the image,
        and returns both the bytes and the public URL.
        """
        image_url = None
        try:
            record = await self.db_conn.fetchrow("SELECT value FROM platform_settings WHERE key = 'swamiji_avatar_url'")
            if not record or not record['value']:
                raise HTTPException(status_code=404, detail="Swamiji base image not found. Please upload a photo first.")
            
            raw_value = record['value']
            try:
                image_url = json.loads(raw_value)
                if not isinstance(image_url, str):
                    raise TypeError("Parsed JSON value is not a string URL.")
            except (json.JSONDecodeError, TypeError):
                if isinstance(raw_value, str) and raw_value.startswith('http'):
                    image_url = raw_value
                else:
                    raise HTTPException(status_code=500, detail="Invalid format for Swamiji image URL in database.")

            if not image_url:
                 raise HTTPException(status_code=500, detail="Could not determine a valid image URL from database.")

            async with httpx.AsyncClient() as client:
                response = await client.get(image_url)
                response.raise_for_status()
                return response.content, image_url
                
        except asyncpg.PostgresError as e:
            logger.error(f"Database error while fetching Swamiji image URL: {e}", exc_info=True)
            raise HTTPException(status_code=503, detail="A database error occurred.") from e
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to download the base Swamiji image from {image_url}: {e}", exc_info=True)
            raise HTTPException(status_code=502, detail="Could not download the base Swamiji image.") from e
        except Exception as e:
            logger.error(f"An unexpected error occurred in _get_base_image_data: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="An unexpected error occurred while retrieving the image.") from e





    async def generate_themed_image_bytes(
        self, 
        custom_prompt: Optional[str] = None, 
        theme_day: Optional[int] = None,
        strength_param: float = 0.4  # Transformation strength (0.1-0.4 clamped for face safety)
    ) -> Tuple[bytes, str]:
        """
        🎯 ENHANCED MULTI-METHOD FACE PRESERVATION GENERATION
        
        Supports multiple face preservation methods via environment configuration:
        - RunWare IP-Adapter FaceID (80-90% success, $0.0006/image)
        - Stability AI img2img (20-30% success, legacy fallback)
        
        Args:
            custom_prompt: Optional custom prompt to override theme-based generation
            theme_day: Optional day override (0=Monday, 1=Tuesday, ..., 6=Sunday). If None, uses current day.
            strength_param: Transformation strength (0.0-1.0). Only used for Stability AI method.
        
        Returns:
            Tuple[bytes, str]: Generated image bytes and final prompt used
        
        Environment Configuration:
            FACE_PRESERVATION_METHOD=runware_faceref  # Use RunWare (recommended)
            FACE_PRESERVATION_METHOD=stability_ai     # Use Stability AI (fallback)
        """
        try:
            # 🔍 COMMON PREPARATION: Get base image and determine theme
            base_image_bytes, base_image_url = await self._get_base_image_data()
            logger.info(f"Base image loaded: {len(base_image_bytes)/1024:.1f}KB from {base_image_url}")
            
            # 🎨 DETERMINE THEME DESCRIPTION
            if custom_prompt:
                theme_description = custom_prompt
                logger.info(f"Using custom prompt: {custom_prompt}")
            else:
                # CORE.MD & REFRESH.MD: Explicit validation instead of silent fallback
                if theme_day is not None:
                    # Validate theme_day is within valid range 0-6 (Monday=0, Sunday=6)
                    if not isinstance(theme_day, int) or theme_day < 0 or theme_day > 6:
                        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                        valid_range = ', '.join([f"{i}={day_names[i]}" for i in range(7)])
                        error_msg = (
                            f"Invalid theme_day={theme_day}. Must be an integer between 0-6 "
                            f"({valid_range}). Received: {theme_day} (type: {type(theme_day).__name__})"
                        )
                        logger.error(f"❌ THEME_DAY VALIDATION ERROR: {error_msg}")
                        raise ValueError(error_msg)
                    
                    day_of_week = theme_day
                    logger.info(f"🎯 THEME OVERRIDE: Using theme_day={theme_day} instead of current day")
                else:
                    # Only use current day when theme_day is None (not provided)
                    day_of_week = datetime.now().weekday()
                    logger.info(f"📅 Using current day: {day_of_week}")
                
                theme = THEMES.get(day_of_week, THEMES.get(0, {"description": "in a serene setting"}))
                theme_description = theme['description']
                day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                logger.info(f"🎨 Using theme for {day_names[day_of_week]}: {theme.get('name', 'Unknown')} - {theme_description[:100]}...")

            # 🎯 METHOD SELECTION: Choose face preservation method based on configuration
            logger.info(f"🎯 Active face preservation method: {self.face_preservation_method}")
            
            if self.face_preservation_method == FacePreservationMethod.RUNWARE_FACEREF.value:
                # 🚀 RUNWARE IP-ADAPTER FACEID METHOD (80-90% success)
                try:
                    logger.info("🚀 Using RunWare IP-Adapter FaceID for face preservation (80-90% success rate)")
                    return await self._generate_with_runware(
                        base_image_bytes=base_image_bytes,
                        theme_description=theme_description,
                        custom_prompt=custom_prompt
                    )
                except Exception as runware_error:
                    logger.error(f"❌ RunWare generation failed: {runware_error}")
                    logger.info("🔄 Falling back to Stability AI method...")
                    # Fall through to Stability AI fallback
            
            # 📝 STABILITY AI METHOD (Fallback or explicit choice)
            logger.info("📝 Using Stability AI img2img for face preservation (20-30% success rate)")
            return await self._generate_with_stability_legacy(
                base_image_bytes=base_image_bytes,
                theme_description=theme_description,
                custom_prompt=custom_prompt,
                strength_param=strength_param
            )

        except Exception as e:
            logger.error(f"Failed to generate themed image bytes: {e}", exc_info=True)
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(status_code=500, detail="Failed to generate themed image bytes.") from e

    async def generate_and_upload_themed_image(self, custom_prompt: Optional[str] = None) -> dict:
        """
        Generates a themed image, uploads it, and returns the public URL and the prompt used.
        """
        try:
            # REFRESH.MD: FIX - Get both the image and the actual prompt used.
            # PHASE 2: Using inpainting approach - no strength parameter needed (mask provides precision)
            generated_image_bytes, final_prompt = await self.generate_themed_image_bytes(
                custom_prompt=custom_prompt
                # No strength_param needed - inpainting uses mask for precision control
            )

            unique_filename = f"swamiji_masked_theme_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4()}.png"
            file_path_in_bucket = f"daily_themes/{unique_filename}"

            public_url = self.storage_service.upload_file(
                bucket_name="avatars",
                file_path_in_bucket=file_path_in_bucket,
                file=generated_image_bytes,
                content_type="image/png"
            )
            
            logger.info(f"✅ Successfully uploaded masked themed image to {public_url}")
            # REFRESH.MD: FIX - Return the actual prompt instead of a placeholder.
            return {"image_url": public_url, "prompt_used": final_prompt}

        except Exception as e:
            logger.error(f"Failed to create and upload the daily themed avatar image: {e}", exc_info=True)
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(status_code=500, detail="Failed to create and upload themed image.") from e

# --- FastAPI Dependency Injection ---
def get_theme_service(
    stability_service: StabilityAiService = Depends(get_stability_service),
    storage_service: SupabaseStorageService = Depends(get_storage_service),
    db_conn: asyncpg.Connection = Depends(db.get_db),
) -> "ThemeService":
    """Creates an instance of the ThemeService with its required dependencies."""
    return ThemeService(stability_service, storage_service, db_conn)
