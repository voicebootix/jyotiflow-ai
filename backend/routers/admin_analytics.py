from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any
from db import get_db
from utils.analytics_utils import calculate_revenue_metrics, generate_ai_recommendations
import uuid
import random

router = APIRouter(prefix="/api/admin", tags=["Admin Analytics"])

@router.get("/analytics")
async def analytics(db=Depends(get_db)):
    return {
        "users": await db.fetchval("SELECT COUNT(*) FROM users"),
        "revenue": await db.fetchval("SELECT SUM(amount) FROM payments"),
        "sessions": await db.fetchval("SELECT COUNT(*) FROM sessions"),
    }

@router.get("/revenue-insights")
async def revenue_insights(db=Depends(get_db)):
    return {
        "monthly": await db.fetch("SELECT date_trunc('month', created_at) as month, SUM(amount) as total FROM payments GROUP BY month ORDER BY month DESC LIMIT 12"),
        "by_product": await db.fetch("SELECT product_id, SUM(amount) as total FROM payments GROUP BY product_id")
    }

@router.get("/pricing-recommendations")
async def pricing_recommendations(db=Depends(get_db)):
    rows = await db.fetch("SELECT * FROM ai_recommendations WHERE recommendation_type='pricing' ORDER BY created_at DESC")
    return [dict(row) for row in rows]

@router.get("/ab-test-results")
async def ab_test_results(db=Depends(get_db)):
    rows = await db.fetch("SELECT * FROM monetization_experiments ORDER BY created_at DESC")
    return [dict(row) for row in rows]

# தமிழ் - மேலோட்டம் மற்றும் பகுப்பாய்வு
@router.get("/overview")
async def get_overview(db=Depends(get_db)):
    total_users = await db.fetchval("SELECT COUNT(*) FROM users")
    active_users = await db.fetchval("SELECT COUNT(*) FROM users WHERE last_login_at >= NOW() - INTERVAL '7 days'")
    total_revenue = await db.fetchval("SELECT COALESCE(SUM(amount), 0) FROM payments WHERE status='completed'")
    monthly_revenue = await db.fetchval("SELECT COALESCE(SUM(amount), 0) FROM payments WHERE status='completed' AND created_at >= NOW() - INTERVAL '30 days'")
    growth_rate = 12.5  # mock
    conversion_rate = 7.8  # mock
    system_health = "healthy"
    ai_alerts = [
        {"type": "info", "message": "All systems operational"},
        {"type": "success", "message": "Revenue up 12% this month"}
    ]
    return {
        "total_users": total_users or 0,
        "active_users": active_users or 0,
        "total_revenue": float(total_revenue or 0),
        "monthly_revenue": float(monthly_revenue or 0),
        "growth_rate": growth_rate,
        "conversion_rate": conversion_rate,
        "system_health": system_health,
        "ai_alerts": ai_alerts
    }

# தமிழ் - AI நுண்ணறிவு பரிந்துரைகள்
@router.get("/ai-insights")
async def get_ai_insights(db=Depends(get_db)):
    recommendations = [
        {
            "type": "pricing_optimization",
            "title": "விலை உகந்தமயமாக்கல்",
            "description": "புதிய கிரெடிட் தொகுப்புகளுக்கு 10% தள்ளுபடி வழங்குங்கள்.",
            "impact": "high",
            "estimated_revenue_increase": 20000
        },
        {
            "type": "content_strategy",
            "title": "உள்ளடக்க மூலோபாயம்",
            "description": "வாரத்திற்கு 2 சத்சங்க் நிகழ்வுகள் நடத்துங்கள்.",
            "impact": "medium",
            "estimated_revenue_increase": 8000
        }
    ]
    return {"recommendations": recommendations} 