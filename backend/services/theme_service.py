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
from pathlib import Path

from services.stability_ai_service import StabilityAiService, get_stability_service
from services.supabase_storage_service import SupabaseStorageService, get_storage_service
# CORE.MD: FaceDetectionService is no longer needed as we are using image-to-image generation.

logger = logging.getLogger(__name__)

# REFRESH.MD: Use a clear, maintainable dictionary structure for themes.
THEMES = {
    0: {"name": "Meditative Monday", "description": "in serene white robes, meditating on a peaceful mountain peak at sunrise"},
    1: {"name": "Teaching Tuesday", "description": "wearing traditional saffron robes, giving a discourse in a vibrant ashram hall"},
    2: {"name": "Wisdom Wednesday", "description": "in simple cotton attire, writing ancient scriptures on palm leaves under a banyan tree"},
    3: {"name": "Thankful Thursday", "description": "in humble orange robes, offering flowers at a serene riverbank"},
    4: {"name": "Festive Friday", "description": "adorned in bright, festive saffron and gold robes, celebrating amidst temple festivities"},
    5: {"name": "Silent Saturday", "description": "in muted, earthy-toned robes, in deep meditation inside a quiet, rustic cave"},
    6: {"name": "Serene Sunday", "description": "wearing a simple, cream-colored dhoti, walking peacefully along a sunlit beach at dawn"},
}

class ThemeService:
    """Orchestrates the generation of daily themes."""

    def __init__(
        self,
        stability_service: StabilityAiService,
        storage_service: SupabaseStorageService,
    ):
        self.stability_service = stability_service
        self.storage_service = storage_service
        # CORE.MD: Use Path for robust, OS-agnostic path construction.
        self.base_dir = Path(__file__).resolve().parent.parent

    async def get_daily_themed_image_url(self, custom_prompt: str = None) -> dict:
        """
        Determines the daily theme or uses a custom prompt, generates an image,
        and returns its public URL along with the prompt used.
        """
        try:
            # CORE.MD: This function now performs text-to-image generation.
            # The base image is no longer required.

            if custom_prompt:
                final_prompt = custom_prompt
            else:
                day_of_week = datetime.now().weekday()
                theme = THEMES.get(day_of_week)

                if theme is None:
                    logger.warning(f"No theme found for day {day_of_week}. Defaulting to day 0.")
                    theme = THEMES.get(0)
                
                if theme is None:
                    logger.error("Default theme (day 0) is missing from the configuration.")
                    raise HTTPException(status_code=500, detail="Server is misconfigured: Default theme is missing.")
                
                # REFRESH.MD: Modified the prompt to be more descriptive for text-to-image generation.
                # It now explicitly describes Swamiji's appearance since there's no base image.
                final_prompt = f"A photorealistic, high-resolution portrait of a wise Indian spiritual master, Swamiji. He has a kind, serene face, a gentle smile, and traditional vibhuti markings on his forehead. The theme is: {theme['description']}."

            prompt = final_prompt
            
            negative_prompt = "blurry, low-resolution, text, watermark, ugly, deformed, disfigured, poor anatomy, bad hands, extra limbs, cartoon, 3d render"

            # CORE.MD: Switched from image-to-image to text-to-image generation as requested.
            generated_image_bytes = await self.stability_service.generate_image_from_text(
                text_prompt=prompt,
                negative_prompt=negative_prompt,
            )

            # REFRESH.MD: Re-introduce UUID to prevent filename race conditions.
            unique_filename = f"swamiji_daily_theme_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4()}.png"

            # 3. Upload to Supabase
            # REFRESH.MD: Corrected the file path construction to avoid nesting.
            theme_folder = "daily_themes"
            file_path_in_bucket = f"{theme_folder}/{unique_filename}"

            public_url = self.storage_service.upload_file(
                bucket_name="avatars",
                file_path_in_bucket=file_path_in_bucket,
                file=generated_image_bytes,
                content_type="image/png"
            )
            
            logger.info(f"✅ Successfully uploaded themed image to {public_url}")
            return {"image_url": public_url, "prompt_used": final_prompt}

        except Exception as e:
            logger.error(f"Failed to create the daily themed avatar image: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to create the daily themed avatar image.") from e

# --- FastAPI Dependency Injection ---
# REFRESH.MD: Removed Depends() from the function signature to resolve static analysis warnings.
# Dependencies will now be injected directly in the route.
def get_theme_service(
    stability_service: StabilityAiService = Depends(get_stability_service),
    storage_service: SupabaseStorageService = Depends(get_storage_service),
) -> "ThemeService":
    """
    Creates an instance of the ThemeService with its required dependencies.
    """
    return ThemeService(stability_service, storage_service) 
