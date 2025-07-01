import os
from fastapi import APIRouter, Request, HTTPException
import httpx
import openai

router = APIRouter(prefix="/api/spiritual", tags=["Spiritual"])

PROKERALA_API_KEY = os.getenv("PROKERALA_API_KEY", "your-prokerala-api-key")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-openai-api-key")

@router.post("/guidance")
async def get_spiritual_guidance(request: Request):
    data = await request.json()
    user_question = data.get("question")
    birth_details = data.get("birth_details")  # Should be a dict: {date, time, location}

    if not user_question or not birth_details:
        raise HTTPException(status_code=400, detail="Missing question or birth details")

    # 1. Prokerala API call (astrology info)
    try:
        async with httpx.AsyncClient() as client:
            prokerala_resp = await client.post(
                "https://api.prokerala.com/v2/astrology/birth-details",
                headers={"Authorization": f"Bearer {PROKERALA_API_KEY}"},
                json=birth_details
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