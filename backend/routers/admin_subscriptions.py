from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from schemas.subscription import SubscriptionPlanCreate, SubscriptionPlanUpdate, SubscriptionPlanOut
from db import get_db
from utils.stripe_utils import create_stripe_subscription_plan
import uuid
import json

router = APIRouter(prefix="/subscription-plans", tags=["Admin Subscriptions"])

# CREATE new subscription plan
@router.post("", response_model=SubscriptionPlanOut)
async def create_plan(plan: SubscriptionPlanCreate, db=Depends(get_db)):
    row = await db.fetchrow("""
        INSERT INTO subscription_plans (name, description, monthly_price, credits_per_month, features, is_active)
        VALUES ($1, $2, $3, $4, $5, $6)
        RETURNING *
    """, plan.name, plan.description, plan.monthly_price, plan.credits_per_month, plan.features, plan.is_active)
    return dict(row)

# LIST all plans
@router.get("", response_model=List[SubscriptionPlanOut])
async def list_plans(db=Depends(get_db)):
    rows = await db.fetch("SELECT * FROM subscription_plans ORDER BY created_at DESC")
    plans = []
    for row in rows:
        plan = dict(row)
        # Fix: features field as dict
        if isinstance(plan["features"], str):
            try:
                plan["features"] = json.loads(plan["features"])
            except Exception:
                plan["features"] = {}
        plans.append(plan)
    return plans

# UPDATE plan
@router.put("/{plan_id}", response_model=SubscriptionPlanOut)
async def update_plan(plan_id: uuid.UUID, plan: SubscriptionPlanUpdate, db=Depends(get_db)):
    row = await db.fetchrow("SELECT * FROM subscription_plans WHERE id=$1", plan_id)
    if not row:
        raise HTTPException(status_code=404, detail="Plan not found")
    updated = row.copy()
    for field, value in plan.dict(exclude_unset=True).items():
        updated[field] = value
    await db.execute("""
        UPDATE subscription_plans SET name=$1, description=$2, monthly_price=$3, credits_per_month=$4, features=$5, is_active=$6, updated_at=NOW()
        WHERE id=$7
    """, updated["name"], updated["description"], updated["monthly_price"], updated["credits_per_month"], updated["features"], updated["is_active"], plan_id)
    return updated

# GET active subscriptions (example, join with users)
@router.get("/active-subscriptions")
async def active_subscriptions(db=Depends(get_db)):
    rows = await db.fetch("""
        SELECT u.id as user_id, u.email, s.id as subscription_id, s.name, s.monthly_price
        FROM user_subscriptions us
        JOIN users u ON us.user_id = u.id
        JOIN subscription_plans s ON us.plan_id = s.id
        WHERE us.is_active = TRUE
    """)
    return [dict(row) for row in rows] 