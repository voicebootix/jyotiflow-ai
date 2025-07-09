from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Optional, List
from datetime import datetime
import logging
import json

# Import dependencies
from deps import get_current_user
from db import get_db
from agora_service import get_agora_service, AgoraServiceManager

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

# Helper functions
async def get_livechat_pricing(session_type: str, duration_minutes: int, mode: str, db) -> int:
    """Get pricing for live chat session from database or default"""
    try:
        # Try to get from pricing_config table
        pricing_query = await db.fetch_one("""
            SELECT config_value FROM pricing_config 
            WHERE config_key = ? AND is_active = true
        """, (f"livechat_{mode}_{session_type}",))
        
        if pricing_query:
            return int(pricing_query['config_value'])
        
        # Default pricing structure
        base_costs = {
            "audio": 3,    # 3 credits base for audio
            "video": 5     # 5 credits base for video
        }
        
        per_minute_costs = {
            "audio": 0.3,  # 0.3 credits per minute for audio
            "video": 0.5   # 0.5 credits per minute for video
        }
        
        base_cost = base_costs.get(mode, 5)
        per_minute_cost = per_minute_costs.get(mode, 0.5)
        
        return int(base_cost + (duration_minutes * per_minute_cost))
        
    except Exception as e:
        logger.error(f"Pricing calculation failed: {e}")
        # Fallback pricing
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
    """
    try:
        user_id = current_user['user_id']
        
        # Calculate required credits using dynamic pricing
        duration_minutes = request.duration_minutes or 30  # Default to 30 minutes
        required_credits = await get_livechat_pricing(
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
        
        # Get Agora service
        agora_service = await get_agora_service()
        
        # Create live session
        session_data = await agora_service.initiate_live_session(
            user_id=user_id,
            session_type=request.session_type
        )
        
        # Deduct credits from user
        await db.execute("""
            UPDATE users 
            SET credits = credits - ? 
            WHERE id = ?
        """, (required_credits, user_id))
        
        # Log the session creation with mode information
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
        
        # Get Agora service
        agora_service = await get_agora_service()
        
        # Get session status
        session_data = await agora_service.channel_manager.get_session_status(session_id)
        
        # Verify user owns this session
        if session_data['user_id'] != user_id:
            raise HTTPException(status_code=403, detail="Unauthorized access to session")
        
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
        raise HTTPException(
            status_code=500,
            detail="सेशन स्थिति प्राप्त करने में विफल"
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
        raise HTTPException(
            status_code=500,
            detail="लाइव सेशन में शामिल होने में विफल"
        )

@router.delete("/end/{session_id}")
async def end_live_session(
    session_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """End a live chat session"""
    try:
        user_id = current_user['user_id']
        
        # Get Agora service
        agora_service = await get_agora_service()
        
        # End session
        end_data = await agora_service.channel_manager.end_session(session_id, user_id)
        
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
        raise HTTPException(
            status_code=500,
            detail="सेशन समाप्त करने में विफल"
        )

@router.get("/user-sessions")
async def get_user_sessions(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get all live chat sessions for current user"""
    try:
        user_id = current_user['user_id']
        
        # Get user's sessions from database
        sessions = await db.fetch_all("""
            SELECT session_id, channel_name, session_type, status, 
                   created_at, expires_at, ended_at
            FROM live_chat_sessions
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT 50
        """, (user_id,))
        
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
        raise HTTPException(
            status_code=500,
            detail="उपयोगकर्ता सेशन प्राप्त करने में विफल"
        )

# Admin endpoints
@router.get("/admin/active-sessions")
async def get_active_sessions(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get all active live chat sessions (Admin only)"""
    try:
        # Check admin privileges
        if not current_user.get('is_admin', False):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        # Get active sessions
        sessions = await db.fetch_all("""
            SELECT s.session_id, s.user_id, s.channel_name, s.session_type, 
                   s.status, s.created_at, s.expires_at, u.username
            FROM live_chat_sessions s
            JOIN users u ON s.user_id = u.id
            WHERE s.status = 'active'
            ORDER BY s.created_at DESC
        """)
        
        active_sessions = []
        for session in sessions:
            active_sessions.append({
                'session_id': session['session_id'],
                'user_id': session['user_id'],
                'username': session['username'],
                'channel_name': session['channel_name'],
                'session_type': session['session_type'],
                'status': session['status'],
                'created_at': session['created_at'],
                'expires_at': session['expires_at']
            })
        
        return {
            'success': True,
            'active_sessions': active_sessions,
            'total_active': len(active_sessions)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get active sessions failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="सक्रिय सेशन प्राप्त करने में विफल"
        )

@router.get("/admin/usage-analytics")
async def get_usage_analytics(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get Agora usage analytics (Admin only)"""
    try:
        # Check admin privileges
        if not current_user.get('is_admin', False):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        # Get usage statistics
        stats = await db.fetch_all("""
            SELECT 
                COUNT(*) as total_sessions,
                SUM(duration_minutes) as total_minutes,
                SUM(cost_credits) as total_credits,
                AVG(duration_minutes) as avg_duration,
                COUNT(DISTINCT user_id) as unique_users
            FROM agora_usage_logs
            WHERE created_at > datetime('now', '-30 days')
        """)
        
        recent_sessions = await db.fetch_all("""
            SELECT session_id, user_id, duration_minutes, cost_credits, created_at
            FROM agora_usage_logs
            ORDER BY created_at DESC
            LIMIT 100
        """)
        
        return {
            'success': True,
            'analytics': {
                'total_sessions': stats[0]['total_sessions'],
                'total_minutes': stats[0]['total_minutes'],
                'total_credits': stats[0]['total_credits'],
                'avg_duration': stats[0]['avg_duration'],
                'unique_users': stats[0]['unique_users']
            },
            'recent_sessions': [
                {
                    'session_id': session['session_id'],
                    'user_id': session['user_id'],
                    'duration_minutes': session['duration_minutes'],
                    'cost_credits': session['cost_credits'],
                    'created_at': session['created_at']
                } for session in recent_sessions
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get usage analytics failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="उपयोग विश्लेषण प्राप्त करने में विफल"
        )

# Health check endpoint
@router.get("/health")
async def livechat_health():
    """Health check for live chat service"""
    try:
        # Test Agora service
        agora_service = await get_agora_service()
        
        return {
            'status': 'healthy',
            'service': 'live_chat',
            'agora_configured': bool(agora_service.app_id),
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                'status': 'unhealthy',
                'service': 'live_chat',
                'error': str(e)
            }
        )