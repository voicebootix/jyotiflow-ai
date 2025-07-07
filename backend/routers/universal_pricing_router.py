"""
Universal Pricing Router for JyotiFlow
Handles dynamic pricing for all services and Satsang management
"""

from fastapi import APIRouter, Depends, HTTPException, Body
from typing import Dict, Any, List, Optional
import json
import sqlite3
from datetime import datetime, timedelta
import sys
import os

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from universal_pricing_engine import (
    UniversalPricingEngine, 
    calculate_universal_pricing,
    get_smart_pricing_recommendations,
    ServiceConfiguration,
    PricingResult
)
from db import get_db

router = APIRouter(prefix="/api/spiritual/enhanced", tags=["Universal Pricing"])

# Universal Pricing Endpoints
@router.get("/pricing/smart-recommendations")
async def get_pricing_recommendations():
    """Get smart pricing recommendations for all services"""
    try:
        recommendations = await get_smart_pricing_recommendations()
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting recommendations: {str(e)}")

@router.post("/pricing/calculate")
async def calculate_service_pricing(service_data: Dict[str, Any] = Body(...)):
    """Calculate pricing for any service"""
    try:
        service_name = service_data.get("service_name")
        if not service_name:
            raise HTTPException(status_code=400, detail="service_name is required")
        
        pricing_result = await calculate_universal_pricing(service_name)
        
        return {
            "success": True,
            "service_name": service_name,
            "pricing": {
                "recommended_price": pricing_result.recommended_price,
                "cost_breakdown": pricing_result.cost_breakdown,
                "confidence_level": pricing_result.confidence_level,
                "pricing_rationale": pricing_result.pricing_rationale,
                "api_costs": pricing_result.api_costs,
                "requires_admin_approval": pricing_result.requires_admin_approval
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating pricing: {str(e)}")

@router.post("/pricing/apply")
async def apply_pricing_change(pricing_data: Dict[str, Any] = Body(...), db=Depends(get_db)):
    """Apply admin-approved pricing change"""
    try:
        service_name = pricing_data.get("service_name")
        approved_price = pricing_data.get("approved_price")
        admin_notes = pricing_data.get("admin_notes", "")
        
        if not service_name or approved_price is None:
            raise HTTPException(status_code=400, detail="service_name and approved_price are required")
        
        # Update service price in database
        await db.execute("""
            UPDATE service_types 
            SET credits_required = ?, 
                updated_at = CURRENT_TIMESTAMP
            WHERE name = ? OR display_name = ?
        """, approved_price, service_name, service_name)
        
        # Log the pricing change
        await db.execute("""
            INSERT INTO ai_pricing_recommendations 
            (service_type, recommendation_data, confidence_score, status, admin_notes, applied_at)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, service_name, json.dumps({
            "approved_price": approved_price,
            "admin_notes": admin_notes,
            "timestamp": datetime.now().isoformat()
        }), 1.0, "approved", admin_notes)
        
        return {
            "success": True,
            "message": f"Price updated for {service_name} to {approved_price} credits",
            "applied_price": approved_price,
            "admin_notes": admin_notes
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error applying pricing: {str(e)}")

@router.get("/pricing/history/{service_name}")
async def get_pricing_history(service_name: str, limit: int = 50, db=Depends(get_db)):
    """Get pricing history for a service"""
    try:
        result = await db.fetch("""
            SELECT recommendation_data, admin_notes, applied_at, status
            FROM ai_pricing_recommendations
            WHERE service_type = ?
            ORDER BY applied_at DESC
            LIMIT ?
        """, service_name, limit)
        
        history = []
        for row in result:
            data = json.loads(row["recommendation_data"]) if row["recommendation_data"] else {}
            history.append({
                "price": data.get("approved_price", 0),
                "admin_notes": row["admin_notes"],
                "applied_at": row["applied_at"],
                "status": row["status"]
            })
        
        return {
            "success": True,
            "service_name": service_name,
            "history": history
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting pricing history: {str(e)}")

# Satsang Management Endpoints
@router.get("/satsang/events")
async def get_satsang_events(status: Optional[str] = None, db=Depends(get_db)):
    """Get Satsang events"""
    try:
        query = "SELECT * FROM satsang_events"
        params = []
        
        if status:
            query += " WHERE status = ?"
            params.append(status)
        
        query += " ORDER BY scheduled_at DESC"
        
        result = await db.fetch(query, *params)
        
        events = []
        for row in result:
            events.append({
                "id": row["id"],
                "title": row["title"],
                "description": row["description"],
                "scheduled_at": row["scheduled_at"],
                "duration_minutes": row["duration_minutes"],
                "max_participants": row["max_participants"],
                "current_participants": row["current_participants"],
                "theme": row["theme"],
                "host_name": row["host_name"],
                "event_type": row["event_type"],
                "has_donations": bool(row["has_donations"]),
                "interactive_level": row["interactive_level"],
                "voice_enabled": bool(row["voice_enabled"]),
                "video_enabled": bool(row["video_enabled"]),
                "base_credits": row["base_credits"],
                "dynamic_pricing_enabled": bool(row["dynamic_pricing_enabled"]),
                "status": row["status"]
            })
        
        return {
            "success": True,
            "events": events
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting Satsang events: {str(e)}")

@router.post("/satsang/create")
async def create_satsang_event(event_data: Dict[str, Any] = Body(...), db=Depends(get_db)):
    """Create a new Satsang event"""
    try:
        # Set default scheduled time if not provided
        scheduled_at = event_data.get("scheduled_at")
        if not scheduled_at:
            # Default to next week, same time
            scheduled_at = (datetime.now() + timedelta(days=7)).isoformat()
        
        # Insert new Satsang event
        await db.execute("""
            INSERT INTO satsang_events 
            (title, description, scheduled_at, duration_minutes, theme, event_type,
             has_donations, interactive_level, voice_enabled, video_enabled, 
             base_credits, dynamic_pricing_enabled, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, 
            event_data.get("title"),
            event_data.get("description", ""),
            scheduled_at,
            event_data.get("duration_minutes", 60),
            event_data.get("theme", ""),
            event_data.get("event_type", "community"),
            event_data.get("has_donations", True),
            event_data.get("interactive_level", "basic"),
            event_data.get("voice_enabled", True),
            event_data.get("video_enabled", True),
            event_data.get("base_credits", 5),
            event_data.get("dynamic_pricing_enabled", True),
            "admin"
        )
        
        return {
            "success": True,
            "message": "Satsang event created successfully",
            "event": event_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating Satsang event: {str(e)}")

@router.get("/satsang/{event_id}/pricing")
async def get_satsang_pricing(event_id: int, db=Depends(get_db)):
    """Get pricing for a specific Satsang event"""
    try:
        # Get event details
        result = await db.fetchone("""
            SELECT title, duration_minutes, event_type, has_donations, 
                   interactive_level, voice_enabled, video_enabled, base_credits
            FROM satsang_events 
            WHERE id = ?
        """, event_id)
        
        if not result:
            raise HTTPException(status_code=404, detail="Satsang event not found")
        
        # Calculate pricing using universal engine
        engine = UniversalPricingEngine()
        pricing_result = await engine.calculate_satsang_pricing(
            satsang_type=result["event_type"],
            duration_minutes=result["duration_minutes"],
            has_donations=bool(result["has_donations"]),
            interactive_level=result["interactive_level"]
        )
        
        return {
            "success": True,
            "event_id": event_id,
            "event_title": result["title"],
            "pricing": {
                "recommended_price": pricing_result.recommended_price,
                "cost_breakdown": pricing_result.cost_breakdown,
                "confidence_level": pricing_result.confidence_level,
                "pricing_rationale": pricing_result.pricing_rationale,
                "api_costs": pricing_result.api_costs
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting Satsang pricing: {str(e)}")

@router.get("/satsang/{event_id}/donations")
async def get_satsang_donations(event_id: int, db=Depends(get_db)):
    """Get donations for a Satsang event"""
    try:
        result = await db.fetch("""
            SELECT user_id, amount_credits, amount_usd, message, is_superchat,
                   highlight_duration, donation_type, created_at
            FROM satsang_donations 
            WHERE satsang_event_id = ?
            ORDER BY created_at DESC
        """, event_id)
        
        donations = []
        total_credits = 0
        total_usd = 0
        superchat_count = 0
        
        for row in result:
            donation = {
                "user_id": row["user_id"],
                "amount_credits": row["amount_credits"],
                "amount_usd": row["amount_usd"],
                "message": row["message"],
                "is_superchat": bool(row["is_superchat"]),
                "highlight_duration": row["highlight_duration"],
                "donation_type": row["donation_type"],
                "created_at": row["created_at"]
            }
            donations.append(donation)
            
            total_credits += row["amount_credits"] or 0
            total_usd += row["amount_usd"] or 0
            if row["is_superchat"]:
                superchat_count += 1
        
        return {
            "success": True,
            "event_id": event_id,
            "donations": donations,
            "summary": {
                "total_donations": len(donations),
                "total_credits": total_credits,
                "total_usd": total_usd,
                "superchat_count": superchat_count
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting Satsang donations: {str(e)}")

@router.post("/satsang/{event_id}/donate")
async def create_satsang_donation(
    event_id: int, 
    donation_data: Dict[str, Any] = Body(...), 
    db=Depends(get_db)
):
    """Create a donation/superchat for a Satsang event"""
    try:
        # Validate donation data
        amount_credits = donation_data.get("amount_credits")
        if not amount_credits or amount_credits <= 0:
            raise HTTPException(status_code=400, detail="amount_credits must be positive")
        
        # Calculate USD equivalent (10 credits = $1)
        amount_usd = amount_credits / 10
        
        # Determine if it's a superchat (donations >= 10 credits)
        is_superchat = amount_credits >= 10
        highlight_duration = min(amount_credits * 5, 60) if is_superchat else 0  # Max 60 seconds
        
        # Insert donation
        await db.execute("""
            INSERT INTO satsang_donations 
            (satsang_event_id, user_id, amount_credits, amount_usd, message,
             is_superchat, highlight_duration, donation_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, 
            event_id,
            donation_data.get("user_id"),
            amount_credits,
            amount_usd,
            donation_data.get("message", ""),
            is_superchat,
            highlight_duration,
            donation_data.get("donation_type", "general")
        )
        
        return {
            "success": True,
            "message": "Donation created successfully",
            "donation": {
                "amount_credits": amount_credits,
                "amount_usd": amount_usd,
                "is_superchat": is_superchat,
                "highlight_duration": highlight_duration,
                "message": donation_data.get("message", "")
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating donation: {str(e)}")

# API Usage Tracking Endpoints
@router.get("/api-usage/metrics")
async def get_api_usage_metrics(days: int = 7, db=Depends(get_db)):
    """Get API usage metrics"""
    try:
        result = await db.fetch("""
            SELECT api_name, SUM(calls_count) as total_calls, 
                   SUM(total_cost_usd) as total_cost_usd,
                   SUM(total_cost_credits) as total_cost_credits,
                   AVG(average_response_time) as avg_response_time,
                   SUM(error_count) as total_errors
            FROM api_usage_metrics 
            WHERE date >= date('now', '-{} days')
            GROUP BY api_name
            ORDER BY total_cost_credits DESC
        """.format(days))
        
        metrics = []
        for row in result:
            metrics.append({
                "api_name": row["api_name"],
                "total_calls": row["total_calls"] or 0,
                "total_cost_usd": row["total_cost_usd"] or 0,
                "total_cost_credits": row["total_cost_credits"] or 0,
                "avg_response_time": row["avg_response_time"] or 0,
                "total_errors": row["total_errors"] or 0,
                "success_rate": (1 - (row["total_errors"] or 0) / max(row["total_calls"] or 1, 1)) * 100
            })
        
        return {
            "success": True,
            "period_days": days,
            "metrics": metrics
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting API metrics: {str(e)}")

@router.post("/api-usage/track")
async def track_api_usage(usage_data: Dict[str, Any] = Body(...), db=Depends(get_db)):
    """Track API usage"""
    try:
        # Insert usage log
        await db.execute("""
            INSERT INTO service_usage_logs 
            (service_type, api_name, usage_type, usage_amount, cost_usd, cost_credits, session_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            usage_data.get("service_type"),
            usage_data.get("api_name"),
            usage_data.get("usage_type"),
            usage_data.get("usage_amount"),
            usage_data.get("cost_usd"),
            usage_data.get("cost_credits"),
            usage_data.get("session_id")
        )
        
        # Update daily metrics
        today = datetime.now().date()
        await db.execute("""
            INSERT OR REPLACE INTO api_usage_metrics 
            (api_name, endpoint, calls_count, total_cost_usd, total_cost_credits, date)
            VALUES (?, ?, 
                COALESCE((SELECT calls_count FROM api_usage_metrics WHERE api_name = ? AND date = ?), 0) + 1,
                COALESCE((SELECT total_cost_usd FROM api_usage_metrics WHERE api_name = ? AND date = ?), 0) + ?,
                COALESCE((SELECT total_cost_credits FROM api_usage_metrics WHERE api_name = ? AND date = ?), 0) + ?,
                ?)
        """,
            usage_data.get("api_name"),
            usage_data.get("endpoint", ""),
            usage_data.get("api_name"), today,
            usage_data.get("api_name"), today, usage_data.get("cost_usd", 0),
            usage_data.get("api_name"), today, usage_data.get("cost_credits", 0),
            today
        )
        
        return {
            "success": True,
            "message": "API usage tracked successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error tracking API usage: {str(e)}")

# System Health Endpoint
@router.get("/system/health")
async def get_system_health():
    """Get universal pricing system health"""
    try:
        engine = UniversalPricingEngine()
        
        # Check API connections
        api_status = {
            "elevenlabs": bool(engine.api_keys["elevenlabs"]),
            "d_id": bool(engine.api_keys["d_id"]),
            "agora": bool(engine.api_keys["agora_app_id"]),
            "openai": bool(engine.api_keys["openai"])
        }
        
        # Calculate system readiness
        connected_apis = sum(api_status.values())
        total_apis = len(api_status)
        system_readiness = (connected_apis / total_apis) * 100
        
        return {
            "success": True,
            "system_status": "operational" if system_readiness >= 75 else "degraded" if system_readiness >= 50 else "critical",
            "system_readiness": system_readiness,
            "api_status": api_status,
            "connected_apis": connected_apis,
            "total_apis": total_apis,
            "features": {
                "universal_pricing": True,
                "satsang_management": True,
                "api_cost_tracking": True,
                "smart_recommendations": True,
                "admin_approval_required": True
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "system_status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }