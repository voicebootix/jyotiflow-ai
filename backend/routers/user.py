from fastapi import APIRouter, Depends, HTTPException, status, Request
from db import get_db
import jwt
import os
from datetime import datetime, timezone
import uuid
from typing import Dict, Any, Optional
import logging

# Import the smart pricing service
try:
    from services.prokerala_smart_service import get_prokerala_smart_service
except ImportError:
    get_prokerala_smart_service = None

router = APIRouter(prefix="/api/user", tags=["User"])
logger = logging.getLogger(__name__)

# SECURITY FIX: Remove hardcoded fallback
JWT_SECRET = os.getenv("JWT_SECRET")
if not JWT_SECRET:
    raise RuntimeError("JWT_SECRET environment variable is required for security. Please set it before starting the application.")
JWT_ALGORITHM = "HS256"

def get_user_id_from_token(request: Request) -> str:
    """Extract user ID from JWT token - OPTIONAL"""
    try:
        auth = request.headers.get("Authorization")
        if not auth or not auth.startswith("Bearer "):
            return None
        token = auth.split(" ")[1]
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        # SURGICAL FIX: Use 'sub' field to match livechat and deps.py
        return payload.get("sub") or payload.get("user_id")
    except Exception:
        return None

# தமிழ் - பயனர் சுயவிவரம் பெறுதல்
@router.get("/profile")
async def get_profile(request: Request, db=Depends(get_db)):
    user_id = get_user_id_from_token(request)
    if not user_id:
        # Return guest user profile for non-authenticated requests
        return {
            "id": "guest",
            "email": "guest@jyotiflow.ai",
            "name": "Guest User",
            "full_name": "Guest User",
            "credits": 0,
            "role": "guest",
            "created_at": datetime.now(timezone.utc)
        }
    
    user = await db.fetchrow("SELECT id, email, name, full_name, credits, role, created_at FROM users WHERE id=$1", user_id)
    if not user:
        # Return guest user profile if user not found
        return {
            "id": "guest",
            "email": "guest@jyotiflow.ai",
            "name": "Guest User",
            "full_name": "Guest User",
            "credits": 0,
            "role": "guest",
            "created_at": datetime.now(timezone.utc)
        }
    return {
        "id": str(user["id"]),
        "email": user["email"],
        "name": user.get("full_name") or user.get("name"),
        "full_name": user.get("full_name"),
        "credits": user["credits"],
        "role": user.get("role", "user"),  # Include role in response
        "created_at": user["created_at"]
    }

@router.get("/credits")
async def get_credits(request: Request, db=Depends(get_db)):
    user_id = get_user_id_from_token(request)
    if not user_id:
        return {"success": True, "data": {"credits": 0}}
    
    user = await db.fetchrow("SELECT credits FROM users WHERE id=$1", user_id)
    if not user:
        return {"success": True, "data": {"credits": 0}}
    return {"success": True, "data": {"credits": user["credits"]}}

@router.get("/sessions")
async def get_sessions(request: Request, db=Depends(get_db)):
    user_id = get_user_id_from_token(request)
    if not user_id:
        return {"success": True, "data": []}
    
    user = await db.fetchrow("SELECT email FROM users WHERE id=$1", user_id)
    if not user:
        return {"success": True, "data": []}
    sessions = await db.fetch("SELECT id, service_type_id, question, created_at FROM sessions WHERE user_email=$1 ORDER BY created_at DESC", user["email"])
    return {"success": True, "data": [dict(row) for row in sessions]}

@router.get("/cosmic-insights")
async def get_cosmic_insights(request: Request, db=Depends(get_db)):
    """
    Free cosmic insights that show limited data
    Implements smart teasing to encourage credit usage
    """
    user_id = get_user_id_from_token(request)
    
    if not user_id:
        return {
            "status": "guest",
            "message": "Login to see your personalized cosmic insights",
            "teaser": "The stars have wisdom waiting for you...",
            "insights": {
                "general": "🌟 The universe holds infinite possibilities for those who seek",
                "daily": "✨ Today brings opportunities for spiritual growth",
                "love": "💕 Love energy is flowing in your direction",
                "career": "💼 Professional success awaits the prepared mind"
            }
        }
    
    try:
        # Check for existing birth profile
        user_data = await db.fetchrow("""
            SELECT email, name, birth_chart_data, created_at
            FROM users WHERE id = $1
        """, user_id)
        
        if not user_data:
            return {"status": "error", "message": "User not found"}
        
        # Check if user has birth chart data
        if not user_data['birth_chart_data']:
            return {
                "status": "incomplete",
                "message": "Complete your birth profile for free personalized insights",
                "action_required": "add_birth_details",
                "teaser_insights": {
                    "moon_sign": "🌙 Your lunar energy awaits discovery...",
                    "lucky_period": "✨ Auspicious times are hidden in your birth chart",
                    "compatibility": "💕 Cosmic compatibility secrets lie within your stars",
                    "career": "💼 Your professional destiny is written in the planets"
                }
            }
        
        # Get basic insights with smart pricing teaser
        insights = await _generate_cosmic_insights(user_id, user_data, db)
        
        # Get personalized service recommendations with cache-based pricing
        services = await _get_personalized_services(user_id, db)
        
        return {
            "status": "active",
            "user_name": user_data['name'],
            "insights": insights,
            "services": services,
            "call_to_action": "Unlock your complete cosmic blueprint"
        }
        
    except Exception as e:
        logger.error(f"Error in cosmic insights: {e}")
        return {
            "status": "error",
            "message": "Unable to load cosmic insights",
            "error": str(e)
        }

