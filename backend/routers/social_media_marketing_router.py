"""
🚀 SOCIAL MEDIA MARKETING API ROUTER

Complete and robust API for all social media marketing operations.
This file follows CORE.MD and REFRESH.MD principles for quality and maintainability.
"""

import logging
from pathlib import Path
import shutil
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel, Field

# CORE.MD: All necessary dependencies are explicitly imported.
from auth.auth_helpers import get_current_admin_user
from schemas.response import StandardResponse
from schemas.social_media import (
    Campaign,
    ContentCalendarItem,
    GenerateAllAvatarPreviewsRequest,
    GenerateAvatarPreviewRequest,
    MarketingAsset,
    MarketingAssetCreate,
    MarketingOverview,
    PlatformConfig,
    PlatformStatus,
    PostExecutionRequest,
    PostExecutionResult,
    TestConnectionRequest,
)
from spiritual_avatar_generation_engine import SpiritualAvatarGenerationEngine, get_avatar_engine
from services.youtube_service import youtube_service
from services.facebook_service import facebook_service
from services.instagram_service import instagram_service
from services.tiktok_service import tiktok_service

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
async def get_marketing_overview(admin_user: dict = Depends(get_current_admin_user)):
    overview_data = MarketingOverview(
        total_campaigns=10, active_campaigns=3, total_posts=150, total_engagement=12500, reach=75000
    )
    return StandardResponse(success=True, data=overview_data, message="Marketing overview retrieved successfully.")

@social_marketing_router.get("/content-calendar", response_model=StandardResponse)
async def get_content_calendar(
    date: Optional[str] = None,
    platform: Optional[str] = None,
    admin_user: dict = Depends(get_current_admin_user)
):
    """Get content calendar with optional date and platform filtering"""
    # Base calendar data
    all_calendar_data = [
        ContentCalendarItem(id=1, date="2024-08-15T10:00:00Z", platform="Facebook", content="Satsang announcement", status="posted"),
        ContentCalendarItem(id=2, date="2024-08-16T12:00:00Z", platform="Twitter", content="Daily wisdom quote", status="scheduled"),
        ContentCalendarItem(id=3, date="2024-08-15T14:00:00Z", platform="Instagram", content="Meditation session", status="posted"),
        ContentCalendarItem(id=4, date="2024-08-17T09:00:00Z", platform="Facebook", content="Weekly blessing", status="scheduled"),
    ]
    
    # Apply filters following CORE.MD principles - explicit filter handling
    filtered_data = all_calendar_data
    
    # Filter by platform if specified
    if platform:
        filtered_data = [item for item in filtered_data if item.platform.lower() == platform.lower()]
        logger.info(f"Filtered calendar by platform: {platform}, found {len(filtered_data)} items")
    
    # Filter by date if specified (matches date part only)
    if date:
        filtered_data = [item for item in filtered_data if item.date.startswith(date)]
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
    admin_user: dict = Depends(get_current_admin_user)
):
    """Get campaigns with optional status and platform filtering"""
    # Base campaign data with more examples for proper filtering demonstration
    all_campaigns = [
        Campaign(id=1, name="Diwali Special Satsang", platform="YouTube", status="active", start_date="2024-10-20", end_date="2024-11-05"),
        Campaign(id=2, name="Summer Wisdom Series", platform="Facebook", status="completed", start_date="2024-06-01", end_date="2024-06-30"),
        Campaign(id=3, name="Meditation Mondays", platform="Instagram", status="active", start_date="2024-08-01", end_date="2024-12-31"),
        Campaign(id=4, name="Spiritual Stories", platform="YouTube", status="paused", start_date="2024-07-01", end_date="2024-09-30"),
        Campaign(id=5, name="Daily Wisdom", platform="Twitter", status="active", start_date="2024-01-01", end_date="2024-12-31"),
    ]
    
    # Apply filters following CORE.MD principles - explicit filter handling
    filtered_campaigns = all_campaigns
    
    # Filter by status if specified
    if status:
        filtered_campaigns = [campaign for campaign in filtered_campaigns if campaign.status.lower() == status.lower()]
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
async def get_platform_config(admin_user: dict = Depends(get_current_admin_user)):
    config_data = PlatformConfig(
        facebook=PlatformStatus(connected=True, username="jyotiflow.ai"),
        twitter=PlatformStatus(connected=False, username=None),
        instagram=PlatformStatus(connected=True, username="@jyotiflow.ai"),
        youtube=PlatformStatus(connected=True, username="JyotiFlowChannel"),
        linkedin=PlatformStatus(connected=False, username=None),
        tiktok=PlatformStatus(connected=False, username=None),
    )
    return StandardResponse(success=True, data=config_data, message="Platform configuration retrieved successfully.")

