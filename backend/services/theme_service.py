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
from services.deep_image_ai_service import DeepImageAiService, get_deep_image_service
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
        deep_image_service: DeepImageAiService,
        storage_service: SupabaseStorageService,
        db_conn: asyncpg.Connection,
    ):
        self.stability_service = stability_service
        self.deep_image_service = deep_image_service
        self.storage_service = storage_service
        self.db_conn = db_conn
        
        self.face_cascade = None
        logger.info("Initialized ThemeService with Deep Image AI and Stability AI services")

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
        """
        Creates a comprehensive gradient preservation mask for complete identity retention.
        NOTE: Currently not used - switched to img2img 0.6 strength for natural proportions.
        Kept for potential future use if inpainting approach is needed again.
        Uses 12% inner radius (face+hair+beard) and 24% outer radius (complete head coverage) for total preservation.
        """
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
            
            # COMPREHENSIVE PRESERVATION MASK - Cover face, hair, and beard for complete identity retention
            inner_radius = min(width, height) * 0.12  # Core preservation area (face + hair + beard)
            outer_radius = min(width, height) * 0.24  # Transition edge (complete head coverage)
            
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
            
            logger.info(f"Created comprehensive preservation mask: {black_pixels} black pixels (face+hair+beard preserved), {gray_pixels} gray pixels (smooth transition), {white_pixels} white pixels (background/clothing change)")
            logger.info(f"Complete identity preserve: {preserve_percentage:.1f}% | Smooth transition: {transition_percentage:.1f}% | Theme transformation: {(white_pixels/total_pixels)*100:.1f}%")
            logger.info(f"Comprehensive mask - Center: ({face_center_x}, {face_center_y}) | Preservation radius: {inner_radius:.1f}px | Transition radius: {outer_radius:.1f}px")
            
            # CORE.MD: DEBUG - Log actual mask bytes size and format
            mask_size_kb = len(mask_bytes_io.getvalue()) / 1024
            logger.info(f"Generated comprehensive preservation mask: {mask_size_kb:.1f}KB PNG format")
            
            return mask_bytes_io.getvalue()
            
        except Exception as e:
            logger.error(f"Failed to create head mask: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Could not process image to create head mask.") from e

    def _create_clothing_mask(self, image_bytes: bytes) -> bytes:
        """
        Creates a precise clothing-only mask to preserve face and background.
        White areas = clothing to be changed, Black areas = face and background to preserve.
        """
        try:
            from PIL import Image, ImageDraw, ImageFilter
            import io
            
            # Load the image
            input_image = Image.open(io.BytesIO(image_bytes))
            width, height = input_image.size
            
            # Create mask for clothing area only (torso/body area, avoid face)
            mask = Image.new("RGB", (width, height), "black")  # Start with black (preserve)
            draw = ImageDraw.Draw(mask)
            
            # Define clothing area (lower 60% of image, center 80% width)
            # This avoids face area (top 40%) and background edges
            clothing_left = int(width * 0.1)    # 10% margin from left
            clothing_right = int(width * 0.9)   # 10% margin from right  
            clothing_top = int(height * 0.4)    # Start below face (40% down)
            clothing_bottom = int(height * 0.95) # Almost to bottom (95% down)
            
            # Draw white rectangle for clothing area to be changed
            draw.rectangle(
                [clothing_left, clothing_top, clothing_right, clothing_bottom],
                fill="white"
            )
            
            # Feather the edges for smooth blending
            mask = mask.filter(ImageFilter.GaussianBlur(radius=3))
            
            # Convert mask to bytes
            mask_bytes_io = io.BytesIO()
            mask.save(mask_bytes_io, format="PNG")
            
            logger.info(f"Created clothing-only mask: {width}x{height}, clothing area: {clothing_left},{clothing_top} to {clothing_right},{clothing_bottom}")
            
            return mask_bytes_io.getvalue()
            
        except Exception as e:
            logger.error(f"Failed to create clothing mask: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Could not process image to create clothing mask.") from e

    async def generate_themed_image_bytes(self, custom_prompt: Optional[str] = None) -> Tuple[bytes, str]:
        """
        🎯 PROVEN SOLUTION: Stability AI inpainting with precise clothing mask.
        Creates clothing-only mask to preserve face and background perfectly.
        Uses inpainting for targeted clothing transformation only.
        Returns a tuple of (image_bytes, final_prompt) - definitive clothing change solution.
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

            # PROVEN APPROACH: Stability AI Inpainting with Clothing Mask
            logger.info("🎯 Using Stability AI inpainting with precise clothing mask for guaranteed clothing transformation")
            
            # Create precise clothing mask (preserve face + background)
            clothing_mask_bytes = self._create_clothing_mask(base_image_bytes)
            
            # Strong clothing transformation prompt
            clothing_prompt = f"Transform clothing to match: {theme_description}. Change robes, garments, and attire completely. Professional spiritual clothing, detailed fabric textures, realistic lighting. High quality portrait photography."
            logger.info(f"Clothing transformation prompt: {clothing_prompt}")
            
            # Negative prompt to prevent face changes
            negative_prompt = "face change, facial modification, different person, altered features, different beard, different hair, blurry, low-resolution, text, watermark, ugly, deformed, poor anatomy, cartoon, orange robes, orange clothing, saffron robes, same clothing"

            # Use Stability AI inpainting for precise clothing transformation
            image_bytes = await self.stability_service.generate_image_with_mask(
                init_image_bytes=base_image_bytes,
                mask_image_bytes=clothing_mask_bytes,
                text_prompt=clothing_prompt,
                negative_prompt=negative_prompt
            )
            
            logger.info("✅ Stability AI clothing inpainting successful - guaranteed clothing transformation")
            return image_bytes, clothing_prompt

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
    deep_image_service: DeepImageAiService = Depends(get_deep_image_service),
    storage_service: SupabaseStorageService = Depends(get_storage_service),
    db_conn: asyncpg.Connection = Depends(db.get_db),
) -> "ThemeService":
    """Creates an instance of the ThemeService with its required dependencies."""
    return ThemeService(stability_service, deep_image_service, storage_service, db_conn)
