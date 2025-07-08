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

    # --- Call both birth-details and chart endpoints ---
    chart_data = {}
    
    # Basic parameters for API call
    basic_params = {
        "datetime": datetime_str,
        "coordinates": coordinates,
        "ayanamsa": "1"
    }
    
    # Chart-specific parameters
    chart_params = {
        "datetime": datetime_str,
        "coordinates": coordinates,
        "chart_type": "rasi",  # Can be rasi, navamsa, chalit, etc.
        "chart_style": "north-indian",  # north-indian, south-indian, east-indian
        "format": "json"
    }
    
    for attempt in range(2):  # Try once, refresh token and retry if 401
        try:
            token = await get_prokerala_token()
            print(f"[BirthChart] Using Prokerala token: {token}")
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {token}"}
                
                # Get basic birth details
                basic_resp = await client.get(
                    "https://api.prokerala.com/v2/astrology/birth-details",
                    headers=headers,
                    params=basic_params
                )
                print(f"[BirthChart] Birth details status: {basic_resp.status_code}")
                
                if basic_resp.status_code == 401 and attempt == 0:
                    # Token expired, refresh and retry
                    await fetch_prokerala_token()
                    continue
                elif basic_resp.status_code == 200:
                    basic_data = basic_resp.json()
                    print(f"[BirthChart] Birth details response: {basic_data}")
                    if "data" in basic_data:
                        chart_data.update(basic_data["data"])
                else:
                    print(f"[BirthChart] Birth details API error: {basic_resp.status_code} - {basic_resp.text}")
                
                # Get chart visualization data
                chart_resp = await client.get(
                    "https://api.prokerala.com/v2/astrology/chart",
                    headers=headers,
                    params=chart_params
                )
                print(f"[BirthChart] Chart visualization status: {chart_resp.status_code}")
                
                if chart_resp.status_code == 200:
                    chart_visual_data = chart_resp.json()
                    print(f"[BirthChart] Chart visualization response: {chart_visual_data}")
                    if "data" in chart_visual_data:
                        chart_data["chart_visualization"] = chart_visual_data["data"]
                    break
                else:
                    print(f"[BirthChart] Chart visualization API error: {chart_resp.status_code} - {chart_resp.text}")
                    # Continue with just basic data if chart endpoint fails
                    if basic_resp.status_code == 200:
                        break
                    else:
                        raise HTTPException(status_code=503, detail=f"Prokerala API error: {basic_resp.status_code}")
                    
        except Exception as e:
            print(f"[BirthChart] Prokerala API error: {e}")
            if attempt == 1:
                raise HTTPException(status_code=503, detail=f"Failed to fetch birth chart data: {str(e)}")

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
                "data_source": "Prokerala API v2/astrology/birth-details + chart",
                "note": "Real astrological data from Prokerala API with chart visualization"
            }
        }
    }
    
    print(f"[BirthChart] Returning real Prokerala data: {chart_data.keys()}")
    return enhanced_response

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