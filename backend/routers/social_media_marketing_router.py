"""
🚀 SOCIAL MEDIA MARKETING API ROUTER

Complete and robust API for all social media marketing operations.
This file follows CORE.MD and REFRESH.MD principles for quality and maintainability.
"""

import logging
import os
from typing import Optional, AsyncGenerator
import hashlib
import httpx
import uuid
import json
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Response, Request
from pydantic import BaseModel, Field
import asyncpg

from auth.auth_helpers import AuthenticationHelper
import db
from schemas.response import StandardResponse
from schemas.social_media import (
    Campaign, ContentCalendarItem, GenerateAllAvatarPreviewsRequest, MarketingAsset,
    MarketingAssetCreate, MarketingOverview, PlatformConfig, PlatformConfigUpdate,
    TestConnectionRequest, PostExecutionRequest, PostExecutionResult, CampaignStatus,
    ContentStatus, YouTubePlatformStatus, FacebookPlatformStatus, InstagramPlatformStatus,
    TikTokPlatformStatus, BasePlatformStatus
)

try:
    from spiritual_avatar_generation_engine import SpiritualAvatarGenerationEngine, get_avatar_engine
    AVATAR_ENGINE_AVAILABLE = True
except ImportError:
    AVATAR_ENGINE_AVAILABLE = False
    class SpiritualAvatarGenerationEngine: pass
    def get_avatar_engine():
        raise HTTPException(status_code=501, detail="Avatar Generation Engine is not available.")

try:
    from services.theme_service import ThemeService, get_theme_service
    THEME_SERVICE_AVAILABLE = True
except ImportError:
    THEME_SERVICE_AVAILABLE = False
    class ThemeService: pass
    def get_theme_service():
        raise HTTPException(status_code=501, detail="Theme service is not available.")

try:
    from services.supabase_storage_service import SupabaseStorageService, get_storage_service
    STORAGE_SERVICE_AVAILABLE = True
except ImportError:
    STORAGE_SERVICE_AVAILABLE = False
    class SupabaseStorageService: pass
    def get_storage_service():
        raise HTTPException(status_code=501, detail="Storage service is not available.")
        
try:
    from services.youtube_service import youtube_service
    YOUTUBE_SERVICE_AVAILABLE = True
except ImportError:
    YOUTUBE_SERVICE_AVAILABLE = False

try:
    from services.facebook_service import facebook_service
    FACEBOOK_SERVICE_AVAILABLE = True
except ImportError:
    FACEBOOK_SERVICE_AVAILABLE = False

try:
    from services.instagram_service import instagram_service
    INSTAGRAM_SERVICE_AVAILABLE = True
except ImportError:
    INSTAGRAM_SERVICE_AVAILABLE = False

try:
    from services.tiktok_service import tiktok_service
    TIKTOK_SERVICE_AVAILABLE = True
except ImportError:
    TIKTOK_SERVICE_AVAILABLE = False

try:
    from social_media_marketing_automation import SocialMediaMarketingEngine, get_social_media_engine
    AUTOMATION_ENGINE_AVAILABLE = True
except ImportError as e:
    AUTOMATION_ENGINE_AVAILABLE = False
    logging.error(f"Failed to import SocialMediaMarketingEngine: {e}", exc_info=True)
    class SocialMediaMarketingEngine:
        pass
    def get_social_media_engine():
        raise HTTPException(status_code=501, detail="The Social Media Automation Engine is not available.")


logger = logging.getLogger(__name__)
social_marketing_router = APIRouter(
    prefix="/api/admin/social-marketing",
    tags=["Social Media Marketing", "Admin"]
)

AVAILABLE_AVATAR_STYLES = ["traditional", "modern", "default"]
MAX_FILE_SIZE = 5 * 1024 * 1024
ALLOWED_MIME_TYPES = ["image/jpeg", "image/png", "image/webp"]
MIME_TYPE_TO_EXTENSION = {
    "image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"
}

@social_marketing_router.get("/overview", response_model=StandardResponse)
async def get_marketing_overview(admin_user: dict = Depends(AuthenticationHelper.verify_admin_access_strict)):
    overview_data = MarketingOverview(
        total_campaigns=10, active_campaigns=3, total_posts=150, total_engagement=12500, reach=75000
    )
    return StandardResponse(success=True, data=overview_data, message="Marketing overview retrieved successfully.")

