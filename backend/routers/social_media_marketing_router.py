"""
🚀 SOCIAL MEDIA MARKETING API ROUTER

Complete and robust API for all social media marketing operations.
This file follows CORE.MD and REFRESH.MD principles for quality and maintainability.
"""

import logging
from pathlib import Path
import shutil
from typing import Optional, AsyncGenerator
import json
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel, Field
import asyncpg

# CORE.MD: All necessary dependencies are explicitly imported using absolute paths from the backend root.
from auth.auth_helpers import AuthenticationHelper
import db
from schemas.response import StandardResponse
from schemas.social_media import (
    Campaign,
    ContentCalendarItem,
    GenerateAllAvatarPreviewsRequest,
    # REFRESH.MD: GenerateAvatarPreviewRequest is no longer needed as the style is dynamic.
    MarketingAsset,
    MarketingAssetCreate,
    MarketingOverview,
    PlatformConfig,
    PlatformConfigUpdate,
    TestConnectionRequest,
    PostExecutionRequest,
    PostExecutionResult,
    CampaignStatus,
    ContentStatus,
    YouTubePlatformStatus,
    FacebookPlatformStatus,
    InstagramPlatformStatus,
    TikTokPlatformStatus,
    BasePlatformStatus,
)
# REFRESH.MD: Use direct imports from the root of the 'backend' package for Render compatibility.
try:
    from spiritual_avatar_generation_engine import SpiritualAvatarGenerationEngine, get_avatar_engine
    AVATAR_ENGINE_AVAILABLE = True
except ImportError:
    AVATAR_ENGINE_AVAILABLE = False
    # CORE.MD: Define stubs for graceful dependency injection failure.
    class SpiritualAvatarGenerationEngine:
        pass  # Empty class definition

    def get_avatar_engine():
        raise HTTPException(status_code=501, detail="Avatar Generation Engine is not available due to missing dependencies.")


# REFRESH.MD: Use try-except blocks for service imports to prevent router import failures.
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

# REFRESH.MD: Use direct imports from the root of the 'backend' package for Render compatibility.
try:
    from social_media_marketing_automation import SocialMediaMarketingEngine, get_social_media_engine
    AUTOMATION_ENGINE_AVAILABLE = True
except ImportError as e:
    AUTOMATION_ENGINE_AVAILABLE = False
    # Log the import error for easier debugging
    logging.error(f"Failed to import SocialMediaMarketingEngine: {e}", exc_info=True)
    # Define a stub for graceful failure
    class SocialMediaMarketingEngine:
        pass
    def get_social_media_engine():
        raise HTTPException(status_code=501, detail="The Social Media Automation Engine is not available.")

# REFRESH.MD: Wrap Supabase service import in a try-except block for robustness.
try:
    from services.supabase_storage_service import SupabaseStorageService, get_storage_service
    STORAGE_SERVICE_AVAILABLE = True
except ImportError:
    STORAGE_SERVICE_AVAILABLE = False
    class SupabaseStorageService: pass
    def get_storage_service():
        raise HTTPException(status_code=501, detail="Storage service is not available.")

# REFRESH.MD: Import the new ThemeService for dynamic avatar generation.
try:
    from services.theme_service import ThemeService, get_theme_service
    THEME_SERVICE_AVAILABLE = True
except ImportError:
    THEME_SERVICE_AVAILABLE = False
    class ThemeService: pass
    # CORE.MD: Define a fallback dependency to prevent NameError if the import fails.
    def get_theme_service():
        raise HTTPException(status_code=501, detail="Theme service is not available.")
    
# CORE.MD: Import the new StabilityAiService for dynamic avatar generation.
try:
    from services.stability_ai_service import StabilityAiService, get_stability_service
    STABILITY_SERVICE_AVAILABLE = True
