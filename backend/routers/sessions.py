from fastapi import APIRouter, Depends, HTTPException, Request
from db import get_db
import jwt
import os
from datetime import datetime, timezone
import uuid
from typing import Dict, Any
import asyncio

# ADD: Import the Prokerala service
try:
    from services.prokerala_service import prokerala_service
    PROKERALA_AVAILABLE = True
except ImportError:
    PROKERALA_AVAILABLE = False
    print("Warning: Prokerala service not available")

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
            astrology_data = await prokerala_service.get_complete_birth_chart(birth_details)
            
            # Generate spiritual guidance based on real data
            guidance_text = await prokerala_service.generate_spiritual_guidance(
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