"""
🎭 AVATAR GENERATION API ROUTER
Real D-ID + ElevenLabs Integration API Endpoints

This router provides the complete API for generating Swamiji avatar videos
with real AI services integration.
"""

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query
from pydantic import BaseModel, Field

from deps import get_current_user, get_admin_user
from core_foundation_enhanced import StandardResponse
from spiritual_avatar_generation_engine import avatar_engine
from enhanced_business_logic import SpiritualAvatarEngine
from universal_pricing_engine import UniversalPricingEngine

logger = logging.getLogger(__name__)

# Request/Response Models
class AvatarGenerationRequest(BaseModel):
    """Request model for avatar generation"""
    session_id: str = Field(..., description="Session ID for tracking")
    guidance_text: str = Field(..., min_length=10, max_length=5000, description="Spiritual guidance text")
    service_type: str = Field(..., description="Type of spiritual service")
    avatar_style: str = Field(default="traditional", description="Avatar style (traditional, modern, festival, meditation)")
    voice_tone: str = Field(default="compassionate", description="Voice tone (compassionate, wise, gentle, powerful, joyful)")
    video_duration: int = Field(default=300, ge=30, le=1800, description="Video duration in seconds")
    include_subtitles: bool = Field(default=True, description="Include subtitles in video")
    video_quality: str = Field(default="high", description="Video quality (low, medium, high)")

class AvatarGenerationResponse(BaseModel):
    """Response model for avatar generation"""
    success: bool
    session_id: str
    video_url: Optional[str] = None
    audio_url: Optional[str] = None
    duration_seconds: Optional[int] = None
    generation_time: Optional[float] = None
    total_cost: Optional[float] = None
    voice_cost: Optional[float] = None
    video_cost: Optional[float] = None
    quality: Optional[str] = None
    status: str = "pending"
    message: str
    estimated_completion_time: Optional[str] = None

class AvatarStatusResponse(BaseModel):
    """Response model for avatar status"""
    session_id: str
    status: str
    video_url: Optional[str] = None
    audio_url: Optional[str] = None
    duration_seconds: Optional[int] = None
    total_cost: Optional[float] = None
    generation_time: Optional[float] = None
    completed_at: Optional[str] = None
    error: Optional[str] = None

# Initialize router
avatar_router = APIRouter(prefix="/api/avatar", tags=["Avatar Generation"])

# Initialize spiritual avatar engine for guidance generation
spiritual_engine = SpiritualAvatarEngine()
pricing_engine = UniversalPricingEngine()

@avatar_router.post("/generate", response_model=AvatarGenerationResponse)
async def generate_avatar_video(
    request: AvatarGenerationRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """
    Generate complete avatar video with Swamiji's guidance
    
    This endpoint:
    1. Validates user credits and service access
    2. Generates voice audio with ElevenLabs
    3. Creates avatar video with D-ID
    4. Stores session data and deducts credits
    5. Returns video URL when complete
    """
    try:
        user_email = current_user["email"]
        
        # Validate service access and pricing
        service_config = await pricing_engine.get_service_config_from_db(request.service_type)
        if not service_config:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid service type: {request.service_type}"
            )
        
        # Check if user has enough credits
        user_credits = current_user.get("credits", 0)
        required_credits = service_config.base_credits
        
        if user_credits < required_credits:
            raise HTTPException(
                status_code=402,
                detail=f"Insufficient credits. Required: {required_credits}, Available: {user_credits}"
            )
        
        # Check if avatar generation is enabled for this service
        if not service_config.video_enabled:
            raise HTTPException(
                status_code=400,
                detail="Avatar video generation not available for this service type"
            )
        
        logger.info(f"🎭 Starting avatar generation for user {user_email}, session {request.session_id}")
        
        # Start avatar generation in background
        background_tasks.add_task(
            generate_avatar_background,
            request.session_id,
            user_email,
            request.guidance_text,
            request.service_type,
            request.avatar_style,
            request.voice_tone,
            request.video_duration,
            required_credits
        )
        
        # Calculate estimated completion time (1-5 minutes typically)
        estimated_completion = datetime.now(timezone.utc)
        estimated_completion = estimated_completion.replace(
            minute=estimated_completion.minute + 3
        )
        
        return AvatarGenerationResponse(
            success=True,
            session_id=request.session_id,
            status="generating",
            message="Avatar generation started successfully. Please check status for completion.",
            estimated_completion_time=estimated_completion.isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Avatar generation request failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Avatar generation failed: {str(e)}"
        )

