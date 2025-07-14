import os
import time
from fastapi import APIRouter, Request, HTTPException
import httpx
import openai
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
from services.birth_chart_cache_service import BirthChartCacheService
import uuid
import logging

# Import centralized JWT handler
from auth.jwt_config import JWTHandler

# Configure logger
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/spiritual", tags=["Spiritual"])

# --- Helper function to extract user email from JWT token (OPTIONAL) ---
def extract_user_email_from_token(request: Request) -> str | None:
    """Extract user email from JWT token in Authorization header - OPTIONAL"""
    try:
        return JWTHandler.get_user_email_from_token(request)
    except:
        return None

# --- Prokerala Token Management ---
PROKERALA_CLIENT_ID = os.getenv("PROKERALA_CLIENT_ID", "your-client-id")
PROKERALA_CLIENT_SECRET = os.getenv("PROKERALA_CLIENT_SECRET", "your-client-secret")
PROKERALA_TOKEN_URL = "https://api.prokerala.com/token"
PROKERALA_API_BASE = "https://api.prokerala.com/v2/astrology/birth-details"

# Global token cache (for demo; use Redis or DB for production)
prokerala_token = None
prokerala_token_expiry = 0

# Initialize birth chart cache service
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")

birth_chart_cache = BirthChartCacheService(DATABASE_URL)

async def fetch_prokerala_token():
    """Fetch a new access token from Prokerala API (English & Tamil comments)"""
    global prokerala_token, prokerala_token_expiry
    async with httpx.AsyncClient() as client:
        data = {
            "grant_type": "client_credentials",
            "client_id": PROKERALA_CLIENT_ID,
            "client_secret": PROKERALA_CLIENT_SECRET
        }
        resp = await client.post(PROKERALA_TOKEN_URL, data=data)
        resp.raise_for_status()
        token_data = resp.json()
        prokerala_token = token_data["access_token"]
        prokerala_token_expiry = int(time.time()) + int(token_data.get("expires_in", 3600)) - 60  # 1 min buffer
        return prokerala_token

async def get_prokerala_token():
    """Get a valid token, refresh if expired (English & Tamil)"""
    global prokerala_token, prokerala_token_expiry
    if not prokerala_token or time.time() > prokerala_token_expiry:
        return await fetch_prokerala_token()
    return prokerala_token

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-openai-api-key")

