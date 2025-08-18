"""
🚀 SOCIAL MEDIA MARKETING API ROUTER

Complete and robust API for all social media marketing operations.
This file follows CORE.MD and REFRESH.MD principles for quality and maintainability.
# Trigger Render build to reinstall dependencies
"""

import logging
import os
from typing import Optional, AsyncGenerator, Callable, TypeVar, Any
import hashlib
import httpx
import uuid
import json
from datetime import datetime, timedelta, date
import asyncio
import base64 # Added for base64 encoding of image bytes
import binascii # Added for base64 decoding errors
import inspect

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Response, Request
from fastapi.dependencies.utils import get_dependant, solve_dependencies
from pydantic import BaseModel, Field
import asyncpg

from auth.auth_helpers import AuthenticationHelper
from db import get_db
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
except ImportError as e:
    # Log the detailed import error to help debug platform-specific issues
    logging.error(f"Failed to import SpiritualAvatarGenerationEngine: {e}", exc_info=True)
    AVATAR_ENGINE_AVAILABLE = False
    class SpiritualAvatarGenerationEngine: pass
    def get_avatar_engine():
        raise HTTPException(status_code=501, detail="Avatar Generation Engine is not available.")

from services.theme_service import ThemeService, get_theme_service

try:
    from services.supabase_storage_service import SupabaseStorageService, get_storage_service
    STORAGE_SERVICE_AVAILABLE = True
except ImportError as e:
    # Log the detailed import error for the same reason
    logging.error(f"Failed to import SupabaseStorageService: {e}", exc_info=True)
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

# This old theme system is now deprecated and handled by the frontend.
# try:
#     from config.social_media_config import THEMES
#     THEMES_AVAILABLE = True
# except ImportError:
#     THEMES_AVAILABLE = False


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

# Helper function to store calendar content in database
async def _store_calendar_content_in_db(calendar_items: list) -> None:
    """Store generated calendar content in database for persistence and analytics"""
    try:
        from db import get_db_pool
        db_pool = get_db_pool()
        
        if not db_pool:
            logger.warning("Database pool not available, skipping content storage")
            return
        
        async with db_pool.acquire() as conn:
            for item in calendar_items:
                try:
                    # Store in social_content table
                    await conn.execute("""
                        INSERT INTO social_content 
                        (platform, content_type, content_text, status, scheduled_at, created_at, metadata)
                        VALUES ($1, $2, $3, $4, $5, NOW(), $6)
                        ON CONFLICT (platform, content_text) DO UPDATE SET
                        updated_at = NOW(), status = $4
                    """, 
                    item.platform,
                    item.content_type or "daily_wisdom", 
                    item.content,
                    item.status,
                    item.scheduled_time,
                    json.dumps({
                        "hashtags": item.hashtags,
                        "source": "rag_generated",
                        "theme_based": True
                    })
                    )
                except Exception as e:
                    logger.error(f"Failed to store individual content item: {e}")
                    continue
                    
        logger.info(f"Successfully stored {len(calendar_items)} calendar items in database")
        
    except Exception as e:
        logger.error(f"Database storage error: {e}", exc_info=True)
        raise