except ImportError:
    STABILITY_SERVICE_AVAILABLE = False
    class StabilityAiService: pass
    # CORE.MD: Define a fallback async generator to match the real dependency's signature.
    async def get_stability_service() -> AsyncGenerator[None, None]:
        """Fallback if StabilityAiService is not available."""
        raise HTTPException(status_code=501, detail="Stability AI service is not available.")
        yield # This makes it a generator, though it's unreachable.
    
# This import is no longer needed as frontend now sends the voice_id
# from spiritual_avatar_generation_engine import DEFAULT_VOICE_ID


# Initialize logger and router
logger = logging.getLogger(__name__)
social_marketing_router = APIRouter(
    prefix="/api/admin/social-marketing",
    tags=["Social Media Marketing", "Admin"]
)

# REFRESH.MD: Centralize available styles to avoid magic strings and promote maintainability.
AVAILABLE_AVATAR_STYLES = ["traditional", "modern", "default"]

# CORE.MD: Define security constants for file uploads
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
ALLOWED_MIME_TYPES = ["image/jpeg", "image/png", "image/webp"]
MIME_TYPE_TO_EXTENSION = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}


# --- Marketing Overview Endpoints (using placeholder data) ---

@social_marketing_router.get("/overview", response_model=StandardResponse)
async def get_marketing_overview(admin_user: dict = Depends(AuthenticationHelper.verify_admin_access_strict)):
    overview_data = MarketingOverview(
        total_campaigns=10, active_campaigns=3, total_posts=150, total_engagement=12500, reach=75000
    )
    return StandardResponse(success=True, data=overview_data, message="Marketing overview retrieved successfully.")

@social_marketing_router.get("/content-calendar", response_model=StandardResponse)
async def get_content_calendar(
    date: Optional[str] = None,
    platform: Optional[str] = None,
    admin_user: dict = Depends(AuthenticationHelper.verify_admin_access_strict)
):
    """Get content calendar with optional date and platform filtering"""
    # Base calendar data
    all_calendar_data = [
        ContentCalendarItem(id=1, date="2024-08-15", platform="Facebook", content="Satsang announcement", status=ContentStatus.POSTED),
        ContentCalendarItem(id=2, date="2024-08-16", platform="Twitter", content="Daily wisdom quote", status=ContentStatus.SCHEDULED),
        ContentCalendarItem(id=3, date="2024-08-15", platform="Instagram", content="Meditation session", status=ContentStatus.POSTED),
        ContentCalendarItem(id=4, date="2024-08-17", platform="Facebook", content="Weekly blessing", status=ContentStatus.SCHEDULED),
    ]
    
    # Apply filters following CORE.MD principles - explicit filter handling
    filtered_data = all_calendar_data
    
    # Filter by platform if specified
    if platform:
        filtered_data = [item for item in filtered_data if item.platform.lower() == platform.lower()]
        logger.info(f"Filtered calendar by platform: {platform}, found {len(filtered_data)} items")
    
    # Filter by date if specified (matches date part only)
    if date:
        # REFRESH.MD: Ensure date filtering is robust.
        # This implementation correctly handles string-based date matching.
        filtered_data = [item for item in filtered_data if str(item.date).startswith(date)]
        logger.info(f"Filtered calendar by date: {date}, found {len(filtered_data)} items")
    
    return StandardResponse(
        success=True, 
        data={"calendar": filtered_data}, 
        message=f"Content calendar retrieved successfully. {len(filtered_data)} items found."
    )

