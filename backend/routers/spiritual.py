import os
from fastapi import APIRouter, Request, HTTPException
import httpx
import openai

router = APIRouter(prefix="/api/spiritual", tags=["Spiritual"])

PROKERALA_API_KEY = os.getenv("PROKERALA_API_KEY", "your-prokerala-api-key")
print("DEBUG: PROKERALA_API_KEY =", PROKERALA_API_KEY)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-openai-api-key")

@router.post("/birth-chart")
async def get_birth_chart(request: Request):
    data = await request.json()
    birth_details = data.get("birth_details")
    if not birth_details:
        raise HTTPException(status_code=400, detail="Missing birth details")

    date = birth_details.get("date")  # "1988-03-02"
    time = birth_details.get("time")  # "05:00"
    # location string: "jaffna,srilanka" → use static lat/lon for demo
    latitude = "9.66845"   # Jaffna latitude
    longitude = "80.00742" # Jaffna longitude

    # Combine date and time to ISO format
    datetime_str = f"{date}T{time}:00+05:30"
    coordinates = f"{latitude},{longitude}"

    payload = {
        "datetime": datetime_str,
        "coordinates": coordinates,
        "ayanamsa": 1
    }

    try:
        async with httpx.AsyncClient() as client:
            prokerala_resp = await client.post(
                "https://api.prokerala.com/v2/astrology/birth-details",
                headers={"Authorization": f"Bearer {PROKERALA_API_KEY}"},
                json=payload
            )
            prokerala_resp.raise_for_status()
            birth_chart_data = prokerala_resp.json()
    except Exception as e:
        return {"success": False, "message": f"Prokerala API error: {str(e)}"}

    return {
        "success": True,
        "birth_chart": birth_chart_data
    }

@router.post("/guidance")
async def get_spiritual_guidance(request: Request):
    data = await request.json()
    user_question = data.get("question")
    birth_details = data.get("birth_details")  # Should be a dict: {date, time, location}

    if not user_question or not birth_details:
        raise HTTPException(status_code=400, detail="Missing question or birth details")

    # Extract date, time, location (split location into latitude, longitude, timezone if needed)
    date = birth_details.get("date")
    time = birth_details.get("time")
    location = birth_details.get("location")
    # For demo: use dummy values for lat/lon/timezone (replace with real geocoding if needed)
    latitude = "9.66845"  # Jaffna latitude
    longitude = "80.00742"  # Jaffna longitude
    timezone = "Asia/Colombo"

    # 1. Prokerala API call (astrology info)
    try:
        async with httpx.AsyncClient() as client:
            params = {
                "date": date,
                "time": time,
                "latitude": latitude,
                "longitude": longitude,
                "timezone": timezone
            }
            prokerala_resp = await client.get(
                "https://api.prokerala.com/v2/astrology/birth-details",
                headers={"Authorization": f"Bearer {PROKERALA_API_KEY}"},
                params=params
            )
            prokerala_resp.raise_for_status()
            prokerala_data = prokerala_resp.json()
    except Exception as e:
        return {"success": False, "message": f"Prokerala API error: {str(e)}"}

    # 2. OpenAI API call (generate guidance)
    try:
        openai.api_key = OPENAI_API_KEY
        prompt = f"User question: {user_question}\nAstrology info: {prokerala_data}\nGive a spiritual, compassionate answer in Tamil."
        openai_resp = openai.ChatCompletion.create(
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