async def _generate_cosmic_insights(user_id: str, user_data: dict, db) -> dict:
    """Generate teaser insights based on user's birth chart data"""
    try:
        birth_data = user_data.get('birth_chart_data', {})
        
        # Extract some basic info if available
        insights = {
            "moon_sign": "🌙 Your moon is in a powerful position for spiritual growth...",
            "lucky_period": "✨ The next 3 days bring special opportunities",
            "compatibility": "💕 Romance energy: High potential for meaningful connections",
            "career": "💼 Professional breakthrough approaching - prepare for success",
            "spiritual": "🧘 Your spiritual journey is entering a transformative phase"
        }
        
        # Add personalized elements if birth data exists
        if birth_data and isinstance(birth_data, dict):
            if 'birth_details' in birth_data:
                details = birth_data['birth_details']
                if 'nakshatra' in details:
                    nakshatra = details['nakshatra'].get('name', 'Unknown')
                    insights['moon_sign'] = f"🌙 Your Nakshatra {nakshatra} brings special blessings..."
                if 'chandra_rasi' in details:
                    rasi = details['chandra_rasi'].get('name', 'Unknown')
                    insights['compatibility'] = f"💕 Your Moon sign {rasi} attracts harmonious relationships..."
        
        # Check for recent activity to personalize timing
        recent_session = await db.fetchrow("""
            SELECT created_at FROM sessions 
            WHERE user_email = $1 
            ORDER BY created_at DESC LIMIT 1
        """, user_data['email'])
        
        if recent_session:
            days_since = (datetime.now(timezone.utc) - recent_session['created_at']).days
            if days_since <= 7:
                insights['special_offer'] = "🎁 Your recent reading unlocks special pricing today!"
        
        return insights
        
    except Exception as e:
        logger.error(f"Error generating cosmic insights: {e}")
        return {
            "moon_sign": "🌙 The cosmos holds wisdom for you...",
            "lucky_period": "✨ Auspicious times are approaching",
            "compatibility": "💕 Love and harmony are in your stars",
            "career": "💼 Success flows to those who seek guidance"
        }

async def _get_personalized_services(user_id: str, db) -> list:
    """Get personalized service recommendations with smart pricing"""
    try:
        # Get available services
        services = await db.fetch("""
            SELECT id, name, display_name, description, credits_required, 
                   duration_minutes, enabled
            FROM service_types 
            WHERE enabled = true 
            ORDER BY credits_required
            LIMIT 5
        """)
        
        if not get_prokerala_smart_service:
            # Return basic service info if smart service not available
            return [
                {
                    "id": service['id'],
                    "name": service['display_name'] or service['name'],
                    "description": service['description'],
                    "credits": service['credits_required'],
                    "duration": service['duration_minutes'],
                    "special_offer": False
                }
                for service in services
            ]
        
        # Get smart pricing for each service
        smart_service = get_prokerala_smart_service(db)
        result = []
        
        for service in services:
            try:
                # Calculate personalized pricing
                cost_analysis = await smart_service.calculate_service_cost(service['id'], user_id)
                
                special_offer = cost_analysis['pricing']['savings_from_cache'] > 0
                
                result.append({
                    "id": service['id'],
                    "name": service['display_name'] or service['name'],
                    "description": service['description'],
                    "original_credits": service['credits_required'],
                    "personalized_credits": cost_analysis['pricing']['suggested_credits'],
                    "savings": int(cost_analysis['pricing']['savings_from_cache']),
                    "special_offer": special_offer,
                    "user_message": cost_analysis['pricing']['user_message'],
                    "duration": service['duration_minutes']
                })
                
            except Exception as e:
                logger.error(f"Error calculating costs for service {service['id']}: {e}")
                # Fallback to basic service info
                result.append({
                    "id": service['id'],
                    "name": service['display_name'] or service['name'],
                    "description": service['description'],
                    "credits": service['credits_required'],
                    "duration": service['duration_minutes'],
                    "special_offer": False
                })
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting personalized services: {e}")
        return [] 