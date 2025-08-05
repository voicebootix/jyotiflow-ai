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
    0: {"name": "Meditative Monday", "description": "wearing serene white robes, meditating on a peaceful mountain peak at sunrise"},
    1: {"name": "Teaching Tuesday", "description": "wearing traditional saffron robes, giving a discourse in a vibrant ashram hall"},
    2: {"name": "Wisdom Wednesday", "description": "wearing simple cotton attire, writing ancient scriptures on palm leaves under a banyan tree"},
    3: {"name": "Thankful Thursday", "description": "wearing humble orange robes, offering flowers at a serene riverbank"},
    4: {"name": "Festive Friday", "description": "adorned in bright, festive saffron and gold robes, celebrating amidst temple festivities"},
    5: {"name": "Silent Saturday", "description": "wearing muted, earthy-toned robes, in deep meditation inside a quiet, rustic cave"},
    6: {"name": "Serene Sunday", "description": "wearing a simple, cream-colored dhoti, walking peacefully along a sunlit beach at dawn"},
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





    async def generate_themed_image_bytes(self, custom_prompt: Optional[str] = None) -> Tuple[bytes, str]:
        """
        🎯 FACE PRESERVATION TRANSFORMATION: Stability AI img2img with low strength for maximum face preservation.
        Uses image-to-image generation with 0.3 strength to keep Swamiji's face identical while only changing clothing/background.
        Returns a tuple of (image_bytes, final_prompt) - complete face preservation with clothing/background transformation only.
        """
        try:
            base_image_bytes, base_image_url = await self._get_base_image_data()
            logger.info(f"Base image loaded: {len(base_image_bytes)/1024:.1f}KB from {base_image_url}")
            
            if custom_prompt:
                theme_description = custom_prompt
                logger.info(f"Using custom prompt: {custom_prompt}")
            else:
                day_of_week = datetime.now().weekday()
                theme = THEMES.get(day_of_week, THEMES.get(0, {"description": "in a serene setting"}))
                theme_description = theme['description']
                logger.info(f"Using daily theme for {['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][day_of_week]}: {theme.get('name', 'Unknown')} - {theme_description}")

            # SIMPLE APPROACH: Stability AI img2img with balanced strength
            logger.info("🚀 Using Stability AI img2img for natural transformation")
            
            # FACE PRESERVATION FOCUSED: Only change clothing and background, keep face identical
            transformation_prompt = f"Transform the clothing and background only: {theme_description}. Keep the person's face, facial features, expressions, skin tone, eyes, nose, mouth, beard, hair EXACTLY the same. Only change robes/clothing colors and background environment. Professional portrait photography, realistic style, detailed textures, vibrant colors."
            logger.info(f"Face-preserving transformation prompt: {transformation_prompt}")
            
            # STRONG face preservation negative prompt
            negative_prompt = "face change, different face, altered facial features, different person, different eyes, different nose, different mouth, different beard, different hair, face swap, facial modification, changed identity, blurry, low-resolution, text, watermark, ugly, deformed, poor anatomy, cartoon"

            # Use Stability AI img2img with LOW strength for maximum face preservation
            image_bytes = await self.stability_service.generate_image_to_image(
                init_image_bytes=base_image_bytes,
                text_prompt=transformation_prompt,
                negative_prompt=negative_prompt,
                strength=0.3  # LOW strength: preserves face completely, only changes clothing/background
            )
            
            logger.info("✅ Stability AI img2img successful - FACE PRESERVED, only clothing/background transformed")
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