@social_marketing_router.get("/content-calendar", response_model=StandardResponse)
async def get_content_calendar(
    date: Optional[str] = None, platform: Optional[str] = None,
    admin_user: dict = Depends(AuthenticationHelper.verify_admin_access_strict)
):
    all_calendar_data = [
        ContentCalendarItem(id=1, date="2024-08-15", platform="Facebook", content="Satsang announcement", status=ContentStatus.POSTED),
        ContentCalendarItem(id=2, date="2024-08-16", platform="Twitter", content="Daily wisdom quote", status=ContentStatus.SCHEDULED),
    ]
    filtered_data = all_calendar_data
    if platform:
        filtered_data = [item for item in filtered_data if item.platform.lower() == platform.lower()]
    if date:
        filtered_data = [item for item in filtered_data if str(item.date).startswith(date)]
    return StandardResponse(success=True, data={"calendar": filtered_data}, message=f"Content calendar retrieved successfully.")

@social_marketing_router.get("/campaigns", response_model=StandardResponse)
async def get_campaigns(
    status: Optional[str] = None, platform: Optional[str] = None,
    admin_user: dict = Depends(AuthenticationHelper.verify_admin_access_strict)
):
    today = datetime.now().date()
    all_campaigns = [
        Campaign(id=1, name="Diwali Special Satsang", platform="YouTube", status=CampaignStatus.ACTIVE, start_date=today - timedelta(days=10), end_date=today + timedelta(days=20)),
        Campaign(id=2, name="Summer Wisdom Series", platform="Facebook", status=CampaignStatus.COMPLETED, start_date=today - timedelta(days=90), end_date=today - timedelta(days=60)),
    ]
    filtered_campaigns = all_campaigns
    if status:
        filtered_campaigns = [campaign for campaign in filtered_campaigns if campaign.status.value.lower() == status.lower()]
    if platform:
        filtered_campaigns = [campaign for campaign in filtered_campaigns if campaign.platform.lower() == platform.lower()]
    return StandardResponse(success=True, data={"campaigns": filtered_campaigns}, message=f"Campaigns retrieved successfully.")

@social_marketing_router.get("/platform-config", response_model=StandardResponse)
async def get_platform_config(
    admin_user: dict = Depends(AuthenticationHelper.verify_admin_access_strict),
    conn: asyncpg.Connection = Depends(db.get_db)
):
    try:
        rows = await conn.fetch("SELECT key, value FROM platform_settings WHERE key LIKE '%\\_config' ESCAPE '\\'")
        config_data = {}
        platform_models = {'youtube': YouTubePlatformStatus, 'facebook': FacebookPlatformStatus, 'instagram': InstagramPlatformStatus, 'tiktok': TikTokPlatformStatus}
        for row in rows:
            key, value = row['key'], row['value']
            if key.endswith('_config'):
                platform_name = key[:-7]
                model = platform_models.get(platform_name, BasePlatformStatus)
                config_data[platform_name] = model(**json.loads(value))
        final_config = PlatformConfig(**config_data)
        return StandardResponse(success=True, data=final_config, message="Platform configuration retrieved successfully.")
    except Exception as e:
        logger.error(f"Failed to retrieve platform configuration: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve platform configuration.")

@social_marketing_router.patch("/platform-config", response_model=StandardResponse)
async def save_platform_config(
    config_update: PlatformConfigUpdate, admin_user: dict = Depends(AuthenticationHelper.verify_admin_access_strict),
    conn: asyncpg.Connection = Depends(db.get_db)
):
    try:
        update_data = config_update.dict(exclude_unset=True)
        if not update_data:
            raise HTTPException(status_code=400, detail="No configuration data provided.")
        async with conn.transaction():
            for platform, status in update_data.items():
                if isinstance(status, dict):
                    key, value = f"{platform}_config", json.dumps(status)
                    await conn.execute("INSERT INTO platform_settings (key, value) VALUES ($1, $2) ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, updated_at = NOW()", key, value)
        return StandardResponse(success=True, message="Configuration saved successfully.")
    except Exception as e:
        logger.error(f"Failed to save platform configuration: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

@social_marketing_router.get("/swamiji-avatar-config", response_model=StandardResponse)
async def get_swamiji_avatar_config(
    admin_user: dict = Depends(AuthenticationHelper.verify_admin_access_strict), conn: asyncpg.Connection = Depends(db.get_db),
    avatar_engine: SpiritualAvatarGenerationEngine = Depends(get_avatar_engine)
):
    available_voices = await avatar_engine.get_available_voices()
    config_data = {"voices": available_voices, "styles": AVAILABLE_AVATAR_STYLES, "default_text": "Greetings from the digital ashram."}
    try:
        record = await conn.fetchrow("SELECT value FROM platform_settings WHERE key = 'swamiji_avatar_url'")
        if record and record['value']:
            try:
                config_data["image_url"] = json.loads(record['value'])
            except json.JSONDecodeError:
                config_data["image_url"] = record['value']
    except Exception as e:
        logger.error(f"Failed to fetch Swamiji avatar URL: {e}", exc_info=True)
    return StandardResponse(success=True, data=config_data, message="Avatar configuration retrieved.")

@social_marketing_router.post("/upload-swamiji-image", response_model=StandardResponse)
async def upload_swamiji_image(
    image: UploadFile = File(...), admin_user: dict = Depends(AuthenticationHelper.verify_admin_access_strict),
    storage_service: SupabaseStorageService = Depends(get_storage_service), conn: asyncpg.Connection = Depends(db.get_db)
):
    if image.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=400, detail="Invalid file type.")
    contents = await image.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File size exceeds limit.")
    
    file_extension = MIME_TYPE_TO_EXTENSION.get(image.content_type, '.png')
    file_name_in_bucket = f"public/swamiji_base_avatar{file_extension}"
    try:
        public_url = storage_service.upload_file(bucket_name="avatars", file_path_in_bucket=file_name_in_bucket, file=contents, content_type=image.content_type)
        await conn.execute("INSERT INTO platform_settings (key, value) VALUES ('swamiji_avatar_url', $1) ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, updated_at = NOW()", json.dumps(public_url))
        return StandardResponse(success=True, message="Image uploaded successfully.", data={"image_url": public_url})
    except Exception as e:
        logger.error(f"Swamiji image upload failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to save uploaded file: {e}")

