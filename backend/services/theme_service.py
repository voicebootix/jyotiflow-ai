# Ithu thevaiyaana modules-ah import pannuthu
import os
from typing import Optional

# Ithu namma log panrathukkum, Replicate and Supabase service-ah use panrathukkum thevai
from ..config.logging_config import get_logger
from ..services.replicate_service import ReplicateService, get_replicate_service
from ..services.supabase_storage_service import SupabaseStorageService, get_storage_service

logger = get_logger(__name__)

# Ithu thaan image generate panra puthu service
class ThemeService:
    # Service create aagum bodhu, thevaiyaana ella connection-ayum ithu eduthukkum
    def __init__(
        self,
        db_pool,
        storage_service: SupabaseStorageService,
        replicate_service: ReplicateService,
    ):
        self.db_pool = db_pool
        self.storage_service = storage_service
        self.replicate_service = replicate_service

    # Ithu thaan RunwayML model kitta neradiyaa pesura main function
    async def _generate_with_runwayml_reference(
        self, prompt: str, reference_image_url: str
    ) -> Optional[bytes]:
        """
        Ithu RunwayML model-ah use panni, oru reference image-oda puthu image-ah uruvaakkum.
        """
        if not self.replicate_service:
            logger.error("ReplicateService ready-aaga illa.")
            return None

        try:
            # Swamiji-oda mugathai sariyaa kondu varathukku, ippadi oru special prompt use panrom
            tagged_prompt = (
                f"a high-resolution, photorealistic portrait of @swamiji, {prompt}"
            )

            # Inga thaan namma Replicate API-ah call panni, image generate panna solrom
            output_url = await self.replicate_service.run_prediction(
                model_name="runwayml/gen4-image-turbo",
                input_data={
                    "prompt": tagged_prompt,
                    "reference_images": [reference_image_url], # Swamiji reference photo URL
                    "reference_tags": ["swamiji"],
                    "aspect_ratio": "9:16",  # Social media-kaana portrait size
                    "resolution": "1080p",
                },
            )

            if not output_url:
                logger.error("Replicate kitta irundhu puthu image URL varala.")
                return None

            # Puthu image URL kedaichathum, antha image-ah download panni anuppurom
            return await self.replicate_service.download_image(output_url)
        except Exception as e:
            logger.error(
                f"RunwayML model-oda image generate pannum bodhu thavaru: {e}",
                exc_info=True,
            )
            return None

    # Intha function-ah thaan namma veliya irundhu (router-la irundhu) call panrom
    async def generate_themed_image_bytes(
        self, theme_prompt: str, reference_avatar_url: str
    ) -> Optional[bytes]:
        """
        Daily theme-ku etha maathiri puthu image-ah ithu generate pannum.
        """
        logger.info(
            f"'{theme_prompt}' enra theme-ku, reference URL vechu image generate panrom."
        )
        # Ithu ulla irukura antha main function-ah thaan call pannuthu
        return await self._generate_with_runwayml_reference(
            prompt=theme_prompt, reference_image_url=reference_avatar_url
        )

# Ithu antha ThemeService-ah thevaiyaana edathula use panrathukku ready panni tharum (dependency injection)
def get_theme_service(db_pool) -> ThemeService:
    """Dependency injector for ThemeService."""
    return ThemeService(
        db_pool=db_pool,
        storage_service=get_storage_service(),
        replicate_service=get_replicate_service(),
    )