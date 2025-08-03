"""
🚀 SOCIAL MEDIA MARKETING API ROUTer

Complete and robust API for all social media marketing operations.
This file follows CORE.MD and REFRESH.MD principles for quality and maintainability.
"""

import logging
from typing import Optional, AsyncGenerator
import json
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Response
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
    from services.stability_ai_service import StabilityAiService, get_stability_service
    STABILITY_SERVICE_AVAILABLE = True
except ImportError:
    STABILITY_SERVICE_AVAILABLE = False
    class StabilityAiService: pass
    async def get_stability_service() -> AsyncGenerator[None, None]:
        raise HTTPException(status_code=501, detail="Stability AI service is not available.")
        yield # REFRESH.MD: FIX - This is unreachable but required for the function to be a valid generator.

logger = logging.getLogger(__name__)
social_marketing_router = APIRouter(
    prefix="/api/admin/social-marketing",
    tags=["Social Media Marketing", "Admin"]
)

class ImagePreviewRequest(BaseModel):
    custom_prompt: Optional[str] = Field(None, description="A custom prompt to override the daily theme.")

@social_marketing_router.post("/generate-image-preview")
async def generate_image_preview(
    request: ImagePreviewRequest,
    admin_user: dict = Depends(AuthenticationHelper.verify_admin_access_strict),
    theme_service: ThemeService = Depends(get_theme_service),
):
    """
    Generates a themed avatar image preview and returns it directly as an image,
    with the prompt included in a custom HTTP header.
    """
    try:
        image_bytes, final_prompt = await theme_service.generate_themed_image_bytes(
            custom_prompt=request.custom_prompt
        )
        
        headers = {
            "X-Generated-Prompt": final_prompt,
            "Access-Control-Expose-Headers": "X-Generated-Prompt",
        }
        
        return Response(content=image_bytes, media_type="image/png", headers=headers)
        
    except Exception as e:
        logger.error(f"Image preview generation failed: {e}", exc_info=True)
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error generating image preview: {e}") from e

# Other endpoints follow... (shortened for brevity)