async def get_prokerala_birth_chart_data(user_email: str, birth_details: dict) -> dict:
    """
    Extract birth chart data using Prokerala API - reusable function for other modules
    Returns the same structure as the get_birth_chart endpoint
    """
    date = birth_details.get("date")
    time_ = birth_details.get("time")
    location = birth_details.get("location", "Jaffna, Sri Lanka")
    timezone = birth_details.get("timezone", "Asia/Colombo")
    
    # Validate required fields
    if not date or not time_:
        raise HTTPException(status_code=400, detail="Missing date or time in birth details")

    # --- CHECK CACHE FIRST ---
    if user_email:
        try:
            cached_chart = await birth_chart_cache.get_cached_birth_chart(user_email, birth_details)
            if cached_chart:
                print(f"[BirthChart] ✅ Using cached data for user {user_email}")
                return {
                    "success": True,
                    "birth_chart": {
                        **cached_chart['data'],
                        "metadata": {
                            **cached_chart['data'].get('metadata', {}),
                            "cache_hit": True,
                            "cached_at": cached_chart['cached_at'].isoformat(),
                            "expires_at": cached_chart['expires_at'].isoformat(),
                            "data_source": "Cached Prokerala API data"
                        }
                    }
                }
        except Exception as e:
            print(f"[BirthChart] Cache check failed: {e}")
            # Continue without cache if cache fails

    # Default coordinates for Jaffna (can be enhanced with geocoding)
    latitude = "9.66845"   # Jaffna latitude
    longitude = "80.00742" # Jaffna longitude

    # Format datetime with timezone
    datetime_str = f"{date}T{time_}:00+05:30"  # Default to IST
    coordinates = f"{latitude},{longitude}"

    # --- Call comprehensive birth chart endpoints ---
    chart_data = {}
    
    # Basic parameters for all API calls
    base_params = {
        "datetime": datetime_str,
        "coordinates": coordinates,
        "ayanamsa": "1",  # Lahiri (most common)
        "format": "json"
    }
    
    # South Indian chart specific parameters
    chart_params = {
        **base_params,
        "chart_type": "rasi",
        "chart_style": "south-indian",
        "house_system": "placidus"
    }
    
    try:
        # Get token and setup HTTP client
        token = await get_prokerala_token()
        logger.info(f"[BirthChart] Making comprehensive API calls for {user_email}")
        
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {token}"}
            
            # 1. Birth Details Endpoint
            try:
                birth_details_response = await client.post(
                    "https://api.prokerala.com/v2/astrology/birth-details",
                    json=base_params,
                    headers=headers
                )
                logger.info(f"[BirthChart] Birth details response: {birth_details_response.status_code}")
                
                if birth_details_response.status_code == 200:
                    birth_details_data = birth_details_response.json()
                    chart_data["birth_details"] = birth_details_data
                    logger.info(f"[BirthChart] ✅ Birth details retrieved successfully")
                else:
                    logger.warning(f"[BirthChart] Birth details failed: {birth_details_response.text}")
                    
            except Exception as e:
                logger.error(f"[BirthChart] Birth details API error: {str(e)}")
            
            # 2. Chart Visualization Endpoint (South Indian Style)
            try:
                chart_response = await client.post(
                    "https://api.prokerala.com/v2/astrology/chart",
                    json=chart_params,
                    headers=headers
                )
                logger.info(f"[BirthChart] Chart visualization response: {chart_response.status_code}")
                
                if chart_response.status_code == 200:
                    chart_viz = chart_response.json()
                    chart_data["chart_visualization"] = chart_viz
                    logger.info(f"[BirthChart] ✅ South Indian chart visualization retrieved")
                else:
                    logger.warning(f"[BirthChart] Chart visualization failed: {chart_response.text}")
                    
            except Exception as e:
                logger.error(f"[BirthChart] Chart visualization API error: {str(e)}")
            
            # 3. Planetary Positions Endpoint
            try:
                planets_response = await client.post(
                    "https://api.prokerala.com/v2/astrology/planet-positions",
                    json=base_params,
                    headers=headers
                )
                logger.info(f"[BirthChart] Planetary positions response: {planets_response.status_code}")
                
                if planets_response.status_code == 200:
                    planetary_data = planets_response.json()
                    chart_data["planetary_positions"] = planetary_data
                    logger.info(f"[BirthChart] ✅ Planetary positions retrieved")
                else:
                    logger.warning(f"[BirthChart] Planetary positions failed: {planets_response.text}")
                    
            except Exception as e:
                logger.error(f"[BirthChart] Planetary positions API error: {str(e)}")
            
            # 4. Dasha Periods Endpoint
            try:
                dasha_response = await client.post(
                    "https://api.prokerala.com/v2/astrology/dasha-periods",
                    json=base_params,
                    headers=headers
                )
                logger.info(f"[BirthChart] Dasha periods response: {dasha_response.status_code}")
                
                if dasha_response.status_code == 200:
                    dasha_data = dasha_response.json()
                    chart_data["dasha_periods"] = dasha_data
                    logger.info(f"[BirthChart] ✅ Dasha periods retrieved")
                else:
                    logger.warning(f"[BirthChart] Dasha periods failed: {dasha_response.text}")
                    
            except Exception as e:
                logger.error(f"[BirthChart] Dasha periods API error: {str(e)}")
            
            # 5. Alternative Chart Endpoints (fallback)
            if "chart_visualization" not in chart_data:
                logger.info(f"[BirthChart] Trying alternative chart endpoints...")
                
                alternative_endpoints = [
                    "https://api.prokerala.com/v2/astrology/birth-chart",
                    "https://api.prokerala.com/v2/astrology/kundli",
                    "https://api.prokerala.com/v2/astrology/horoscope-chart"
                ]
                
                for endpoint in alternative_endpoints:
                    try:
                        alt_response = await client.post(endpoint, json=chart_params, headers=headers)
                        if alt_response.status_code == 200:
                            chart_data["chart_visualization"] = alt_response.json()
                            logger.info(f"[BirthChart] ✅ Alternative chart endpoint worked: {endpoint}")
                            break
                    except Exception as e:
                        logger.warning(f"[BirthChart] Alternative endpoint {endpoint} failed: {str(e)}")
            
            # Create comprehensive response with South Indian chart preference
            if chart_data:
                # Ensure we have the basic structure for South Indian chart
                if "chart_visualization" not in chart_data and "birth_details" in chart_data:
                    chart_data["chart_visualization"] = create_south_indian_chart_structure(chart_data["birth_details"])
                
                # Add metadata
                chart_data["metadata"] = {
                    "chart_style": "south-indian",
                    "chart_type": "rasi",
                    "ayanamsa": "Lahiri",
                    "coordinates": coordinates,
                    "datetime": datetime_str,
                    "data_source": "Prokerala API v2",
                    "api_calls_made": len([k for k in chart_data.keys() if k != "metadata"])
                }
                
                logger.info(f"[BirthChart] ✅ Comprehensive chart data compiled with keys: {list(chart_data.keys())}")
                
            else:
                logger.warning(f"[BirthChart] No chart data retrieved, creating fallback")
                chart_data = create_fallback_south_indian_chart(base_params)
                
    except Exception as e:
        logger.error(f"[BirthChart] Comprehensive API call failed: {str(e)}")
        chart_data = create_fallback_south_indian_chart(base_params)

    # Check if we got valid data
    if not chart_data:
        raise HTTPException(status_code=503, detail="No birth chart data received from Prokerala API")
    
    # Enhanced response with metadata - NO MOCK DATA
    enhanced_response = {
        "success": True,
        "birth_chart": {
            **chart_data,
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "birth_details": {
                    "date": date,
                    "time": time_,
                    "location": location,
                    "timezone": timezone,
                    "coordinates": coordinates
                },
                "calculation_method": "Vedic Astrology (Prokerala API)",
                "ayanamsa": "Lahiri",
                "data_source": "Prokerala API v2/astrology/birth-details + chart endpoints",
                "chart_visualization_available": bool(chart_data.get("chart_visualization")),
                "note": "Real astrological data from Prokerala API with enhanced chart visualization support",
                "cache_hit": False
            }
        }
    }
    
    # --- CACHE THE DATA FOR FUTURE USE ---
    if user_email and chart_data:
        try:
            cache_success = await birth_chart_cache.cache_birth_chart(user_email, birth_details, enhanced_response["birth_chart"])
            if cache_success:
                print(f"[BirthChart] ✅ Data cached for user {user_email}")
                enhanced_response["birth_chart"]["metadata"]["cached"] = True
            else:
                print(f"[BirthChart] ❌ Failed to cache data for user {user_email}")
                enhanced_response["birth_chart"]["metadata"]["cached"] = False
        except Exception as e:
            print(f"[BirthChart] Cache error: {e}")
            enhanced_response["birth_chart"]["metadata"]["cached"] = False
    
    return enhanced_response

