import os
from typing import Optional

from ..config.logging_config import get_logger
from ..services.replicate_service import ReplicateService, get_replicate_service
from ..services.supabase_storage_service import SupabaseStorageService, get_storage_service

logger = get_logger(__name__)

class ThemeService:
    ASPECT_RATIOS = {
        "instagram_feed": "4:5",
        "instagram_story": "9:16",
        "tiktok": "9:16",
        "facebook_post": "1:1",
        "x_post": "16:9",
        "pinterest_pin": "2:3",
    }

    def __init__(
        self,
        storage_service: SupabaseStorageService,
        replicate_service: ReplicateService,
    ):
        self.storage_service = storage_service
        self.replicate_service = replicate_service

    async def _generate_with_runwayml_reference(
        self, prompt: str, reference_image_url: str, target_platform: Optional[str] = None
    ) -> Optional[bytes]:
        """
        Generates an image using the RunwayML Gen-4 Turbo model on Replicate,
        which uses a reference image for character consistency.
        The aspect ratio is chosen based on the target_platform.
        """
        if not self.replicate_service:
            logger.error("ReplicateService is not initialized.")
            return None

        try:
            # The prompt needs to reference the character using a tag.
            # We'll use "@swamiji" as the standard tag.
            tagged_prompt = (
                f"a high-resolution, photorealistic portrait of @swamiji, {prompt}"
            )

            aspect_ratio = self.ASPECT_RATIOS.get(target_platform, "9:16")
            logger.info(f"Using aspect ratio '{aspect_ratio}' for platform '{target_platform or 'default'}'.")

            # Note: We are not specifying a version, so the service will fetch the latest.
            output_url = await self.replicate_service.run_prediction(
                model_name="runwayml/gen4-image-turbo",
                input_data={
                    "prompt": tagged_prompt,
                    "reference_images": [reference_image_url],
                    "reference_tags": ["swamiji"],
                    "aspect_ratio": aspect_ratio,
                    "resolution": "1080p",
                },
            )

            if not output_url:
                logger.error("Failed to get output URL from Replicate prediction.")
                return None

            return await self.replicate_service.download_image(output_url)
        except Exception as e:
            logger.error(
                f"Error generating image with RunwayML reference model: {e}",
                exc_info=True,
            )
            return None

    async def generate_themed_image_bytes(
        self, theme_prompt: str, reference_avatar_url: str, target_platform: Optional[str] = None
    ) -> Optional[bytes]:
        """
        Generates the final themed image using the RunwayML reference model.
        """
        logger.info(
            f"Generating themed image for prompt: '{theme_prompt}' using reference URL."
        )
        return await self._generate_with_runwayml_reference(
            prompt=theme_prompt, 
            reference_image_url=reference_avatar_url,
            target_platform=target_platform
        )


def get_theme_service() -> ThemeService:
    """Dependency injector for ThemeService."""
    return ThemeService(
        storage_service=get_storage_service(),
        replicate_service=get_replicate_service(),
    )