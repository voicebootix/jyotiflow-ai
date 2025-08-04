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

    def _create_face_only_mask(self, image_bytes: bytes) -> bytes:
        """
        🎯 REAL SWAMIJI FACE PRESERVATION: Advanced OpenCV face detection + precise masking.
        Uses Haar Cascade to detect actual face location for perfect Swamiji preservation.
        Creates larger protection zone with proper grayscale mask for realistic results.
        """
        try:
            from PIL import Image, ImageDraw, ImageFilter
            import cv2
            import numpy as np
            import io
            
            # Load the image for face detection
            image_array = np.frombuffer(image_bytes, dtype=np.uint8)
            cv_image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            height, width = gray.shape
            
            # Load Haar Cascade for face detection (using the asset file)
            cascade_path = "backend/assets/haarcascade_frontalface_default.xml"
            face_cascade = cv2.CascadeClassifier(cascade_path)
            
            # Detect faces with optimized parameters for portrait photos
            faces = face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(int(width*0.15), int(height*0.15)),  # Face must be at least 15% of image
                flags=cv2.CASCADE_SCALE_IMAGE
            )
            
            # Create grayscale mask for proper inpainting (not RGB!)
            mask = Image.new("L", (width, height), 255)  # Start with white (transform) - GRAYSCALE
            draw = ImageDraw.Draw(mask)
            
            if len(faces) > 0:
                # Use detected face (take the largest one if multiple detected)
                x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
                
                # Expand protection zone for complete face + hair + beard preservation
                expansion_factor = 1.4  # 40% larger than detected face
                expanded_w = int(w * expansion_factor)
                expanded_h = int(h * expansion_factor)
                
                # Center the expanded area on the detected face
                face_center_x = x + w // 2
                face_center_y = y + h // 2
                
                # Calculate expanded boundaries
                face_left = max(0, face_center_x - expanded_w // 2)
                face_right = min(width, face_center_x + expanded_w // 2)
                face_top = max(0, face_center_y - expanded_h // 2)
                face_bottom = min(height, face_center_y + expanded_h // 2)
                
                logger.info(f"🎯 DETECTED Swamiji face at: ({x},{y}) size: {w}x{h}")
                logger.info(f"🛡️ EXPANDED protection zone: ({face_left},{face_top}) to ({face_right},{face_bottom}) size: {expanded_w}x{expanded_h}")
                
            else:
                # Fallback to center-based detection if OpenCV fails
                logger.warning("⚠️ Face detection failed, using center-based fallback")
                face_center_x = width // 2
                face_center_y = int(height * 0.3)  # Slightly lower for better coverage
                
                # Larger fallback protection area
                expanded_w = int(width * 0.4)   # 40% of image width
                expanded_h = int(height * 0.35)  # 35% of image height
                
                face_left = max(0, face_center_x - expanded_w // 2)
                face_right = min(width, face_center_x + expanded_w // 2)
                face_top = max(0, face_center_y - expanded_h // 2)
                face_bottom = min(height, face_center_y + expanded_h // 2)
                
                logger.info(f"🔄 FALLBACK protection zone: ({face_left},{face_top}) to ({face_right},{face_bottom})")
            
            # Draw black oval for PRECISE face preservation (grayscale: 0 = preserve)
            draw.ellipse(
                [face_left, face_top, face_right, face_bottom],
                fill=0  # Black (0) in grayscale = preserve this area
            )
            
            # Gentle feathering for natural blending (reduced from radius=8 to radius=4)
            mask = mask.filter(ImageFilter.GaussianBlur(radius=4))
            
            # Convert to bytes
            mask_bytes_io = io.BytesIO()
            mask.save(mask_bytes_io, format="PNG")
            
            logger.info(f"✅ Created REAL SWAMIJI face preservation mask: {width}x{height} (grayscale format)")
            logger.info(f"🎭 Face protection zone: {face_right-face_left}x{face_bottom-face_top} pixels")
            
            return mask_bytes_io.getvalue()
            
        except Exception as e:
            logger.error(f"Failed to create advanced face mask: {e}", exc_info=True)
            # Fallback to simple center mask if advanced detection fails
            return self._create_simple_face_mask(image_bytes)
    
    def _create_simple_face_mask(self, image_bytes: bytes) -> bytes:
        """Fallback simple face mask if OpenCV detection fails."""
        try:
            from PIL import Image, ImageDraw, ImageFilter
            import io
            
            input_image = Image.open(io.BytesIO(image_bytes))
            width, height = input_image.size
            
            # Grayscale mask (proper format for inpainting)
            mask = Image.new("L", (width, height), 255)  # White = transform
            draw = ImageDraw.Draw(mask)
            
            # Larger center face area
            face_center_x = width // 2
            face_center_y = int(height * 0.3)
            face_width = int(width * 0.4)
            face_height = int(height * 0.35)
            
            face_left = face_center_x - face_width // 2
            face_right = face_center_x + face_width // 2
            face_top = face_center_y - face_height // 2
            face_bottom = face_center_y + face_height // 2
            
            draw.ellipse([face_left, face_top, face_right, face_bottom], fill=0)  # Black = preserve
            mask = mask.filter(ImageFilter.GaussianBlur(radius=4))
            
            mask_bytes_io = io.BytesIO()
            mask.save(mask_bytes_io, format="PNG")
            
            logger.info(f"🔄 Simple fallback mask created: {width}x{height}")
            return mask_bytes_io.getvalue()
            
        except Exception as e:
            logger.error(f"Even simple mask creation failed: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Could not create any face mask.") from e

    async def generate_themed_image_bytes(self, custom_prompt: Optional[str] = None) -> Tuple[bytes, str]:
        """
        🎯 AGGRESSIVE TRANSFORMATION: Stability AI inpainting with face-only mask.
        Creates face-only mask to preserve core facial features only.
        Uses inpainting for complete clothing + background transformation.
        Returns a tuple of (image_bytes, final_prompt) - maximum transformation with face protection.
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

            # AGGRESSIVE APPROACH: Stability AI Inpainting with Face-Only Mask
            logger.info("🚀 Using Stability AI inpainting with face-only mask for complete transformation")
            
            # Create face-only mask (preserve core face, transform everything else)
            face_mask_bytes = self._create_face_only_mask(base_image_bytes)
            
            # Complete transformation prompt - clothing + background
            transformation_prompt = f"A photorealistic portrait of a South Indian spiritual guru, {theme_description}. Transform clothing completely to match theme. Change background environment to spiritual setting. Professional portrait photography, realistic style, detailed textures, vibrant colors."
            logger.info(f"Complete transformation prompt: {transformation_prompt}")
            
            # Dynamic negative prompt based on theme requirements
            def _get_theme_aware_negative_prompt(theme_desc: str) -> str:
                """Create negative prompt that doesn't conflict with theme colors."""
                base_negative = "face change, facial modification, different person, altered features, different eyes, different nose, different mouth, different beard, different hair, face replacement, face swap, AI hallucination, blurry, low-resolution, text, watermark, ugly, deformed, poor anatomy, cartoon, same clothing, unchanged clothing"
                
                # Color-specific negatives - only add if theme doesn't require these colors
                color_negatives = []
                
                theme_lower = theme_desc.lower()
                if "orange" not in theme_lower and "saffron" not in theme_lower:
                    color_negatives.extend(["orange robes", "orange clothing", "saffron robes"])
                if "white" not in theme_lower and "serene white" not in theme_lower:
                    color_negatives.extend(["unchanged white clothing"])
                if "gold" not in theme_lower:
                    color_negatives.extend(["unchanged gold"])
                    
                # Combine base negatives with appropriate color negatives
                if color_negatives:
                    return base_negative + ", " + ", ".join(color_negatives)
                else:
                    return base_negative
            
            negative_prompt = _get_theme_aware_negative_prompt(theme_description)

            # Use Stability AI inpainting for complete transformation with enhanced parameters
            image_bytes = await self.stability_service.generate_image_with_mask(
                init_image_bytes=base_image_bytes,
                mask_image_bytes=face_mask_bytes,
                text_prompt=transformation_prompt,
                negative_prompt=negative_prompt,
                cfg_scale=12,  # Higher guidance scale for better prompt adherence
                steps=30       # More steps for higher quality
            )
            
            logger.info("✅ Stability AI face-only inpainting successful - complete clothing + background transformation")
            return image_bytes, transformation_prompt

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
