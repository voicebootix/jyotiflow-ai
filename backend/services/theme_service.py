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

from services.stability_ai_service import StabilityAiService, get_stability_service
from services.supabase_storage_service import SupabaseStorageService, get_storage_service
import db

logger = logging.getLogger(__name__)

THEMES = {
    0: {"name": "Meditative Monday", "description": "wearing pristine white ceremonial robes with flowing fabric and silver borders, sitting in lotus position on a snow-capped Himalayan mountain peak at golden sunrise, surrounded by swirling morning mist and ancient prayer flags, with soft ethereal lighting illuminating the serene meditation pose"},
    1: {"name": "Teaching Tuesday", "description": "wearing rich saffron-colored traditional robes with intricate golden embroidery and sacred symbols, seated on an ornate wooden throne in a magnificent ashram hall with carved pillars, colorful tapestries, brass oil lamps, and devoted disciples seated on the marble floor, warm temple lighting creating a divine atmosphere"},
    2: {"name": "Wisdom Wednesday", "description": "wearing earth-toned simple cotton kurta with natural hemp threads, sitting cross-legged under a massive ancient banyan tree with sprawling roots, surrounded by palm leaf manuscripts, traditional ink pots, wooden writing stylus, dappled sunlight filtering through dense green foliage creating a scholarly forest retreat"},
    3: {"name": "Thankful Thursday", "description": "wearing humble burnt orange robes with simple rope belt, kneeling gracefully by a sacred crystal-clear river with lotus flowers floating on the surface, holding a brass plate filled with marigold offerings, coconut, incense, surrounded by ancient stone ghats and temple spires in the misty distance"},
    4: {"name": "Festive Friday", "description": "adorned in magnificent bright saffron and gold silk robes with elaborate zari work, ruby gemstones, sacred rudraksha beads, standing in a grand temple courtyard during festival celebrations with colorful rangoli patterns, hanging marigold garlands, burning oil lamps, devotees with musical instruments, vibrant festival atmosphere"},
    5: {"name": "Silent Saturday", "description": "wearing simple muted brown and ochre meditation robes with rough handwoven texture, sitting in perfect stillness inside a dimly lit ancient cave with smooth stone walls, flickering butter lamps casting dancing shadows, stalactites overhead, complete silence and spiritual solitude, minimal natural lighting from cave entrance"},
    6: {"name": "Serene Sunday", "description": "wearing flowing cream-colored cotton dhoti with subtle golden threads, walking barefoot on pristine white sand along an endless ocean beach at peaceful dawn, gentle waves lapping the shore, seagulls in the distance, palm trees swaying, soft morning sunlight creating a heavenly coastal sanctuary"},
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





    async def generate_themed_image_bytes(self, custom_prompt: Optional[str] = None, theme_day: Optional[int] = None) -> Tuple[bytes, str]:
        """
        🎯 PRIORITY 3: ENHANCED PROMPT ENGINEERING - Explicit face preservation + detailed themes.
        Uses ultra-specific identity anchoring commands + enhanced theme descriptions + strength 0.4 (maximum safe).
        Returns a tuple of (image_bytes, final_prompt) - Professional face preservation with dramatic theme transformations.
        
        Args:
            custom_prompt: Optional custom prompt to override theme-based generation
            theme_day: Optional day override (0=Monday, 1=Tuesday, ..., 6=Sunday). If None, uses current day.
        
        Priority 3 Enhancements:
        - Explicit face preservation commands with ultra-specific feature descriptions
        - Enhanced theme descriptions with rich details (clothing, background, lighting, atmosphere)
        - Theme day selection for testing all 7 daily themes
        - Follows stability_ai_service.py documentation: 0.3-0.4 recommended for identity preservation
        """
        try:
            base_image_bytes, base_image_url = await self._get_base_image_data()
            logger.info(f"Base image loaded: {len(base_image_bytes)/1024:.1f}KB from {base_image_url}")
            
            if custom_prompt:
                theme_description = custom_prompt
                logger.info(f"Using custom prompt: {custom_prompt}")
            else:
                # Use theme_day override if provided, otherwise use current day
                if theme_day is not None and 0 <= theme_day <= 6:
                    day_of_week = theme_day
                    logger.info(f"🎯 THEME OVERRIDE: Using theme_day={theme_day} instead of current day")
                else:
                    day_of_week = datetime.now().weekday()
                    logger.info(f"📅 Using current day: {day_of_week}")
                
                theme = THEMES.get(day_of_week, THEMES.get(0, {"description": "in a serene setting"}))
                theme_description = theme['description']
                day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                logger.info(f"🎨 Using theme for {day_names[day_of_week]}: {theme.get('name', 'Unknown')} - {theme_description[:100]}...")

            # PRIORITY 3 APPROACH: Enhanced prompt engineering + ultra-detailed theme descriptions for optimal results
            logger.info("🚀 PRIORITY 3: Enhanced prompt engineering + detailed theme descriptions + explicit face preservation commands")
            
            # PRIORITY 3: EXPLICIT FACE PRESERVATION - Ultra-specific identity anchoring commands
            # Enhanced identity anchor with explicit AI instructions
            identity_anchor = f"""CRITICAL INSTRUCTION: Keep the same person's face 100% identical to the reference image. 
            PRESERVE EXACTLY without any changes: the same eyes (identical shape, size, color, pupil position, eyebrow arch), 
            the same nose (identical bridge, nostrils, tip shape), the same mouth (identical lip shape, smile, teeth), 
            the same beard (identical pattern, color, thickness, style), the same hair (identical texture, color, hairline), 
            the same skin tone and complexion, the same facial bone structure, the same forehead and cheekbones, 
            the same facial expressions and spiritual character. The person's identity must remain completely unchanged."""
            
            # Enhanced transformation scope with detailed theme instructions  
            transformation_scope = f"""TRANSFORM COMPLETELY: Replace the clothing with {theme_description}, 
            change the background environment to match the spiritual theme with rich details, 
            adjust lighting to enhance the new setting atmosphere, modify props and surroundings, 
            create the daily theme mood while keeping the person's face absolutely identical."""
            
            # Quality directives for professional results
            quality_directives = """Professional portrait photography, photorealistic style, 
            high detail, sharp focus, natural lighting that enhances features, vibrant colors, 
            detailed fabric textures, spiritual atmosphere, realistic rendering."""
            
            transformation_prompt = f"{identity_anchor} {transformation_scope} {quality_directives}"
            logger.info(f"Priority 2 advanced prompt engineering: {transformation_prompt[:150]}...")
            
            # PRIORITY 2: ENHANCED NEGATIVE PROMPT - Comprehensive face preservation (from Priority 1)
            negative_prompt = "different face, face swap, altered facial features, changed identity, different person, modified eyes, changed nose, altered mouth, different beard, changed hair, face modification, facial reconstruction, different skin tone, altered bone structure, changed eyebrows, different forehead, face replacement, identity change, blurry, low-resolution, text, watermark, ugly, deformed, poor anatomy, cartoon"

            # PRIORITY 2+: MAXIMUM SAFE STRENGTH - Following stability_ai_service.py documentation (0.3-0.4 range)
            image_bytes = await self.stability_service.generate_image_to_image(
                init_image_bytes=base_image_bytes,
                text_prompt=transformation_prompt,
                negative_prompt=negative_prompt,
                strength=0.4  # PRIORITY 2+: 0.4 maximum safe - top of documented range for identity preservation
            )
            
            logger.info("✅ PRIORITY 3 SUCCESS: Enhanced prompt engineering + detailed themes + explicit face preservation commands")
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
            generated_image_bytes, final_prompt = await self.generate_themed_image_bytes(custom_prompt)

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
