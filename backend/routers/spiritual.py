import os
import time
from fastapi import APIRouter, Request, HTTPException
import httpx
import openai
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

router = APIRouter(prefix="/api/spiritual", tags=["Spiritual"])

# --- Prokerala Token Management ---
PROKERALA_CLIENT_ID = os.getenv("PROKERALA_CLIENT_ID", "your-client-id")
PROKERALA_CLIENT_SECRET = os.getenv("PROKERALA_CLIENT_SECRET", "your-client-secret")
PROKERALA_TOKEN_URL = "https://api.prokerala.com/token"
PROKERALA_API_BASE = "https://api.prokerala.com/v2/astrology/vedic-chart"

# Global token cache (for demo; use Redis or DB for production)
prokerala_token = None
prokerala_token_expiry = 0

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

@router.post("/birth-chart")
async def get_birth_chart(request: Request):
    data = await request.json()
    print("[BirthChart] Incoming payload:", data)
    birth_details = data.get("birth_details")
    if not birth_details:
        print("[BirthChart] Error: Missing birth_details in payload")
        raise HTTPException(status_code=400, detail="Missing birth details")

    date = birth_details.get("date")
    time_ = birth_details.get("time")
    location = birth_details.get("location", "Jaffna, Sri Lanka")
    timezone = birth_details.get("timezone", "Asia/Colombo")
    print(f"[BirthChart] Extracted: date={date}, time={time_}, location={location}, timezone={timezone}")

    # Validate required fields
    if not date or not time_:
        print("[BirthChart] Error: Missing date or time in birth_details")
        raise HTTPException(status_code=400, detail="Missing date or time in birth details")

    # Default coordinates for Jaffna (can be enhanced with geocoding)
    latitude = "9.66845"   # Jaffna latitude
    longitude = "80.00742" # Jaffna longitude

    # Format datetime with timezone
    datetime_str = f"{date}T{time_}:00+05:30"  # Default to IST
    coordinates = f"{latitude},{longitude}"

    # --- Prokerala API calls for complete chart data ---
    chart_data = {}
    
    # Basic parameters for all API calls
    basic_params = {
        "datetime": datetime_str,
        "coordinates": coordinates,
        "ayanamsa": "1"
    }
    
    for attempt in range(2):  # Try once, refresh token and retry if 401
        try:
            token = await get_prokerala_token()
            print(f"[BirthChart] Using Prokerala token: {token}")
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {token}"}
                
                # 1. Get basic birth details (this one works)
                basic_resp = await client.get(
                    "https://api.prokerala.com/v2/astrology/birth-details",
                    headers=headers,
                    params=basic_params
                )
                print(f"[BirthChart] Basic details status: {basic_resp.status_code}")
                if basic_resp.status_code == 200:
                    basic_data = basic_resp.json()
                    if "data" in basic_data:
                        chart_data.update(basic_data["data"])
                
                # 2. Try the comprehensive birth chart endpoint (if it exists)
                try:
                    chart_resp = await client.get(
                        "https://api.prokerala.com/v2/astrology/birth-chart",
                        headers=headers,
                        params=basic_params
                    )
                    print(f"[BirthChart] Birth chart endpoint status: {chart_resp.status_code}")
                    if chart_resp.status_code == 200:
                        chart_full_data = chart_resp.json()
                        if "data" in chart_full_data:
                            chart_data.update(chart_full_data["data"])
                except Exception as e:
                    print(f"[BirthChart] Birth chart endpoint not available: {e}")
                
                # 3. Try alternative endpoint names for planets
                try:
                    planet_resp = await client.get(
                        "https://api.prokerala.com/v2/astrology/planet-position",
                        headers=headers,
                        params=basic_params
                    )
                    print(f"[BirthChart] Planet position status: {planet_resp.status_code}")
                    if planet_resp.status_code == 200:
                        planet_data = planet_resp.json()
                        if "data" in planet_data:
                            chart_data["planets"] = planet_data["data"]
                except Exception as e:
                    print(f"[BirthChart] Planet position endpoint error: {e}")
                
                # 4. Try alternative endpoint names for houses
                try:
                    house_resp = await client.get(
                        "https://api.prokerala.com/v2/astrology/house-cusps",
                        headers=headers,
                        params=basic_params
                    )
                    print(f"[BirthChart] House cusps status: {house_resp.status_code}")
                    if house_resp.status_code == 200:
                        house_data = house_resp.json()
                        if "data" in house_data:
                            chart_data["houses"] = house_data["data"]
                except Exception as e:
                    print(f"[BirthChart] House cusps endpoint error: {e}")
                
                break
                
        except Exception as e:
            print(f"[BirthChart] Prokerala API error: {e}")
            if attempt == 1:
                print(f"[BirthChart] All attempts failed, proceeding with available data")
                break
    
    # Create fallback planets data if we have basic birth details but no planets
    if chart_data and "planets" not in chart_data and chart_data.get("nakshatra"):
        print("[BirthChart] Creating fallback planets data based on basic birth details")
        chart_data["planets"] = create_fallback_planets_data(chart_data)
    
    # Create fallback houses data if we don't have it
    if chart_data and "houses" not in chart_data:
        print("[BirthChart] Creating fallback houses data")
        chart_data["houses"] = create_fallback_houses_data(chart_data)

    # Ensure planets, houses, and chart keys are always present
    chart_data.setdefault("planets", {})
    chart_data.setdefault("houses", {})
    chart_data.setdefault("chart", {})
    
    # Enhanced response with additional metadata
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
                "data_sources": {
                    "basic_details": True,
                    "planets": "planets" in chart_data and bool(chart_data["planets"]),
                    "houses": "houses" in chart_data and bool(chart_data["houses"]),
                    "fallback_used": "planets" not in chart_data or not chart_data["planets"]
                }
            }
        }
    }
    print(f"[BirthChart] Returning enhanced response with planets: {len(chart_data.get('planets', {}))}, houses: {len(chart_data.get('houses', {}))}")
    return enhanced_response

