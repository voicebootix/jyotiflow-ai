from fastapi import APIRouter, Depends, HTTPException, Request
from db import get_db
import jwt
import os
from datetime import datetime, timezone
import uuid
from typing import Dict, Any
import asyncio

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
    """Start a spiritual guidance session with credit deduction"""
    user_id = get_user_id_from_token(request)
    
    # Get user details
    user = await db.fetchrow("SELECT id, email, credits FROM users WHERE id=$1", user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get service details
    service_type = session_data.get("service_type")
    if not service_type:
        raise HTTPException(status_code=400, detail="Service type is required")
    
    service = await db.fetchrow(
        "SELECT id, name, credits_required, price_usd FROM service_types WHERE name=$1 AND enabled=TRUE",
        service_type
    )
    if not service:
        raise HTTPException(status_code=400, detail="Invalid or disabled service type")
    
    # Check if user has enough credits
    if user["credits"] < service["credits_required"]:
        raise HTTPException(
            status_code=402, 
            detail=f"Insufficient credits. Required: {service['credits_required']}, Available: {user['credits']}"
        )
    
    # Start transaction for atomic credit deduction and session creation
    async with db.transaction():
        # Deduct credits
        await db.execute(
            "UPDATE users SET credits = credits - $1 WHERE id = $2",
            service["credits_required"], user_id
        )
        
        # Create session record
        session_id = str(uuid.uuid4())
        await db.execute("""
            INSERT INTO sessions (id, user_email, service_type, question, guidance, 
                                avatar_video_url, credits_used, original_price, status, created_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, 'completed', NOW())
        """, (
            session_id, 
            user["email"], 
            service_type, 
            session_data.get("question", ""),
            "Divine guidance will be provided...",  # Placeholder guidance
            None,  # avatar_video_url
            service["credits_required"],
            service["price_usd"]
        ))
    
    # Generate guidance (placeholder - replace with actual AI guidance)
    guidance_text = f"Divine guidance for your question: {session_data.get('question', '')}"
    
    # Schedule automatic follow-up (non-blocking)
    asyncio.create_task(schedule_session_followup(session_id, user["email"], service_type, db))
    
    return {
        "success": True,
        "data": {
            "session_id": session_id,
            "guidance": guidance_text,
            "astrology": {
                "data": {
                    "nakshatra": {"name": "Ashwini"},
                    "chandra_rasi": {"name": "Mesha"}
                }
            },
            "credits_deducted": service["credits_required"],
            "remaining_credits": user["credits"] - service["credits_required"]
        }
    } 