@social_marketing_router.get("/campaigns", response_model=StandardResponse)
async def get_campaigns(
    status: Optional[str] = None,
    platform: Optional[str] = None,
    admin_user: dict = Depends(AuthenticationHelper.verify_admin_access_strict)
):
    """Get campaigns with optional status and platform filtering"""
    # Base campaign data with more examples for proper filtering demonstration
    # REFRESH.MD: Using dynamic, future-proof dates to ensure deterministic behavior.
    today = datetime.now().date()
    all_campaigns = [
        Campaign(id=1, name="Diwali Special Satsang", platform="YouTube", status=CampaignStatus.ACTIVE, start_date=today - timedelta(days=10), end_date=today + timedelta(days=20)),
        Campaign(id=2, name="Summer Wisdom Series", platform="Facebook", status=CampaignStatus.COMPLETED, start_date=today - timedelta(days=90), end_date=today - timedelta(days=60)),
        Campaign(id=3, name="Meditation Mondays", platform="Instagram", status=CampaignStatus.ACTIVE, start_date=today, end_date=today + timedelta(days=150)),
        Campaign(id=4, name="Spiritual Stories", platform="YouTube", status=CampaignStatus.DRAFT, start_date=today + timedelta(days=5), end_date=today + timedelta(days=100)),
        Campaign(id=5, name="Daily Wisdom", platform="Twitter", status=CampaignStatus.ACTIVE, start_date=today - timedelta(days=365), end_date=today + timedelta(days=365)),
    ]
    
    # Apply filters following CORE.MD principles - explicit filter handling
    filtered_campaigns = all_campaigns
    
    # Filter by status if specified
    if status:
        filtered_campaigns = [campaign for campaign in filtered_campaigns if campaign.status.value.lower() == status.lower()]
        logger.info(f"Filtered campaigns by status: {status}, found {len(filtered_campaigns)} campaigns")
    
    # Filter by platform if specified
    if platform:
        filtered_campaigns = [campaign for campaign in filtered_campaigns if campaign.platform.lower() == platform.lower()]
        logger.info(f"Filtered campaigns by platform: {platform}, found {len(filtered_campaigns)} campaigns")
    
    return StandardResponse(
        success=True, 
        data={"campaigns": filtered_campaigns}, 
        message=f"Campaigns retrieved successfully. {len(filtered_campaigns)} campaigns found."
    )

# --- Platform Configuration Endpoints (using placeholder data) ---

@social_marketing_router.get("/platform-config", response_model=StandardResponse)
async def get_platform_config(
    admin_user: dict = Depends(AuthenticationHelper.verify_admin_access_strict),
    conn: asyncpg.Connection = Depends(db.get_db)
):
    """Retrieve current platform configurations from the database."""
    try:
        # REFRESH.MD: Escaped the underscore in the LIKE clause to treat it as a literal.
        rows = await conn.fetch("SELECT key, value FROM platform_settings WHERE key LIKE '%\\_config' ESCAPE '\\'")
        
        config_data = {}
        platform_models = {
            'youtube': YouTubePlatformStatus,
            'facebook': FacebookPlatformStatus,
            'instagram': InstagramPlatformStatus,
            'tiktok': TikTokPlatformStatus,
        }

        for row in rows:
            key = row['key']
            if key.endswith('_config'):
                platform_name = key[:-7]
                model = platform_models.get(platform_name, BasePlatformStatus)
                config_data[platform_name] = model(**json.loads(row['value']))

        # Ensure all platforms are present in the response, even if not in the DB
        final_config = PlatformConfig(**config_data)
        
        return StandardResponse(success=True, data=final_config, message="Platform configuration retrieved successfully.")
    except Exception as e:
        logger.error(f"Failed to retrieve platform configuration from database: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve platform configuration.")


@social_marketing_router.patch("/platform-config", response_model=StandardResponse)
async def save_platform_config(
    config_update: PlatformConfigUpdate,
    admin_user: dict = Depends(AuthenticationHelper.verify_admin_access_strict),
    conn: asyncpg.Connection = Depends(db.get_db)
):
    """Save a single platform's configuration to the database."""
    try:
        update_data = config_update.dict(exclude_unset=True)
        if not update_data:
            raise HTTPException(status_code=400, detail="No configuration data provided.")

        logger.info(f"Attempting to save platform config to database: {update_data}")
        
        async with conn.transaction():
            for platform, status in update_data.items():
                if isinstance(status, dict):
                    key = f"{platform}_config"
                    value = json.dumps(status)
                    
                    await conn.execute(
                        """
                        INSERT INTO platform_settings (key, value)
                        VALUES ($1, $2)
                        ON CONFLICT (key) DO UPDATE
                        SET value = EXCLUDED.value, updated_at = NOW()
                        """,
                        key,
                        value
                    )

        return StandardResponse(success=True, message="Configuration saved successfully.")
    except Exception as e:
        logger.error(f"Failed to save platform configuration to database: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred while saving the configuration: {e}")