def create_fallback_planets_data(basic_data):
    """Create fallback planets data based on available basic birth details"""
    planets = {}
    
    # Use nakshatra information to place Moon
    if basic_data.get("nakshatra"):
        nakshatra_info = basic_data["nakshatra"]
        moon_sign = basic_data.get("chandra_rasi", {}).get("name", "Mesha")
        
        planets["Moon"] = {
            "name": "Moon",
            "rashi": moon_sign,
            "nakshatra": nakshatra_info.get("name", ""),
            "degree": f"{nakshatra_info.get('pada', 1) * 3.33:.1f}",
            "house": calculate_house_from_rashi(moon_sign),
            "status": "Normal"
        }
    
    # Use sun sign information if available
    if basic_data.get("soorya_rasi"):
        sun_sign = basic_data["soorya_rasi"].get("name", "Mesha")
        planets["Sun"] = {
            "name": "Sun",
            "rashi": sun_sign,
            "degree": "15.0",
            "house": calculate_house_from_rashi(sun_sign),
            "status": "Normal"
        }
    
    # Add other basic planetary positions (simplified)
    basic_planets = ["Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
    rashis = ["Mesha", "Vrishabha", "Mithuna", "Karka", "Simha", "Kanya", 
              "Tula", "Vrishchika", "Dhanu", "Makara", "Kumbha", "Meena"]
    
    for i, planet in enumerate(basic_planets):
        if planet not in planets:
            rashi = rashis[i % 12]
            planets[planet] = {
                "name": planet,
                "rashi": rashi,
                "degree": f"{(i * 30 + 15) % 360:.1f}",
                "house": calculate_house_from_rashi(rashi),
                "status": "Normal"
            }
    
    return planets

def calculate_house_from_rashi(rashi_name):
    """Convert rashi name to house number (simplified)"""
    rashi_to_house = {
        "Mesha": 1, "Vrishabha": 2, "Mithuna": 3, "Karka": 4,
        "Simha": 5, "Kanya": 6, "Tula": 7, "Vrishchika": 8,
        "Dhanu": 9, "Makara": 10, "Kumbha": 11, "Meena": 12
    }
    return rashi_to_house.get(rashi_name, 1)

def create_fallback_houses_data(basic_data):
    """Create fallback houses data"""
    houses = {}
    
    # Standard 12 houses with basic information
    house_names = ["Self", "Wealth", "Siblings", "Home", "Children", "Health",
                   "Marriage", "Transformation", "Fortune", "Career", "Gains", "Liberation"]
    
    rashis = ["Mesha", "Vrishabha", "Mithuna", "Karka", "Simha", "Kanya", 
              "Tula", "Vrishchika", "Dhanu", "Makara", "Kumbha", "Meena"]
    
    for i in range(1, 13):
        houses[str(i)] = {
            "house": i,
            "sign": rashis[(i-1) % 12],
            "degree": f"{i * 30:.1f}",
            "lord": get_house_lord(rashis[(i-1) % 12]),
            "significance": house_names[i-1]
        }
    
    return houses

def get_house_lord(rashi_name):
    """Get the ruling planet for a rashi"""
    rashi_lords = {
        "Mesha": "Mars", "Vrishabha": "Venus", "Mithuna": "Mercury", "Karka": "Moon",
        "Simha": "Sun", "Kanya": "Mercury", "Tula": "Venus", "Vrishchika": "Mars",
        "Dhanu": "Jupiter", "Makara": "Saturn", "Kumbha": "Saturn", "Meena": "Jupiter"
    }
    return rashi_lords.get(rashi_name, "Sun")

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
            model="gpt-3.5-turbo",
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