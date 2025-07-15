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

# Import centralized JWT handler
from auth.jwt_config import JWTHandler

router = APIRouter(prefix="/api/user", tags=["User"])
logger = logging.getLogger(__name__)

def get_user_id_from_token(request: Request) -> str | None:
    """Extract user ID from JWT token - OPTIONAL"""
    try:
        return JWTHandler.get_user_id_from_token(request)
    except Exception:
        return None

<<<<<<< HEAD
def get_user_id_as_int(request: Request) -> int | None:
    """Extract user ID from JWT token and convert to integer - OPTIONAL"""
    try:
        user_id_str = JWTHandler.get_user_id_from_token(request)
        return int(user_id_str) if user_id_str else None
    except (ValueError, TypeError):
=======
def convert_user_id_to_int(user_id: str | None) -> int | None:
    """Convert string user_id to integer for database queries"""
    if not user_id:
        return None
    try:
        return int(user_id)
    except ValueError:
>>>>>>> b6cf023a81d2ea433ed88e2e83deaec274010f50
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
    
    user_id_int = convert_user_id_to_int(user_id)
    if user_id_int is None:
        # Return guest user profile for invalid user IDs (maintain fallback behavior)
        return {
            "id": "guest",
            "email": "guest@jyotiflow.ai",
            "name": "Guest User",
            "full_name": "Guest User",
            "credits": 0,
            "role": "guest",
            "created_at": datetime.now(timezone.utc)
        }
    
    user = await db.fetchrow("SELECT id, email, name, full_name, credits, role, created_at FROM users WHERE id=$1", user_id_int)
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
    
    user_id_int = convert_user_id_to_int(user_id)
    if user_id_int is None:
        return {"success": False, "error": "Invalid user ID"}
    
    user = await db.fetchrow("SELECT credits FROM users WHERE id=$1", user_id_int)
    if not user:
        return {"success": True, "data": {"credits": 0}}
    return {"success": True, "data": {"credits": user["credits"]}}

@router.get("/sessions")
async def get_sessions(request: Request, db=Depends(get_db)):
    user_id = get_user_id_as_int(request)
    if not user_id:
        return {"success": True, "data": []}
    
    user_id_int = convert_user_id_to_int(user_id)
    if user_id_int is None:
        return {"success": False, "error": "Invalid user ID"}
    
    user = await db.fetchrow("SELECT email FROM users WHERE id=$1", user_id_int)
    if not user:
        return {"success": True, "data": []}
<<<<<<< HEAD
    sessions = await db.fetch("SELECT id, service_type_id, question, created_at FROM sessions WHERE user_email=$1 ORDER BY created_at DESC", user["email"])
    return {"success": True, "data": [dict(row) for row in sessions]}

<<<<<<< HEAD
# தமிழ் - கடன் வரலாறு பெறுதல்
@router.get("/credit-history")
async def get_credit_history(request: Request, db=Depends(get_db)):
    """Get user's credit purchase and usage history"""
    user_id = get_user_id_as_int(request)
    if not user_id:
        return {"success": True, "data": []}
    
    try:
        # Get credit transactions from credit_packages table
        history = await db.fetch("""
            SELECT 
                cp.id,
                cp.package_name,
                cp.credits,
                cp.price,
                cp.created_at as purchase_date,
                'purchase' as transaction_type
            FROM credit_packages cp
            WHERE cp.user_id = $1
            ORDER BY cp.created_at DESC
        """, user_id)
        
        return {"success": True, "data": [dict(row) for row in history]}
    except Exception as e:
        print(f"Error fetching credit history: {e}")
        return {"success": True, "data": []}

# தமிழ் - பயனர் பரிந்துரைகள் பெறுதல்
@router.get("/recommendations")
async def get_user_recommendations(request: Request, db=Depends(get_db)):
    """Get personalized recommendations for the user"""
    user_id = get_user_id_as_int(request)
    if not user_id:
        return {"success": True, "data": []}
    
    try:
        # Get user's session history to generate recommendations
        user = await db.fetchrow("SELECT email FROM users WHERE id=$1", user_id)
        if not user:
            return {"success": True, "data": []}
        
        sessions = await db.fetch("""
            SELECT service_type_id, COUNT(*) as session_count
            FROM sessions 
            WHERE user_email = $1 
            GROUP BY service_type_id 
            ORDER BY session_count DESC
        """, user["email"])
        
        # Get available services
        services = await db.fetch("SELECT id, name, description, base_credits FROM service_types")
        
        # Generate recommendations based on usage patterns
        recommendations = []
        for service in services:
            service_sessions = next((s for s in sessions if s["service_type_id"] == service["id"]), None)
            session_count = service_sessions["session_count"] if service_sessions else 0
            
            if session_count == 0:
                # Recommend new services
                recommendations.append({
                    "type": "new_service",
                    "service_id": service["id"],
                    "service_name": service["name"],
                    "description": f"Try {service['name']} for spiritual growth",
                    "priority": "high"
                })
            elif session_count < 3:
                # Recommend continuing with low-usage services
                recommendations.append({
                    "type": "continue_service",
                    "service_id": service["id"],
                    "service_name": service["name"],
                    "description": f"Continue exploring {service['name']}",
                    "priority": "medium"
                })
        
        return {"success": True, "data": recommendations[:5]}  # Return top 5 recommendations
    except Exception as e:
        print(f"Error generating recommendations: {e}")
        return {"success": True, "data": []} 
=======
=======
    sessions = await db.fetch("SELECT id, service_type, question, created_at FROM sessions WHERE user_email=$1 ORDER BY created_at DESC", user["email"])
    return {"success": True, "data": [dict(row) for row in sessions]}

>>>>>>> b6cf023a81d2ea433ed88e2e83deaec274010f50
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
<<<<<<< HEAD
                "career": "💼 Professional success awaits the prepared mind"
            }
        }
    
    try:
        # Check for existing birth profile
        user_data = await db.fetchrow("""
            SELECT email, name, birth_chart_data, created_at
            FROM users WHERE id = $1
        """, user_id)
=======
                "career": "💼 Success awaits those who align with their purpose",
                "spiritual": "🧘 Your spiritual journey is beginning to unfold"
            }
        }
    
    user_id_int = convert_user_id_to_int(user_id)
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
>>>>>>> b6cf023a81d2ea433ed88e2e83deaec274010f50
        
        if not user_data:
            return {"status": "error", "message": "User not found"}
        
<<<<<<< HEAD
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
=======
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
>>>>>>> b6cf023a81d2ea433ed88e2e83deaec274010f50
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
<<<<<<< HEAD
        return [] 
>>>>>>> ebb270206b7cb1ec381dc99947af617c6f103580
=======
        return [] 
>>>>>>> b6cf023a81d2ea433ed88e2e83deaec274010f50