@social_marketing_router.post("/test-connection", response_model=StandardResponse)
async def test_platform_connection(
    request: TestConnectionRequest,
    admin_user: dict = Depends(AuthenticationHelper.verify_admin_access_strict)
):
    logger.info(f"Testing connection for platform: {request.platform}")
    if not request.config:
        raise HTTPException(status_code=400, detail="Configuration data is missing in the request.")

    try:
        result = None
        if request.platform == "youtube":
            if not YOUTUBE_SERVICE_AVAILABLE:
                raise HTTPException(status_code=501, detail="YouTube service is not available.")
            api_key = request.config.get("api_key")
            channel_id = request.config.get("channel_id")
            if not api_key or not channel_id:
                raise HTTPException(status_code=400, detail="YouTube API key and Channel ID are required.")
            result = await youtube_service.validate_credentials(api_key, channel_id)

        elif request.platform == "facebook":
            if not FACEBOOK_SERVICE_AVAILABLE:
                raise HTTPException(status_code=501, detail="Facebook service is not available.")
            app_id = request.config.get("app_id")
            app_secret = request.config.get("app_secret")
            access_token = request.config.get("page_access_token")
            if not all([app_id, app_secret, access_token]):
                 raise HTTPException(status_code=400, detail="Facebook App ID, App Secret, and Page Access Token are required.")
            result = await facebook_service.validate_credentials(app_id, app_secret, access_token)

        elif request.platform == "instagram":
            if not INSTAGRAM_SERVICE_AVAILABLE:
                raise HTTPException(status_code=501, detail="Instagram service is not available.")
            app_id = request.config.get("app_id")
            app_secret = request.config.get("app_secret")
            access_token = request.config.get("access_token")
            if not all([app_id, app_secret, access_token]):
                raise HTTPException(status_code=400, detail="Instagram App ID, App Secret, and Access Token are required.")
            result = await instagram_service.validate_credentials(app_id, app_secret, access_token)
        
        elif request.platform == "tiktok":
            if not TIKTOK_SERVICE_AVAILABLE:
                raise HTTPException(status_code=501, detail="TikTok service is not available.")
            client_key = request.config.get("client_key")
            client_secret = request.config.get("client_secret")
            if not client_key or not client_secret:
                raise HTTPException(status_code=400, detail="TikTok Client Key and Secret are required.")
            result = await tiktok_service.validate_credentials(client_key, client_secret)

        else:
            # CORE.MD: Ensure all branches return a standardized response.
            raise HTTPException(status_code=404, detail=f"Connection testing for {request.platform} is not implemented yet.")

        # REFRESH.MD: Standardize response handling from all services.
        if result and result.get("success"):
            return StandardResponse(success=True, data=result, message=result.get("message", "Connection successful."))
        else:
            # REFRESH.MD: Uniformly handle varying error structures.
            error_detail = result.get("error", "Unknown error during validation.")
            if isinstance(error_detail, dict):
                 error_detail = error_detail.get("message", "Nested error occurred.")
            return StandardResponse(success=False, message=str(error_detail), data=result)

    except HTTPException as http_exc:
        # Re-raise HTTP exceptions to be handled by FastAPI
        raise http_exc
    except Exception as e:
        logger.error(f"Connection test failed for {request.platform}: {e}", exc_info=True)
        # REFRESH.MD: Use 'from e' for proper exception chaining.
        raise HTTPException(status_code=500, detail="An unexpected error occurred during the connection test.") from e


# --- Spiritual Avatar Endpoints ---

