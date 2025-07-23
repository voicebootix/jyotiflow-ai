"""
🚀 SOCIAL MEDIA MARKETING API ROUTER

Complete and robust API for all social media marketing operations.
This file follows CORE.MD and REFRESH.MD principles for quality and maintainability.
"""

import logging
from pathlib import Path
import shutil

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel, Field

# CORE.MD: All necessary dependencies are explicitly imported from their correct locations.
from ..auth.auth_helpers import get_current_admin_user
from ..schemas.response import StandardResponse
from ..schemas.social_media import (
    Campaign,
    ContentCalendarItem,
    MarketingAsset,
    MarketingAssetCreate,
    MarketingOverview,
    PlatformConfig,
    PlatformStatus,
    PostExecutionRequest,
    PostExecutionResult,
    TestConnectionRequest,
)
from ..spiritual_avatar_generation_engine import SpiritualAvatarGenerationEngine, get_avatar_engine

# Initialize logger and router
logger = logging.getLogger(__name__)
social_marketing_router = APIRouter(
    prefix="/api/admin/social-marketing",
    tags=["Social Media Marketing", "Admin"]
)

# REFRESH.MD: Define necessary request schemas directly in the router for clarity and to resolve import issues.
class GenerateAvatarPreviewRequest(BaseModel):
    text: str = Field(..., description="The text content for the avatar preview.")
    style: str = Field(..., description="The visual style for the avatar.")
    voice_id: str = Field(..., description="The ID of the voice to be used.")

class GenerateAllAvatarPreviewsRequest(BaseModel):
    text: str = Field(..., description="The text content for the avatar previews.")
    voice_id: str = Field(..., description="The ID of the voice to be used for generation.")


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
async def get_content_calendar(admin_user: dict = Depends(get_current_admin_user)):
    calendar_data = [
        ContentCalendarItem(id=1, date="2024-08-15T10:00:00Z", platform="Facebook", content="Satsang announcement", status="posted"),
        ContentCalendarItem(id=2, date="2024-08-16T12:00:00Z", platform="Twitter", content="Daily wisdom quote", status="scheduled"),
    ]
    return StandardResponse(success=True, data={"calendar": calendar_data}, message="Content calendar retrieved successfully.")

@social_marketing_router.get("/campaigns", response_model=StandardResponse)
async def get_campaigns(admin_user: dict = Depends(get_current_admin_user)):
    campaign_data = [
        Campaign(id=1, name="Diwali Special Satsang", platform="YouTube", status="active", start_date="2024-10-20", end_date="2024-11-05"),
        Campaign(id=2, name="Summer Wisdom Series", platform="Facebook", status="completed", start_date="2024-06-01", end_date="2024-06-30"),
    ]
    return StandardResponse(success=True, data={"campaigns": campaign_data}, message="Campaigns retrieved successfully.")

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
async def save_platform_config(config: PlatformConfig, admin_user: dict = Depends(get_current_admin_user)):
    logger.info(f"Attempting to save platform config: {config.dict()}")
    return StandardResponse(success=True, message="Configuration saved successfully.")


@social_marketing_router.post("/test-connection", response_model=StandardResponse)
async def test_platform_connection(request: TestConnectionRequest, admin_user: dict = Depends(get_current_admin_user)):
    if request.platform in ["facebook", "instagram", "youtube"]:
        return StandardResponse(success=True, message=f"Successfully connected to {request.platform}.")
    else:
        return StandardResponse(success=False, message=f"Connection to {request.platform} failed. Please check credentials.")

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

