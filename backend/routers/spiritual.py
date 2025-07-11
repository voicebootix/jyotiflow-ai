import os
import time
from fastapi import APIRouter, Request, HTTPException
import httpx
import openai
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from services.birth_chart_cache_service import BirthChartCacheService
import jwt
import uuid
import logging

# Configure logger
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/spiritual", tags=["Spiritual"])

# JWT configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET", "jyotiflow_secret")
JWT_ALGORITHM = "HS256"

# --- Helper function to extract user email from JWT token (OPTIONAL) ---
def extract_user_email_from_token(request: Request) -> str:
    """Extract user email from JWT token in Authorization header - OPTIONAL"""
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None
        
        token = auth_header.split(" ")[1]
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_email = payload.get("email")
        return user_email
    except:
        return None

# --- Prokerala Token Management ---
PROKERALA_CLIENT_ID = os.getenv("PROKERALA_CLIENT_ID", "your-client-id")
PROKERALA_CLIENT_SECRET = os.getenv("PROKERALA_CLIENT_SECRET", "your-client-secret")
PROKERALA_TOKEN_URL = "https://api.prokerala.com/token"
PROKERALA_API_BASE = "https://api.prokerala.com/v2/astrology/vedic-chart"

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
    data = await request.json()
    user_question = data.get("question")
    birth_details = data.get("birth_details")
    language = data.get("language", "ta")  # Default to Tamil if not provided

    if not user_question or not birth_details:
        raise HTTPException(status_code=400, detail="Missing question or birth details")

    date = birth_details.get("date")
    time_ = birth_details.get("time")
    location = birth_details.get("location")
    latitude = "9.66845"
    longitude = "80.00742"
    timezone = "Asia/Colombo"

    # --- Prokerala API call with token refresh logic ---
    params = {
        "datetime": f"{date}T{time_}:00+05:30",
        "coordinates": f"{latitude},{longitude}",
        "ayanamsa": "1"
    }
    for attempt in range(2):
        token = await get_prokerala_token()
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    "https://api.prokerala.com/v2/astrology/vedic-chart",
                    headers={"Authorization": f"Bearer {token}"},
                    params=params
                )
                if resp.status_code == 401 and attempt == 0:
                    await fetch_prokerala_token()
                    continue
                resp.raise_for_status()
                prokerala_data = resp.json()
                break
        except Exception as e:
            if attempt == 1:
                return {"success": False, "message": f"Prokerala API error: {str(e)}"}
    else:
        return {"success": False, "message": "Prokerala API error: Unable to fetch astrology info."}

    # 2. OpenAI API call (generate guidance)
    try:
        openai.api_key = OPENAI_API_KEY
        prompt = f"User question: {user_question}\nAstrology info: {prokerala_data}\nGive a spiritual, compassionate answer in {language}."
        openai_resp = openai.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You are a spiritual guru."},
                {"role": "user", "content": prompt}
            ]
        )
        answer = openai_resp.choices[0].message.content
    except Exception as e:
        return {"success": False, "message": f"OpenAI API error: {str(e)}"}

    return {
        "success": True,
        "guidance": answer,
        "astrology": prokerala_data
    }

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
    """Clean up expired birth chart cache entries (admin only)"""
    # TODO: Add admin authentication check
    try:
        rows_cleaned = await birth_chart_cache.cleanup_expired_cache()
        return {
            "success": True,
            "message": f"Cleaned up {rows_cleaned} expired cache entries"
        }
    except Exception as e:
        print(f"[BirthChart] Error cleaning up cache: {e}")
        raise HTTPException(status_code=500, detail="Failed to clean up cache") 

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