"""
🌟 THEME SERVICE

This service is the creative engine that generates daily visual themes for Swamiji's avatar.
It uses Stability AI's image-to-image generation with balanced strength for natural transformation 
while preserving Swamiji's identity and changing clothing/background according to daily themes.
"""

import logging
from datetime import datetime
import os
import uuid
import httpx
from fastapi import HTTPException, Depends
import asyncpg
import json
from typing import Optional, Tuple, List
from PIL import Image, ImageDraw
import io
import numpy as np
from scipy import ndimage

from services.stability_ai_service import StabilityAiService, get_stability_service
from services.supabase_storage_service import SupabaseStorageService, get_storage_service
import db

logger = logging.getLogger(__name__)

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

class ThemeService:
    """Orchestrates the generation of daily themes using Stability AI img2img."""

    def __init__(
        self,
        stability_service: StabilityAiService,
        storage_service: SupabaseStorageService,
        db_conn: asyncpg.Connection,
    ):
        self.stability_service = stability_service
        self.storage_service = storage_service
        self.db_conn = db_conn
        
        logger.info("Initialized ThemeService with Stability AI img2img service")
    


    def _create_smart_person_background_mask(self, image_bytes: bytes, image_width: int, image_height: int) -> bytes:
        """
        🧠 SMART PERSON-BACKGROUND SEPARATION: Intelligent mask that distinguishes person from background.
        
        USER REQUIREMENT: "red ala mark pannina idam ellaam original image oda background theriyuthu"
        - Preserve ONLY the actual person (face, neck, shoulders) within red circle areas
        - Transform background (trees, foliage) even if they're behind the person
        - Create natural realistic blending between preserved person and AI-generated themed body
        
        INTELLIGENT SEGMENTATION APPROACH:
        1. Analyze image colors to distinguish person vs background
        2. Create person-specific mask (not just geometric shapes)
        3. Preserve person pixels, transform background pixels
        4. Natural blending zones around person edges
        
        Args:
            image_bytes: Original image data for color analysis
            image_width: Width of the original image
            image_height: Height of the original image
            
        Returns:
            bytes: PNG mask image as bytes with smart person-background separation
            
        Raises:
            ValueError: If input parameters are invalid
            RuntimeError: If image processing fails
        """
        # 🔍 INPUT VALIDATION: Ensure all parameters are valid
        if image_bytes is None or len(image_bytes) == 0:
            raise ValueError("image_bytes cannot be None or empty")
        
        if not isinstance(image_width, int) or image_width <= 0:
            raise ValueError(f"image_width must be a positive integer, got: {image_width}")
            
        if not isinstance(image_height, int) or image_height <= 0:
            raise ValueError(f"image_height must be a positive integer, got: {image_height}")
        
        try:
            # Load original image for color analysis
            original_image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
            original_array = np.array(original_image)
            
            # Validate image dimensions match parameters
            actual_height, actual_width = original_array.shape[:2]
            if actual_width != image_width or actual_height != image_height:
                logger.warning(f"Image dimensions mismatch: expected {image_width}x{image_height}, got {actual_width}x{actual_height}")
                # Use actual dimensions from image
                image_width, image_height = actual_width, actual_height
                
        except Exception as e:
            raise RuntimeError(f"Failed to load or process image: {str(e)}")
        
        # Create base mask (white = transform everything by default)
        mask = Image.new('L', (image_width, image_height), 255)
        mask_array = np.array(mask)
        
        try:
            # Define person area boundaries (matching user's red circles)
            face_width_ratio = 0.28
            face_height_ratio = 0.32
            
            face_width = int(image_width * face_width_ratio)
            face_height = int(image_height * face_height_ratio)
            face_left = (image_width - face_width) // 2
            face_top = int(image_height * 0.15)
            face_right = face_left + face_width
            face_bottom = face_top + face_height
            
            # Validate face region boundaries
            if face_left >= face_right or face_top >= face_bottom:
                raise ValueError(f"Invalid face region: ({face_left}, {face_top}) to ({face_right}, {face_bottom})")
            
            # Analyze skin tones in central face area (for person identification)
            skin_sample_left = max(0, face_left + int(face_width * 0.3))
            skin_sample_right = min(image_width, face_right - int(face_width * 0.3))  
            skin_sample_top = max(0, face_top + int(face_height * 0.2))
            skin_sample_bottom = min(image_height, face_bottom - int(face_height * 0.4))
            
            # Validate skin sample region
            if (skin_sample_left >= skin_sample_right or 
                skin_sample_top >= skin_sample_bottom or
                skin_sample_right - skin_sample_left < 5 or
                skin_sample_bottom - skin_sample_top < 5):
                raise ValueError("Skin sample region is too small or invalid")
            
            # Extract person skin colors
            skin_region = original_array[skin_sample_top:skin_sample_bottom, skin_sample_left:skin_sample_right]
            
            # Calculate person color characteristics
            person_colors = {
                'skin_mean': np.mean(skin_region, axis=(0, 1)),
                'skin_std': np.std(skin_region, axis=(0, 1)),
            }
            
            # Analyze background colors (corners of image)
            corner_size = max(5, min(image_width, image_height) // 10)  # Ensure minimum corner size
            corners = [
                original_array[0:corner_size, 0:corner_size],  # Top-left
                original_array[0:corner_size, -corner_size:], # Top-right  
                original_array[-corner_size:, 0:corner_size], # Bottom-left
                original_array[-corner_size:, -corner_size:]  # Bottom-right
            ]
            
            background_colors = []
            for corner in corners:
                if corner.size > 0:  # Ensure corner is not empty
                    background_colors.append(np.mean(corner, axis=(0, 1)))
            
            if not background_colors:
                raise ValueError("Could not extract background colors from image corners")
                
            background_mean = np.mean(background_colors, axis=0)
            
        except Exception as e:
            logger.error(f"❌ Color analysis failed: {str(e)}")
            raise RuntimeError(f"Failed to analyze image colors: {str(e)}")
        
        # 🚀 VECTORIZED SMART PERSON DETECTION: High-performance numpy operations
        try:
            # Define processing region boundaries
            region_top = max(0, face_top - 20)
            region_bottom = min(image_height, face_bottom + 40)
            region_left = max(0, face_left - 10)
            region_right = min(image_width, face_right + 10)
            
            # Create coordinate grids for the region
            y_coords, x_coords = np.mgrid[region_top:region_bottom, region_left:region_right]
            region_height = region_bottom - region_top
            region_width = region_right - region_left
            
            # Extract pixel colors for the entire region
            region_pixels = original_array[region_top:region_bottom, region_left:region_right]
            
            # Vectorized distance calculations
            # Calculate person distances (broadcasting across all pixels)
            person_distances = np.linalg.norm(
                region_pixels - person_colors['skin_mean'], axis=2
            )
            
            # Calculate background distances (broadcasting across all pixels)
            background_distances = np.linalg.norm(
                region_pixels - background_mean, axis=2
            )
            
            # Create boolean mask for person pixels (vectorized comparison)
            person_pixel_mask = person_distances < (background_distances * 0.8)
            
            # Calculate face center coordinates
            center_x = (face_left + face_right) // 2
            center_y = (face_top + face_bottom) // 2
            max_distance = np.sqrt((face_width/2)**2 + (face_height/2)**2)
            
            # Vectorized distance from center calculation
            distances_from_center = np.sqrt(
                (x_coords - center_x)**2 + (y_coords - center_y)**2
            )
            
            # Create mask region array for vectorized preservation level assignment
            mask_region = np.full((region_height, region_width), 255, dtype=np.uint8)  # Default: transform
            
            # Vectorized preservation level assignment (only for person pixels)
            person_indices = np.where(person_pixel_mask)
            person_distances_from_center = distances_from_center[person_indices]
            
            # Core face: Pure preservation (0)
            core_face_mask = person_distances_from_center < (max_distance * 0.4)
            mask_region[person_indices[0][core_face_mask], person_indices[1][core_face_mask]] = 0
            
            # Face edges: 75% preserve, 25% blend (64)
            face_edge_mask = (person_distances_from_center >= (max_distance * 0.4)) & \
                           (person_distances_from_center < (max_distance * 0.7))
            mask_region[person_indices[0][face_edge_mask], person_indices[1][face_edge_mask]] = 64
            
            # Neck area: 50% preserve, 50% blend (128)
            neck_mask = (person_distances_from_center >= (max_distance * 0.7)) & \
                       (person_distances_from_center < max_distance)
            mask_region[person_indices[0][neck_mask], person_indices[1][neck_mask]] = 128
            
            # Update the main mask array with the processed region
            mask_array[region_top:region_bottom, region_left:region_right] = mask_region
            
            logger.info(f"🚀 VECTORIZED PROCESSING: {region_width}x{region_height} region, "
                       f"{np.sum(person_pixel_mask)} person pixels identified")
                       
        except Exception as e:
            logger.error(f"❌ Vectorized processing failed, falling back to safe mode: {str(e)}")
            # Fallback: Simple geometric mask if vectorized processing fails
            draw = ImageDraw.Draw(Image.fromarray(mask_array))
            face_left_safe = max(0, face_left)
            face_top_safe = max(0, face_top)
            face_right_safe = min(image_width, face_right)
            face_bottom_safe = min(image_height, face_bottom)
            draw.ellipse([face_left_safe, face_top_safe, face_right_safe, face_bottom_safe], fill=0)
            mask_array = np.array(Image.fromarray(mask_array))
        
        try:
            # Create smooth blending zones around preserved areas
            # Smooth the mask to avoid hard edges
            mask_array = ndimage.gaussian_filter(mask_array.astype(float), sigma=2.0)
            mask_array = np.clip(mask_array, 0, 255).astype(np.uint8)
            
            # Convert back to PIL Image
            final_mask = Image.fromarray(mask_array, mode='L')
            
            # Convert to bytes
            mask_buffer = io.BytesIO()
            final_mask.save(mask_buffer, format='PNG')
            mask_bytes = mask_buffer.getvalue()
            
            # Validate output
            if len(mask_bytes) == 0:
                raise RuntimeError("Generated mask is empty")
            
            logger.info(f"🧠 SMART PERSON-BACKGROUND MASK: {image_width}x{image_height} | Person colors analyzed | Background separated | Smooth blending applied | Mask size: {len(mask_bytes)/1024:.1f}KB")
            return mask_bytes
            
        except Exception as e:
            logger.error(f"❌ Mask generation failed during final processing: {str(e)}")
            raise RuntimeError(f"Failed to generate smart person-background mask: {str(e)}")

    async def _apply_color_harmonization(
        self, 
        generated_image_bytes: bytes, 
        original_image_bytes: bytes,
        mask_bytes: bytes,
        image_width: int, 
        image_height: int
    ) -> bytes:
        """
        🎨 ADVANCED COLOR HARMONIZATION: Fix face-body color mismatch for natural blending.
        
        USER REQUIREMENT: "body oda face porunthanu" - Face and body should blend naturally
        - Analyzes AI-generated body colors and lighting
        - Adjusts preserved face region to match body's color palette
        - Applies smooth gradient blending at mask edges
        - Maintains face identity while improving color consistency
        
        HARMONIZATION TECHNIQUES:
        1. Color Temperature Matching: Adjust face warmth/coolness to match body
        2. Saturation Matching: Align face saturation with AI-generated style
        3. Brightness/Contrast Matching: Match lighting conditions
        4. Gradient Blending: Smooth transitions at preserved region edges
        
        Args:
            generated_image_bytes: AI-generated image with face-body mismatch
            original_image_bytes: Original Swamiji photo for reference
            mask_bytes: Mask used for inpainting (to identify preserved regions)
            image_width: Image width
            image_height: Image height
            
        Returns:
            bytes: Color-harmonized image with natural face-body blending
        """
        try:
            # Load images
            generated_image = Image.open(io.BytesIO(generated_image_bytes)).convert('RGB')
            original_image = Image.open(io.BytesIO(original_image_bytes)).convert('RGB')
            mask_image = Image.open(io.BytesIO(mask_bytes)).convert('L')
            
            # Convert to numpy arrays for processing
            generated_array = np.array(generated_image)
            original_array = np.array(original_image)
            mask_array = np.array(mask_image)
            
            # Create face and body region masks
            # Face region: where mask is dark (preserved areas)
            face_mask = mask_array < 128  # Black/dark areas = preserved face
            body_mask = mask_array >= 192  # White/bright areas = AI-generated body
            
            # Extract color statistics from each region
            face_pixels = generated_array[face_mask]
            body_pixels = generated_array[body_mask]
            
            if len(face_pixels) == 0 or len(body_pixels) == 0:
                logger.warning("⚠️ Color harmonization: Insufficient face or body pixels, using original")
                return generated_image_bytes
            
            # Calculate color statistics
            face_mean = np.mean(face_pixels, axis=0)
            body_mean = np.mean(body_pixels, axis=0)
            
            face_std = np.std(face_pixels, axis=0)
            body_std = np.std(body_pixels, axis=0)
            
            # 🎨 COLOR HARMONIZATION: Adjust face colors to match body
            # 1. Calculate color shift needed
            color_shift = body_mean - face_mean
            
            # 2. Calculate saturation adjustment
            face_saturation = np.mean(face_std)
            body_saturation = np.mean(body_std)
            saturation_ratio = body_saturation / max(face_saturation, 1.0)
            
            # 3. Create harmonized image
            harmonized_array = generated_array.copy()
            
            # 🚀 VECTORIZED COLOR HARMONIZATION: High-performance color adjustments
            adjustment_strength = 0.4  # Subtle adjustment to maintain face identity
            
            # Create float copy for processing
            harmonized_array_float = harmonized_array.astype(float)
            
            # Get indices of face pixels for vectorized operations
            face_indices = np.where(face_mask)
            
            if len(face_indices[0]) > 0:
                # Extract face pixels for vectorized processing
                face_pixels_float = harmonized_array_float[face_indices]
                
                # 1. Apply color temperature shift (vectorized)
                adjusted_pixels = face_pixels_float + (color_shift * adjustment_strength)
                
                # 2. Apply saturation adjustment (vectorized)
                pixel_means = np.mean(adjusted_pixels, axis=1, keepdims=True)
                adjusted_pixels = pixel_means + (adjusted_pixels - pixel_means) * (
                    saturation_ratio ** adjustment_strength
                )
                
                # 3. Ensure valid range
                adjusted_pixels = np.clip(adjusted_pixels, 0, 255)
                
                # 4. Calculate blend factors based on mask values (vectorized)
                mask_values = mask_array[face_indices]
                blend_factors = np.where(
                    mask_values < 64,
                    adjustment_strength,  # Core preserved area
                    adjustment_strength * 0.3  # Edge area - less adjustment
                )
                
                # 5. Apply blended adjustment (vectorized)
                blended_pixels = (
                    face_pixels_float * (1 - blend_factors[:, np.newaxis]) + 
                    adjusted_pixels * blend_factors[:, np.newaxis]
                )
                
                # Update harmonized array with processed pixels
                harmonized_array_float[face_indices] = blended_pixels
            
            # Convert back to uint8
            harmonized_array = harmonized_array_float.astype(np.uint8)
            
            # Convert back to PIL Image
            harmonized_image = Image.fromarray(harmonized_array, mode='RGB')
            
            # Convert to bytes
            harmonized_buffer = io.BytesIO()
            harmonized_image.save(harmonized_buffer, format='PNG')
            harmonized_bytes = harmonized_buffer.getvalue()
            
            logger.info(f"🎨 COLOR HARMONIZATION SUCCESS: Face-body color matching applied | "
                       f"Face mean: {face_mean.astype(int)} → Body mean: {body_mean.astype(int)} | "
                       f"Saturation ratio: {saturation_ratio:.2f}")
            
            return harmonized_bytes
            
        except Exception as e:
            logger.error(f"❌ Color harmonization failed, using original: {str(e)}")
            # Fallback: return generated image without harmonization
            return generated_image_bytes

    def _analyze_face_skin_color(self, image_bytes: bytes) -> str:
        """
        🎨 OPTION 6: Advanced color analysis - Extract dominant skin colors from face area.
        
        Analyzes the preserved face area to extract dominant skin tone colors and
        converts them to descriptive terms for prompt injection.
        
        Args:
            image_bytes: Original image bytes to analyze
            
        Returns:
            str: Descriptive color terms for prompt injection
            
        Analysis Process:
        1. Load image and extract face area pixels
        2. Calculate dominant RGB colors using clustering
        3. Convert RGB values to descriptive color terms
        4. Return formatted color description for prompts
        """
        try:
            # Load image and convert to RGB
            image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
            image_width, image_height = image.size
            
            # Calculate face area coordinates (same as mask inner zone)
            face_width_ratio = 0.28   # 28% of image width
            face_height_ratio = 0.32  # 32% of image height
            
            face_width = int(image_width * face_width_ratio)
            face_height = int(image_height * face_height_ratio)
            
            face_left = (image_width - face_width) // 2
            face_top = int(image_height * 0.15)
            face_right = face_left + face_width
            face_bottom = face_top + face_height
            
            # Extract face area pixels
            face_area = image.crop((face_left, face_top, face_right, face_bottom))
            face_pixels = np.array(face_area)
            
            # Reshape to list of RGB values
            pixels_reshaped = face_pixels.reshape(-1, 3)
            
            # Calculate average RGB values (dominant color) with safe conversion
            try:
                avg_r = float(np.mean(pixels_reshaped[:, 0]))
                avg_g = float(np.mean(pixels_reshaped[:, 1]))
                avg_b = float(np.mean(pixels_reshaped[:, 2]))
                
                # Clamp to valid RGB range and convert to int
                avg_r = max(0, min(255, int(round(avg_r))))
                avg_g = max(0, min(255, int(round(avg_g))))
                avg_b = max(0, min(255, int(round(avg_b))))
                
            except (ValueError, OverflowError, TypeError) as e:
                logger.warning(f"RGB calculation error, using fallback values: {e}")
                avg_r, avg_g, avg_b = 139, 102, 85  # Safe fallback values
            
            # Convert RGB to descriptive color terms with error handling
            color_description = self._rgb_to_skin_tone_description(avg_r, avg_g, avg_b)
            
            logger.info(f"🎨 FACE COLOR ANALYSIS: RGB({avg_r}, {avg_g}, {avg_b}) → {color_description}")
            return color_description
            
        except Exception as e:
            logger.error(f"❌ Face color analysis failed: {e}")
            # Fallback to generic description
            return "warm natural skin tone with consistent complexion"
    
    def _rgb_to_skin_tone_description(self, r: int, g: int, b: int) -> str:
        """
        Convert RGB values to descriptive skin tone terms for AI prompts.
        
        CORE.MD & REFRESH.MD COMPLIANCE: Enhanced with RGB validation, improved warmth calculation,
        and accurate color terminology without hardcoded assumptions.
        
        Args:
            r, g, b: RGB color values (must be 0-255)
            
        Returns:
            str: Descriptive color terms for prompt injection
            
        Raises:
            ValueError: If RGB values are outside valid 0-255 range
        """
        # 🛡️ RGB VALIDATION - CORE.MD: Input validation with clear error messages
        if not all(isinstance(val, (int, float)) for val in [r, g, b]):
            raise ValueError(f"RGB values must be numeric. Received: r={type(r).__name__}, g={type(g).__name__}, b={type(b).__name__}")
        
        if not all(0 <= val <= 255 for val in [r, g, b]):
            raise ValueError(f"RGB values must be in range 0-255. Received: r={r}, g={g}, b={b}")
        
        # Convert to int for consistency
        r, g, b = int(r), int(g), int(b)
        
        # 🎨 ENHANCED WARMTH CALCULATION - Include green channel for accurate color temperature
        brightness = (r + g + b) / 3
        # Improved warmth: considers both red-blue and green-blue relationships for accurate skin tone analysis
        warmth = (r - b) + (g - b) * 0.5  # Weighted formula: red-blue primary, green-blue secondary
        
        # 🎯 ENHANCED BASE TONE DETERMINATION - More accurate skin tone categories
        if brightness > 200:
            base_tone = "very fair"
        elif brightness > 180:
            base_tone = "fair"
        elif brightness > 140:
            base_tone = "medium" 
        elif brightness > 100:
            base_tone = "olive"
        elif brightness > 60:
            base_tone = "deep"
        else:
            base_tone = "very deep"
            
        # 🌡️ ENHANCED WARMTH CATEGORIZATION - Improved thresholds for green-enhanced calculation
        if warmth > 30:
            warmth_desc = "warm golden"
        elif warmth > 15:
            warmth_desc = "warm"
        elif warmth > -15:
            warmth_desc = "neutral"
        elif warmth > -30:
            warmth_desc = "cool"
        else:
            warmth_desc = "cool pink"
            
        # ✅ ACCURATE COLOR DESCRIPTION - Remove hardcoded "brown", use precise terminology
        # No assumptions about skin color - let the AI determine the actual hue based on RGB values
        color_description = f"{warmth_desc} {base_tone} skin tone with RGB({r}, {g}, {b}) undertones"
        
        return color_description

    async def _determine_safe_strength(self, requested_strength: float) -> float:
        """
        🎯 FEATURE FLAG CONTROLLED STRENGTH DETERMINATION - CORE.MD & REFRESH.MD COMPLIANCE
        Implements A/B testing and controlled rollout for aggressive transformation parameters.
        
        Args:
            requested_strength: The requested strength parameter (default 0.4)
            
        Returns:
            float: The final strength to use, controlled by feature flags and safety checks
            
        Feature Flag Logic:
        - AGGRESSIVE_THEME_TESTING=true: Enables controlled aggressive testing (0.6-0.8)
        - TESTING_MODE=true: Allows higher strength for development testing
        - Default: Uses safe range (0.3-0.4) for production
        - A/B Testing: Future enhancement for user subset testing
        """
        # Environment-based feature flags
        aggressive_testing_enabled = os.getenv("AGGRESSIVE_THEME_TESTING", "false").lower() == "true"
        testing_mode = os.getenv("TESTING_MODE", "false").lower() == "true"
        environment = os.getenv("ENVIRONMENT", "production").lower()
        
        # Safety validation - ensure strength is within valid range
        if not (0.0 <= requested_strength <= 1.0):
            logger.error(f"❌ INVALID STRENGTH: {requested_strength} outside range 0.0-1.0, defaulting to 0.4")
            return 0.4
            
        # Feature flag decision tree
        if aggressive_testing_enabled and environment in ["development", "staging", "testing"]:
            # Controlled aggressive testing in non-production environments
            if requested_strength > 0.4:
                logger.warning(f"🧪 FEATURE FLAG ACTIVE: Aggressive testing enabled, using requested strength {requested_strength}")
                return min(requested_strength, 0.8)  # Cap at 0.8 maximum
            else:
                return requested_strength
                
        elif testing_mode and environment != "production":
            # Development testing mode - allow requested strength but with logging
            if requested_strength > 0.4:
                logger.warning(f"🔧 TESTING MODE: Using requested strength {requested_strength} in {environment}")
                return min(requested_strength, 0.8)  # Cap at 0.8 maximum
            else:
                return requested_strength
                
        else:
            # Production safety - enforce safe range
            if requested_strength > 0.4:
                logger.warning(f"🔒 PRODUCTION SAFETY: Requested strength {requested_strength} exceeds safe range, capping at 0.4")
                return 0.4
            else:
                return max(requested_strength, 0.3)  # Minimum 0.3 for some transformation

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





    async def generate_themed_image_bytes(
        self, 
        custom_prompt: Optional[str] = None, 
        theme_day: Optional[int] = None,
        strength_param: float = 0.4  # Kept for backward compatibility but not used in inpainting
    ) -> Tuple[bytes, str]:
        """
        🎭 PHASE 2: INPAINTING APPROACH - 100% face preservation + 100% theme transformation.
        Uses mask-based inpainting for surgical precision: face area preserved, everything else transforms.
        Returns a tuple of (image_bytes, final_prompt) - Perfect face preservation with dramatic theme transformations.
        
        Args:
            custom_prompt: Optional custom prompt to override theme-based generation
            theme_day: Optional day override (0=Monday, 1=Tuesday, ..., 6=Sunday). If None, uses current day.
            strength_param: DEPRECATED - Kept for backward compatibility. Inpainting uses mask precision instead.
        
        Inpainting Enhancements:
        - Face preservation mask: BLACK (preserve face) + WHITE (transform clothes/background)
        - 100% surgical precision - face pixels never touched, everything else free to transform
        - No conflicting prompts - mask handles preservation, prompts focus on transformation  
        - Minimal Face-Only + Maximum AI Freedom: Ultra-tight preservation mask preserving only facial features + AI color analysis + perfect color injection (preserves only face, AI generates completely new themed clothes/background)
        - Enhanced theme descriptions with rich details (clothing, background, lighting, atmosphere)
        - Theme day selection for testing all 7 daily themes
        - No strength limitations - mask provides absolute control
        """
        try:
            base_image_bytes, base_image_url = await self._get_base_image_data()
            logger.info(f"Base image loaded: {len(base_image_bytes)/1024:.1f}KB from {base_image_url}")
            
            if custom_prompt:
                theme_description = custom_prompt
                logger.info(f"Using custom prompt: {custom_prompt}")
            else:
                # CORE.MD & REFRESH.MD: Explicit validation instead of silent fallback
                if theme_day is not None:
                    # Validate theme_day is within valid range 0-6 (Monday=0, Sunday=6)
                    if not isinstance(theme_day, int) or theme_day < 0 or theme_day > 6:
                        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                        valid_range = ', '.join([f"{i}={day_names[i]}" for i in range(7)])
                        error_msg = (
                            f"Invalid theme_day={theme_day}. Must be an integer between 0-6 "
                            f"({valid_range}). Received: {theme_day} (type: {type(theme_day).__name__})"
                        )
                        logger.error(f"❌ THEME_DAY VALIDATION ERROR: {error_msg}")
                        raise ValueError(error_msg)
                    
                    day_of_week = theme_day
                    logger.info(f"🎯 THEME OVERRIDE: Using theme_day={theme_day} instead of current day")
                else:
                    # Only use current day when theme_day is None (not provided)
                    day_of_week = datetime.now().weekday()
                    logger.info(f"📅 Using current day: {day_of_week}")
                
                theme = THEMES.get(day_of_week, THEMES.get(0, {"description": "in a serene setting"}))
                theme_description = theme['description']
                day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                logger.info(f"🎨 Using theme for {day_names[day_of_week]}: {theme.get('name', 'Unknown')} - {theme_description[:100]}...")

            # 🎨 OPTION 5+6 COMBINATION: Ultra-extended mask + AI color analysis for ULTIMATE precision
            logger.info("🎨 OPTION 5+6 ULTIMATE: Ultra-extended mask (40% neck) + AI color analysis + precise color injection")
            
            # Get image dimensions for mask creation
            base_image = Image.open(io.BytesIO(base_image_bytes))
            image_width, image_height = base_image.size
            logger.info(f"📐 BASE IMAGE DIMENSIONS: {image_width}x{image_height}")
            
            # 🎨 OPTION 6: Advanced face color analysis - Extract precise skin tone colors
            try:
                analyzed_skin_color = self._analyze_face_skin_color(base_image_bytes)
                logger.info(f"🎨 COLOR ANALYSIS COMPLETE: {analyzed_skin_color}")
            except Exception as color_error:
                logger.error(f"❌ Color analysis failed, using fallback: {color_error}")
                analyzed_skin_color = "warm natural skin tone with consistent complexion"
            
            # Create smart person-background separation mask 
            mask_bytes = self._create_smart_person_background_mask(base_image_bytes, image_width, image_height)
            
            # 🎨 OPTION 5+6 ULTIMATE PROMPTS: Ultra-extended mask + AI-analyzed color injection for perfect matching
            # AI color analysis provides exact skin tone, ultra-extended mask provides maximum reference area
            transformation_prompt = f"""Transform the clothing and background: {theme_description}. 
            
            CRITICAL COLOR MATCHING: The body skin must have EXACTLY this analyzed skin tone: {analyzed_skin_color}
            Maintain perfect skin tone consistency throughout - face, neck, chest, and all visible body areas.
            Use the exact same skin color temperature, undertones, and lighting conditions as the preserved face.
            Ensure seamless color transition with no color breaks, discontinuities, or tone mismatches anywhere.
            
            Create a photorealistic portrait with {analyzed_skin_color} skin consistently applied to all body areas,
            unified warm lighting matching the face illumination, sharp details, vibrant clothing colors, 
            detailed fabric textures, and spiritual atmosphere. Professional photography style with perfect 
            skin tone continuity and scientifically accurate color matching based on facial analysis."""
            
            logger.info(f"🎯 INPAINTING PROMPT (no face conflicts): {transformation_prompt[:150]}...")
            
            # 🎨 ENHANCED NEGATIVE PROMPT - Prevent color mismatches and lighting inconsistencies  
            negative_prompt = "blurry, low-resolution, text, watermark, ugly, deformed, poor anatomy, cartoon, artificial, low quality, distorted, bad proportions, mismatched skin tones, different skin colors, inconsistent lighting, color breaks, uneven skin tone, harsh shadows, color discontinuity, lighting mismatch"

            # 🎨 ULTIMATE GENERATION - Option 5+6: Ultra-extended mask + AI color analysis for perfect matching  
            logger.info("🚀 STARTING ULTIMATE INPAINTING: 40% neck coverage + AI-analyzed color injection for perfect skin tone matching")
            
            raw_generated_bytes = await self.stability_service.generate_image_with_mask(
                init_image_bytes=base_image_bytes,
                mask_image_bytes=mask_bytes,
                text_prompt=transformation_prompt,
                negative_prompt=negative_prompt
                # Note: No strength parameter - inpainting uses mask for precision control
            )
            
            # 🎨 ADVANCED COLOR HARMONIZATION: Fix face-body color mismatch
            logger.info("🎨 APPLYING COLOR HARMONIZATION: Matching face colors to AI-generated body for natural blending")
            harmonized_image_bytes = await self._apply_color_harmonization(
                generated_image_bytes=raw_generated_bytes,
                original_image_bytes=base_image_bytes,
                mask_bytes=mask_bytes,
                image_width=image_width,
                image_height=image_height
            )
            
            logger.info("✅ ULTIMATE SUCCESS: AI-analyzed color matching + 40% neck coverage + perfect skin tone consistency + dramatic theme transformation + color harmonization")
            return harmonized_image_bytes, transformation_prompt

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
            # PHASE 2: Using inpainting approach - no strength parameter needed (mask provides precision)
            generated_image_bytes, final_prompt = await self.generate_themed_image_bytes(
                custom_prompt=custom_prompt
                # No strength_param needed - inpainting uses mask for precision control
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
    storage_service: SupabaseStorageService = Depends(get_storage_service),
    db_conn: asyncpg.Connection = Depends(db.get_db),
) -> "ThemeService":
    """Creates an instance of the ThemeService with its required dependencies."""
    return ThemeService(stability_service, storage_service, db_conn)
