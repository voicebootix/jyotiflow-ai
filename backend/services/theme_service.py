import os
import logging
import asyncio
from typing import Optional

import httpx
from fastapi import Depends, HTTPException

from services.supabase_storage_service import get_storage_service, SupabaseStorageService
from services.replicate_service import get_replicate_service, ReplicateService

logger = logging.getLogger(__name__)

# Environment variables for configuration
LORA_MODEL_NAME = os.getenv("LORA_MODEL_NAME")
LORA_MODEL_VERSION = os.getenv("LORA_MODEL_VERSION")

class ThemeService:
    def __init__(
        self,
        storage_service: SupabaseStorageService,
        replicate_service: ReplicateService
    ):
        self.storage_service = storage_service
        self.replicate_service = replicate_service
        self.http_client = httpx.AsyncClient(timeout=120.0)

    async def generate_themed_image_bytes(
        self,
        theme_prompt: str,
        reference_avatar_url: str,
        target_platform: Optional[str] = None
    ) -> Optional[bytes]:
        
        if not self.replicate_service.is_configured:
            raise HTTPException(status_code=501, detail="Replicate service is not configured on the server.")
        if not LORA_MODEL_NAME or not LORA_MODEL_VERSION:
            raise HTTPException(status_code=501, detail="LORA_MODEL_NAME or LORA_MODEL_VERSION is not set on the server.")

        try:
            # Run prediction using Replicate service with only the LoRA model and prompt.
            # The reference_avatar_url is no longer passed to Replicate.
            generated_image_url = await asyncio.to_thread(
                self.replicate_service.run_lora_prediction,
                model_name=LORA_MODEL_NAME,
                model_version=LORA_MODEL_VERSION,
                prompt=theme_prompt
            )

            if not generated_image_url:
                raise HTTPException(status_code=500, detail="Image generation with Replicate failed.")

            # Download the generated image
            response = await self.http_client.get(generated_image_url)
            response.raise_for_status()
            
            return response.content

        except Exception as e:
            logger.error(f"Error during themed image generation with Replicate: {e}", exc_info=True)
            if isinstance(e, HTTPException):
                raise
            raise HTTPException(status_code=500, detail="An unexpected error occurred during image generation.")


def get_theme_service(
    storage_service: SupabaseStorageService = Depends(get_storage_service),
    replicate_service: ReplicateService = Depends(get_replicate_service),
) -> ThemeService:
    return ThemeService(
        storage_service=storage_service,
        replicate_service=replicate_service
    )
