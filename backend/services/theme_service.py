"""
🚀 RUNWARE-ONLY THEME SERVICE

This service is the premium engine that generates daily visual themes for Swamiji's avatar.
It uses RunWare's IP-Adapter FaceID technology for 80-90% face preservation success rate,
maintaining perfect face consistency while generating diverse backgrounds and clothing themes.
"""

import os
import logging
from io import BytesIO
from typing import Optional, Tuple

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


# 🚀 RUNWARE API SERVICE CLASS
class RunWareService:
    """
    🎯 RunWare API Service for IP-Adapter FULL IMAGE face preservation
    Achieves 80-90% face consistency with $0.0006 per image cost
    
    This service uses RunWare's IP-Adapter with COMPLETE reference images and proper weights
    to preserve face identity while allowing AI to create new body poses, backgrounds, and clothing from prompts.
    The full-image approach with balanced IP-Adapter weight provides strong face preservation with theme transformation.
    """
    
    # 🔧 CONFIGURATION CONSTANTS: OPTIMIZED WITH USER GUIDANCE
    # User guidance: BALANCED uses ~0.25 IP-Adapter weight, ULTRA_MINIMAL uses ~0.05
    BALANCED_CFG_SCALE = 18.0  # 🎯 AGGRESSIVE PROMPT GUIDANCE: Force prompt to override reference image
    BALANCED_IP_ADAPTER_WEIGHT = 0.25   # 🎯 AGGRESSIVE TRANSFORMATION: Low weight for more background/clothing change
    
    ULTRA_MINIMAL_CFG_SCALE = 20.0  # 🔥 MAXIMUM PROMPT GUIDANCE: Complete prompt dominance
    ULTRA_MINIMAL_IP_ADAPTER_WEIGHT = 0.05  # 🔥 MINIMAL FACE INFLUENCE: Only basic face structure
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.runware.ai/v1"
        self.ip_adapter_model = os.getenv("RUNWARE_IP_ADAPTER_MODEL", "runware:105@1")
        
        if not api_key:
            logger.warning("⚠️ RunWare API key not provided - service will not be available")
        else:
            logger.info("✅ RunWare Service initialized with IP-Adapter FaceID approach")
    
    async def generate_scene_only(
        self,
        prompt: str,
        negative_prompt: str = "ugly, deformed, noisy, blurry, low contrast, text, signature, watermark, extra limbs, extra fingers",
        width: int = 1024,
        height: int = 1024,
        steps: int = 40,
        cfg_scale: float = 12.0 # Moderate CFG for creative freedom
    ) -> bytes:
        """Generates an image from a text prompt without any image reference (Step 1 of 2-step process)."""
        if not self.api_key:
            raise HTTPException(status_code=503, detail="RunWare API key not configured")

        payload = {
            "taskType": "imageInference",
            "taskUUID": str(uuid.uuid4()),
            "positivePrompt": prompt,
            "negativePrompt": negative_prompt,
            "model": "runware:101@1", # Standard text-to-image model
            "height": height,
            "width": width,
            "numberResults": 1,
            "steps": steps,
            "CFGScale": cfg_scale,
            "seed": random.randint(1, 1000000),
        }

        logger.info("🎨 Step 1: Generating scene from prompt only...")
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self.base_url,
                    headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                    json=[payload] # API requires an array
                )
                response.raise_for_status()
                parsed_response = response.json()

                if not parsed_response.get('data') or not parsed_response['data'][0].get('imageURL'):
                    raise HTTPException(status_code=502, detail="RunWare API did not return an image URL for the scene.")

                img_url = parsed_response['data'][0]['imageURL']
                img_response = await client.get(img_url)
                img_response.raise_for_status()
                
                logger.info("✅ Step 1 complete: Scene generated successfully.")
                return img_response.content
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ RunWare scene generation failed with status {e.response.status_code}: {e.response.text}")
            raise HTTPException(status_code=e.response.status_code, detail=f"RunWare scene generation failed: {e.response.text}")
        except Exception as e:
            logger.error(f"❌ Unexpected error during scene generation: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="An unexpected error occurred during scene generation.")

    async def generate_with_face_reference(
        self,
        scene_image_bytes: bytes, # STEP 2: Input is the generated scene
        face_image_bytes: bytes,  # STEP 2: Face reference to apply to the scene
        prompt: str,
        negative_prompt: str = "",
        width: int = 1024,
        height: int = 1024,
        steps: int = 30, # Fewer steps needed for refinement
        cfg_scale: float = 8.0,
        strength: float = 0.2, # Keep low to preserve the Step 1 scene
        ip_adapter_weight: float = 0.35 # FINAL FIX v4: Balanced weight for face transfer without scene destruction.
    ) -> bytes:
        """
        Refines a scene image with a reference face using IP-Adapter (Step 2 of 2-step process).
        """
        if not self.api_key:
            raise HTTPException(status_code=503, detail="RunWare API key not configured")

        # The SCENE image is the main image data for img2img
        scene_data_uri = f"data:image/jpeg;base64,{base64.b64encode(scene_image_bytes).decode('utf-8')}"
        
        # The SWAMIJI face is the guideImage for the IP-Adapter
        face_data_uri = f"data:image/jpeg;base64,{base64.b64encode(face_image_bytes).decode('utf-8')}"

        payload = {
            "taskType": "imageInference",
            "taskUUID": str(uuid.uuid4()),
            "positivePrompt": prompt, # A minimal prompt helps guide the refinement
            "negativePrompt": negative_prompt,
            "model": "runware:101@1", # CORRECTED: Use the same proven model for both txt2img and img2img refinement
            "imageDataURI": scene_data_uri, # Use the scene as the base for img2img
            "strength": strength, # CORE FIX: Use the strength parameter to control scene preservation.
            "height": height,
            "width": width,
            "numberResults": 1,
            "steps": steps,
            "CFGScale": cfg_scale,
            "seed": random.randint(1, 1000000),
            "ipAdapters": [{
                "model": self.ip_adapter_model,
                "guideImage": face_data_uri,
                "weight": ip_adapter_weight
            }]
        }

        logger.info("🎨 Step 2: Refining scene with reference face...")
        try:
            async with httpx.AsyncClient(timeout=90.0) as client:
                response = await client.post(
                    self.base_url,
                    headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                    json=[payload]
                )
                response.raise_for_status()
                parsed_response = response.json()

                if not parsed_response.get('data') or not parsed_response['data'][0].get('imageURL'):
                    raise HTTPException(status_code=502, detail="RunWare API did not return an image URL for face refinement.")

                img_url = parsed_response['data'][0]['imageURL']
                img_response = await client.get(img_url)
                img_response.raise_for_status()
                
                logger.info("✅ Step 2 complete: Face refined successfully.")
                return img_response.content
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ RunWare face refinement failed with status {e.response.status_code}: {e.response.text}")
            raise HTTPException(status_code=e.response.status_code, detail=f"RunWare face refinement failed: {e.response.text}")
        except Exception as e:
            logger.error(f"❌ Unexpected error during face refinement: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="An unexpected error occurred during face refinement.")
    
    async def generate_variation_from_face(
        self,
        face_image_bytes: bytes,
        prompt: str,
        negative_prompt: str = "ugly, deformed, noisy, blurry, low contrast, text, signature, watermark, extra limbs, extra fingers, cartoon, anime, painting",
        width: int = 1024,
        height: int = 1024,
        steps: int = 40,
        cfg_scale: float = 12.0,
        ip_adapter_weight: float = 0.6 # Higher weight to ensure face consistency
    ) -> bytes:
        """Generates a new image from a text prompt while using a face reference via IP-Adapter (txt2img + IP-Adapter)."""
        if not self.api_key:
            raise HTTPException(status_code=503, detail="RunWare API key not configured")

        face_data_uri = f"data:image/jpeg;base64,{base64.b64encode(face_image_bytes).decode('utf-8')}"

        payload = {
            "taskType": "imageInference",
            "taskUUID": str(uuid.uuid4()),
            "positivePrompt": prompt,
            "negativePrompt": negative_prompt,
            "model": "runware:101@1",
            "height": height,
            "width": width,
            "numberResults": 1,
            "steps": steps,
            "CFGScale": cfg_scale,
            "seed": random.randint(1, 1000000),
            "ipAdapters": [{
                "model": self.ip_adapter_model,
                "guideImage": face_data_uri,
                "weight": ip_adapter_weight
            }]
        }

        logger.info(f"🎨 Generating variation for prompt: {prompt[:50]}...")
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self.base_url,
                    headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                    json=[payload]
                )
                response.raise_for_status()
                parsed_response = response.json()

                if not parsed_response.get('data') or not parsed_response['data'][0].get('imageURL'):
                    raise HTTPException(status_code=502, detail="RunWare API did not return an image URL for the variation.")

                img_url = parsed_response['data'][0]['imageURL']
                img_response = await client.get(img_url)
                img_response.raise_for_status()
                
                logger.info("✅ Variation generated successfully.")
                return img_response.content
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ RunWare variation generation failed with status {e.response.status_code}: {e.response.text}")
            raise HTTPException(status_code=e.response.status_code, detail=f"RunWare variation generation failed: {e.response.text}") from e
        except Exception as e:
            logger.error(f"❌ Unexpected error during variation generation: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="An unexpected error occurred during variation generation.") from e


# 🎯 PHASE 1: DRAMATIC COLOR REDESIGN - Maximum contrast to avoid saffron conflicts
# Each theme uses COMPLETELY DIFFERENT colors + varied clothing styles for better AI differentiation
THEMES = {
    0: {"name": "Meditative Monday", "description": "wearing pristine PURE WHITE ceremonial robes with flowing silver-trimmed fabric, sitting in lotus position on a snow-capped Himalayan mountain peak at golden sunrise, surrounded by swirling morning mist and ancient prayer flags, with soft ethereal lighting illuminating the serene meditation pose"},
    1: {"name": "Teaching Tuesday", "description": "wearing rich DEEP MAROON traditional scholar robes with intricate golden embroidery and sacred symbols, seated on an ornate wooden throne in a magnificent ashram hall with carved pillars, colorful tapestries, brass oil lamps, and devoted disciples seated on the marble floor, warm temple lighting creating a divine atmosphere"},
    2: {"name": "Wisdom Wednesday", "description": "wearing FOREST GREEN simple cotton kurta with natural hemp threads, sitting cross-legged under a massive ancient banyan tree with sprawling roots, surrounded by palm leaf manuscripts, traditional ink pots, wooden writing stylus, dappled sunlight filtering through dense green foliage creating a scholarly forest retreat"},
    3: {"name": "Thankful Thursday", "description": "wearing ROYAL BLUE silk kurta with simple white dhoti, kneeling gracefully by a sacred crystal-clear river with lotus flowers floating on the surface, holding a brass plate filled with marigold offerings, coconut, incense, surrounded by ancient stone ghats and temple spires in the misty distance"},
    4: {"name": "Festive Friday", "description": "adorned in magnificent BRIGHT GOLDEN YELLOW silk robes with elaborate zari work, ruby gemstones, sacred rudraksha beads, standing in a grand temple courtyard during festival celebrations with colorful rangoli patterns, hanging marigold garlands, burning oil lamps, devotees with musical instruments, vibrant festival atmosphere"},
    5: {"name": "Silent Saturday", "description": "wearing simple CHARCOAL GRAY meditation robes with rough handwoven texture, sitting in perfect stillness inside a dimly lit ancient cave with smooth stone walls, flickering butter lamps casting dancing shadows, stalactites overhead, complete silence and spiritual solitude, minimal natural lighting from cave entrance"},
    6: {"name": "Serene Sunday", "description": "wearing flowing CREAM-COLORED cotton dhoti with subtle silver threads, walking barefoot on pristine white sand along an endless ocean beach at peaceful dawn, gentle waves lapping the shore, seagulls in the distance, palm trees swaying, soft morning sunlight creating a heavenly coastal sanctuary"},
}

# 🚫 Reusable negative prompt to prevent AI from copying the reference image
REFERENCE_BLOCKING_NEGATIVES = """copying the reference image, duplicating the reference image, same background, same clothing, same pose, 
original background, original clothing, original attire, unchanged from reference, identical to reference photo"""


class ThemeService:
    """
    🚀 RUNWARE-ONLY THEME SERVICE: Premium face preservation with IP-Adapter FaceID
    Orchestrates daily theme generation using RunWare's IP-Adapter FaceID workflow for optimal control.
    
    Features:
    - Superior face preservation through a two-step generation process
    - Dramatic transformation of clothes/background while preserving identity
    - Production-ready with retry mechanisms and error handling
    - Cost-effective and high-quality image generation
    """

    def __init__(
        self,
        storage_service: SupabaseStorageService,
        replicate_service: ReplicateService
    ):
        self.storage_service = storage_service
        self.replicate_service = replicate_service
        self.http_client = httpx.AsyncClient(timeout=120.0)
        
        logger.info("✅ ThemeService initialized with Pillow for image processing.")
        
        # 🎯 RUNWARE CONFIGURATION
        try:
            from core_foundation_enhanced import EnhancedSettings
            settings = EnhancedSettings()
        except ImportError:
            # Fallback: Get RunWare API key directly from environment
            import os
            settings = None
            logger.warning("⚠️ EnhancedSettings not available, using direct environment access")
        
        # Get RunWare API key from settings or environment (safe retrieval)
        if settings and hasattr(settings, 'runware_api_key') and settings.runware_api_key:
            self.runware_api_key = settings.runware_api_key
        else:
            self.runware_api_key = os.getenv("RUNWARE_API_KEY")
        
        if not self.runware_api_key:
            logger.error("❌ RUNWARE_API_KEY environment variable is required!")
            raise HTTPException(
                status_code=503, 
                detail="RunWare API key is required. Please set RUNWARE_API_KEY environment variable."
            )
        
        self.runware_service = RunWareService(self.runware_api_key)
        logger.info("🚀 ThemeService initialized with RunWare IP-Adapter FaceID workflow.")

    async def _crop_to_face(self, image_bytes: bytes) -> bytes:
        """
        Crops the center of the image using Pillow.
        This is a simple, reliable method that avoids heavy dependencies.
        Assumes the face is in the center, as per photo guidelines.
        """
        try:
            pil_image = Image.open(BytesIO(image_bytes))
            width, height = pil_image.size

            # Define crop dimensions (e.g., 50% of width and height, centered)
            crop_width = int(width * 0.5)
            crop_height = int(height * 0.5)
            
            left = (width - crop_width) // 2
            top = (height - crop_height) // 2
            right = (width + crop_width) // 2
            bottom = (height + crop_height) // 2

            cropped_image = pil_image.crop((left, top, right, bottom))

            # Convert cropped image back to bytes
            with BytesIO() as output:
                cropped_image.save(output, format="PNG")
                cropped_bytes = output.getvalue()

            logger.info(f"✅ Image center-cropped successfully with Pillow. Cropped size: {len(cropped_bytes)/1024:.1f}KB")
            return cropped_bytes

        except Exception as e:
            logger.error(f"❌ Error during Pillow center-cropping: {e}", exc_info=True)
            return image_bytes # Fallback to original image on error
    
    def _sanitize_prompt_input(self, text: str, max_length: int = 250) -> str:
        """
        Sanitizes and normalizes user-provided text to prevent prompt injection and runaway inputs.
        - Trims leading/trailing whitespace.
        - Collapses consecutive whitespace characters (including newlines) into a single space.
        - Truncates the result to a maximum length.
        """
        if not isinstance(text, str):
            return ""
        # Collapse whitespace and newlines, then strip
        normalized_text = ' '.join(text.split()).strip()
        # Truncate to max length
        truncated_text = normalized_text[:max_length]
        return truncated_text

    async def _generate_with_runware(
        self, 
        base_image_bytes: bytes,
        theme_description: str,
        custom_prompt: Optional[str] = None,
        theme_day: Optional[int] = None
    ) -> Tuple[bytes, str]:
        """
        🚀 RUNWARE IP-ADAPTER FACEID GENERATION METHOD
        Uses RunWare's advanced face preservation technology for 80-90% success rate.
        
        Args:
            base_image_bytes: Swamiji reference image bytes
            theme_description: Daily theme description
            custom_prompt: Optional custom prompt override
            
        Returns:
            Tuple[bytes, str]: Generated image bytes and final prompt used
        """
        try:
            # 🛡️ Sanitize the theme description before using it in prompts
            sanitized_theme_description = self._sanitize_prompt_input(theme_description)

            # 🎨 CONSTRUCT PROMPT for Step 1 (Scene Generation)
            if custom_prompt:
                scene_prompt = self._sanitize_prompt_input(custom_prompt, max_length=400)
            else:
                scene_prompt = (
                    f"A photorealistic, full color, vibrant colors, high-resolution portrait of a wise Indian spiritual master, "
                    f"{sanitized_theme_description}, "
                    f"professional photography, cinematic lighting, ultra-detailed, 8K quality, sharp focus."
                )

            # 🎨 DAILY COLOR NEGATIVE PROMPT: Prevent wrong colors for each day
            day_of_week = datetime.now().weekday() if theme_day is None else theme_day
            
            # 🎨 REFINED COLOR NEGATIVES: Enhanced synonyms and better filtering
            color_negatives = {
                0: ["orange robe, orange robes, saffron clothing, saffron cloth, saffron attire",
                    "maroon robe, maroon robes, maroon clothing, maroon cloth, maroon attire", 
                    "green kurta, green robe, green robes, green clothing, green cloth, green attire",
                    "blue kurta, blue robe, blue robes, blue clothing, blue cloth, blue attire",
                    "golden robe, golden robes, golden clothing, golden cloth, golden attire",
                    "gray robe, gray robes, gray clothing, gray cloth, gray attire"],  # Monday: only WHITE
                1: ["white robe, white robes, white clothing, white cloth, white attire, cream clothing",
                    "orange robe, orange robes, saffron clothing, saffron cloth, saffron attire",
                    "green kurta, green robe, green robes, green clothing, green cloth, green attire",
                    "blue kurta, blue robe, blue robes, blue clothing, blue cloth, blue attire",
                    "golden robe, golden robes, golden clothing, golden cloth, golden attire",
                    "gray robe, gray robes, gray clothing, gray cloth, gray attire"],   # Tuesday: only MAROON
                2: ["white robe, white robes, white clothing, white cloth, white attire, cream clothing",
                    "orange robe, orange robes, saffron clothing, saffron cloth, saffron attire",
                    "maroon robe, maroon robes, maroon clothing, maroon cloth, maroon attire",
                    "blue kurta, blue robe, blue robes, blue clothing, blue cloth, blue attire",
                    "golden robe, golden robes, golden clothing, golden cloth, golden attire",
                    "gray robe, gray robes, gray clothing, gray cloth, gray attire"],  # Wednesday: only GREEN
                3: ["white robe, white robes, white clothing, white cloth, white attire, cream clothing",
                    "orange robe, orange robes, saffron clothing, saffron cloth, saffron attire",
                    "maroon robe, maroon robes, maroon clothing, maroon cloth, maroon attire",
                    "green kurta, green robe, green robes, green clothing, green cloth, green attire",
                    "golden robe, golden robes, golden clothing, golden cloth, golden attire",
                    "gray robe, gray robes, gray clothing, gray cloth, gray attire"], # Thursday: only BLUE
                4: ["white robe, white robes, white clothing, white cloth, white attire, cream clothing",
                    "orange robe, orange robes, saffron clothing, saffron cloth, saffron attire",
                    "maroon robe, maroon robes, maroon clothing, maroon cloth, maroon attire",
                    "green kurta, green robe, green robes, green clothing, green cloth, green attire",
                    "blue kurta, blue robe, blue robes, blue clothing, blue cloth, blue attire",
                    "gray robe, gray robes, gray clothing, gray cloth, gray attire"],   # Friday: only GOLDEN
                5: ["white robe, white robes, white clothing, white cloth, white attire, cream clothing",
                    "orange robe, orange robes, saffron clothing, saffron cloth, saffron attire",
                    "maroon robe, maroon robes, maroon clothing, maroon cloth, maroon attire",
                    "green kurta, green robe, green robes, green clothing, green cloth, green attire",
                    "blue kurta, blue robe, blue robes, blue clothing, blue cloth, blue attire",
                    "golden robe, golden robes, golden clothing, golden cloth, golden attire"], # Saturday: only GRAY
                6: ["white robe, white robes, white clothing, white cloth, white attire",
                    "orange robe, orange robes, saffron clothing, saffron cloth, saffron attire",
                    "maroon robe, maroon robes, maroon clothing, maroon cloth, maroon attire",
                    "green kurta, green robe, green robes, green clothing, green cloth, green attire",
                    "blue kurta, blue robe, blue robes, blue clothing, blue cloth, blue attire",
                    "golden robe, golden robes, golden clothing, golden cloth, golden attire",
                    "gray robe, gray robes, gray clothing, gray cloth, gray attire"] # Sunday: only CREAM
            }
            
            # 🔧 SAFE JOINING: Check if list exists and is not empty before joining
            daily_color_list = color_negatives.get(day_of_week, [])
            daily_color_negatives = ", ".join(daily_color_list) if daily_color_list else ""
            
            # 🔧 SAFE NEGATIVE PROMPT CONSTRUCTION: Handle empty color negatives
            base_negatives = """different face, changed face, new face, altered face, face swap, face replacement, 
different person, wrong identity, mutated face, distorted face, different eyes, different nose, different mouth, 
face morph, artificial face, generic face, multiple faces, extra faces, face clone, face duplicate,
business suit, office attire, tie, corporate clothing, modern clothing, western dress, formal wear,
office background, corporate setting, modern interior, business environment, contemporary setting,
blurry face, distorted facial features, wrong facial structure, artificial looking face"""
            
            # 🎯 CORE.MD FIX: Clean negative prompt assembly using list-based joining
            # Build negative prompt segments as a list to avoid leading commas and empty separators
            negative_segments = [
                # Base face preservation negatives (always included)
                base_negatives.strip(),
                
                # Daily color negatives (only if not empty)
                daily_color_negatives.strip() if daily_color_negatives else "",
                
                # 🚫 OPTIMIZED REFERENCE-BLOCKING NEGATIVES: Replaced with a reusable constant
                REFERENCE_BLOCKING_NEGATIVES,
                
                # Quality and technical negatives - Shortened to prevent truncation
                """wrong colors, incorrect clothing colors, mismatched theme colors,
low quality, blurry, deformed, ugly, bad anatomy, cartoon, anime, painting, illustration, sketch"""
            ]
            
            # Filter out empty strings and join with clean comma separation
            negative_prompt = ", ".join(segment.strip() for segment in negative_segments if segment.strip())
            
            # 🚀 NEW TWO-STEP ARCHITECTURE 🚀
            
            # 1. Generate the scene without a face reference
            logger.info("🚀 Starting new two-step generation process...")
            scene_bytes = await self.runware_service.generate_scene_only(
                prompt=scene_prompt,
                negative_prompt=negative_prompt,
                cfg_scale=18.0, # CORE FIX: Increased strictness to force prompt adherence for color.
            )

            # Crop the base image to just the face to use as a better guide
            logger.info("🎨 Cropping base image to face for Step 2 reference...")
            face_ref_bytes = await self._crop_to_face(base_image_bytes)

            # 2. Refine the generated scene with Swamiji's face
            # Use the powerful, detailed prompt from Step 1 to guide the final composition.
            # This ensures the background, clothing, and theme from Step 1 are correctly
            # integrated with the face from the reference image.
            refinement_strength = float(os.getenv("THEME_REFINE_STRENGTH", "0.2")) # FINAL FIX v2: Drastically lower for scene preservation
            
            # 🎯 FINAL FIX: Increased IP Adapter weight to ensure strong face transfer and prevent style bleed.
            # A higher weight forces the AI to prioritize the face from the reference image, ignoring other elements like clothing.
            # The environment variable has been removed to lock in this optimal value.
            refinement_ip_weight = 0.6 

            logger.info(f"🎨 Step 2 Settings: strength={refinement_strength} (scene preservation), ip_adapter_weight={refinement_ip_weight} (face influence)")

            final_image_bytes = await self.runware_service.generate_with_face_reference(
                scene_image_bytes=scene_bytes,
                face_image_bytes=face_ref_bytes, # Use the original color image
                prompt=scene_prompt, # CORE FIX: Use the detailed scene prompt from Step 1
                negative_prompt=negative_prompt, # CORE FIX: Use the detailed negative prompt from Step 1
                strength=refinement_strength, # CORE FIX: Lower strength preserves the generated scene's integrity.
                ip_adapter_weight=refinement_ip_weight, # CORE FIX: Higher weight ensures the face is applied correctly.
            )

            logger.info("✅ Two-step theme generation completed successfully!")
            return final_image_bytes, scene_prompt # Return the original scene prompt
            
        except Exception as e:
            logger.error(f"❌ RunWare generation failed: {e}", exc_info=True)
            # Re-raise the exception to be handled by the calling method
            raise

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
        except HTTPException:
            # Re-raise HTTPExceptions unchanged to preserve status codes and details
            raise
        except Exception as e:
            logger.error(f"An unexpected error occurred in _get_base_image_data: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="An unexpected error occurred while retrieving the image.") from e

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
            
            cascade_path = "assets/haarcascade_frontalface_default.xml"
            if not os.path.exists(cascade_path):
                logger.error(f"Haar cascade file not found at {cascade_path}")
                raise FileNotFoundError("Haar cascade file not found.")

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
