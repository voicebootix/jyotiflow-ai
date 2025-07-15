from fastapi import APIRouter, Depends, HTTPException, status, Request
from db import get_db
import os
from datetime import datetime, timezone
from typing import Dict, Any

# Import centralized JWT handler
from auth.jwt_config import JWTHandler

router = APIRouter(prefix="/api/community", tags=["Community"])

def get_user_id_from_token(request: Request) -> str | None:
    """Extract user ID from JWT token - OPTIONAL"""
    try:
        return JWTHandler.get_user_id_from_token(request)
    except Exception:
        return None

def get_user_id_as_int(request: Request) -> int | None:
    """Extract user ID from JWT token and convert to integer - OPTIONAL"""
    try:
        user_id_str = JWTHandler.get_user_id_from_token(request)
        return int(user_id_str) if user_id_str else None
    except (ValueError, TypeError):
        return None

# தமிழ் - பயனர் சமூக பங்கேற்பு பெறுதல்
@router.get("/my-participation")
async def get_user_participation(request: Request, db=Depends(get_db)):
    """Get user's community participation metrics"""
    user_id = get_user_id_as_int(request)
    if not user_id:
        return {"success": True, "data": {}}
    
    try:
        user = await db.fetchrow("SELECT email FROM users WHERE id=$1", user_id)
        if not user:
            return {"success": True, "data": {}}
        
        # Get user's session data for community metrics
        sessions = await db.fetch("""
            SELECT 
                COUNT(*) as total_sessions,
                COUNT(DISTINCT DATE(created_at)) as active_days,
                MAX(created_at) as last_activity,
                AVG(EXTRACT(EPOCH FROM (updated_at - created_at))) as avg_session_duration
            FROM sessions 
            WHERE user_email = $1
        """, user["email"])
        
        if not sessions:
            return {"success": True, "data": {}}
        
        session_data = sessions[0]
        
        # Calculate community participation metrics
        participation = {
            "total_sessions": session_data["total_sessions"] or 0,
            "active_days": session_data["active_days"] or 0,
            "last_activity": session_data["last_activity"].isoformat() if session_data["last_activity"] else None,
            "avg_session_duration": round(session_data["avg_session_duration"] or 0, 2),
            "participation_level": "active" if session_data["total_sessions"] > 10 else "regular" if session_data["total_sessions"] > 5 else "new",
            "community_rank": "Seeker" if session_data["total_sessions"] < 10 else "Practitioner" if session_data["total_sessions"] < 25 else "Guide",
            "contribution_score": min(session_data["total_sessions"] * 10, 100),
            "engagement_rate": min((session_data["active_days"] / max(session_data["total_sessions"], 1)) * 100, 100)
        }
        
        return {"success": True, "data": participation}
    except Exception as e:
        print(f"Error getting community participation: {e}")
        return {"success": True, "data": {}}

# தமிழ் - சமூக புள்ளிவிவரங்கள் பெறுதல்
@router.get("/stats")
async def get_community_stats(db=Depends(get_db)):
    """Get community statistics"""
    try:
        # Get community statistics
        stats = await db.fetchrow("""
            SELECT 
                COUNT(DISTINCT user_email) as active_members,
                COUNT(*) as total_sessions,
                COUNT(DISTINCT DATE(created_at)) as active_days,
                AVG(EXTRACT(EPOCH FROM (updated_at - created_at))) as avg_session_duration
            FROM sessions 
            WHERE created_at > NOW() - INTERVAL '30 days'
        """)
        
        if not stats:
            return {"success": True, "data": {}}
        
        community_stats = {
            "active_members": stats["active_members"] or 0,
            "total_sessions": stats["total_sessions"] or 0,
            "active_days": stats["active_days"] or 0,
            "avg_session_duration": round(stats["avg_session_duration"] or 0, 2),
            "community_health": "thriving" if stats["active_members"] > 50 else "growing" if stats["active_members"] > 20 else "developing",
            "engagement_rate": min((stats["active_days"] / max(stats["total_sessions"], 1)) * 100, 100)
        }
        
        return {"success": True, "data": community_stats}
    except Exception as e:
        print(f"Error getting community stats: {e}")
        return {"success": True, "data": {}} 