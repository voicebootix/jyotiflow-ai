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
from typing import Optional, Tuple
from PIL import Image, ImageDraw
import io

from services.stability_ai_service import StabilityAiService, get_stability_service
from services.supabase_storage_service import SupabaseStorageService, get_storage_service
import db

logger = logging.getLogger(__name__)

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
    """Orchestrates the generation of daily themes using Stability AI img2img."""

    def __init__(
        self,
        stability_service: StabilityAiService,
        storage_service: SupabaseStorageService,
        db_conn: asyncpg.Connection,
    ):
        self.stability_service = stability_service
        self.storage_service = storage_service
        self.db_conn = db_conn
        
        logger.info("Initialized ThemeService with Stability AI img2img service")
    


    def _create_face_preservation_mask(self, image_width: int, image_height: int) -> bytes:
        """
        🎨 SOFT GRADIENT MASK: Create natural blending mask for head-body integration.
        
        Creates a multi-zone gradient mask for smooth transitions:
        - BLACK (0) = Core face area PRESERVED completely
        - DARK GRAY (64) = Blend zone with 75% preservation, 25% transformation  
        - MEDIUM GRAY (128) = Neck/collar blend zone with 50% preservation, 50% transformation
        - WHITE (255) = Clothes/background area TRANSFORMED completely
        
        Args:
            image_width: Width of the original image
            image_height: Height of the original image
            
        Returns:
            bytes: PNG mask image as bytes
            
        Mask Strategy (OPTION 4 - HYBRID APPROACH):
        - Extended soft gradient mask with 3-zone blending + color matching prompts
        - Inner zone (black): Core face features preserved (eyes, nose, mouth) 
        - Middle zone (dark gray): 75% preserve, 25% blend for smooth transitions
        - Outer zone (medium gray): Extended 25% more for neck/upper chest skin tone reference
        - Color prompts: Explicit skin tone matching and lighting consistency instructions
        - White areas: Complete transformation freedom for clothes/background
        """
        # Create a white background (transform everything by default)
        mask = Image.new('L', (image_width, image_height), 255)  # 'L' = grayscale, 255 = white
        draw = ImageDraw.Draw(mask)
        
        # 🎯 PRECISION MASK: Match user's red circle - tight face area only
        # Adjusted to match screenshot red circle precision
        face_width_ratio = 0.28   # 28% of image width (reduced from 40% - more precise)
        face_height_ratio = 0.32  # 32% of image height (reduced from 50% - tighter)
        
        face_width = int(image_width * face_width_ratio)
        face_height = int(image_height * face_height_ratio)
        
        # Center the face horizontally, position vertically at 15% from top for precision
        face_left = (image_width - face_width) // 2
        face_top = int(image_height * 0.15)  # Start 15% from top (matches user's red circle specification)
        face_right = face_left + face_width
        face_bottom = face_top + face_height
        
        # 🎨 SOFT GRADIENT MASK: Create natural blending for head-body integration
        
        # Step 1: Create inner face oval (pure preservation - black)
        inner_face_left = face_left + int(face_width * 0.1)   # Shrink by 10%
        inner_face_top = face_top + int(face_height * 0.1)    # Shrink by 10% 
        inner_face_right = face_right - int(face_width * 0.1)
        inner_face_bottom = face_bottom - int(face_height * 0.1)
        
        # Step 2: Create extended blend zone for skin tone reference (OPTION 4 - HYBRID APPROACH)
        outer_face_left = face_left - int(face_width * 0.20)   # Expand by 20% (was 15%) - more skin reference
        outer_face_top = face_top - int(face_height * 0.12)    # Expand by 12% (was 10%) - slight forehead extension
        outer_face_right = face_right + int(face_width * 0.20) # Expand by 20% (was 15%) - more skin reference  
        outer_face_bottom = face_bottom + int(face_height * 0.25) # Expand by 25% (was 15%) - include more neck/upper chest
        
        # Ensure boundaries don't exceed image dimensions
        outer_face_left = max(0, outer_face_left)
        outer_face_top = max(0, outer_face_top)  
        outer_face_right = min(image_width, outer_face_right)
        outer_face_bottom = min(image_height, outer_face_bottom)
        
        # Step 3: Draw gradient blending zones
        # Outer zone: Medium gray (blend zone)
        draw.ellipse([outer_face_left, outer_face_top, outer_face_right, outer_face_bottom], fill=128)  # 128 = 50% blend
        
        # Middle zone: Darker gray (more preservation) 
        draw.ellipse([face_left, face_top, face_right, face_bottom], fill=64)  # 64 = 25% blend, 75% preserve
        
        # Inner zone: Pure black (complete preservation)
        draw.ellipse([inner_face_left, inner_face_top, inner_face_right, inner_face_bottom], fill=0)  # 0 = 100% preserve
        
        # Convert to bytes
        mask_buffer = io.BytesIO()
        mask.save(mask_buffer, format='PNG')
        mask_bytes = mask_buffer.getvalue()
        
        logger.info(f"🎨 HYBRID MASK: {image_width}x{image_height} | Core face: {inner_face_right-inner_face_left}x{inner_face_bottom-inner_face_top} | Extended blend zone: {outer_face_right-outer_face_left}x{outer_face_bottom-outer_face_top} (25% more neck coverage) | Mask size: {len(mask_bytes)/1024:.1f}KB")
        return mask_bytes

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
        strength_param: float = 0.4  # Kept for backward compatibility but not used in inpainting
    ) -> Tuple[bytes, str]:
        """
        🎭 PHASE 2: INPAINTING APPROACH - 100% face preservation + 100% theme transformation.
        Uses mask-based inpainting for surgical precision: face area preserved, everything else transforms.
        Returns a tuple of (image_bytes, final_prompt) - Perfect face preservation with dramatic theme transformations.
        
        Args:
            custom_prompt: Optional custom prompt to override theme-based generation
            theme_day: Optional day override (0=Monday, 1=Tuesday, ..., 6=Sunday). If None, uses current day.
            strength_param: DEPRECATED - Kept for backward compatibility. Inpainting uses mask precision instead.
        
        Inpainting Enhancements:
        - Face preservation mask: BLACK (preserve face) + WHITE (transform clothes/background)
        - 100% surgical precision - face pixels never touched, everything else free to transform
        - No conflicting prompts - mask handles preservation, prompts focus on transformation  
        - Hybrid approach: Extended mask (25% more neck coverage) + color matching prompts for perfect skin tone consistency
        - Enhanced theme descriptions with rich details (clothing, background, lighting, atmosphere)
        - Theme day selection for testing all 7 daily themes
        - No strength limitations - mask provides absolute control
        """
        try:
            base_image_bytes, base_image_url = await self._get_base_image_data()
            logger.info(f"Base image loaded: {len(base_image_bytes)/1024:.1f}KB from {base_image_url}")
            
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

            # 🎨 OPTION 4 HYBRID INPAINTING: Extended mask + color prompts for perfect integration
            logger.info("🎨 HYBRID APPROACH: Extended mask zones + color matching prompts for skin tone consistency")
            
            # Get image dimensions for mask creation
            base_image = Image.open(io.BytesIO(base_image_bytes))
            image_width, image_height = base_image.size
            logger.info(f"📐 BASE IMAGE DIMENSIONS: {image_width}x{image_height}")
            
            # Create face preservation mask (black=preserve face, white=transform clothes/background)
            mask_bytes = self._create_face_preservation_mask(image_width, image_height)
            
            # 🎨 OPTION 4 HYBRID PROMPTS: Color matching + lighting consistency for natural integration
            # Extended mask provides skin tone reference, prompts ensure color/lighting harmony
            transformation_prompt = f"""Transform the clothing and background: {theme_description}. 
            
            CRITICAL: Maintain perfect skin tone consistency - the body skin color must exactly match the face skin tone.
            Use consistent warm lighting across the entire portrait with natural shadows and highlights.
            Ensure seamless color transition from face to neck to chest area with no color breaks or mismatches.
            
            Create a photorealistic portrait with unified lighting, matching skin complexion throughout, 
            sharp details, vibrant clothing colors, detailed fabric textures, and spiritual atmosphere. 
            Professional photography style with natural skin tone continuity and consistent illumination."""
            
            logger.info(f"🎯 INPAINTING PROMPT (no face conflicts): {transformation_prompt[:150]}...")
            
            # 🎨 ENHANCED NEGATIVE PROMPT - Prevent color mismatches and lighting inconsistencies  
            negative_prompt = "blurry, low-resolution, text, watermark, ugly, deformed, poor anatomy, cartoon, artificial, low quality, distorted, bad proportions, mismatched skin tones, different skin colors, inconsistent lighting, color breaks, uneven skin tone, harsh shadows, color discontinuity, lighting mismatch"

            # 🎨 HYBRID GENERATION - Extended mask + color prompts for perfect skin tone matching  
            logger.info("🚀 STARTING HYBRID INPAINTING: Extended mask zones + color prompts for skin tone consistency")
            
            image_bytes = await self.stability_service.generate_image_with_mask(
                init_image_bytes=base_image_bytes,
                mask_image_bytes=mask_bytes,
                text_prompt=transformation_prompt,
                negative_prompt=negative_prompt
                # Note: No strength parameter - inpainting uses mask for precision control
            )
            
            logger.info("✅ HYBRID SUCCESS: Perfect skin tone consistency + natural head-body integration + dramatic theme transformation")
            return image_bytes, transformation_prompt

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