@social_marketing_router.post("/platform-config", response_model=StandardResponse)
async def save_platform_config(
    config_request: PlatformConfig,
    admin_user: dict = Depends(get_current_admin_user)
):
    try:
        logger.info(f"Attempting to save platform config: {config_request.dict()}")
        
        # In a real application, this would save to a database.
        # For now, we'll use a placeholder file to simulate persistence.
        # CORE.MD: Use a structured approach for data persistence.
        config_path = Path("backend/platform_config_cache.json")
        with open(config_path, "w") as f:
            import json
            json.dump(config_request.dict(), f, indent=2)

        return StandardResponse(success=True, message="Configuration saved successfully.")
    except Exception as e:
        logger.error(f"Failed to save platform configuration: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred while saving the configuration: {e}")


@social_marketing_router.post("/test-connection", response_model=StandardResponse)
async def test_platform_connection(
    request: TestConnectionRequest,
    admin_user: dict = Depends(get_current_admin_user)
):
    logger.info(f"Testing connection for platform: {request.platform}")
    if not request.config:
        raise HTTPException(status_code=400, detail="Configuration data is missing in the request.")

    try:
        if request.platform == "youtube":
            api_key = request.config.get("api_key")
            channel_id = request.config.get("channel_id")
            if not api_key or not channel_id:
                raise HTTPException(status_code=400, detail="YouTube API key and Channel ID are required.")
            
            result = await youtube_service.validate_credentials(api_key, channel_id)

        elif request.platform == "facebook":
            # This assumes facebook_service has a similar validate_credentials method
            # You would need to implement this in facebook_service.py
            page_access_token = request.config.get("page_access_token")
            if not page_access_token:
                 raise HTTPException(status_code=400, detail="Facebook Page Access Token is required.")
            result = await facebook_service.validate_credentials(page_access_token)

        elif request.platform == "instagram":
            # Placeholder for Instagram validation
            access_token = request.config.get("access_token")
            if not access_token:
                raise HTTPException(status_code=400, detail="Instagram Access Token is required.")
            result = await instagram_service.validate_credentials(access_token)
        
        elif request.platform == "tiktok":
            # Placeholder for TikTok validation
            client_key = request.config.get("client_key")
            client_secret = request.config.get("client_secret")
            if not client_key or not client_secret:
                raise HTTPException(status_code=400, detail="TikTok Client Key and Secret are required.")
            result = await tiktok_service.validate_credentials(client_key, client_secret)

        else:
            return StandardResponse(success=False, message=f"Connection testing for {request.platform} is not implemented yet.")

        if result and result.get("success"):
            return StandardResponse(success=True, data=result, message=result.get("message"))
        else:
            # REFRESH.MD: Provide detailed error messages back to the frontend.
            error_detail = result.get("error", "Unknown error during validation.")
            return StandardResponse(success=False, message=error_detail, data=result)

    except HTTPException as http_exc:
        # Re-raise HTTP exceptions to be handled by FastAPI
        raise http_exc
    except Exception as e:
        logger.error(f"Connection test failed for {request.platform}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

# --- Spiritual Avatar Endpoints ---

@social_marketing_router.get("/swamiji-avatar-config", response_model=StandardResponse)
async def get_swamiji_avatar_config(admin_user: dict = Depends(get_current_admin_user)):
    config_data = {
        "voices": [{"id": "swamiji_voice_v1", "name": "Swamiji Calm Voice"}],
        "styles": AVAILABLE_AVATAR_STYLES,
        "default_text": "Greetings from the digital ashram. May you find peace and wisdom."
    }
    return StandardResponse(success=True, data=config_data, message="Avatar configuration retrieved.")

@social_marketing_router.post("/upload-swamiji-image", response_model=StandardResponse)
async def upload_swamiji_image(file: UploadFile = File(...), admin_user: dict = Depends(get_current_admin_user)):
    # REFRESH.MD: Restore filename null check (regression fix)
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided.")

    # CORE.MD: Add MIME Type validation (security fix)
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=400, detail=f"Invalid file type. Only {', '.join(ALLOWED_MIME_TYPES)} are allowed.")

    # REFRESH.MD: Read the file ONCE into memory to be efficient and avoid pointer issues.
    contents = await file.read()

    # CORE.MD: Enforce file size limit on the in-memory content.
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail=f"File size exceeds the limit of {MAX_FILE_SIZE / 1024 / 1024} MB.")

    # CORE.MD: Sanitize filename and use extension from validated MIME type
    upload_dir = Path("backend/static_uploads/avatars")
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_extension = MIME_TYPE_TO_EXTENSION[file.content_type]
    file_name = f"swamiji_base_avatar{file_extension}"
    file_path = upload_dir / file_name

    try:
        # Write the in-memory contents to the file.
        with open(file_path, "wb") as buffer:
            buffer.write(contents)
    except Exception as e:
        logger.error(f"Could not write uploaded file to disk: {e}")
        raise HTTPException(status_code=500, detail="Failed to save uploaded file.")

    logger.info(f"✅ Swamiji's photo saved to: {file_path}")
    return StandardResponse(success=True, message="Image uploaded successfully.", data={"url": f"/static/avatars/{file_name}"})