# Helper function to resolve FastAPI dependencies manually
async def _resolve_dependency_via_fastapi(request: Request, call: Callable) -> Any:
    """
    Resolves FastAPI dependencies manually for a given callable.
    Used when we need to call dependency-injected functions outside of FastAPI context.
    """
    try:
        # Get the dependency information
        dependant = get_dependant(path="", call=call)
        
        # Solve the dependencies
        values, errors, _, _, _ = await solve_dependencies(
            request=request,
            dependant=dependant
        )
        
        if errors:
            error_details = [str(error) for error in errors]
            raise HTTPException(
                status_code=500, 
                detail=f"Dependency resolution failed: {', '.join(error_details)}"
            )
        
        # Call the function with resolved dependencies
        result = call(**values)
        
        # Await if it's a coroutine
        if inspect.iscoroutine(result):
            result = await result
            
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resolving dependency for {call.__name__}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to resolve dependency: {str(e)}"
        )

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
    request: Request,
    date: Optional[str] = None, platform: Optional[str] = None,
    admin_user: dict = Depends(AuthenticationHelper.verify_admin_access_strict)
):
    # Check if automation engine is available
    if not AUTOMATION_ENGINE_AVAILABLE:
        logger.warning("Social Media Automation Engine not available, using enhanced fallback data")
        # Enhanced fallback data with spiritual themes
        try:
            from services.spiritual_calendar_service import SpiritualCalendarService
            calendar_service = SpiritualCalendarService()
            daily_theme = await calendar_service.get_daily_spiritual_theme()
            theme_name = daily_theme.get('theme', 'Spiritual Guidance')
            theme_description = daily_theme.get('description', 'Daily spiritual wisdom')
        except Exception:
            theme_name = "Spiritual Guidance"
            theme_description = "Daily spiritual wisdom"
        
        # Generate enhanced fallback content
        platforms = ["Facebook", "Instagram", "Twitter", "YouTube", "TikTok"]
        calendar_items = []
        
        for i, platform_name in enumerate(platforms):
            calendar_item = ContentCalendarItem(
                id=i + 1,
                date=datetime.now().date(),
                platform=platform_name,
                content=f"{theme_name}: {theme_description[:80]}...",
                status=ContentStatus.DRAFT,
                content_type="daily_wisdom",
                hashtags=[f"#{theme_name.replace(' ', '').lower()}", "#jyotiflow", "#spirituality"],
                scheduled_time=None
            )
            calendar_items.append(calendar_item)
        
        # Apply filters
        filtered_data = calendar_items
        if platform:
            filtered_data = [item for item in filtered_data if item.platform.lower() == platform.lower()]
        if date:
            filtered_data = [item for item in filtered_data if str(item.date).startswith(date)]
        
        # Store content in database for persistence
        try:
            await _store_calendar_content_in_db(filtered_data)
            storage_message = " Content stored in database."
        except Exception as e:
            logger.error(f"Failed to store calendar content: {e}")
            storage_message = " (Storage failed)"
        
        return StandardResponse(
            success=True, 
            data={"calendar": filtered_data}, 
            message=f"Content calendar retrieved with enhanced fallback data ({len(filtered_data)} items).{storage_message}"
        )
    
    try:
        # Get marketing engine instance via dependency resolution
        marketing_engine = await _resolve_dependency_via_fastapi(request, get_social_media_engine)
        
        # Generate daily content plan using the marketing engine
        daily_plan = await marketing_engine.generate_daily_content_plan()
        
        # Convert content plans to calendar items
        calendar_items = []
        item_id = 1
        
        for platform_name, content_plans in daily_plan.items():
            for plan in content_plans:
                # Determine status and date based on scheduled_time
                scheduled_time = plan.scheduled_time if hasattr(plan, 'scheduled_time') else None
                if scheduled_time:
                    status = ContentStatus.SCHEDULED
                    item_date = scheduled_time.date()
                else:
                    status = ContentStatus.DRAFT
                    item_date = datetime.now().date()
                
                calendar_item = ContentCalendarItem(
                    id=item_id,
                    date=item_date,
                    platform=platform_name.title(),
                    content=f"{plan.title}: {plan.description[:100]}..." if len(plan.description) > 100 else f"{plan.title}: {plan.description}",
                    status=status,
                    content_type=plan.content_type if hasattr(plan, 'content_type') else None,
                    hashtags=plan.hashtags if hasattr(plan, 'hashtags') else None,
                    scheduled_time=scheduled_time
                )
                calendar_items.append(calendar_item)
                item_id += 1
        
        # Apply filters
        filtered_data = calendar_items
        if platform:
            filtered_data = [item for item in filtered_data if item.platform.lower() == platform.lower()]
        if date:
            filtered_data = [item for item in filtered_data if str(item.date).startswith(date)]
        
        # Store content in database for persistence
        try:
            await _store_calendar_content_in_db(filtered_data)
            storage_message = " Content stored in database."
        except Exception as e:
            logger.error(f"Failed to store calendar content: {e}")
            storage_message = " (Storage failed)"
        
        return StandardResponse(
            success=True, 
            data={"calendar": filtered_data}, 
            message=f"Content calendar retrieved successfully with {len(filtered_data)} items.{storage_message}"
        )
        
    except Exception as e:
        logger.error(f"Error generating content calendar: {e}", exc_info=True)
        # Final fallback to basic mock data
        fallback_data = [
            ContentCalendarItem(id=1, date=datetime.now().date(), platform="Facebook", content="Daily spiritual wisdom", status=ContentStatus.DRAFT),
            ContentCalendarItem(id=2, date=datetime.now().date(), platform="Instagram", content="Mindfulness quote", status=ContentStatus.DRAFT),
        ]
        return StandardResponse(success=True, data={"calendar": fallback_data}, message="Content calendar retrieved with basic fallback data.")

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
    conn: asyncpg.Connection = Depends(get_db)
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
    conn: asyncpg.Connection = Depends(get_db)
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
    admin_user: dict = Depends(AuthenticationHelper.verify_admin_access_strict), conn: asyncpg.Connection = Depends(get_db),
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
    storage_service: SupabaseStorageService = Depends(get_storage_service), conn: asyncpg.Connection = Depends(get_db)
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

class UploadPreviewRequest(BaseModel):
    image_base64: str
    filename: str

