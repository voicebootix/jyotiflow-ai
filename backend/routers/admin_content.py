from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from schemas.content import SocialContentCreate, SocialContentOut, SatsangEventCreate, SatsangEventOut
from db import get_db
import uuid
from deps import get_admin_user

router = APIRouter(prefix="/api/admin", tags=["Admin Content"])

# Social content queue
@router.get("/social-content", response_model=List[SocialContentOut])
async def social_content(db=Depends(get_db)):
    rows = await db.fetch("SELECT * FROM social_content ORDER BY scheduled_at DESC")
    return [dict(row) for row in rows]

# Schedule content
@router.post("/social-content/schedule", response_model=SocialContentOut)
async def schedule_content(content: SocialContentCreate, db=Depends(get_db)):
    row = await db.fetchrow("""
        INSERT INTO social_content (platform, content_type, content_text, media_url, scheduled_at, status)
        VALUES ($1, $2, $3, $4, $5, $6)
        RETURNING *
    """, content.platform, content.content_type, content.content_text, content.media_url, content.scheduled_at, content.status)
    return dict(row)

# Satsang events
@router.get("/satsang-events", response_model=List[SatsangEventOut])
async def satsang_events(db=Depends(get_db)):
    rows = await db.fetch("SELECT * FROM satsang_events ORDER BY event_date DESC")
    return [dict(row) for row in rows]

@router.post("/satsang-events", response_model=SatsangEventOut)
async def create_satsang_event(event: SatsangEventCreate, db=Depends(get_db)):
    row = await db.fetchrow("""
        INSERT INTO satsang_events (title, description, event_date, duration_minutes, max_attendees, zoom_link, status)
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        RETURNING *
    """, event.title, event.description, event.event_date, event.duration_minutes, event.max_attendees, event.zoom_link, event.status)
    return dict(row)

@router.get("/users")
async def get_admin_users(db=Depends(get_db), admin_user: dict = Depends(get_admin_user)):
    rows = await db.fetch("SELECT id, email, name, role, credits, created_at FROM users ORDER BY created_at DESC")
    return [dict(row) for row in rows] 