@social_marketing_router.post("/upload-preview-image", response_model=StandardResponse)
async def upload_preview_image(
    image: UploadFile = File(...),
    admin_user: dict = Depends(AuthenticationHelper.verify_admin_access_strict),
    storage_service: SupabaseStorageService = Depends(get_storage_service)
):
    """
    Uploads a generated preview image to storage and returns the public URL.
    This is used by the frontend to get a stable URL for a generated preview.
    """
    if image.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=400, detail="Invalid file type for preview.")
    
    contents = await image.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="Preview file size exceeds limit.")

    try:
        import uuid
        unique_filename = f"preview_{uuid.uuid4()}.png"
        file_path_in_bucket = f"previews/{unique_filename}"
        
        public_url = storage_service.upload_file(
            bucket_name="avatars",
            file_path_in_bucket=file_path_in_bucket,
            file=contents,
            content_type="image/png"
        )
        
        logger.info(f"✅ Successfully uploaded preview image to {public_url}")
        return StandardResponse(success=True, data={"image_url": public_url}, message="Preview image uploaded successfully.")
        
    except Exception as e:
        logger.error(f"Failed to upload preview image: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to upload preview image.")


class ImagePreviewRequest(BaseModel):
    custom_prompt: Optional[str] = Field(None, description="A custom prompt to override the daily theme.")
    theme_day: Optional[int] = Field(None, description="Override daily theme with specific day (0=Monday, 1=Tuesday, ..., 6=Sunday). If None, uses current day.")
    strength_param: float = Field(0.4, ge=0.0, le=1.0, description="Transformation strength (0.0-1.0). Default 0.4 (safe). Higher values enable aggressive testing controlled by feature flags.")

async def get_admin_or_test_bypass(request: Request):
    """
    🔒 SECURE ADMIN AUTHENTICATION WITH CONTROLLED TESTING BYPASS
    
    Production: Full admin authentication enforced (secure)
    Development/Testing: TESTING_MODE=true enables bypass with validation
    
    ⚠️  DEPLOYMENT WARNING: Remove TESTING_MODE from production environment!
    🔍 Security logging: All bypass usage is logged for audit trails
    """
    testing_mode = os.getenv("TESTING_MODE", "").lower()
    environment = os.getenv("ENVIRONMENT", "production").lower()
    
    # Environment validation - only allow bypass in non-production environments
    if testing_mode == "true":
        # Security check: Prevent bypass in production environment
        if environment in ["production", "prod"]:
            logger.warning(
                "🚨 SECURITY ALERT: TESTING_MODE bypass attempted in production environment. "
                "Falling back to full authentication. Remove TESTING_MODE from production!"
            )
        else:
            # Log bypass usage for security audit trail
            logger.warning(
                f"🔓 AUTH BYPASS ACTIVATED: Using TESTING_MODE in {environment} environment. "
                f"This should NEVER happen in production. Timestamp: {datetime.now()}"
            )
            return {"email": "test@admin.com", "role": "admin", "id": 1, "bypass_used": True}
    
    # Default: Full admin authentication (production-safe)
    return AuthenticationHelper.verify_admin_access_strict(request)

