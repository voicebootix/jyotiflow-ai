"""
🌟 THEME SERVICE

This service is the creative engine that generates daily visual themes for Swamiji's avatar.
It orchestrates image generation and storage to provide a dynamic source URL for the avatar.
"""

import logging
from datetime import datetime
import uuid
import os
from fastapi import HTTPException, Depends

from services.stability_ai_service import StabilityAiService, get_stability_service
from services.supabase_storage_service import SupabaseStorageService, get_storage_service
from services.face_detection_service import FaceDetectionService, get_face_detection_service

logger = logging.getLogger(__name__)

class ThemeService:
    """Orchestrates the generation of daily themes."""

    def __init__(
        self,
        stability_service: StabilityAiService,
        storage_service: SupabaseStorageService,
        face_detection_service: FaceDetectionService,
    ):
        self.stability_service = stability_service
        self.storage_service = storage_service
        self.face_detection_service = face_detection_service
        self.themes = {
            0: ("Meditative Mountain", "in serene white robes, meditating on a peaceful mountain peak at sunrise"), # Monday
            1: ("Temple Blessings", "in vibrant saffron robes, offering blessings in front of a traditional temple"), # Tuesday
            2: ("Forest Wisdom", "in simple earth-toned robes, teaching in a lush, green forest"), # Wednesday
            3: ("Golden Light", "in bright yellow robes, surrounded by a golden aura of light"), # Thursday
            4: ("Lotus Pond", "in elegant pink robes, sitting beside a tranquil pond with lotus flowers"), # Friday
            5: ("Night Sky", "in deep blue robes, under a starry night sky"), # Saturday
            6: ("Joyful Celebration", "in festive colorful robes, celebrating amidst a joyful crowd") # Sunday
        }

    async def get_daily_themed_image_url(self) -> str:
        """
        Determines the daily theme, generates an image if it doesn't exist,
        and returns its public URL.
        """
        try:
            day_of_week = datetime.now().weekday()
            original_day_for_logging = day_of_week
            
            theme = self.themes.get(day_of_week)

            if not theme:
                logger.warning(
                    f"Theme not found for day {original_day_for_logging}. "
                    f"Falling back to theme for day 0."
                )
                day_of_week = 0
                theme = self.themes[0]

            theme_name, theme_description = theme
            logger.info(f"Today's theme (day {original_day_for_logging}): {theme_name}")

            # CORE.MD: Corrected the prompt structure to directly use the theme_description,
            # which already contains the full attire and setting details. This avoids
            # grammatical errors and creates a more coherent prompt.
            prompt = (
                f"A serene Indian spiritual master (Swamiji) with a gentle smile, "
                f"{theme_description}. "
                f"Photorealistic, digital art, full body shot."
            )

            logger.info(f"Generated daily theme prompt: {prompt}")

            # CORE.MD: The base image path is now configurable via an environment variable.
            base_image_path = os.getenv("SWAMIJI_BASE_IMAGE_PATH", "backend/assets/swamiji_base_image.png")
            if not os.path.exists(base_image_path):
                logger.error(f"Base image not found at {base_image_path}")
                raise HTTPException(status_code=500, detail="Base Swamiji image not found.")

            with open(base_image_path, "rb") as f:
                base_image_bytes = f.read()

            # 1. Create a face mask
            logger.info("Creating face mask from base image.")
            mask_bytes = self.face_detection_service.create_face_mask(base_image_bytes)

            # 2. Inpaint the new image
            logger.info("Inpainting the new themed image with Stability.ai.")
            inpainted_image_bytes = await self.stability_service.inpaint_image(
                image_bytes=base_image_bytes,
                mask_bytes=mask_bytes,
                text_prompt=prompt
            )

            # 3. Upload to Supabase
            file_name = f"public/daily_themes/swamiji_{datetime.now().strftime('%Y-%m-%d')}_{uuid.uuid4()}.png"
            file_path_on_storage = f"avatar_assets/{file_name}"
            public_url = self.storage_service.upload_file(
                file_path_on_storage, inpainted_image_bytes, {"content-type": "image/png"}
            )
            
            logger.info(f"✅ Successfully uploaded themed image to {public_url}")
            return public_url

        except Exception as e:
            logger.error(f"Failed to create the daily themed avatar image: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to create the daily themed avatar image.") from e

# --- FastAPI Dependency Injection ---
# REFRESH.MD: Removed Depends() from the function signature to resolve static analysis warnings.
# Dependencies will now be injected directly in the route.
def get_theme_service(
    stability_service: StabilityAiService = Depends(get_stability_service),
    storage_service: SupabaseStorageService = Depends(get_storage_service),
    face_detection_service: FaceDetectionService = Depends(get_face_detection_service),
) -> "ThemeService":
    """
    Creates an instance of the ThemeService with its required dependencies.
    """
    return ThemeService(stability_service, storage_service, face_detection_service) 