import os
import logging
from io import BytesIO
from typing import Optional

import httpx
from PIL import Image, ImageDraw
import cv2
import numpy as np
from fastapi import Depends, HTTPException

from services.supabase_storage_service import get_storage_service, SupabaseStorageService
# NEW: Import the ReplicateService
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

    async def _get_base_image_bytes(self, reference_avatar_url: str) -> Optional[bytes]:
        try:
            response = await self.http_client.get(reference_avatar_url)
            response.raise_for_status()
            return response.content
        except httpx.RequestError as e:
            logger.error(f"Failed to download base image from URL {reference_avatar_url}: {e}")
            return None

    async def _create_head_mask(self, image_bytes: bytes) -> Optional[bytes]:
        try:
            image_np = np.frombuffer(image_bytes, np.uint8)
            image_bgr = cv2.imdecode(image_np, cv2.IMREAD_COLOR)
            if image_bgr is None:
                raise ValueError("Failed to decode image.")
            
            gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
            
            # Use an environment variable for the cascade path with a sensible default
            default_cascade_path = "assets/haarcascade_frontalface_default.xml"
            cascade_path = os.environ.get("HAAR_CASCADE_PATH", default_cascade_path)

            if not os.path.exists(cascade_path):
                error_msg = (
                    f"Haar cascade file not found. "
                    f"Set the HAAR_CASCADE_PATH environment variable or ensure the default path is correct. "
                    f"Resolved path: {os.path.abspath(cascade_path)}"
                )
                logger.error(error_msg)
                raise FileNotFoundError(error_msg)

            face_cascade = cv2.CascadeClassifier(cascade_path)
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)

            if len(faces) == 0:
                logger.warning("No faces detected, creating a fallback centered mask.")
                h, w = gray.shape
                mask = np.full((h, w), 255, dtype=np.uint8)
                center_x, center_y = w // 2, h // 2
                rect_w, rect_h = int(w * 0.4), int(h * 0.6)
                start_x, start_y = center_x - rect_w // 2, center_y - rect_h // 2
                end_x, end_y = start_x + rect_w, start_y + rect_h
                mask[start_y:end_y, start_x:end_x] = 0
            else:
                x, y, w, h = faces[0]
                mask = np.full(gray.shape, 255, dtype=np.uint8)
                cv2.rectangle(mask, (x, y), (x + w, y + h), (0, 0, 0), -1)

            is_success, buffer = cv2.imencode(".png", mask)
            if not is_success:
                raise ValueError("Failed to encode mask image.")
            
            return buffer.tobytes()

        except Exception as e:
            logger.error(f"Failed to create head mask: {e}", exc_info=True)
            return None

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

        base_image_bytes = await self._get_base_image_bytes(reference_avatar_url)
        if not base_image_bytes:
            raise HTTPException(status_code=500, detail="Could not download the base Swamiji image.")

        head_mask_bytes = await self._create_head_mask(base_image_bytes)
        if not head_mask_bytes:
            raise HTTPException(status_code=500, detail="Could not create the head mask for the image.")

        try:
            # Upload mask to get a public URL
            mask_url = self.storage_service.upload_file(
                bucket_name="masks",
                file_path_in_bucket=f"mask_{os.urandom(8).hex()}.png",
                file=head_mask_bytes,
                content_type="image/png"
            )
            if not mask_url:
                raise HTTPException(status_code=500, detail="Failed to upload head mask to storage.")

            # Run prediction using Replicate service
            generated_image_url = self.replicate_service.run_lora_prediction(
                model_name=LORA_MODEL_NAME,
                model_version=LORA_MODEL_VERSION,
                prompt=theme_prompt,
                image_url=reference_avatar_url,
                mask_url=mask_url
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
