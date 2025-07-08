from fastapi import APIRouter, Depends, HTTPException, Request
from db import get_db
import jwt
import os
import time
from datetime import datetime, timezone
import uuid
from typing import Dict, Any
import asyncio

# PROKERALA INTEGRATION - Using existing working logic from spiritual.py
import httpx
import openai

PROKERALA_CLIENT_ID = os.getenv("PROKERALA_CLIENT_ID", "your-client-id")
PROKERALA_CLIENT_SECRET = os.getenv("PROKERALA_CLIENT_SECRET", "your-client-secret")
PROKERALA_TOKEN_URL = "https://api.prokerala.com/token"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-openai-api-key")

# Global token cache
prokerala_token = None
prokerala_token_expiry = 0

async def fetch_prokerala_token():
    """Fetch a new access token from Prokerala API"""
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
        prokerala_token_expiry = int(time.time()) + int(token_data.get("expires_in", 3600)) - 60
        return prokerala_token

async def get_prokerala_token():
    """Get a valid token, refresh if expired"""
    global prokerala_token, prokerala_token_expiry
    if not prokerala_token or time.time() > prokerala_token_expiry:
        return await fetch_prokerala_token()
    return prokerala_token

async def get_prokerala_chart_data(birth_details: Dict[str, Any]) -> Dict[str, Any]:
    """Get birth chart data from Prokerala - MOVED FROM spiritual.py"""
    date = birth_details.get("date")
    time_str = birth_details.get("time")
    location = birth_details.get("location", "Jaffna, Sri Lanka")
    
    # Format datetime with timezone
    datetime_str = f"{date}T{time_str}:00+05:30"
    coordinates = "9.66845,80.00742"  # Default Jaffna coordinates
    
    params = {
        "datetime": datetime_str,
        "coordinates": coordinates,
        "ayanamsa": "1"
    }
    
    chart_data = {}
    
    for attempt in range(2):  # Try once, refresh token and retry if 401
        try:
            token = await get_prokerala_token()
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {token}"}
                
                # Get birth details
                basic_resp = await client.get(
                    "https://api.prokerala.com/v2/astrology/birth-details",
                    headers=headers,
                    params=params
                )
                if basic_resp.status_code == 200:
                    chart_data.update(basic_resp.json())
                
                # Get planets data
                planets_resp = await client.get(
                    "https://api.prokerala.com/v2/astrology/planets",
                    headers=headers,
                    params=params
                )
                if planets_resp.status_code == 200:
                    planets_data = planets_resp.json()
                    if "data" in planets_data:
                        chart_data["planets"] = planets_data["data"]
                
                # Get houses data
                houses_resp = await client.get(
                    "https://api.prokerala.com/v2/astrology/houses",
                    headers=headers,
                    params=params
                )
                if houses_resp.status_code == 200:
                    houses_data = houses_resp.json()
                    if "data" in houses_data:
                        chart_data["houses"] = houses_data["data"]
                
                # Ensure required keys exist
                chart_data.setdefault("planets", {})
                chart_data.setdefault("houses", {})
                chart_data.setdefault("data", {})
                
                return chart_data
                
        except Exception as e:
            if attempt == 0 and "401" in str(e):
                await fetch_prokerala_token()
                continue
            raise e
    
    # Return minimal data if all attempts fail
    return {
        "data": {
            "nakshatra": {"name": "Unable to calculate"},
            "chandra_rasi": {"name": "Unable to calculate"}
        },
        "error": "Prokerala API unavailable"
    }

async def generate_spiritual_guidance_with_ai(question: str, astrology_data: Dict[str, Any]) -> str:
    """Generate spiritual guidance using OpenAI - MOVED FROM spiritual.py"""
    try:
        openai.api_key = OPENAI_API_KEY
        prompt = f"""You are Swami Jyotirananthan, a revered Tamil spiritual master.

User's Question: {question}
Astrological Data: {astrology_data}

Provide compassionate spiritual guidance that includes:
1. Direct response to their question
2. Astrological insights from their chart
3. Tamil spiritual wisdom
4. Practical advice

Write in English with Tamil spiritual concepts."""

        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are Swami Jyotirananthan, a compassionate Tamil spiritual guide."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        # Fallback guidance if OpenAI fails
        return f"""🕉️ Divine Guidance from Swami Jyotirananthan

Your Question: {question}

Though the AI guidance is temporarily unavailable, I offer you this wisdom from the eternal Tamil tradition:

The ancient texts teach us that every question arises from the soul's journey toward truth. Your sincere inquiry itself shows spiritual awakening.

May divine grace illuminate your path forward.

Om Namah Shivaya 🙏"""

PROKERALA_AVAILABLE = bool(PROKERALA_CLIENT_ID and PROKERALA_CLIENT_ID != "your-client-id")

router = APIRouter(prefix="/api/sessions", tags=["Sessions"])

JWT_SECRET = os.getenv("JWT_SECRET", "jyotiflow_secret")
JWT_ALGORITHM = "HS256"

