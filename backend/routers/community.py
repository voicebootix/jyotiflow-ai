from fastapi import APIRouter, Depends, HTTPException, status, Request
from ..db import get_db
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
    """Get user's community participation metrics - returns exactly what frontend expects"""
    user_id = get_user_id_as_int(request)
    if not user_id:
        return {"success": True, "data": {
            "satsang_attended": 0,
            "satsang_upcoming": [],
            "community_rank": "New Member",
            "contribution_score": 0
        }}
    
    try:
        # Get user email for additional queries
        user = await db.fetchrow("SELECT email FROM users WHERE id=$1", user_id)
        if not user:
            return {"success": True, "data": {
                "satsang_attended": 0,
                "satsang_upcoming": [],
                "community_rank": "New Member",
                "contribution_score": 0
            }}
        
        user_email = user["email"]
        
        # Count satsang events attended
        satsang_attended_count = 0
        try:
            # Try to get actual satsang attendance if table exists
            satsang_count = await db.fetchval("""
                SELECT COUNT(*) 
                FROM satsang_attendees 
                WHERE user_email = $1 AND attended = true
            """, user_email)
            if satsang_count:
                satsang_attended_count = satsang_count
        except Exception:
            # If satsang_attendees table doesn't exist, use sessions as proxy
            # Count unique days with sessions as a proxy for satsang attendance
            session_days = await db.fetchval("""
                SELECT COUNT(DISTINCT DATE(created_at))
                FROM sessions 
                WHERE user_email = $1
            """, user_email)
            satsang_attended_count = session_days or 0
        
        # Get upcoming satsang events
        satsang_upcoming = []
        try:
            # Get upcoming satsang events from satsang_events table
            upcoming_events = await db.fetch("""
                SELECT 
                    id,
                    title,
                    description,
                    scheduled_at,
                    duration_minutes,
                    max_attendees,
                    status
                FROM satsang_events 
                WHERE scheduled_at > NOW() 
                    AND status IN ('scheduled', 'upcoming')
                ORDER BY scheduled_at ASC
                LIMIT 5
            """)
            
            satsang_upcoming = [
                {
                    "id": event["id"],
                    "title": event["title"],
                    "description": event["description"],
                    "scheduled_at": event["scheduled_at"].isoformat() if event["scheduled_at"] else None,
                    "duration_minutes": event["duration_minutes"],
                    "status": event["status"]
                }
                for event in upcoming_events
            ]
        except Exception:
            # If satsang_events table doesn't exist, return empty array
            satsang_upcoming = []
        
        # Calculate community rank and contribution score based on activity
        total_sessions = await db.fetchval("""
            SELECT COUNT(*) FROM sessions WHERE user_email = $1
        """, user_email) or 0
        
        # Determine community rank based on participation
        if total_sessions >= 50 or satsang_attended_count >= 20:
            community_rank = "Spiritual Guide"
            contribution_score = 100
        elif total_sessions >= 25 or satsang_attended_count >= 10:
            community_rank = "Active Practitioner"
            contribution_score = 75
        elif total_sessions >= 10 or satsang_attended_count >= 5:
            community_rank = "Regular Seeker"
            contribution_score = 50
        elif total_sessions >= 5 or satsang_attended_count >= 2:
            community_rank = "Growing Member"
            contribution_score = 25
        else:
            community_rank = "New Member"
            contribution_score = 10
        
        # Return exactly what frontend expects
        return {
            "success": True,
            "data": {
                "satsang_attended": satsang_attended_count,
                "satsang_upcoming": satsang_upcoming,
                "community_rank": community_rank,
                "contribution_score": contribution_score
            }
        }
        
    except Exception as e:
        print(f"Error getting community participation: {e}")
        # Return default values on error
        return {
            "success": True, 
            "data": {
                "satsang_attended": 0,
                "satsang_upcoming": [],
                "community_rank": "New Member",
                "contribution_score": 0
            }
        }

# தமிழ் - சமூக புள்ளிவிவரங்கள் பெறுதல்
@router.get("/stats")
async def get_community_stats(db=Depends(get_db)):
    """Get community statistics"""
    try:
        # Get community statistics
        stats = await db.fetchrow("""
            SELECT 
                COUNT(DISTINCT user_email) as total_members,
                COUNT(*) as total_sessions,
                AVG(EXTRACT(EPOCH FROM (updated_at - created_at))) as avg_session_duration
            FROM sessions
            WHERE created_at > NOW() - INTERVAL '30 days'
        """)
        
        if not stats:
            return {"success": True, "data": {}}
        
        # Get active members (users with sessions in last 7 days)
        active_members = await db.fetchval("""
            SELECT COUNT(DISTINCT user_email)
            FROM sessions
            WHERE created_at > NOW() - INTERVAL '7 days'
        """) or 0  # Ensure we always have a number, not None
        
        # Calculate proper engagement rate: (7-day active / 30-day total) * 100
        # This shows what percentage of monthly users are currently active
        total_members = stats["total_members"] or 0
        engagement_rate = 0.0
        
        if total_members > 0:
            # Calculate engagement as percentage of monthly users who were active in last 7 days
            engagement_rate = round((active_members / total_members) * 100, 2)
        
        # Calculate growth trend by comparing current month to previous month
        growth_trend = "placeholder"  # Default placeholder value
        try:
            # Get member count from previous month
            prev_month_members = await db.fetchval("""
                SELECT COUNT(DISTINCT user_email)
                FROM sessions
                WHERE created_at > NOW() - INTERVAL '60 days'
                  AND created_at <= NOW() - INTERVAL '30 days'
            """)
            
            current_members = total_members
            
            if prev_month_members and prev_month_members > 0:
                growth_percentage = ((current_members - prev_month_members) / prev_month_members) * 100
                if growth_percentage > 5:
                    growth_trend = "positive"
                elif growth_percentage < -5:
                    growth_trend = "negative"
                else:
                    growth_trend = "stable"
            else:
                # Not enough historical data
                growth_trend = "placeholder_insufficient_data"
                
        except Exception as e:
            print(f"Error calculating growth trend: {e}")
            growth_trend = "placeholder_error"
        
        community_stats = {
            "total_members": total_members,
            "active_members": active_members,
            "total_sessions": stats["total_sessions"] or 0,
            "avg_session_duration": round(stats["avg_session_duration"] or 0, 2),
            "engagement_rate": engagement_rate,
            "growth_trend": growth_trend
        }
        
        return {"success": True, "data": community_stats}
    except Exception as e:
        print(f"Error getting community stats: {e}")
        return {"success": True, "data": {}} 