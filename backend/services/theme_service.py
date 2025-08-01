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

from services.stability_ai_service import StabilityAiService, get_stability_service
from services.supabase_storage_service import SupabaseStorageService, get_storage_service
import db # For database connection

logger = logging.getLogger(__name__)

# REFRESH.MD: Prompts now focus on attire and background, as the head is preserved.
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
        # CORE.MD: Load the pre-trained face and body detector models once.
        # These files must be present in the `backend/assets` directory.
        cascade_path = "backend/assets/"
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    async def _get_base_image_bytes(self) -> bytes:
        """Fetches the uploaded Swamiji image URL from the DB and downloads the image."""
        try:
            record = await self.db_conn.fetchrow("SELECT value FROM platform_settings WHERE key = 'swamiji_avatar_url'")
            if not record or not record['value']:
                raise HTTPException(status_code=404, detail="Swamiji base image not found. Please upload a photo first.")
            
            image_url = json.loads(record['value'])
            
            async with httpx.AsyncClient() as client:
                response = await client.get(image_url)
                response.raise_for_status()
            return response.content
        except (json.JSONDecodeError, httpx.HTTPStatusError) as e:
            logger.error(f"Failed to fetch or download the base Swamiji image: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Could not retrieve the base Swamiji image.") from e

    def _create_head_mask(self, image_bytes: bytes) -> bytes:
        """Detects the head and creates a black mask to protect it."""
        try:
            # Decode the image
            np_arr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Create a black mask with the same dimensions as the image
            mask = np.full(img.shape[:2], 255, dtype=np.uint8) # Start with a white mask (all changeable)

            # Detect faces
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
            
            if len(faces) == 0:
                logger.warning("No face detected in the image. Masking cannot be applied.")
                # Return a fully white mask, which means the whole image is editable
                _, mask_bytes = cv2.imencode('.png', mask)
                return mask_bytes.tobytes()

            # Assume the largest detected face is the correct one
            x, y, w, h = max(faces, key=lambda item: item[2] * item[3])
            
            # CORE.MD: Expand the mask to include the entire head, hair, and shoulders.
            # These values can be tuned for better results.
            y_expand = int(h * 0.5) # Expand upwards to cover hair
            h_expand = int(h * 0.8) # Expand downwards to cover beard and neck
            x_expand = int(w * 0.3) # Expand sideways
            
            y_start = max(0, y - y_expand)
            y_end = min(img.shape[0], y + h + h_expand)
            x_start = max(0, x - x_expand)
            x_end = min(img.shape[1], x + w + x_expand)

            # Set the head area to black (0) to protect it from changes
            mask[y_start:y_end, x_start:x_end] = 0
            
            # Encode the mask back to bytes
            _, mask_bytes = cv2.imencode('.png', mask)
            return mask_bytes.tobytes()
            
        except Exception as e:
            logger.error(f"Failed to create head mask: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Could not process image to create head mask.")

    async def get_daily_themed_image_url(self, custom_prompt: str = None) -> dict:
        """
        Generates a themed image using masking to preserve Swamiji's head.
        """
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

            # REFRESH.MD: Prompt is now more direct, describing the changes to be made.
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
