from fastapi import APIRouter, Depends, HTTPException, status, Request
from db import get_db
import os
from datetime import datetime, timezone
import uuid
from typing import Dict, Any

# Import centralized JWT handler
from auth.jwt_config import JWTHandler

router = APIRouter(prefix="/api/user", tags=["User"])

def get_user_id_from_token(request: Request) -> str | None:
    """Extract user ID from JWT token - OPTIONAL"""
    try:
        return JWTHandler.get_user_id_from_token(request)
    except Exception:
        return None

# தமிழ் - பயனர் சுயவிவரம் பெறுதல்
@router.get("/profile")
async def get_profile(request: Request, db=Depends(get_db)):
    user_id = get_user_id_from_token(request)
    if not user_id:
        # Return guest user profile for non-authenticated requests
        return {
            "id": "guest",
            "email": "guest@jyotiflow.ai",
            "name": "Guest User",
            "full_name": "Guest User",
            "credits": 0,
            "role": "guest",
            "created_at": datetime.now(timezone.utc)
        }
    
    user = await db.fetchrow("SELECT id, email, name, full_name, credits, role, created_at FROM users WHERE id=$1", user_id)
    if not user:
        # Return guest user profile if user not found
        return {
            "id": "guest",
            "email": "guest@jyotiflow.ai",
            "name": "Guest User",
            "full_name": "Guest User",
            "credits": 0,
            "role": "guest",
            "created_at": datetime.now(timezone.utc)
        }
    return {
        "id": str(user["id"]),
        "email": user["email"],
        "name": user.get("full_name") or user.get("name"),
        "full_name": user.get("full_name"),
        "credits": user["credits"],
        "role": user.get("role", "user"),  # Include role in response
        "created_at": user["created_at"]
    }

@router.get("/credits")
async def get_credits(request: Request, db=Depends(get_db)):
    user_id = get_user_id_from_token(request)
    if not user_id:
        return {"success": True, "data": {"credits": 0}}
    
    user = await db.fetchrow("SELECT credits FROM users WHERE id=$1", user_id)
    if not user:
        return {"success": True, "data": {"credits": 0}}
    return {"success": True, "data": {"credits": user["credits"]}}

@router.get("/sessions")
async def get_sessions(request: Request, db=Depends(get_db)):
    user_id = get_user_id_from_token(request)
    if not user_id:
        return {"success": True, "data": []}
    
    user = await db.fetchrow("SELECT email FROM users WHERE id=$1", user_id)
    if not user:
        return {"success": True, "data": []}
    sessions = await db.fetch("SELECT id, service_type_id, question, created_at FROM sessions WHERE user_email=$1 ORDER BY created_at DESC", user["email"])
    return {"success": True, "data": [dict(row) for row in sessions]} 