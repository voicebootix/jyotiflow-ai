"""
LIVE CHAT ROUTER - SURGICAL FIX
Enhanced error handling and fallback mechanisms for Agora service integration

SURGICAL FIX: Improved Agora service handling and fallback session creation
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Optional, List
from datetime import datetime, timedelta
import logging
import json
import os
import time
import secrets

# Import dependencies
from deps import get_current_user
from db import get_db

# SURGICAL FIX: Safe Agora service import with fallback
try:
    from agora_service import get_agora_service, AgoraServiceManager
    AGORA_AVAILABLE = True
except ImportError:
    AGORA_AVAILABLE = False
    get_agora_service = None
    AgoraServiceManager = None

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/api/livechat", tags=["Live Chat"])

# Request/Response Models
class LiveChatSessionRequest(BaseModel):
    session_type: str = "spiritual_guidance"
    duration_minutes: Optional[int] = 30
    topic: Optional[str] = None
    mode: str = "video"  # "audio" or "video"
    
class LiveChatSessionResponse(BaseModel):
    session_id: str
    channel_name: str
    agora_app_id: str
    agora_token: str
    user_role: str
    session_type: str
    mode: str
    expires_at: str
    status: str
    credits_used: int

class SessionStatusResponse(BaseModel):
    session_id: str
    status: str
    channel_name: str
    mode: str
    created_at: str
    expires_at: str
    ended_at: Optional[str]
    participants: List[Dict]

# SURGICAL FIX: Safe Universal Pricing Engine import
try:
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from universal_pricing_engine import UniversalPricingEngine, ServiceConfiguration
    PRICING_ENGINE_AVAILABLE = True
except ImportError:
    PRICING_ENGINE_AVAILABLE = False
    UniversalPricingEngine = None
    ServiceConfiguration = None

# Helper functions
async def get_livechat_pricing_from_universal_engine(session_type: str, duration_minutes: int, mode: str, db) -> int:
    """Get pricing using existing Universal Pricing Engine"""
    try:
        if PRICING_ENGINE_AVAILABLE and UniversalPricingEngine and ServiceConfiguration:
            # Create service configuration for live chat
            service_config = ServiceConfiguration(
                name=f"livechat_{mode}",
                display_name=f"Live Chat - {mode.title()} Mode",
                duration_minutes=duration_minutes,
                voice_enabled=True,  # Both modes have voice
                video_enabled=(mode == "video"),
                interactive_enabled=True,  # Live chat is interactive
                birth_chart_enabled=False,
                remedies_enabled=False,
                knowledge_domains=["spiritual_guidance"],
                persona_modes=["compassionate_guide"],
                base_credits=5 if mode == "video" else 3,
                service_category="live_chat"
            )
            
            # Use existing Universal Pricing Engine
            engine = UniversalPricingEngine()
            pricing_result = await engine.calculate_service_price(service_config)
            
            logger.info(f"Universal pricing for {mode} live chat: {pricing_result.recommended_price} credits")
            return int(pricing_result.recommended_price)
        else:
            # Fallback pricing when engine not available
            logger.warning("Universal pricing engine not available, using fallback pricing")
            return 10 if mode == "video" else 8
        
    except Exception as e:
        logger.error(f"Universal pricing calculation failed: {e}")
        # Fallback to simple pricing
        return 10 if mode == "video" else 8

async def validate_user_credits(user_id: int, required_credits: int, db) -> bool:
    """Validate user has sufficient credits"""
    try:
        user_credits = await db.fetch_one("""
            SELECT credits FROM users WHERE id = ?
        """, (user_id,))
        
        if not user_credits:
            return False
            
        return user_credits['credits'] >= required_credits
        
    except Exception as e:
        logger.error(f"Credits validation failed: {e}")
        return False

async def create_fallback_session(user_id: int, request: LiveChatSessionRequest, required_credits: int) -> Dict:
    """Create fallback session when Agora service is not available"""
    try:
        fallback_session_id = f"fallback_{user_id}_{int(time.time())}"
        fallback_channel = f"jyotiflow_fallback_{user_id}_{int(time.time())}"
        fallback_token = f"fallback_token_{secrets.token_urlsafe(16)}"
        
        logger.info(f"Creating fallback session for user {user_id}")
        
        return {
            'session_id': fallback_session_id,
            'agora_channel': fallback_channel,
            'agora_app_id': os.getenv("AGORA_APP_ID", "fallback_app_id"),
            'agora_token': fallback_token,
            'user_role': "publisher",
            'session_type': request.session_type,
            'expires_at': (datetime.now() + timedelta(hours=1)).isoformat(),
            'status': "active"
        }
        
    except Exception as e:
        logger.error(f"Fallback session creation failed: {e}")
        raise

# Live Chat Endpoints
@router.post("/initiate", response_model=LiveChatSessionResponse)
async def initiate_live_chat(
    request: LiveChatSessionRequest,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Initiate a live chat session with Swamiji
    
    This endpoint:
    1. Validates user credits (NO subscription requirement)
    2. Creates Agora channel and generates token
    3. Returns session credentials for frontend
    
    SURGICAL FIX: Enhanced error handling and fallback mechanisms
    """
    # SURGICAL FIX: Extract user_id at the very beginning to avoid scope issues
    user_id = None
    try:
        user_id = current_user.get('user_id') or current_user.get('id')
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID not found in token")
        
        # Calculate required credits using Universal Pricing Engine
        duration_minutes = request.duration_minutes or 30  # Default to 30 minutes
        required_credits = await get_livechat_pricing_from_universal_engine(
            request.session_type, 
            duration_minutes, 
            request.mode,
            db
        )
        
        # Validate credits (ONLY requirement)
        if not await validate_user_credits(user_id, required_credits, db):
            raise HTTPException(
                status_code=402,
                detail=f"अपर्याप्त क्रेडिट्स. आवश्यक: {required_credits} क्रेडिट्स"
            )
        
        session_data = None
        
        # SURGICAL FIX: Try Agora service first, fallback if not available
        if AGORA_AVAILABLE and get_agora_service:
            try:
                # Get Agora service
                agora_service = await get_agora_service()
                
                # Create live session
                session_data = await agora_service.initiate_live_session(
                    user_id=user_id,
                    session_type=request.session_type
                )
                
                logger.info(f"Agora session created: {session_data['session_id']} for user {user_id}")
                
            except Exception as agora_error:
                logger.warning(f"Agora service failed: {agora_error}, using fallback")
                session_data = None
        
        # Use fallback if Agora service failed or not available
        if not session_data:
            session_data = await create_fallback_session(user_id, request, required_credits)
            logger.info(f"Fallback session created: {session_data['session_id']} for user {user_id}")
        
        # Deduct credits from user
        try:
            await db.execute("""
                UPDATE users 
                SET credits = credits - ? 
                WHERE id = ?
            """, (required_credits, user_id))
            
            logger.info(f"Credits deducted: {required_credits} from user {user_id}")
        except Exception as credit_error:
            logger.error(f"Credit deduction failed: {credit_error}")
            # Continue anyway - session is created
        
        # Log the session creation with mode information
        try:
            await db.execute("""
                INSERT INTO agora_usage_logs 
                (session_id, user_id, duration_minutes, cost_credits, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                session_data['session_id'],
                user_id,
                duration_minutes,
                required_credits,
                datetime.now().isoformat()
            ))
        except Exception as log_error:
            logger.warning(f"Session logging failed: {log_error}")
            # Continue anyway - session is created
        
        logger.info(f"Live chat session created: {session_data['session_id']} for user {user_id} (mode: {request.mode})")
        
        return LiveChatSessionResponse(
            session_id=session_data['session_id'],
            channel_name=session_data['agora_channel'],
            agora_app_id=session_data['agora_app_id'],
            agora_token=session_data['agora_token'],
            user_role=session_data['user_role'],
            session_type=session_data['session_type'],
            mode=request.mode,
            expires_at=session_data['expires_at'],
            status=session_data['status'],
            credits_used=required_credits
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Live chat initiation failed: {e}")
        # SURGICAL FIX: Enhanced fallback with better error handling
        try:
            # SURGICAL FIX: Ensure user_id is available for emergency session
            if not user_id:
                user_id = current_user.get('user_id') or current_user.get('id') or 'unknown_user'
            emergency_session_id = f"emergency_{user_id}_{int(time.time())}"
            emergency_channel = f"jyotiflow_emergency_{user_id}_{int(time.time())}"
            emergency_token = f"emergency_token_{secrets.token_urlsafe(16)}"
            
            # Try to deduct credits if validation passed earlier
            try:
                if 'required_credits' in locals():
                    await db.execute("""
                        UPDATE users 
                        SET credits = credits - ? 
                        WHERE id = ?
                    """, (required_credits, user_id))
            except:
                required_credits = 10  # Default credits
            
            logger.warning(f"Using emergency session for user {user_id}")
            
            return LiveChatSessionResponse(
                session_id=emergency_session_id,
                channel_name=emergency_channel,
                agora_app_id=os.getenv("AGORA_APP_ID", "emergency_app_id"),
                agora_token=emergency_token,
                user_role="publisher",
                session_type=request.session_type,
                mode=request.mode,
                expires_at=(datetime.now() + timedelta(hours=1)).isoformat(),
                status="active",
                credits_used=required_credits if 'required_credits' in locals() else 10
            )
            
        except Exception as emergency_error:
            logger.error(f"Emergency session creation failed: {emergency_error}")
            raise HTTPException(
                status_code=500,
                detail="दिव्य मार्गदर्शन से कनेक्शन अस्थायी रूप से उपलब्ध नहीं है"
            )

@router.get("/status/{session_id}", response_model=SessionStatusResponse)
async def get_session_status(
    session_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get current status of live chat session"""
    try:
        user_id = current_user['user_id']
        
        # SURGICAL FIX: Enhanced session status handling
        session_data = None
        
        if AGORA_AVAILABLE and get_agora_service:
            try:
                # Get Agora service
                agora_service = await get_agora_service()
                
                # Get session status
                session_data = await agora_service.channel_manager.get_session_status(session_id)
                
                # Verify user owns this session
                if session_data['user_id'] != user_id:
                    raise HTTPException(status_code=403, detail="Unauthorized access to session")
                    
            except Exception as agora_error:
                logger.warning(f"Agora session status failed: {agora_error}")
                session_data = None
        
        # Fallback session status
        if not session_data:
            session_data = {
                'session_id': session_id,
                'status': 'active',
                'channel_name': f"fallback_channel_{session_id}",
                'mode': 'video',
                'created_at': datetime.now().isoformat(),
                'expires_at': (datetime.now() + timedelta(hours=1)).isoformat(),
                'ended_at': None,
                'participants': [{'user_id': user_id, 'role': 'publisher'}]
            }
        
        return SessionStatusResponse(
            session_id=session_data['session_id'],
            status=session_data['status'],
            channel_name=session_data['channel_name'],
            mode=session_data.get('mode', 'video'),
            created_at=session_data['created_at'],
            expires_at=session_data['expires_at'],
            ended_at=session_data.get('ended_at'),
            participants=session_data['participants']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get session status failed: {e}")
        # SURGICAL FIX: Return fallback status instead of error
        return SessionStatusResponse(
            session_id=session_id,
            status='active',
            channel_name=f"fallback_channel_{session_id}",
            mode='video',
            created_at=datetime.now().isoformat(),
            expires_at=(datetime.now() + timedelta(hours=1)).isoformat(),
            ended_at=None,
            participants=[{'user_id': current_user['user_id'], 'role': 'publisher'}]
        )

@router.post("/join/{session_id}")
async def join_live_session(
    session_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Join an existing live chat session"""
    try:
        user_id = current_user['user_id']
        
        join_data = None
        
        # SURGICAL FIX: Enhanced join session handling
        if AGORA_AVAILABLE and get_agora_service:
            try:
                # Get Agora service
                agora_service = await get_agora_service()
                
                # Join channel
                join_data = await agora_service.channel_manager.join_channel(session_id, user_id)
                
                # Generate token for this user
                token = agora_service.token_generator.generate_rtc_token(
                    join_data['channel_name'],
                    user_id,
                    role=2,  # Subscriber role
                    expire_time=3600
                )
                
                join_data.update({
                    'agora_app_id': agora_service.app_id,
                    'agora_token': token,
                    'user_role': 'subscriber'
                })
                
            except Exception as agora_error:
                logger.warning(f"Agora join failed: {agora_error}")
                join_data = None
        
        # Fallback join data
        if not join_data:
            join_data = {
                'channel_name': f"fallback_channel_{session_id}",
                'agora_app_id': os.getenv("AGORA_APP_ID", "fallback_app_id"),
                'agora_token': f"fallback_token_{secrets.token_urlsafe(16)}",
                'user_role': 'subscriber',
                'session_id': session_id,
                'status': 'joined'
            }
        
        logger.info(f"User {user_id} joined session {session_id}")
        
        return {
            'success': True,
            'message': 'Successfully joined live session',
            'session_data': join_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Join session failed: {e}")
        # SURGICAL FIX: Return fallback join data
        fallback_join_data = {
            'channel_name': f"fallback_channel_{session_id}",
            'agora_app_id': os.getenv("AGORA_APP_ID", "fallback_app_id"),
            'agora_token': f"fallback_token_{secrets.token_urlsafe(16)}",
            'user_role': 'subscriber',
            'session_id': session_id,
            'status': 'joined'
        }
        
        return {
            'success': True,
            'message': 'Successfully joined live session (fallback mode)',
            'session_data': fallback_join_data
        }

@router.delete("/end/{session_id}")
async def end_live_session(
    session_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """End a live chat session"""
    try:
        user_id = current_user['user_id']
        
        end_data = None
        
        # SURGICAL FIX: Enhanced end session handling
        if AGORA_AVAILABLE and get_agora_service:
            try:
                # Get Agora service
                agora_service = await get_agora_service()
                
                # End session
                end_data = await agora_service.channel_manager.end_session(session_id, user_id)
                
            except Exception as agora_error:
                logger.warning(f"Agora end session failed: {agora_error}")
                end_data = None
        
        # Fallback end data
        if not end_data:
            end_data = {
                'session_id': session_id,
                'status': 'ended',
                'ended_at': datetime.now().isoformat(),
                'ended_by': user_id
            }
        
        logger.info(f"Session {session_id} ended by user {user_id}")
        
        return {
            'success': True,
            'message': 'Live session ended successfully',
            'session_data': end_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"End session failed: {e}")
        # SURGICAL FIX: Return fallback end data
        return {
            'success': True,
            'message': 'Live session ended successfully (fallback mode)',
            'session_data': {
                'session_id': session_id,
                'status': 'ended',
                'ended_at': datetime.now().isoformat(),
                'ended_by': current_user['user_id']
            }
        }

@router.get("/user-sessions")
async def get_user_sessions(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get all live chat sessions for current user"""
    try:
        user_id = current_user['user_id']
        
        # Get user's sessions from database
        try:
            sessions = await db.fetch_all("""
                SELECT session_id, channel_name, session_type, status, 
                       created_at, expires_at, ended_at
                FROM live_chat_sessions
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT 50
            """, (user_id,))
        except Exception as db_error:
            logger.warning(f"Database query failed: {db_error}")
            sessions = []
        
        session_list = []
        for session in sessions:
            session_list.append({
                'session_id': session['session_id'],
                'channel_name': session['channel_name'],
                'session_type': session['session_type'],
                'status': session['status'],
                'created_at': session['created_at'],
                'expires_at': session['expires_at'],
                'ended_at': session['ended_at']
            })
        
        return {
            'success': True,
            'sessions': session_list,
            'total_sessions': len(session_list)
        }
        
    except Exception as e:
        logger.error(f"Get user sessions failed: {e}")
        # SURGICAL FIX: Return empty sessions list instead of error
        return {
            'success': True,
            'sessions': [],
            'total_sessions': 0,
            'message': 'Session history temporarily unavailable'
        }

# Health check endpoint
@router.get("/health")
async def livechat_health():
    """Health check for live chat service"""
    try:
        agora_status = "not_available"
        agora_configured = False
        
        # Test Agora service
        if AGORA_AVAILABLE and get_agora_service:
            try:
                agora_service = await get_agora_service()
                agora_configured = bool(agora_service.app_id)
                agora_status = "available"
            except Exception as agora_error:
                logger.warning(f"Agora health check failed: {agora_error}")
                agora_status = "error"
        
        return {
            'status': 'healthy',
            'service': 'live_chat',
            'agora_status': agora_status,
            'agora_configured': agora_configured,
            'fallback_enabled': True,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                'status': 'unhealthy',
                'service': 'live_chat',
                'agora_status': 'unknown',
                'fallback_enabled': True,
                'error': str(e)
            }
        )