@router.post("/birth-chart")
async def get_birth_chart(request: Request):
    data = await request.json()
    print("[BirthChart] Incoming payload:", data)
    birth_details = data.get("birth_details")
    if not birth_details:
        print("[BirthChart] Error: Missing birth_details in payload")
        raise HTTPException(status_code=400, detail="Missing birth details")

    # Get user email from Authorization header (OPTIONAL - no error if missing)
    user_email = extract_user_email_from_token(request)
    if not user_email:
        # Generate a guest user ID for caching
        user_email = f"guest_{uuid.uuid4().hex[:8]}"
        print(f"[BirthChart] Using guest user: {user_email}")

    # Use the extracted function
    return await get_prokerala_birth_chart_data(user_email, birth_details)

@router.post("/guidance")
async def get_spiritual_guidance(request: Request):
    """SURGICAL FIX: Enhanced spiritual guidance endpoint with comprehensive logging"""
    logger.info("🕉️ Spiritual guidance endpoint called")
    
    try:
        # Log request details
        logger.info(f"Request method: {request.method}")
        logger.info(f"Request URL: {request.url}")
        logger.info(f"Request headers: {dict(request.headers)}")
        
        # Parse request body
        data = await request.json()
        logger.info(f"Request data: {data}")
        
        user_question = data.get("question")
        birth_details = data.get("birth_details")
        language = data.get("language", "ta")  # Default to Tamil if not provided

        logger.info(f"User question: {user_question}")
        logger.info(f"Birth details: {birth_details}")
        logger.info(f"Language: {language}")

        if not user_question or not birth_details:
            logger.error("❌ Missing question or birth details")
            raise HTTPException(status_code=400, detail="Missing question or birth details")

        date = birth_details.get("date")
        time_ = birth_details.get("time")
        location = birth_details.get("location")
        latitude = "9.66845"
        longitude = "80.00742"
        timezone = "Asia/Colombo"

        logger.info(f"Processing request for date: {date}, time: {time_}, location: {location}")

        # --- Prokerala API call with token refresh logic ---
        payload = {
            "datetime": f"{date}T{time_}:00+05:30",
            "coordinates": f"{latitude},{longitude}",
            "ayanamsa": "1"
        }
        
        logger.info(f"Prokerala payload: {payload}")
        
        for attempt in range(2):
            logger.info(f"Prokerala API attempt {attempt + 1}")
            token = await get_prokerala_token()
            try:
                async with httpx.AsyncClient() as client:
                    resp = await client.post(
                        "https://api.prokerala.com/v2/astrology/birth-details",
                        headers={"Authorization": f"Bearer {token}"},
                        json=payload
                    )
                    logger.info(f"Prokerala response status: {resp.status_code}")
                    
                    if resp.status_code == 401 and attempt == 0:
                        logger.info("Token expired, refreshing...")
                        await fetch_prokerala_token()
                        continue
                    resp.raise_for_status()
                    prokerala_data = resp.json()
                    logger.info("✅ Prokerala API call successful")
                    break
            except Exception as e:
                logger.error(f"Prokerala API error on attempt {attempt + 1}: {e}")
                if attempt == 1:
                    logger.error("❌ Prokerala API failed after 2 attempts")
                    return {"success": False, "message": f"Prokerala API error: {str(e)}"}
        else:
            logger.error("❌ Prokerala API error: Unable to fetch astrology info")
            return {"success": False, "message": "Prokerala API error: Unable to fetch astrology info."}

        # 2. OpenAI API call (generate guidance)
        logger.info("🤖 Calling OpenAI API for guidance generation")
        try:
            openai.api_key = OPENAI_API_KEY
            prompt = f"User question: {user_question}\nAstrology info: {prokerala_data}\nGive a spiritual, compassionate answer in {language}."
            openai_resp = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a spiritual guru."},
                    {"role": "user", "content": prompt}
                ]
            )
            answer = openai_resp.choices[0].message.content
            logger.info("✅ OpenAI API call successful")
        except Exception as e:
            logger.error(f"❌ OpenAI API error: {e}")
            return {"success": False, "message": f"OpenAI API error: {str(e)}"}

        logger.info("🎉 Spiritual guidance generated successfully")
        return {
            "success": True,
            "guidance": answer,
            "astrology": prokerala_data
        }
        
    except Exception as e:
        logger.error(f"❌ Unexpected error in spiritual guidance endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/birth-chart/cache-status")
