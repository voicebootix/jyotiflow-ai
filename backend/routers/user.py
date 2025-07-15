from fastapi import APIRouter, Depends, HTTPException, status, Request
from db import get_db
import os
from datetime import datetime, timezone
import uuid
import logging

# Import the smart pricing service
try:
    from services.prokerala_smart_service import get_prokerala_smart_service
except ImportError:
    get_prokerala_smart_service = None

# Import centralized authentication helper
from auth.auth_helpers import AuthenticationHelper

router = APIRouter(prefix="/api/user", tags=["User"])
logger = logging.getLogger(__name__)

def get_user_id_as_int(request: Request) -> int | None:
    """Extract user ID from JWT token and convert to integer - OPTIONAL"""
    try:
        user_id_str = AuthenticationHelper.get_user_id_optional(request)
        return int(user_id_str) if user_id_str else None
    except (ValueError, TypeError):
        return None

# தமிழ் - பயனர் சுயவிவரம் பெறுதல்
@router.get("/profile")
async def get_profile(request: Request, db=Depends(get_db)):
    user_id = get_user_id_as_int(request)
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
    
    # user_id is already an integer, no need for conversion
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
        "id": user["id"],
        "email": user["email"],
        "name": user["name"],
        "full_name": user["full_name"],
        "credits": user["credits"],
        "role": user["role"],
        "created_at": user["created_at"]
    }

@router.get("/credits")
async def get_credits(request: Request, db=Depends(get_db)):
    user_id = get_user_id_as_int(request)
    if not user_id:
        return {"success": True, "data": {"credits": 0}}
    
    # user_id is already an integer, no need for conversion
    user = await db.fetchrow("SELECT credits FROM users WHERE id=$1", user_id)
    if not user:
        return {"success": True, "data": {"credits": 0}}
    return {"success": True, "data": {"credits": user["credits"]}}

@router.get("/sessions")
async def get_sessions(request: Request, db=Depends(get_db)):
    user_id = get_user_id_as_int(request)
    if not user_id:
        return {"success": True, "data": []}
    
    # user_id is already an integer, no need for conversion
    user = await db.fetchrow("SELECT email FROM users WHERE id=$1", user_id)
    if not user:
        return {"success": True, "data": []}
    
    # Fixed: Changed service_type to service_type_id to match database schema
    sessions = await db.fetch("SELECT id, service_type_id, question, created_at FROM sessions WHERE user_email=$1 ORDER BY created_at DESC", user["email"])
    return {"success": True, "data": [dict(row) for row in sessions]}

@router.get("/cosmic-insights")
async def get_cosmic_insights(request: Request, db=Depends(get_db)):
    """
    Free cosmic insights that show limited data
    Implements smart teasing to encourage credit usage
    """
    user_id = AuthenticationHelper.get_user_id_optional(request)
    
    if not user_id:
        return {
            "status": "guest",
            "message": "Login to see your personalized cosmic insights",
            "teaser": "The stars have wisdom waiting for you...",
            "insights": {
                "general": "🌟 The universe holds infinite possibilities for those who seek",
                "daily": "✨ Today brings opportunities for spiritual growth",
                "love": "💕 Love energy is flowing in your direction",
                "career": "💼 Professional success awaits the prepared mind",
                "spiritual": "🧘 Your spiritual journey is beginning to unfold"
            }
        }
    
    user_id_int = AuthenticationHelper.convert_user_id_to_int(user_id)
    if user_id_int is None:
        return {"status": "error", "message": "Invalid user ID"}
    
    try:
        # Get user's basic info and birth chart data
        user_data = await db.fetchrow("""
            SELECT id, email, full_name, date_of_birth, birth_time, birth_location, 
                   birth_chart_data, credits, created_at
            FROM users 
            WHERE id = $1
        """, user_id_int)
        
        if not user_data:
            return {"status": "error", "message": "User not found"}
        
        # Generate personalized cosmic insights
        insights = await _generate_cosmic_insights(user_id, dict(user_data), db)
        
        # Get personalized service recommendations
        services = await _get_personalized_services(user_id, db)
        
        return {
            "status": "success",
            "user_credits": user_data["credits"],
            "insights": insights,
            "personalized_services": services,
            "upgrade_message": "✨ Unlock your complete cosmic blueprint with a personalized reading",
            "call_to_action": "Get your detailed birth chart analysis and guidance"
        }
    except Exception as e:
        logger.error(f"Error generating cosmic insights: {e}")
        return {
            "status": "error",
            "message": "Unable to generate cosmic insights at this time"
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
        # Import db module to access the pool
        from db import get_db_pool
        db_pool = get_db_pool()
        if not db_pool:
            # Fallback to basic service data if pool not available
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
        
        smart_service = get_prokerala_smart_service(db_pool)
        result = []
        
        for service in services:
            try:
                # Calculate personalized pricing
                cost_analysis = await smart_service.calculate_service_cost(service['id'], user_id)
                
                # Safely access nested dictionary keys with defaults
                pricing_data = cost_analysis.get('pricing', {})
                savings_from_cache = pricing_data.get('savings_from_cache', 0)
                suggested_credits = pricing_data.get('suggested_credits', service['credits_required'])
                user_message = pricing_data.get('user_message', '')
                
                special_offer = savings_from_cache > 0
                
                result.append({
                    "id": service['id'],
                    "name": service['display_name'] or service['name'],
                    "description": service['description'],
                    "original_credits": service['credits_required'],
                    "personalized_credits": suggested_credits,
                    "savings": int(savings_from_cache),
                    "special_offer": special_offer,
                    "user_message": user_message,
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