@social_marketing_router.post("/generate-image-preview")
async def generate_image_preview(
    request: ImagePreviewRequest, 
    admin_user: dict = Depends(get_admin_or_test_bypass),  # Secure + testable
    theme_service: ThemeService = Depends(get_theme_service),
):
    try:
        # The service now returns the generated image, the prompt, and the base image bytes
        image_bytes, final_prompt, base_image_bytes = await theme_service.generate_themed_image_bytes(
            custom_prompt=request.custom_prompt, 
            theme_day=request.theme_day
        )
        
        # Compute hash of generated image
        generated_hash_full = hashlib.sha256(image_bytes).hexdigest()
        generated_hash_short = generated_hash_full[:16]

        # EFFICIENCY FIX: No need to download the base image again.
        # Compute its hash from the bytes returned by the service.
        image_diff = "unknown"
        base_hash_short = ""
        if base_image_bytes:
            try:
                base_hash_full = hashlib.sha256(base_image_bytes).hexdigest()
                base_hash_short = base_hash_full[:16]
                image_diff = "different" if generated_hash_full != base_hash_full else "same"
                logger.info(f"Image diff check successful. Base hash: {base_hash_short}, Generated hash: {generated_hash_short}")
            except Exception as diff_err:
                logger.warning(f"Could not compute base image hash for diff check: {diff_err}")
        
        # 🛡️ ENHANCED HTTP header sanitization - CORE.MD: Fix emoji encoding errors
        # 1. Handle None/non-string values defensively
        if final_prompt is None or not isinstance(final_prompt, str):
            clean_prompt = "Generated image preview"
        else:
            # 2. Remove ALL HTTP-invalid characters including emojis and Unicode
            # This prevents latin-1 encoding errors: 'latin-1 codec can't encode character'
            import re
            # Remove control characters (0x00–0x1F and 0x7F)
            clean_prompt = re.sub(r'[\x00-\x1F\x7F]', ' ', final_prompt)
            # Remove emoji and non-ASCII Unicode characters that cause encoding errors
            clean_prompt = re.sub(r'[^\x20-\x7E]', ' ', clean_prompt)  # Keep only printable ASCII
            # 3. Normalize whitespace and trim to valid length
            clean_prompt = ' '.join(clean_prompt.split()).strip()[:500]
            # 4. Fallback if cleaning resulted in empty string
            if not clean_prompt:
                clean_prompt = "Generated image preview"
        
        headers = {
            "X-Generated-Prompt": clean_prompt,
            "X-Image-Diff": image_diff,
            "X-Generated-Hash": generated_hash_short,
            **({"X-Base-Hash": base_hash_short} if base_hash_short else {}),
            # Expose custom headers to browser
            "Access-Control-Expose-Headers": "X-Generated-Prompt, X-Image-Diff, X-Generated-Hash, X-Base-Hash",
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
        }
        return Response(content=image_bytes, media_type="image/png", headers=headers)
    except ValueError as e:
        # CORE.MD & REFRESH.MD: Handle validation errors with HTTP 400 (Bad Request)
        logger.warning(f"⚠️  VALIDATION ERROR in image preview generation: {e}")
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.error(f"Image preview generation failed: {e}", exc_info=True)
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail=f"Error generating image preview: {e}") from e

class VideoFromPreviewRequest(BaseModel):
    image_url: str
    sample_text: str
    voice_id: str

@social_marketing_router.post("/generate-video-from-preview", response_model=StandardResponse)
async def generate_video_from_preview(
    request: VideoFromPreviewRequest, admin_user: dict = Depends(AuthenticationHelper.verify_admin_access_strict),
    avatar_engine: SpiritualAvatarGenerationEngine = Depends(get_avatar_engine)
):
    try:
        result = await avatar_engine.generate_avatar_preview_lightweight(
            guidance_text=request.sample_text, voice_id=request.voice_id, source_image_url=request.image_url
        )
        if result.get("success"):
            return StandardResponse(success=True, message="Avatar video generated successfully.", data=result)
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Failed to generate video."))
    except Exception as e:
        logger.error(f"Video generation from preview failed: {e}", exc_info=True)
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail=f"Error generating video from preview: {e}") from e

@social_marketing_router.post("/generate-daily-content", response_model=StandardResponse)
async def generate_daily_content(
    admin_user: dict = Depends(AuthenticationHelper.verify_admin_access_strict),
    social_engine: SocialMediaMarketingEngine = Depends(get_social_media_engine),
    conn = Depends(db.get_db)
):
    try:
        daily_plan = await social_engine.generate_daily_content_plan()
        await social_engine._store_content_plan_in_db(daily_plan, conn)
        summary = {p: f"{len(posts)} posts planned" for p, posts in daily_plan.items()}
        serializable_plan = {p: [post.dict() for post in posts] for p, posts in daily_plan.items()}
        return StandardResponse(success=True, message="Daily content plan generated.", data={"plan_summary": summary, "full_plan": serializable_plan})
    except Exception as e:
        logger.error(f"Error in daily content generation endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate daily content plan: {e}")