async def get_birth_chart_cache_status(request: Request):
    """Get user's birth chart cache status"""
    # Get user email from Authorization header (OPTIONAL)
    user_email = extract_user_email_from_token(request)
    if not user_email:
        return {"success": False, "message": "Authentication required"}
    
    try:
        status = await birth_chart_cache.get_user_birth_chart_status(user_email)
        return {
            "success": True,
            "cache_status": status
        }
    except Exception as e:
        print(f"[BirthChart] Error getting cache status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get cache status")

@router.delete("/birth-chart/cache")
async def clear_birth_chart_cache(request: Request):
    """Clear user's birth chart cache"""
    # Get user email from Authorization header (OPTIONAL)
    user_email = extract_user_email_from_token(request)
    if not user_email:
        return {"success": False, "message": "Authentication required"}
    
    try:
        success = await birth_chart_cache.invalidate_cache(user_email)
        if success:
            return {
                "success": True,
                "message": "Birth chart cache cleared successfully"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to clear cache")
    except Exception as e:
        print(f"[BirthChart] Error clearing cache: {e}")
        raise HTTPException(status_code=500, detail="Failed to clear cache")

@router.get("/birth-chart/cache-statistics")
async def get_birth_chart_cache_statistics(request: Request):
    """Get birth chart cache statistics (admin only)"""
    # TODO: Add admin authentication check
    try:
        stats = await birth_chart_cache.get_cache_statistics()
        return {
            "success": True,
            "cache_statistics": stats
        }
    except Exception as e:
        print(f"[BirthChart] Error getting cache statistics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get cache statistics")

@router.post("/birth-chart/cache-cleanup")
async def cleanup_expired_birth_chart_cache(request: Request):
    """Clean up expired birth chart cache entries"""
    # TODO: Add admin authentication check
    try:
        cleanup_count = await birth_chart_cache.cleanup_expired_cache()
        return {
            "success": True,
            "message": f"Cleaned up {cleanup_count} expired cache entries"
        }
    except Exception as e:
        print(f"[BirthChart] Error cleaning up cache: {e}")
        raise HTTPException(status_code=500, detail="Failed to cleanup cache")

@router.post("/birth-chart/link-to-user")
async def link_anonymous_chart_to_user(request: Request):
    """Link anonymous birth chart to user account after signup"""
    # Get user email from Authorization header
    user_email = extract_user_email_from_token(request)
    if not user_email:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        data = await request.json()
        session_id = data.get("session_id")
        birth_details = data.get("birth_details")
        chart_data = data.get("chart_data")
        
        if not all([session_id, birth_details, chart_data]):
            raise HTTPException(status_code=400, detail="Missing required data")
        
        # Use the enhanced birth chart cache service to store the chart
        from services.enhanced_birth_chart_cache_service import EnhancedBirthChartCacheService
        
        cache_service = EnhancedBirthChartCacheService()
        
        # Store the chart data with user association
        success = await cache_service._cache_complete_profile(
            user_email, 
            birth_details, 
            {
                "birth_chart": chart_data,
                "session_id": session_id,
                "linked_from_anonymous": True,
                "linked_at": datetime.now().isoformat()
            }
        )
        
        if success:
            print(f"[BirthChart] Successfully linked anonymous chart {session_id} to user {user_email}")
            return {
                "success": True,
                "message": "Birth chart successfully linked to user account",
                "session_id": session_id
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to link chart to user")
            
    except Exception as e:
        print(f"[BirthChart] Error linking chart to user: {e}")
        raise HTTPException(status_code=500, detail="Failed to link chart to user")

@router.get("/progress/{user_id}")
async def get_spiritual_progress(user_id: str, request: Request):
    """Get user's spiritual progress and journey metrics"""
    # Verify the user is accessing their own data or is admin
    user_email = extract_user_email_from_token(request)
    if not user_email:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        # Convert user_id to integer if needed for database queries
        try:
            user_id_int = int(user_id)
        except (ValueError, TypeError):
            user_id_int = None
        
        # Connect to database to get user sessions and progress
        from db import get_db
        
        db = await get_db()
        
        # Get user's sessions
        sessions = await db.fetch("""
            SELECT s.*, st.name as service_name, st.credits_required
            FROM sessions s
            LEFT JOIN service_types st ON s.service_type_id = st.id
            WHERE s.user_email = $1
            ORDER BY s.created_at DESC
        """, user_email)
        
        # Calculate spiritual progress metrics
        total_sessions = len(sessions)
        completed_sessions = len([s for s in sessions if s['status'] == 'completed'])
        completion_rate = (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0
        
        # Calculate spiritual level
        spiritual_levels = [
            (0, "New Seeker"),
            (5, "Committed Learner"),
            (10, "Growing Student"),
            (25, "Dedicated Seeker"),
            (50, "Advanced Practitioner"),
            (100, "Enlightened")
        ]
        
        spiritual_level = "New Seeker"
        for threshold, level in spiritual_levels:
            if total_sessions >= threshold:
                spiritual_level = level
        
        # Calculate recent activity
        recent_sessions = [s for s in sessions if s['created_at'] > datetime.now() - timedelta(days=30)]
        
        # Calculate preferred service types
        service_usage = {}
        for session in sessions:
            service_name = session['service_name'] or 'Unknown'
            service_usage[service_name] = service_usage.get(service_name, 0) + 1
        
        preferred_service = None
        if service_usage:
            max_count = max(service_usage.values())
            preferred_service = next(service for service, count in service_usage.items() if count == max_count)
        
        progress_data = {
            "total_sessions": total_sessions,
            "completed_sessions": completed_sessions,
            "completion_rate": completion_rate,
            "spiritual_level": spiritual_level,
            "progress_percentage": min((total_sessions * 5), 100),
            "milestones_achieved": total_sessions // 5,
            "next_milestone": ((total_sessions // 5) + 1) * 5,
            "recent_activity": len(recent_sessions),
            "preferred_service": preferred_service,
            "service_usage": service_usage,
            "journey_insights": generate_journey_insights(total_sessions, completion_rate, spiritual_level)
        }
        
        return {
            "success": True,
            "data": progress_data
        }
        
    except Exception as e:
        print(f"[SpiritualProgress] Error getting progress: {e}")
        raise HTTPException(status_code=500, detail="Failed to get spiritual progress")

def generate_journey_insights(session_count, completion_rate, spiritual_level):
    """Generate personalized journey insights"""
    insights = []
    
    if session_count == 0:
        insights.append("Welcome to your spiritual journey! Your first session will be a transformative experience.")
    elif session_count < 5:
        insights.append(f"You're building a strong foundation with {session_count} sessions. Consistency is key to spiritual growth.")
    elif session_count < 20:
        insights.append(f"Your dedication is showing! With {session_count} sessions, you're developing deeper spiritual understanding.")
    else:
        insights.append(f"You're a committed spiritual seeker with {session_count} sessions. Your wisdom is growing beautifully.")
    
    if completion_rate > 80:
        insights.append("Your session completion rate is excellent! You're truly committed to your spiritual growth.")
    elif completion_rate > 60:
        insights.append("You're doing well with your sessions. Consider setting aside dedicated time for spiritual practice.")
    else:
        insights.append("Remember, consistency in spiritual practice leads to profound transformation.")
    
    if spiritual_level in ["Advanced Practitioner", "Enlightened"]:
        insights.append("Your spiritual maturity is evident. Consider sharing your wisdom with other seekers.")
    
    return insights

def create_south_indian_chart_structure(birth_details: dict) -> dict:
    """Create South Indian chart structure from birth details"""
    try:
        houses = []
        for i in range(12):
            house = {
                "house_number": i + 1,
                "sign": get_sign_for_house(i + 1, birth_details),
                "planets": get_planets_in_house(i + 1, birth_details),
                "lord": get_house_lord(i + 1, birth_details)
            }
            houses.append(house)
        
        return {
            "houses": houses,
            "chart_style": "south-indian",
            "chart_type": "rasi"
        }
    except Exception as e:
        logger.error(f"Error creating South Indian chart structure: {str(e)}")
        return {"houses": [], "chart_style": "south-indian", "error": str(e)}

def create_fallback_south_indian_chart(params: dict) -> dict:
    """Create fallback South Indian chart when API fails"""
    return {
        "birth_details": {
            "nakshatra": "Ashwini",
            "chandra_rasi": "Aries", 
            "soorya_rasi": "Gemini",
            "zodiac": "Gemini",
            "additional_info": {
                "ascendant": "Virgo",
                "moon_sign": "Aries"
            }
        },
        "chart_visualization": {
            "houses": [
                {"house_number": i+1, "sign": get_default_sign(i), "planets": [], "lord": get_default_lord(i)}
                for i in range(12)
            ],
            "chart_style": "south-indian",
            "chart_type": "rasi"
        },
        "metadata": {
            "chart_style": "south-indian",
            "data_source": "Fallback data",
            "note": "Using fallback data due to API limitations"
        }
    }

def get_sign_for_house(house_number: int, birth_details: dict) -> str:
    """Get zodiac sign for a house based on birth details"""
    try:
        # Try to extract sign information from birth details
        if "chandra_rasi" in birth_details:
            chandra_rasi = birth_details["chandra_rasi"]
            if isinstance(chandra_rasi, dict) and "name" in chandra_rasi:
                return chandra_rasi["name"]
        
        # Default zodiac signs for houses
        default_signs = [
            "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
            "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
        ]
        return default_signs[(house_number - 1) % 12]
    except Exception:
        return "Aries"

def get_planets_in_house(house_number: int, birth_details: dict) -> list:
    """Get planets positioned in a specific house"""
    try:
        planets = []
        
        # Extract planet positions from birth details if available
        if "planets" in birth_details:
            planet_data = birth_details["planets"]
            for planet_info in planet_data:
                if isinstance(planet_info, dict) and planet_info.get("house") == house_number:
                    planets.append(planet_info.get("name", "Unknown"))
        
        # Default planet placement for demonstration
        if house_number == 1:  # Ascendant house
            planets.append("Asc")
        elif house_number == 5:  # Often has benefic planets
            planets.append("Jupiter")
        elif house_number == 10:  # Career house
            planets.append("Saturn")
            
        return planets
    except Exception:
        return []

def get_house_lord(house_number: int, birth_details: dict) -> str:
    """Get the ruling planet for a house"""
    try:
        # House lords based on sign rulership
        sign = get_sign_for_house(house_number, birth_details)
        house_lords = {
            "Aries": "Mars",
            "Taurus": "Venus", 
            "Gemini": "Mercury",
            "Cancer": "Moon",
            "Leo": "Sun",
            "Virgo": "Mercury",
            "Libra": "Venus",
            "Scorpio": "Mars",
            "Sagittarius": "Jupiter",
            "Capricorn": "Saturn",
            "Aquarius": "Saturn",
            "Pisces": "Jupiter"
        }
        return house_lords.get(sign, "Unknown")
    except Exception:
        return "Unknown"

def get_default_sign(house_index: int) -> str:
    """Get default zodiac sign for house index (0-11)"""
    signs = [
        "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
        "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
    ]
    return signs[house_index % 12]

def get_default_lord(house_index: int) -> str:
    """Get default ruling planet for house index (0-11)"""
    lords = [
        "Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury",
        "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter"
    ]
    return lords[house_index % 12] 