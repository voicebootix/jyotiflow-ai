from fastapi import APIRouter, Depends, HTTPException, status, Request
from db import get_db
import os
from datetime import datetime, timezone
from typing import Dict, Any

# Import centralized JWT handler
from auth.jwt_config import JWTHandler

router = APIRouter(prefix="/api/ai", tags=["AI"])

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

# தமிழ் - பயனர் AI பரிந்துரைகள் பெறுதல்
@router.get("/user-recommendations")
async def get_user_recommendations(request: Request, db=Depends(get_db)):
    """Get AI-powered personalized recommendations for the user"""
    user_id = get_user_id_as_int(request)
    if not user_id:
        return {"success": True, "data": []}
    
    try:
        # Get user's session history to generate AI recommendations
        user = await db.fetchrow("SELECT email, credits FROM users WHERE id=$1", user_id)
        if not user:
            return {"success": True, "data": []}
        
        # Get user's session patterns
        sessions = await db.fetch("""
            SELECT 
                service_type_id,
                COUNT(*) as session_count,
                MAX(created_at) as last_session
            FROM sessions 
            WHERE user_email = $1 
            GROUP BY service_type_id 
            ORDER BY session_count DESC
        """, user["email"])
        
        # Get available services
        services = await db.fetch("SELECT id, name, description, base_credits FROM service_types")
        
        # Generate AI-powered recommendations
        recommendations = []
        
        # 1. New service recommendations based on user's spiritual journey
        unused_services = [s for s in services if not any(sess["service_type_id"] == s["id"] for sess in sessions)]
        for service in unused_services[:3]:  # Top 3 new services
            recommendations.append({
                "type": "discovery",
                "title": f"Explore {service['name']}",
                "description": f"Discover new spiritual insights through {service['name'].lower()}",
                "service_id": service["id"],
                "credits_required": service["base_credits"],
                "priority": "high" if user["credits"] >= service["base_credits"] else "medium",
                "reason": "new_experience"
            })
        
        # 2. Continue recommendations for services with low usage
        low_usage_services = [s for s in sessions if s["session_count"] < 3]
        for session in low_usage_services[:2]:
            service = next((s for s in services if s["id"] == session["service_type_id"]), None)
            if service:
                recommendations.append({
                    "type": "continuation",
                    "title": f"Dive deeper into {service['name']}",
                    "description": f"You've tried {service['name'].lower()} {session['session_count']} times. Continue your journey.",
                    "service_id": service["id"],
                    "credits_required": service["base_credits"],
                    "priority": "medium",
                    "reason": "low_usage"
                })
        
        # 3. Popular service recommendations
        popular_services = await db.fetch("""
            SELECT service_type_id, COUNT(*) as usage_count
            FROM sessions 
            GROUP BY service_type_id 
            ORDER BY usage_count DESC 
            LIMIT 3
        """)
        
        for popular in popular_services:
            service = next((s for s in services if s["id"] == popular["service_type_id"]), None)
            if service and not any(sess["service_type_id"] == service["id"] for sess in sessions):
                recommendations.append({
                    "type": "trending",
                    "title": f"Join the {service['name']} community",
                    "description": f"Many seekers find {service['name'].lower()} transformative",
                    "service_id": service["id"],
                    "credits_required": service["base_credits"],
                    "priority": "medium",
                    "reason": "popular_choice"
                })
        
        # 4. Credit-based recommendations
        if user["credits"] < 5:
            recommendations.append({
                "type": "credit_boost",
                "title": "Recharge your spiritual journey",
                "description": "Add credits to continue your spiritual exploration",
                "action": "purchase_credits",
                "priority": "high",
                "reason": "low_credits"
            })
        
        return {"success": True, "data": recommendations[:6]}  # Return top 6 recommendations
    except Exception as e:
        print(f"Error generating AI recommendations: {e}")
        return {"success": True, "data": []}

# தமிழ் - AI சுயவிவர பகுப்பாய்வு
@router.get("/profile-analysis")
async def get_profile_analysis(request: Request, db=Depends(get_db)):
    """Get AI analysis of user's spiritual profile"""
    user_id = get_user_id_as_int(request)
    if not user_id:
        return {"success": True, "data": {}}
    
    try:
        user = await db.fetchrow("SELECT email, credits, created_at FROM users WHERE id=$1", user_id)
        if not user:
            return {"success": True, "data": {}}
        
        # Get comprehensive session data
        sessions = await db.fetch("""
            SELECT 
                s.service_type_id,
                st.name as service_name,
                COUNT(*) as session_count,
                AVG(EXTRACT(EPOCH FROM (s.updated_at - s.created_at))) as avg_duration
            FROM sessions s
            JOIN service_types st ON s.service_type_id = st.id
            WHERE s.user_email = $1
            GROUP BY s.service_type_id, st.name
        """, user["email"])
        
        total_sessions = sum(s["session_count"] for s in sessions)
        days_since_join = (datetime.now(timezone.utc) - user["created_at"]).days
        
        # Calculate spiritual journey metrics
        analysis = {
            "journey_stage": "beginner" if total_sessions < 5 else "intermediate" if total_sessions < 20 else "advanced",
            "total_sessions": total_sessions,
            "days_active": days_since_join,
            "sessions_per_day": round(total_sessions / max(days_since_join, 1), 2),
            "favorite_service": max(sessions, key=lambda x: x["session_count"])["service_name"] if sessions else None,
            "exploration_score": len(sessions) / 5 * 100,  # Based on number of different services tried
            "consistency_score": min((total_sessions / max(days_since_join, 1)) * 10, 100),  # Sessions per day * 10
            "spiritual_level": "Seeker" if total_sessions < 10 else "Practitioner" if total_sessions < 30 else "Guide"
        }
        
        return {"success": True, "data": analysis}
    except Exception as e:
        print(f"Error generating profile analysis: {e}")
        return {"success": True, "data": {}} 