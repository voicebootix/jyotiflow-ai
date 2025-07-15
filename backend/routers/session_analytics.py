from fastapi import APIRouter, Depends, HTTPException, status, Request
from db import get_db
import os
from datetime import datetime, timezone, timedelta
from typing import Dict, Any

# Import centralized JWT handler
from auth.jwt_config import JWTHandler

router = APIRouter(prefix="/api/sessions", tags=["Session Analytics"])

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

# தமிழ் - அமர்வு பகுப்பாய்வு பெறுதல்
@router.get("/analytics")
async def get_session_analytics(request: Request, db=Depends(get_db)):
    """Get comprehensive session analytics for the user"""
    user_id = get_user_id_as_int(request)
    if not user_id:
        return {"success": True, "data": {}}
    
    try:
        user = await db.fetchrow("SELECT email FROM users WHERE id=$1", user_id)
        if not user:
            return {"success": True, "data": {}}
        
        # Get comprehensive session analytics
        analytics = await db.fetchrow("""
            SELECT 
                COUNT(*) as total_sessions,
                COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_sessions,
                COUNT(CASE WHEN status = 'in_progress' THEN 1 END) as in_progress_sessions,
                COUNT(CASE WHEN status = 'cancelled' THEN 1 END) as cancelled_sessions,
                AVG(EXTRACT(EPOCH FROM (updated_at - created_at))) as avg_session_duration,
                MIN(created_at) as first_session,
                MAX(created_at) as last_session,
                COUNT(DISTINCT DATE(created_at)) as active_days,
                COUNT(DISTINCT service_type_id) as services_used,
                SUM(credits_used) as total_credits_used
            FROM sessions 
            WHERE user_email = $1
        """, user["email"])
        
        if not analytics:
            return {"success": True, "data": {}}
        
        # Get session trends by day of week
        daily_trends = await db.fetch("""
            SELECT 
                EXTRACT(DOW FROM created_at) as day_of_week,
                COUNT(*) as session_count
            FROM sessions 
            WHERE user_email = $1
            GROUP BY EXTRACT(DOW FROM created_at)
            ORDER BY day_of_week
        """, user["email"])
        
        # Get session trends by hour
        hourly_trends = await db.fetch("""
            SELECT 
                EXTRACT(HOUR FROM created_at) as hour_of_day,
                COUNT(*) as session_count
            FROM sessions 
            WHERE user_email = $1
            GROUP BY EXTRACT(HOUR FROM created_at)
            ORDER BY hour_of_day
        """, user["email"])
        
        # Get service usage breakdown
        service_usage = await db.fetch("""
            SELECT 
                st.name as service_name,
                COUNT(*) as usage_count,
                AVG(EXTRACT(EPOCH FROM (s.updated_at - s.created_at))) as avg_duration
            FROM sessions s
            JOIN service_types st ON s.service_type_id = st.id
            WHERE s.user_email = $1
            GROUP BY st.name
            ORDER BY usage_count DESC
        """, user["email"])
        
        # Calculate analytics
        total_sessions = analytics["total_sessions"] or 0
        completed_sessions = analytics["completed_sessions"] or 0
        completion_rate = (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0
        
        # Calculate session frequency
        if analytics["first_session"] and analytics["last_session"]:
            days_between = (analytics["last_session"] - analytics["first_session"]).days
            session_frequency = total_sessions / max(days_between, 1)
        else:
            session_frequency = 0
        
        # Format daily trends
        daily_trends_dict = {}
        for trend in daily_trends:
            day_names = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
            day_name = day_names[int(trend["day_of_week"])]
            daily_trends_dict[day_name] = trend["session_count"]
        
        # Format hourly trends
        hourly_trends_dict = {}
        for trend in hourly_trends:
            hour = int(trend["hour_of_day"])
            hourly_trends_dict[f"{hour:02d}:00"] = trend["session_count"]
        
        # Format service usage
        service_usage_list = []
        for service in service_usage:
            service_usage_list.append({
                "service_name": service["service_name"],
                "usage_count": service["usage_count"],
                "avg_duration": round(service["avg_duration"] or 0, 2)
            })
        
        analytics_data = {
            "overview": {
                "total_sessions": total_sessions,
                "completed_sessions": completed_sessions,
                "completion_rate": round(completion_rate, 2),
                "avg_session_duration": round(analytics["avg_session_duration"] or 0, 2),
                "total_credits_used": analytics["total_credits_used"] or 0,
                "services_used": analytics["services_used"] or 0
            },
            "trends": {
                "session_frequency": round(session_frequency, 2),
                "active_days": analytics["active_days"] or 0,
                "first_session": analytics["first_session"].isoformat() if analytics["first_session"] else None,
                "last_session": analytics["last_session"].isoformat() if analytics["last_session"] else None
            },
            "daily_trends": daily_trends_dict,
            "hourly_trends": hourly_trends_dict,
            "service_usage": service_usage_list,
            "insights": generate_session_insights(total_sessions, completion_rate, session_frequency)
        }
        
        return {"success": True, "data": analytics_data}
    except Exception as e:
        print(f"Error getting session analytics: {e}")
        return {"success": True, "data": {}}

def generate_session_insights(total_sessions, completion_rate, session_frequency):
    """Generate insights based on session analytics"""
    insights = []
    
    if total_sessions == 0:
        insights.append("Welcome to your spiritual journey! Your first session will be transformative.")
    elif total_sessions < 5:
        insights.append(f"You're building a strong foundation with {total_sessions} sessions.")
    elif total_sessions < 20:
        insights.append(f"Your dedication is showing! {total_sessions} sessions demonstrate commitment.")
    else:
        insights.append(f"You're a committed spiritual seeker with {total_sessions} sessions.")
    
    if completion_rate > 80:
        insights.append("Excellent session completion rate! You're truly committed to your growth.")
    elif completion_rate > 60:
        insights.append("Good completion rate. Consider setting dedicated time for sessions.")
    else:
        insights.append("Try to complete more sessions for better spiritual progress.")
    
    if session_frequency > 1:
        insights.append("High session frequency shows strong spiritual dedication.")
    elif session_frequency > 0.5:
        insights.append("Regular session frequency indicates good spiritual practice.")
    else:
        insights.append("Consider increasing session frequency for better progress.")
    
    return insights 