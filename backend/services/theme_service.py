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
        """Creates a gradient head mask for smooth face preservation with natural background blending."""
        try:
            from PIL import Image, ImageDraw
            import io
            
            image = Image.open(io.BytesIO(image_bytes))
            width, height = image.size
            
            # CORE.MD: ADVANCED FIX - Gradient mask: Smooth transition from face preserve to background change
            mask_array = np.full((height, width), 255, dtype=np.uint8)  # Start with white (change everything)
            
            # Face center positioning - typically upper portion of image
            face_center_x = width // 2
            face_center_y = int(height * 0.25)  # Face usually in upper 25% of portrait
            
            # Gradient radial mask parameters
            inner_radius = min(width, height) * 0.12  # Core face area (black = preserve 100%)
            outer_radius = min(width, height) * 0.25  # Transition edge (white = change 100%)
            
            # Create gradient mask using distance-based blending
            for y in range(height):
                for x in range(width):
                    # Calculate distance from face center
                    distance = np.sqrt((x - face_center_x)**2 + (y - face_center_y)**2)
                    
                    if distance <= inner_radius:
                        # Core face area: Black (preserve completely)
                        mask_array[y, x] = 0
                    elif distance <= outer_radius:
                        # Transition area: Gradient from black to white
                        transition_ratio = (distance - inner_radius) / (outer_radius - inner_radius)
                        mask_array[y, x] = int(255 * transition_ratio)
                    # Outer area remains white (change completely)
            
            # Convert numpy array to PIL Image
            mask_image = Image.fromarray(mask_array, 'L')
            mask_bytes_io = io.BytesIO()
            mask_image.save(mask_bytes_io, format='PNG')
            
            # CORE.MD: DEBUG - Enhanced debugging for gradient mask analysis
            white_pixels = np.sum(mask_array == 255)  # White = change body/background
            black_pixels = np.sum(mask_array == 0)    # Black = preserve face
            gray_pixels = np.sum((mask_array > 0) & (mask_array < 255))  # Gray = transition area
            total_pixels = mask_array.size
            preserve_percentage = (black_pixels / total_pixels) * 100
            transition_percentage = (gray_pixels / total_pixels) * 100
            
            logger.info(f"Created gradient mask: {black_pixels} black pixels (preserve), {gray_pixels} gray pixels (transition), {white_pixels} white pixels (change)")
            logger.info(f"Face preserve: {preserve_percentage:.1f}% | Transition blend: {transition_percentage:.1f}% | Background change: {(white_pixels/total_pixels)*100:.1f}%")
            logger.info(f"Gradient mask - Center: ({face_center_x}, {face_center_y}) | Inner radius: {inner_radius:.1f}px | Outer radius: {outer_radius:.1f}px")
            
            # CORE.MD: DEBUG - Log actual mask bytes size and format
            mask_size_kb = len(mask_bytes_io.getvalue()) / 1024
            logger.info(f"Generated gradient mask: {mask_size_kb:.1f}KB PNG format")
            
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
            # CORE.MD: REVERT - img2img changing face, back to inpainting with face protection mask
            head_mask_bytes = self._create_head_mask(base_image_bytes)
            logger.info(f"Head mask created: {len(head_mask_bytes)/1024:.1f}KB")

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

            # CORE.MD: BACK TO INPAINTING - img2img was changing face, inpainting protects face with mask
            image_bytes = await self.stability_service.generate_image_with_mask(
                init_image_bytes=base_image_bytes,
                mask_image_bytes=head_mask_bytes,
                text_prompt=final_prompt,
                negative_prompt=negative_prompt
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