@social_marketing_router.get("/swamiji-avatar-config", response_model=StandardResponse)
async def get_swamiji_avatar_config(
    admin_user: dict = Depends(AuthenticationHelper.verify_admin_access_strict),
    conn: asyncpg.Connection = Depends(db.get_db),
    avatar_engine: SpiritualAvatarGenerationEngine = Depends(get_avatar_engine)
):
    # REFRESH.MD: Dynamically fetch available voices from the avatar engine.
    available_voices = await avatar_engine.get_available_voices()
    
    config_data = {
        "voices": available_voices,
        "styles": AVAILABLE_AVATAR_STYLES,
        "default_text": "Greetings from the digital ashram. May you find peace and wisdom."
    }
    
    # REFRESH.MD: Fetch the avatar URL from the database instead of the local filesystem
    try:
        record = await conn.fetchrow("SELECT value FROM platform_settings WHERE key = 'swamiji_avatar_url'")
        if record and record['value']:
            # REFRESH.MD: Handle both JSON-encoded strings and plain strings for backward compatibility.
            try:
                config_data["image_url"] = json.loads(record['value'])
            except json.JSONDecodeError:
                config_data["image_url"] = record['value'] # Fallback for old plain string URLs
    except Exception as e:
        logger.error(f"Failed to fetch Swamiji avatar URL from database: {e}", exc_info=True)
        # Non-fatal, we can proceed without the image URL

    return StandardResponse(success=True, data=config_data, message="Avatar configuration retrieved.")

@social_marketing_router.post("/upload-swamiji-image", response_model=StandardResponse)
async def upload_swamiji_image(
    image: UploadFile = File(...), 
    admin_user: dict = Depends(AuthenticationHelper.verify_admin_access_strict),
    storage_service: SupabaseStorageService = Depends(get_storage_service),
    conn: asyncpg.Connection = Depends(db.get_db)
):
    if not image.filename:
        raise HTTPException(status_code=400, detail="No filename provided.")

    if image.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=400, detail=f"Invalid file type. Only {', '.join(ALLOWED_MIME_TYPES)} are allowed.")

    contents = await image.read()

    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail=f"File size exceeds the limit of {MAX_FILE_SIZE / 1024 / 1024} MB.")

    file_extension = MIME_TYPE_TO_EXTENSION.get(image.content_type, '.png')
    file_name_in_bucket = f"public/swamiji_base_avatar{file_extension}"
    bucket_name = "avatars"

    try:
        # Upload to Supabase Storage instead of local file
        public_url = storage_service.upload_file(
            bucket_name=bucket_name,
            file_path_in_bucket=file_name_in_bucket,
            file=contents,
            content_type=image.content_type
        )

        # Save the public URL to the database
        await conn.execute(
            """
            INSERT INTO platform_settings (key, value)
            VALUES ('swamiji_avatar_url', $1)
            ON CONFLICT (key) DO UPDATE
            SET value = EXCLUDED.value, updated_at = NOW()
            """,
            json.dumps(public_url)
        )
        
        logger.info(f"✅ Swamiji's photo saved to Supabase and URL stored in DB: {public_url}")
        return StandardResponse(success=True, message="Image uploaded successfully.", data={"image_url": public_url})
        
    except Exception as e:
        logger.error(f"An error occurred during Swamiji image upload: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to save uploaded file: {e}")


class ImagePreviewRequest(BaseModel):
    custom_prompt: Optional[str] = Field(None, description="A custom prompt to override the daily theme.")

@social_marketing_router.post("/generate-image-preview", response_model=StandardResponse)
async def generate_image_preview(
    request: ImagePreviewRequest,
    admin_user: dict = Depends(AuthenticationHelper.verify_admin_access_strict),
    theme_service: ThemeService = Depends(get_theme_service),
):
    """
    Generates a daily-themed or custom-prompted avatar image preview.
    Does not generate video. Returns the image URL and the prompt used.
    """
    try:
        # The ThemeService now accepts an optional custom prompt
        result = await theme_service.get_daily_themed_image_url(
            custom_prompt=request.custom_prompt
        )
        return StandardResponse(success=True, message="Image preview generated successfully.", data=result)
    except Exception as e:
        logger.error(f"Image preview generation failed: {e}", exc_info=True)
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error generating image preview: {e}") from e

