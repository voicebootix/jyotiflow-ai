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

def get_user_id_as_int(request: Request) -> int | None:
    """Extract user ID from JWT token and convert to integer - OPTIONAL"""
    try:
        user_id_str = JWTHandler.get_user_id_from_token(request)
        return int(user_id_str) if user_id_str else None
    except (ValueError, TypeError):
        return None

# தமிழ் - பயனர் சுயவிவரம் பெறுதல்
@router.get("/profile")
async def get_profile(request: Request, db=Depends(get_db)):
    user_id = get_user_id_as_int(request)
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
    user_id = get_user_id_as_int(request)
    if not user_id:
        return {"success": True, "data": {"credits": 0}}
    
    user = await db.fetchrow("SELECT credits FROM users WHERE id=$1", user_id)
    if not user:
        return {"success": True, "data": {"credits": 0}}
    return {"success": True, "data": {"credits": user["credits"]}}

@router.get("/sessions")
async def get_sessions(request: Request, db=Depends(get_db)):
    user_id = get_user_id_as_int(request)
    if not user_id:
        return {"success": True, "data": []}
    
    user = await db.fetchrow("SELECT email FROM users WHERE id=$1", user_id)
    if not user:
        return {"success": True, "data": []}
    sessions = await db.fetch("SELECT id, service_type_id, question, created_at FROM sessions WHERE user_email=$1 ORDER BY created_at DESC", user["email"])
    return {"success": True, "data": [dict(row) for row in sessions]}

# தமிழ் - கடன் வரலாறு பெறுதல்
@router.get("/credit-history")
async def get_credit_history(request: Request, db=Depends(get_db)):
    """Get user's credit purchase and usage history"""
    user_id = get_user_id_as_int(request)
    if not user_id:
        return {"success": True, "data": []}
    
    try:
        # Get credit transactions from credit_packages table
        history = await db.fetch("""
            SELECT 
                cp.id,
                cp.package_name,
                cp.credits,
                cp.price,
                cp.created_at as purchase_date,
                'purchase' as transaction_type
            FROM credit_packages cp
            WHERE cp.user_id = $1
            ORDER BY cp.created_at DESC
        """, user_id)
        
        return {"success": True, "data": [dict(row) for row in history]}
    except Exception as e:
        print(f"Error fetching credit history: {e}")
        return {"success": True, "data": []}

# தமிழ் - பயனர் பரிந்துரைகள் பெறுதல்
@router.get("/recommendations")
async def get_user_recommendations(request: Request, db=Depends(get_db)):
    """Get personalized recommendations for the user"""
    user_id = get_user_id_as_int(request)
    if not user_id:
        return {"success": True, "data": []}
    
    try:
        # Get user's session history to generate recommendations
        user = await db.fetchrow("SELECT email FROM users WHERE id=$1", user_id)
        if not user:
            return {"success": True, "data": []}
        
        sessions = await db.fetch("""
            SELECT service_type_id, COUNT(*) as session_count
            FROM sessions 
            WHERE user_email = $1 
            GROUP BY service_type_id 
            ORDER BY session_count DESC
        """, user["email"])
        
        # Get available services
        services = await db.fetch("SELECT id, name, description, base_credits FROM service_types")
        
        # Generate recommendations based on usage patterns
        recommendations = []
        for service in services:
            service_sessions = next((s for s in sessions if s["service_type_id"] == service["id"]), None)
            session_count = service_sessions["session_count"] if service_sessions else 0
            
            if session_count == 0:
                # Recommend new services
                recommendations.append({
                    "type": "new_service",
                    "service_id": service["id"],
                    "service_name": service["name"],
                    "description": f"Try {service['name']} for spiritual growth",
                    "priority": "high"
                })
            elif session_count < 3:
                # Recommend continuing with low-usage services
                recommendations.append({
                    "type": "continue_service",
                    "service_id": service["id"],
                    "service_name": service["name"],
                    "description": f"Continue exploring {service['name']}",
                    "priority": "medium"
                })
        
        return {"success": True, "data": recommendations[:5]}  # Return top 5 recommendations
    except Exception as e:
        print(f"Error generating recommendations: {e}")
        return {"success": True, "data": []} 