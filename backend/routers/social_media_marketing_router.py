"""
🚀 SOCIAL MEDIA MARKETING API ROUTER

Complete and robust API for all social media marketing operations.
This file follows CORE.MD and REFRESH.MD principles for quality and maintainability.
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from pydantic import BaseModel, Field

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

logger = logging.getLogger(__name__)
social_marketing_router = APIRouter(
    prefix="/api/admin/social-marketing",
    tags=["Social Media Marketing", "Admin"]
)

class GenerateAvatarPreviewRequest(BaseModel):
    text: str = Field(..., description="The text content for the avatar preview.")
    style: str = Field(..., description="The visual style for the avatar.")
    voice_id: str = Field(..., description="The ID of the voice to be used.")

class GenerateAllAvatarPreviewsRequest(BaseModel):
    text: str = Field(..., description="The text content for the avatar previews.")
    voice_id: str = Field(..., description="The ID of the voice to be used for generation.")

AVAILABLE_AVATAR_STYLES = ["traditional", "modern", "default"]

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