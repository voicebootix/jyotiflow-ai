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

# Schema cache to avoid repeated database queries
_sessions_schema_cache = None

async def _get_sessions_schema(db):
    """Get sessions table schema with caching for performance optimization"""
    global _sessions_schema_cache
    if _sessions_schema_cache is None:
        try:
            columns_result = await db.fetch("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'sessions' AND table_schema = 'public'
            """)
            _sessions_schema_cache = {row['column_name'] for row in columns_result}
            logger.info(f"Cached sessions table schema: {_sessions_schema_cache}")
        except Exception as e:
            logger.exception("Failed to cache sessions table schema", exc_info=e)
            raise
    return _sessions_schema_cache

def _clear_sessions_schema_cache():
    """Clear the sessions schema cache (useful for testing or after schema changes)"""
    global _sessions_schema_cache
    _sessions_schema_cache = None
    logger.info("Sessions schema cache cleared")

# Use centralized authentication helpers - eliminates duplication and inconsistencies
get_user_id_from_token = AuthenticationHelper.get_user_id_optional
convert_user_id_to_int = AuthenticationHelper.convert_user_id_to_int

def get_user_id_as_int(request: Request) -> int | None:
    """Extract user ID from JWT token and convert to integer - OPTIONAL"""
    user_id_str = get_user_id_from_token(request)
    return convert_user_id_to_int(user_id_str)

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
        "name": user["name"] or user["full_name"],
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
    user_id_int = get_user_id_as_int(request)  # Already returns int or None
    if not user_id_int:
        return {"success": True, "data": []}
    
    user = await db.fetchrow("SELECT email FROM users WHERE id=$1", user_id_int)
    if not user:
        return {"success": True, "data": []}
    
    # SECURE: Check column existence first, ensure user privacy always protected
    
    # Step 1: Get cached schema information (performance optimized)
    try:
        available_columns = await _get_sessions_schema(db)
        logger.debug(f"Available sessions columns: {available_columns}")
    except Exception as e:
        logger.exception("Failed to check sessions table columns", exc_info=e)
        raise HTTPException(
            status_code=500,
            detail="Unable to verify database schema"
        )
    
    # SECURITY: Refuse to operate without user filtering capability
    if 'user_email' not in available_columns and 'user_id' not in available_columns:
        logger.error("Sessions table lacks user filtering columns (user_email, user_id) - cannot ensure data privacy")
        raise HTTPException(
            status_code=500,
            detail="Database schema incomplete - user filtering not possible"
        )
    
    # Step 2: Build safe query based on available columns
    select_parts = ['id', 'created_at']  # Always safe
    
    # Add optional columns only if they exist
    if 'service_type' in available_columns:
        select_parts.append("service_type")
    if 'service_type_id' in available_columns and 'service_type' not in available_columns:
        select_parts.append("service_type_id::text as service_type")
    if 'question' in available_columns:
        select_parts.append("question")
    
    # Step 3: Determine user filtering (guaranteed to exist due to check above)
    user_filter = ""
    user_params = []
    if 'user_email' in available_columns:
        user_filter = "WHERE user_email = $1"
        user_params = [user["email"]]
    elif 'user_id' in available_columns:
        user_filter = "WHERE user_id = $1"
        user_params = [user_id_int]
    
    # Step 4: Execute secure query with guaranteed user filtering
    try:
        query = f"""
            SELECT {', '.join(select_parts)}
            FROM sessions 
            {user_filter}
            ORDER BY created_at DESC 
            LIMIT 50
        """
        
        sessions = await db.fetch(query, *user_params)
        logger.info(f"Retrieved {len(sessions)} sessions for user {user_id_int}")
        
        # Step 5: Normalize response format
        sessions_data = []
        for session in sessions:
            session_data = {
                "id": session["id"],
                "service_type": session.get("service_type", "unknown"),
                "question": session.get("question", "No question recorded"),
                "created_at": session["created_at"]
            }
            sessions_data.append(session_data)
        
        return {"success": True, "data": sessions_data}
        
    except Exception as e:
        logger.exception("Sessions query failed", exc_info=e)
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve sessions"
        )
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

from services.spiritual_calendar_service import SpiritualCalendarService
# RAG system import moved to runtime to avoid startup dependencies
from auth.jwt_config import get_user_email_from_token


@router.get("/daily-wisdom")
async def get_daily_wisdom(request: Request, db=Depends(get_db)):
    """
    Provides a personalized, RAG-powered "Daily Wisdom" quote for the user.
    """
    try:
        user_email = get_user_email_from_token(request)
    except Exception:
        user_email = None
        
    if not user_email:
        raise HTTPException(status_code=401, detail="Authentication required")

    try:
        # 1. Get user profile to understand their level
        user_data = await db.fetchrow("SELECT spiritual_level FROM users WHERE email = $1", user_email)
        spiritual_level = user_data['spiritual_level'] if user_data and user_data['spiritual_level'] else 'beginner'

        # 2. Get today's spiritual theme
        calendar_service = SpiritualCalendarService()
        daily_theme = await calendar_service.get_daily_spiritual_theme()
        theme_name = daily_theme.get("theme", "general well-being")

        # 3. Construct a query for the RAG engine
        rag_query = f"I am a '{spiritual_level}' on my spiritual journey. Today's spiritual theme is '{theme_name}'. Please provide me with a short, compassionate, and inspiring 'Daily Wisdom' quote (1-2 sentences) from the perspective of a wise Swamiji that is suitable for my level and today's theme."

        # 4. Call the RAG engine with runtime import
        try:
            from ..enhanced_rag_knowledge_engine import get_rag_enhanced_guidance
            
            rag_response = await get_rag_enhanced_guidance(
                user_query=rag_query,
                birth_details=None, # Not needed for this query
                service_type="daily_wisdom"
            )
            wisdom_quote = rag_response.get("enhanced_guidance", "Embrace the peace within and let your spirit soar. The universe is always guiding you towards your true path.")
        except ImportError:
            logger.warning("RAG system not available for daily wisdom")
            wisdom_quote = "Embrace the peace within and let your spirit soar. The universe is always guiding you towards your true path."
        except Exception as e:
            logger.error(f"RAG query for daily wisdom failed: {e}")
            wisdom_quote = "Embrace the peace within and let your spirit soar. The universe is always guiding you towards your true path."

        return {
            "success": True,
            "daily_wisdom": {
                "quote": wisdom_quote,
                "theme": theme_name,
                "date": daily_theme.get("date")
            }
        }

    except Exception as e:
        logger.error(f"Failed to generate Daily Wisdom for {user_email}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Could not generate your daily wisdom at this time.")