class VideoFromPreviewRequest(BaseModel):
    image_url: str = Field(..., description="The URL of the confirmed preview image.")
    sample_text: str = Field(..., description="The text to be spoken in the video.")
    voice_id: str = Field(..., description="The voice ID to be used for the video.")

@social_marketing_router.post("/generate-video-from-preview", response_model=StandardResponse)
async def generate_video_from_preview(
    request: VideoFromPreviewRequest,
    admin_user: dict = Depends(AuthenticationHelper.verify_admin_access_strict),
    avatar_engine: SpiritualAvatarGenerationEngine = Depends(get_avatar_engine),
):
    """
    Generates the final video using a confirmed image URL.
    """
    try:
        result = await avatar_engine.generate_avatar_preview_lightweight(
            guidance_text=request.sample_text,
            voice_id=request.voice_id,
            source_image_url=request.image_url
        )
        if result.get("success"):
            return StandardResponse(success=True, message="Avatar video generated successfully.", data=result)
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Failed to generate video from preview."))
    except Exception as e:
        logger.error(f"Video generation from preview failed: {e}", exc_info=True)
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error generating video from preview: {e}") from e



@social_marketing_router.post("/generate-all-avatar-previews", response_model=StandardResponse)
async def generate_all_avatar_previews(
    request: GenerateAllAvatarPreviewsRequest,
    admin_user: dict = Depends(AuthenticationHelper.verify_admin_access_strict),
    avatar_engine: SpiritualAvatarGenerationEngine = Depends(get_avatar_engine),
    theme_service: ThemeService = Depends(get_theme_service),
):
    """
    DEPRECATED: This endpoint now generates a single daily preview, just like
    generate_avatar_preview. It's kept for backward compatibility.
    """
    try:
        # CORE.MD: The ThemeService now orchestrates image generation internally and returns a dict.
        theme_result = await theme_service.get_daily_themed_image_url()
        themed_image_url = theme_result.get("image_url")

        if not themed_image_url:
            raise HTTPException(status_code=500, detail="Failed to retrieve themed image URL from theme service.")

        # Generate the video preview with the new themed image
        result = await avatar_engine.generate_avatar_preview_lightweight(
            guidance_text=request.sample_text,
            voice_id=request.voice_id,
            source_image_url=themed_image_url
        )

        if not result or not result.get("success"):
             raise HTTPException(status_code=500, detail=result.get("error", "Failed to generate preview."))

        # The frontend expects a "previews" array, so we wrap the single result.
        return StandardResponse(success=True, message="Daily avatar preview generated.", data={"previews": [result]})
    except Exception as e:
        logger.error(f"All avatar previews generation failed: {e}", exc_info=True)
        # REFRESH.MD: Check if the exception is already an HTTPException.
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error generating all previews: {e}") from e

class ApproveSwamijiAvatarRequest(BaseModel):
    image_url: str = Field(..., description="The original uploaded image URL of Swamiji.")
    video_url: str = Field(..., description="The final generated video URL to be approved.")
    prompt: str = Field(..., description="The prompt used to generate the video's image.")

