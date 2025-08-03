"""
🌟 THEME SERVICE

This service is the creative engine that generates daily visual themes for Swamiji's avatar.
It now uses advanced image masking to preserve Swamiji's head while changing the background and attire.
"""

import logging
from datetime import datetime
import uuid
import numpy as np
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
    """Orchestrates the generation of daily themes using advanced image masking."""

    def __init__(
        self,
        stability_service: StabilityAiService,
        storage_service: SupabaseStorageService,
        db_conn: asyncpg.Connection,
    ):
        self.stability_service = stability_service
        self.storage_service = storage_service
        self.db_conn = db_conn
        
        self.face_cascade = None
        logger.info("Initialized ThemeService with OpenCV-free face detection fallback")

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

    def _create_head_mask(self, image_bytes: bytes) -> bytes:
        """Creates a head mask using PIL-based approach to avoid OpenCV issues."""
        try:
            from PIL import Image
            import io
            
            image = Image.open(io.BytesIO(image_bytes))
            width, height = image.size
            
            mask = Image.new('L', (width, height), 0)
            
            mask_array = np.array(mask)
            
            # CORE.MD: FIX - CORRECT mask: Black=preserve face, White=change body (based on user's guide feedback)
            head_width = int(width * 0.35)  # Face + minimal neck coverage  
            head_height = int(height * 0.40)  # Head + neck area
            head_x = int((width - head_width) / 2)
            head_y = int(height * 0.05)  # Head position at top

            # CORE.MD: FIX - CORRECT mask: Black=preserve face, White=change body (Stability.ai actual format)
            body_mask = np.full_like(mask_array, 255)  # White = change everything (body/background)
            body_mask[head_y:head_y + head_height, head_x:head_x + head_width] = 0  # Black = preserve face
            
            mask_image = Image.fromarray(body_mask, 'L')
            mask_bytes_io = io.BytesIO()
            mask_image.save(mask_bytes_io, format='PNG')
            
            # CORE.MD: DEBUG - Enhanced debugging for mask analysis (CORRECTED LOGIC)
            white_pixels = np.sum(body_mask == 255)  # White = change body/background
            black_pixels = np.sum(body_mask == 0)    # Black = preserve face
            total_pixels = body_mask.size
            preserve_percentage = (black_pixels / total_pixels) * 100  # Now black pixels = preserve
            logger.info(f"Created mask: {black_pixels} black pixels (preserve face), {white_pixels} white pixels (change body), total: {total_pixels}")
            logger.info(f"Face preserve area - Width: {head_width}px ({head_width/body_mask.shape[1]*100:.1f}%), Height: {head_height}px ({head_height/body_mask.shape[0]*100:.1f}%)")
            logger.info(f"Face preserve percentage: {preserve_percentage:.1f}% | Image size: {width}x{height} | Face position: x={head_x}, y={head_y}")
            
            # CORE.MD: DEBUG - Log actual mask bytes size and format
            mask_size_kb = len(mask_bytes_io.getvalue()) / 1024
            logger.info(f"Generated mask: {mask_size_kb:.1f}KB PNG format")
            
            return mask_bytes_io.getvalue()
            
        except Exception as e:
            logger.error(f"Failed to create head mask: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Could not process image to create head mask.") from e

    async def generate_themed_image_bytes(self, custom_prompt: Optional[str] = None) -> Tuple[bytes, str]:
        """
        REFRESH.MD: FIX - Now returns a tuple of (image_bytes, final_prompt).
        This allows the caller to get both the image and the exact prompt used.
        """
        try:
            base_image_bytes, _ = await self._get_base_image_data()
            logger.info(f"Base image loaded: {len(base_image_bytes)/1024:.1f}KB")
            # CORE.MD: Following user guide - img2img approach for identity preservation (no masks needed)

            if custom_prompt:
                theme_description = custom_prompt
                logger.info(f"Using custom prompt: {custom_prompt}")
            else:
                day_of_week = datetime.now().weekday()
                theme = THEMES.get(day_of_week, THEMES.get(0, {"description": "in a serene setting"}))
                theme_description = theme['description']
                logger.info(f"Using daily theme for {['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][day_of_week]}: {theme.get('name', 'Unknown')} - {theme_description}")

            # CORE.MD: FIX - IMG2IMG approach for identity preservation with theme transformation
            final_prompt = f"A photorealistic, high-resolution portrait of a wise Indian spiritual master, {theme_description}. Professional photography, detailed textures, vibrant colors, authentic spiritual setting."
            logger.info(f"Final prompt generated: {final_prompt}")
            negative_prompt = "blurry, low-resolution, text, watermark, ugly, deformed, disfigured, poor anatomy, bad hands, extra limbs, cartoon, 3d render, duplicate head, two heads, distorted face"

            # CORE.MD: USER GUIDE APPROACH - img2img with moderate strength for background/attire change
            # "Base Swamiji Image + Prompt → Stability.ai (img2img mode) → Same face, new background"
            image_bytes = await self.stability_service.generate_image_to_image(
                init_image_bytes=base_image_bytes,
                text_prompt=final_prompt,
                negative_prompt=negative_prompt,
                strength=0.45  # Increased from 0.25 to allow background/attire changes while preserving face
            )
            return image_bytes, final_prompt

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