@social_marketing_router.post("/upload-preview-image", response_model=StandardResponse)
async def upload_preview_image(
    request: UploadPreviewRequest,
    admin_user: dict = Depends(AuthenticationHelper.verify_admin_access_strict),
    storage_service: SupabaseStorageService = Depends(get_storage_service)
):
    """
    Uploads a Base64 encoded preview image to storage and returns the public URL.
    Handles potential double-encoding and validates payload.
    """
    try:
        # Pre-flight size check to prevent decoding massive payloads
        # Estimate decoded size: floor(len(s) * 3 / 4) - padding
        padding = request.image_base64.count('=')
        decoded_size_estimate = (len(request.image_base64) * 3 // 4) - padding
        if decoded_size_estimate > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="Estimated payload size exceeds limit.")

        image_data = None
        try:
            image_data = base64.b64decode(request.image_base64, validate=True)
        except (ValueError, binascii.Error):
            raise HTTPException(status_code=400, detail="Invalid base64 payload.")

        # Detect and handle common double-encoding case (result is still base64 text)
        try:
            if image_data.isascii() and all(c in b'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=' for c in image_data):
                logger.warning("Potential double-encoding detected. Attempting second decode.")
                image_data = base64.b64decode(image_data, validate=True)
        except (ValueError, binascii.Error):
            raise HTTPException(status_code=400, detail="Invalid double-encoded base64 payload.")
        
        if len(image_data) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="Final payload size exceeds limit.")

        unique_filename = f"preview_{uuid.uuid4()}.png"
        file_path_in_bucket = f"previews/{unique_filename}"
        
        public_url = storage_service.upload_file(
            bucket_name="avatars",
            file_path_in_bucket=file_path_in_bucket,
            file=image_data,
            content_type="image/png"  # We know it's PNG from our conversion
        )
        
        logger.info(f"✅ Successfully uploaded preview image to {public_url}")
        return StandardResponse(success=True, data={"image_url": public_url}, message="Preview image uploaded successfully.")
        
    except Exception as e:
        logger.error(f"Failed to upload preview image: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to upload preview image.")


class ImagePreviewRequest(BaseModel):
    custom_prompt: str = Field(..., description="The theme prompt for image generation.")
    target_platform: Optional[str] = Field(None, description="Target platform for aspect ratio (e.g., 'instagram_story', 'facebook_post').")

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
    conn: asyncpg.Connection = Depends(get_db)
):
    try:
        # 1. Get the theme prompt directly from the request
        theme_prompt = request.custom_prompt
        if not theme_prompt:
            raise HTTPException(status_code=400, detail="A theme prompt is required.")

        # 2. Get the reference avatar URL from database
        record = await conn.fetchrow("SELECT value FROM platform_settings WHERE key = 'swamiji_avatar_url'")
        if not record or not record['value']:
            raise HTTPException(status_code=404, detail="Master Swamiji avatar URL not found in settings. Please set a master avatar first.")
        
        reference_avatar_url = json.loads(record['value'])

        # 3. Call the new, simplified theme service
        image_bytes, mime_type = await theme_service.generate_themed_image_bytes(
            theme_prompt=theme_prompt, 
            reference_avatar_url=reference_avatar_url,
            target_platform=request.target_platform
        )
        
        if not image_bytes:
            raise HTTPException(status_code=500, detail="Failed to generate image from the theme service.")

        # 4. Compute hash and prepare response (adapted from existing logic)
        generated_hash_full = hashlib.sha256(image_bytes).hexdigest()
        generated_hash_short = generated_hash_full[:16]
        image_diff = "unknown"
        base_hash_short = None

        # try:
        #     base_image_bytes = await get_storage_service().download_public_file_bytes("avatars", "public/swamiji_base_avatar.png")
        #     if base_image_bytes:
        #         base_hash_full = hashlib.sha256(base_image_bytes).hexdigest()
        #         base_hash_short = base_hash_full[:16]
        #         image_diff = "different" if generated_hash_full != base_hash_full else "same"
        #         logger.info(f"Image diff check successful. Base hash: {base_hash_short}, Generated hash: {generated_hash_short}")
        # except Exception as diff_err:
        #     logger.warning(f"Could not compute base image hash for diff check: {diff_err}")

        encoded_image = base64.b64encode(image_bytes).decode("utf-8")
        
        import re
        clean_prompt = re.sub(r'[^\x20-\x7E]', ' ', theme_prompt)
        clean_prompt = ' '.join(clean_prompt.split()).strip()[:500]
        if not clean_prompt:
            clean_prompt = "Generated image preview"
        
        headers = {
            "X-Generated-Prompt": clean_prompt,
            "X-Image-Diff": image_diff,
            "X-Generated-Hash": generated_hash_short,
            **({"X-Base-Hash": base_hash_short} if base_hash_short else {}),
            "Access-Control-Expose-Headers": "X-Generated-Prompt, X-Image-Diff, X-Generated-Hash, X-Base-Hash",
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
        }
        return Response(content=encoded_image, media_type=mime_type, headers=headers)
    except ValueError as e:
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
    conn: asyncpg.Connection = Depends(get_db)
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