@social_marketing_router.post("/approve-swamiji-avatar", response_model=StandardResponse)
async def approve_swamiji_avatar(
    request: ApproveSwamijiAvatarRequest,
    admin_user: dict = Depends(AuthenticationHelper.verify_admin_access_strict),
    conn: asyncpg.Connection = Depends(db.get_db),
):
    """
    Approves and saves the final Swamiji avatar configuration.
    This stores the approved image and video URL in the database for future use.
    """
    try:
        async with conn.transaction():
            # CORE.MD: Use a structured JSON object for the configuration value for better extensibility.
            config_value = {
                "approved_at": datetime.now().isoformat(),
                "approved_by": admin_user.get("email"),
                "base_image_url": request.image_url,
                "approved_video_url": request.video_url,
                "generation_prompt": request.prompt,
            }
            
            # Storing base image URL consistently as a JSON-encoded string.
            await conn.execute(
                """
                INSERT INTO platform_settings (key, value, updated_at)
                VALUES ('swamiji_avatar_url', $1, NOW())
                ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, updated_at = NOW()
                """,
                json.dumps(request.image_url)
            )

            # Storing the full approved configuration object
            await conn.execute(
                """
                INSERT INTO platform_settings (key, value, updated_at)
                VALUES ('swamiji_approved_config', $1, NOW())
                ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, updated_at = NOW()
                """,
                json.dumps(config_value)
            )
        
        logger.info(f"✅ Swamiji avatar configuration approved and saved by {admin_user.get('email')}.")
        
        return StandardResponse(
            success=True, 
            message="Avatar configuration approved successfully.",
            data={"configuration": config_value}
        )
    except Exception as e:
        logger.error(f"Failed to save approved Swamiji avatar configuration: {e}", exc_info=True)
        # REFRESH.MD: Use `from e` to preserve the original exception context.
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred while saving the configuration.") from e

# --- Content Automation Endpoints ---

@social_marketing_router.post("/generate-daily-content", response_model=StandardResponse)
async def generate_daily_content(
    admin_user: dict = Depends(AuthenticationHelper.verify_admin_access_strict),
    social_engine: SocialMediaMarketingEngine = Depends(get_social_media_engine),
    conn = Depends(db.get_db)
):
    """
    Triggers the AI Marketing Engine to generate a content plan for the day.
    This is the main entry point for the daily automation task.
    """
    try:
        # This one call orchestrates the entire planning process
        daily_plan = await social_engine.generate_daily_content_plan()
        
        # Now, store the plan using the connection from this endpoint
        await social_engine._store_content_plan_in_db(daily_plan, conn)

        # The plan is stored in the DB by the engine itself.
        # The response can be a summary of the plan.
        summary = {
            platform: f"{len(posts)} posts planned"
            for platform, posts in daily_plan.items()
        }
        
        # REFRESH.MD: Convert Pydantic models to dicts for JSON serialization
        serializable_plan = {
            platform: [post.dict() for post in posts]
            for platform, posts in daily_plan.items()
        }

        return StandardResponse(
            success=True,
            message="Daily content plan generated successfully.",
            data={"plan_summary": summary, "full_plan": serializable_plan}
        )
    except Exception as e:
        logger.error(f"Error during daily content generation endpoint: {e}", exc_info=True)
        # The dependency injector or the engine itself might raise HTTPExceptions,
        # but we catch any other unexpected errors here.
        raise HTTPException(status_code=500, detail=f"A critical error occurred while generating the daily content plan: {e}")


# --- Content Posting & Asset Management (using placeholder data) ---

@social_marketing_router.post("/execute-posting", response_model=StandardResponse)
async def execute_posting(request: PostExecutionRequest, admin_user: dict = Depends(AuthenticationHelper.verify_admin_access_strict)):
    result = PostExecutionResult(
        success=True, message="Content posting has been scheduled.", task_id="task_12345",
        platform_statuses={platform: "scheduled" for platform in request.platforms}
    )
    return StandardResponse(success=True, data=result, message="Posting scheduled.")

@social_marketing_router.post("/assets", response_model=StandardResponse, status_code=201)
async def create_marketing_asset(asset: MarketingAssetCreate, admin_user: dict = Depends(AuthenticationHelper.verify_admin_access_strict)):
    new_asset = MarketingAsset(
        id=1, name=asset.name, type=asset.type, url=asset.url, created_at="2024-08-15T15:00:00Z"
    )
    return StandardResponse(success=True, data=new_asset, message="Asset created successfully.")

