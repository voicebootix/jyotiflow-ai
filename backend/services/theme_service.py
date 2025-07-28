"""
🌟 THEME SERVICE

This service is the creative engine that generates daily visual themes for Swamiji's avatar.
It orchestrates image generation and storage to provide a dynamic source URL for the avatar.
"""

import logging
from datetime import datetime
import uuid

from fastapi import HTTPException

from services.stability_ai_service import StabilityAiService
from services.supabase_storage_service import SupabaseStorageService

logger = logging.getLogger(__name__)

class ThemeService:
    """Orchestrates the generation of daily themes."""

    def __init__(
        self,
        stability_service: StabilityAiService,
        storage_service: SupabaseStorageService,
    ):
        self.stability_service = stability_service
        self.storage_service = storage_service
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

            # 1. Generate the image
            logger.info("Generating a new themed image with Stability.ai.")
            image_bytes = await self.stability_service.generate_image(prompt)

            # 2. Upload the image to storage
            file_name = f"public/daily_themes/swamiji_{datetime.now().strftime('%Y-%m-%d')}_{uuid.uuid4()}.png"
            bucket_name = "avatars"
            
            public_url = self.storage_service.upload_file(
                bucket_name=bucket_name,
                file_path_in_bucket=file_name,
                file=image_bytes,
                content_type="image/png"
            )

            logger.info(f"✅ Successfully generated and stored daily themed image at: {public_url}")
            return public_url

        except Exception as e:
            logger.error(f"Failed to generate daily themed image: {e}", exc_info=True)
            # REFRESH.MD: Raise a specific HTTPException that the router can handle.
            raise HTTPException(status_code=500, detail="Failed to create the daily themed avatar image.") from e

# --- FastAPI Dependency Injection ---
# REFRESH.MD: Removed Depends() from the function signature to resolve static analysis warnings.
# Dependencies will now be injected directly in the route.
def get_theme_service(
    stability_service: StabilityAiService,
    storage_service: SupabaseStorageService,
) -> ThemeService:
    """
    Creates an instance of the ThemeService with its required dependencies.
    """
    return ThemeService(stability_service, storage_service) 