def get_user_id_from_token(request: Request) -> str:
    """Extract user ID from JWT token"""
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = auth.split(" ")[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload["user_id"]
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

async def schedule_session_followup(session_id: str, user_email: str, service_type: str, db):
    """Schedule automatic follow-up after session completion"""
    try:
        # Import here to avoid circular imports
        from utils.followup_service import FollowUpService
        from schemas.followup import FollowUpRequest, FollowUpChannel
        
        followup_service = FollowUpService(db)
        
        # Get default session follow-up template
        conn = await db.get_connection()
        try:
            if hasattr(db, 'is_sqlite') and db.is_sqlite:
                template = await conn.fetchrow("""
                    SELECT id FROM follow_up_templates 
                    WHERE template_type = 'session_followup' AND is_active = 1 
                    ORDER BY created_at ASC LIMIT 1
                """)
            else:
                template = await conn.fetchrow("""
                    SELECT id FROM follow_up_templates 
                    WHERE template_type = 'session_followup' AND is_active = TRUE 
                    ORDER BY created_at ASC LIMIT 1
                """)
        finally:
            await db.release_connection(conn)
        
        if template:
            # Schedule follow-up
            request = FollowUpRequest(
                user_email=user_email,
                session_id=session_id,
                template_id=template['id'],
                channel=FollowUpChannel.EMAIL
            )
            
            # Schedule asynchronously to not block session response
            asyncio.create_task(followup_service.schedule_followup(request))
            
    except Exception as e:
        # Log error but don't fail the session
        print(f"Failed to schedule follow-up for session {session_id}: {e}")

@router.post("/start")
async def start_session(request: Request, session_data: Dict[str, Any], db=Depends(get_db)):
    """Start a spiritual guidance session with atomic credit deduction"""
    user_id = get_user_id_from_token(request)
    
    # Get service details first
    service_type = session_data.get("service_type")
    if not service_type:
        raise HTTPException(status_code=400, detail="Service type is required")
    
    # Use transaction to ensure atomicity - check credits and deduct in same transaction
    async with db.transaction():
        # Get user with FOR UPDATE to prevent race conditions
        user = await db.fetchrow("""
            SELECT id, email, credits FROM users 
            WHERE id = $1 FOR UPDATE
        """, user_id)
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get service details
        service = await db.fetchrow("""
            SELECT id, name, credits_required, price_usd 
            FROM service_types 
            WHERE name = $1 AND enabled = TRUE
        """, service_type)
        
        if not service:
            raise HTTPException(status_code=400, detail="Invalid or disabled service type")
        
        # Check credits within transaction
        if user["credits"] < service["credits_required"]:
            raise HTTPException(
                status_code=402, 
                detail=f"போதிய கிரெடிட்கள் இல்லை. தேவை: {service['credits_required']}, கிடைக்கும்: {user['credits']}"
            )
        
        # Deduct credits atomically
        result = await db.execute("""
            UPDATE users SET credits = credits - $1 
            WHERE id = $2 AND credits >= $1
        """, service["credits_required"], user_id)
        
        if result.rowcount == 0:
            raise HTTPException(
                status_code=402, 
                detail="Credit deduction failed - insufficient credits or concurrent transaction"
            )
        
        # Create session record
        session_id = str(uuid.uuid4())
        await db.execute("""
            INSERT INTO sessions (id, user_email, service_type, question, guidance, 
                                avatar_video_url, credits_used, original_price, status, created_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, 'completed', NOW())
        """, 
            session_id, 
            user["email"], 
            service_type, 
            session_data.get("question", ""),
            f"Divine guidance for: {session_data.get('question', '')}",
            None,  # avatar_video_url
            service["credits_required"],
            service["price_usd"]
        )
        
        # Calculate remaining credits
        remaining_credits = user["credits"] - service["credits_required"]
    
    # NEW: Get real astrological data and guidance
    birth_details = session_data.get("birth_details")
    astrology_data = {}
    guidance_text = ""
    
    if PROKERALA_AVAILABLE and birth_details and all(birth_details.get(key) for key in ["date", "time", "location"]):
        try:
            # Get real birth chart data from Prokerala
            astrology_data = await get_prokerala_chart_data(birth_details)
            
            # Generate spiritual guidance based on real data
            guidance_text = await generate_spiritual_guidance_with_ai(
                session_data.get("question", ""), 
                astrology_data
            )
            
        except Exception as e:
            print(f"Prokerala API error for session {session_id}: {e}")
            # Fallback to basic guidance
            astrology_data = {
                "data": {
                    "nakshatra": {"name": "Unable to calculate"},
                    "chandra_rasi": {"name": "Please check birth details"}
                },
                "error": str(e)
            }
            guidance_text = f"""🕉️ Divine Guidance from Swami Jyotirananthan

Your Question: {session_data.get('question', '')}

While the cosmic calculations are temporarily unavailable, the divine wisdom flows through eternal principles:

The Tamil spiritual tradition teaches us that every question arises from the soul's journey toward truth. Your inquiry itself shows spiritual awakening.

Consider these timeless insights:
1. Practice daily meditation and prayer
2. Serve others with compassion
3. Trust in divine timing
4. Cultivate gratitude and humility

May the divine light guide you on your sacred path.

Om Namah Shivaya 🙏"""
    else:
        # No birth details provided or Prokerala unavailable
        astrology_data = {"data": {"message": "Birth details required for astrological analysis"}}
        guidance_text = f"""🕉️ Divine Guidance from Swami Jyotirananthan

Your Question: {session_data.get('question', '')}

Though complete birth details would enhance the astrological guidance, the divine wisdom speaks through your sincere inquiry.

The ancient Tamil wisdom teaches that the answers we seek often reside within us, waiting to be unveiled through spiritual practice and divine grace.

May you find clarity and peace on your spiritual journey.

Om Namah Shivaya 🙏"""
    
    # Schedule automatic follow-up (non-blocking)
    asyncio.create_task(schedule_session_followup(session_id, user["email"], service_type, db))
    
    return {
        "success": True,
        "data": {
            "session_id": session_id,
            "guidance": guidance_text,  # Real AI-generated guidance
            "astrology": astrology_data,  # Real Prokerala data
            "birth_chart": astrology_data,  # Complete chart data
            "birth_details": birth_details,  # Echo back for verification
            "credits_deducted": service["credits_required"],
            "remaining_credits": remaining_credits,
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "prokerala_integration": PROKERALA_AVAILABLE,
                "service_type": service_type
            }
        }
    } 