@avatar_router.get("/status/{session_id}", response_model=AvatarStatusResponse)
async def get_avatar_status(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get avatar generation status and results
    
    This endpoint returns:
    - Generation status (pending, generating, completed, failed)
    - Video URL when complete
    - Cost breakdown
    - Generation time
    """
    try:
        # Get generation status from avatar engine
        status_data = await avatar_engine.get_avatar_generation_status(session_id)
        
        if status_data.get("status") == "not_found":
            raise HTTPException(
                status_code=404,
                detail=f"Avatar session not found: {session_id}"
            )
        
        return AvatarStatusResponse(
            session_id=session_id,
            status=status_data.get("status", "unknown"),
            video_url=status_data.get("video_url"),
            audio_url=status_data.get("audio_url"),
            duration_seconds=status_data.get("duration_seconds"),
            total_cost=status_data.get("total_cost"),
            generation_time=status_data.get("generation_time"),
            completed_at=status_data.get("completed_at"),
            error=status_data.get("error")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Avatar status check failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Status check failed: {str(e)}"
        )

@avatar_router.post("/generate-with-guidance")
async def generate_avatar_with_spiritual_guidance(
    question: str = Field(..., min_length=10, description="Spiritual question"),
    service_type: str = Field(..., description="Service type"),
    avatar_style: str = Field(default="traditional", description="Avatar style"),
    voice_tone: str = Field(default="compassionate", description="Voice tone"),
    birth_details: Optional[Dict[str, Any]] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Generate spiritual guidance AND avatar video in one request
    
    This endpoint:
    1. Generates spiritual guidance based on question
    2. Creates avatar video with the guidance
    3. Returns both text guidance and video URL
    """
    try:
        user_email = current_user["email"]
        
        # Generate spiritual guidance first
        guidance_context = {
            "user_id": current_user.get("id"),
            "service_type": service_type,
            "cultural_context": {"language": "en", "tradition": "tamil_vedic"},
            "previous_sessions": []
        }
        
        guidance_text, video_metadata = await spiritual_engine.generate_personalized_guidance(
            context=guidance_context,
            user_query=question,
            birth_details=birth_details
        )
        
        # Create session ID
        session_id = f"guidance_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{user_email[:8]}"
        
        # Start avatar generation with the guidance
        result = await avatar_engine.generate_complete_avatar_video(
            session_id=session_id,
            user_email=user_email,
            guidance_text=guidance_text,
            service_type=service_type,
            avatar_style=avatar_style,
            voice_tone=voice_tone,
            video_duration=min(len(guidance_text) // 2, 600)  # ~2 chars per second
        )
        
        if result["success"]:
            # Deduct credits from user
            await deduct_user_credits(user_email, service_type)
            
            return {
                "success": True,
                "session_id": session_id,
                "guidance_text": guidance_text,
                "video_url": result["video_url"],
                "audio_url": result["audio_url"],
                "total_cost": result["total_cost"],
                "generation_time": result["generation_time"],
                "message": "Complete spiritual guidance with avatar video generated successfully"
            }
        else:
            return {
                "success": False,
                "session_id": session_id,
                "guidance_text": guidance_text,
                "error": result["error"],
                "message": "Guidance generated but avatar creation failed"
            }
            
    except Exception as e:
        logger.error(f"❌ Complete guidance generation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Complete guidance generation failed: {str(e)}"
        )

@avatar_router.get("/services/test")
async def test_avatar_services(admin_user: dict = Depends(get_admin_user)):
    """
    Test D-ID and ElevenLabs service connectivity
    Admin endpoint to verify avatar services are working
    """
    try:
        test_results = await avatar_engine.test_avatar_services()
        return {
            "success": True,
            "test_results": test_results,
            "message": "Avatar services test completed"
        }
        
    except Exception as e:
        logger.error(f"❌ Avatar services test failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Service test failed: {str(e)}"
        )

@avatar_router.post("/presenter/create")
async def create_swamiji_presenter(admin_user: dict = Depends(get_admin_user)):
    """
    Create or update Swamiji presenter in D-ID
    Admin endpoint to set up the avatar presenter
    """
    try:
        result = await avatar_engine.create_swamiji_presenter()
        return {
            "success": result["success"],
            "presenter_id": result.get("presenter_id"),
            "message": result["message"],
            "error": result.get("error")
        }
        
    except Exception as e:
        logger.error(f"❌ Presenter creation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Presenter creation failed: {str(e)}"
        )

@avatar_router.get("/user/history")
async def get_user_avatar_history(
    limit: int = Query(default=10, ge=1, le=50),
    current_user: dict = Depends(get_current_user)
):
    """
    Get user's avatar generation history
    """
    try:
        user_email = current_user["email"]
        
        # This would typically query the database for user's avatar sessions
        # For now, return a placeholder response
        return {
            "success": True,
            "user_email": user_email,
            "avatar_history": [],
            "total_sessions": 0,
            "total_minutes": 0,
            "message": "Avatar history retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"❌ Avatar history retrieval failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"History retrieval failed: {str(e)}"
        )

# Background task function
async def generate_avatar_background(
    session_id: str,
    user_email: str,
    guidance_text: str,
    service_type: str,
    avatar_style: str,
    voice_tone: str,
    video_duration: int,
    required_credits: int
):
    """
    Background task for avatar generation
    This runs the actual generation process asynchronously
    """
    try:
        logger.info(f"🎭 Background avatar generation started for {session_id}")
        
        # Generate the avatar video
        result = await avatar_engine.generate_complete_avatar_video(
            session_id=session_id,
            user_email=user_email,
            guidance_text=guidance_text,
            service_type=service_type,
            avatar_style=avatar_style,
            voice_tone=voice_tone,
            video_duration=video_duration
        )
        
        if result["success"]:
            # Deduct credits from user
            await deduct_user_credits(user_email, service_type)
            logger.info(f"✅ Avatar generation completed for {session_id}")
        else:
            logger.error(f"❌ Avatar generation failed for {session_id}: {result['error']}")
            
    except Exception as e:
        logger.error(f"❌ Background avatar generation failed: {e}")

async def deduct_user_credits(user_email: str, service_type: str):
    """Deduct credits from user account"""
    try:
        # This would typically update the user's credit balance
        # For now, just log the operation
        logger.info(f"💰 Credits deducted for {user_email}, service: {service_type}")
        
    except Exception as e:
        logger.error(f"❌ Credit deduction failed: {e}")

# Export router
__all__ = ["avatar_router"]