@social_marketing_router.post("/generate-avatar-preview", response_model=StandardResponse)
async def generate_avatar_preview(
    request: GenerateAvatarPreviewRequest,
    admin_user: dict = Depends(get_current_admin_user),
    avatar_engine: SpiritualAvatarGenerationEngine = Depends(get_avatar_engine)
):
    """Generates a single, lightweight avatar preview."""
    try:
        result = await avatar_engine.generate_avatar_preview_lightweight(
            guidance_text=request.text,
            avatar_style=request.style,
            voice_id=request.voice_id
        )
        if result.get("success"):
            return StandardResponse(success=True, message="Avatar preview generated.", data=result)
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Failed to generate preview."))
    except Exception as e:
        logger.error(f"Avatar preview generation failed for style {request.style}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error generating preview: {e}") from e


@social_marketing_router.post("/generate-all-avatar-previews", response_model=StandardResponse)
async def generate_all_avatar_previews(
    request: GenerateAllAvatarPreviewsRequest,
    admin_user: dict = Depends(get_current_admin_user),
    avatar_engine: SpiritualAvatarGenerationEngine = Depends(get_avatar_engine)
):
    """Generates lightweight avatar previews for all available styles."""
    try:
        results = []
        for style in AVAILABLE_AVATAR_STYLES:
            style_result = await avatar_engine.generate_avatar_preview_lightweight(
                guidance_text=request.text,
                avatar_style=style,
                voice_id=request.voice_id
            )
            results.append(style_result)
        return StandardResponse(success=True, message="All avatar previews generated.", data={"previews": results})
    except Exception as e:
        logger.error(f"All avatar previews generation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error generating all previews: {e}") from e

# --- Content Posting & Asset Management (using placeholder data) ---

@social_marketing_router.post("/execute-posting", response_model=StandardResponse)
async def execute_posting(request: PostExecutionRequest, admin_user: dict = Depends(get_current_admin_user)):
    result = PostExecutionResult(
        success=True, message="Content posting has been scheduled.", task_id="task_12345",
        platform_statuses={platform: "scheduled" for platform in request.platforms}
    )
    return StandardResponse(success=True, data=result, message="Posting scheduled.")

@social_marketing_router.post("/assets", response_model=StandardResponse, status_code=201)
async def create_marketing_asset(asset: MarketingAssetCreate, admin_user: dict = Depends(get_current_admin_user)):
    new_asset = MarketingAsset(
        id=1, name=asset.name, type=asset.type, url=asset.url, created_at="2024-08-15T15:00:00Z"
    )
    return StandardResponse(success=True, data=new_asset, message="Asset created successfully.")

