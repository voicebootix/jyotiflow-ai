"""
🌟 THEME SERVICE

This service is the creative engine that generates daily visual themes for Swamiji's avatar.
It now uses advanced image masking to preserve Swamiji's head while changing the background and attire.
"""

import logging
from datetime import datetime
import uuid
import cv2
import numpy as np
import httpx
from fastapi import HTTPException, Depends
import asyncpg
import json
from pathlib import Path # CORE.MD: Import 'pathlib' for robust path resolution.

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
        
        base_path = Path(__file__).parent.parent
        cascade_file = base_path / "assets" / "haarcascade_frontalface_default.xml"
        
        if not cascade_file.is_file():
            logger.error(f"Haar Cascade file not found at {cascade_file}. Face detection will fail.")
            raise RuntimeError(f"Missing critical asset: {cascade_file}")
            
        self.face_cascade = cv2.CascadeClassifier(str(cascade_file))

        # CORE.MD: Add a validation check to ensure the cascade classifier was loaded correctly.
        # This prevents the '!empty()' assertion error during runtime if the XML is invalid.
        if self.face_cascade.empty():
            logger.error(f"Failed to load Haar Cascade classifier from {cascade_file}. The file might be corrupt or invalid.")
            raise RuntimeError(f"Failed to load Haar Cascade from {cascade_file}")


    async def _get_base_image_bytes(self) -> bytes:
        """Fetches the uploaded Swamiji image URL from the DB and downloads the image."""
        image_url = None
        try:
            record = await self.db_conn.fetchrow("SELECT value FROM platform_settings WHERE key = 'swamiji_avatar_url'")
            if not record or not record['value']:
                raise HTTPException(status_code=404, detail="Swamiji base image not found. Please upload a photo first.")
            
            raw_value = record['value']
            try:
                parsed_value = json.loads(raw_value)
                if isinstance(parsed_value, str):
                    image_url = parsed_value
                else:
                    raise TypeError("Parsed JSON value is not a string.")
            except (json.JSONDecodeError, TypeError) as e:
                if isinstance(raw_value, str) and raw_value.startswith('http'):
                    image_url = raw_value
                else:
                    # REFRESH.MD: Add exception chaining for better traceability.
                    raise HTTPException(status_code=500, detail="Invalid format for Swamiji image URL in database.") from e

            if not image_url:
                 raise HTTPException(status_code=500, detail="Could not determine a valid image URL from database.")

            async with httpx.AsyncClient() as client:
                response = await client.get(image_url)
                response.raise_for_status()
                return response.content
                
        except asyncpg.PostgresError as e:
            logger.error(f"Database error while fetching Swamiji image URL: {e}", exc_info=True)
            raise HTTPException(status_code=503, detail="A database error occurred.") from e
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to download the base Swamiji image from {image_url}: {e}", exc_info=True)
            raise HTTPException(status_code=502, detail="Could not download the base Swamiji image.") from e
        except Exception as e:
            logger.error(f"An unexpected error occurred in _get_base_image_bytes: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="An unexpected error occurred while retrieving the image.") from e

    def _create_head_mask(self, image_bytes: bytes) -> bytes:
        """Detects the head and creates a black mask to protect it."""
        try:
            np_arr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            if img is None:
                raise ValueError("Could not decode image bytes.")
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            mask = np.full(img.shape[:2], 255, dtype=np.uint8)

            faces = self.face_cascade.detectMultiScale(gray, 1.1, 5)
            
            if len(faces) == 0:
                logger.warning("No face detected in the image. Masking cannot be applied.")
                _, mask_bytes = cv2.imencode('.png', mask)
                return mask_bytes.tobytes()

            x, y, w, h = max(faces, key=lambda item: item[2] * item[3])
            
            y_expand = int(h * 0.5)
            h_expand = int(h * 0.8)
            x_expand = int(w * 0.3)
            
            y_start = max(0, y - y_expand)
            y_end = min(img.shape[0], y + h + h_expand)
            x_start = max(0, x - x_expand)
            x_end = min(img.shape[1], x + w + x_expand)

            mask[y_start:y_end, x_start:x_end] = 0
            
            _, mask_bytes = cv2.imencode('.png', mask)
            return mask_bytes.tobytes()
            
        except Exception as e:
            logger.error(f"Failed to create head mask: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Could not process image to create head mask.") from e

    async def get_daily_themed_image_url(self, custom_prompt: str = None) -> dict:
        """Generates a themed image using masking to preserve Swamiji's head."""
        try:
            base_image_bytes = await self._get_base_image_bytes()
            
            head_mask_bytes = self._create_head_mask(base_image_bytes)

            if custom_prompt:
                theme_description = custom_prompt
            else:
                day_of_week = datetime.now().weekday()
                theme = THEMES.get(day_of_week, THEMES.get(0))
                if theme is None:
                    raise HTTPException(status_code=500, detail="Server theme configuration is missing.")
                theme_description = theme['description']

            final_prompt = f"A photorealistic, high-resolution portrait of a wise Indian spiritual master, {theme_description}."
            negative_prompt = "blurry, low-resolution, text, watermark, ugly, deformed, disfigured, poor anatomy, bad hands, extra limbs, cartoon, 3d render, duplicate head, two heads"

            generated_image_bytes = await self.stability_service.generate_image_with_mask(
                image_bytes=base_image_bytes,
                mask_bytes=head_mask_bytes,
                text_prompt=final_prompt,
                negative_prompt=negative_prompt
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
            return {"image_url": public_url, "prompt_used": final_prompt}

        except Exception as e:
            logger.error(f"Failed to create the daily themed avatar image with masking: {e}", exc_info=True)
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(status_code=500, detail="Failed to create themed image.") from e

# --- FastAPI Dependency Injection ---
def get_theme_service(
    stability_service: StabilityAiService = Depends(get_stability_service),
    storage_service: SupabaseStorageService = Depends(get_storage_service),
    db_conn: asyncpg.Connection = Depends(db.get_db),
) -> "ThemeService":
    """Creates an instance of the ThemeService with its required dependencies."""
    return ThemeService(stability_service, storage_service, db_conn)
