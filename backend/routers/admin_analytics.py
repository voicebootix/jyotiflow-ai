from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any
from db import get_db
from utils.analytics_utils import calculate_revenue_metrics, generate_ai_recommendations
import uuid

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