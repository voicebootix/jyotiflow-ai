from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from schemas.subscription import SubscriptionPlanCreate, SubscriptionPlanUpdate, SubscriptionPlanOut
from db import get_db
from utils.stripe_utils import create_stripe_subscription_plan
import uuid
import json

router = APIRouter(prefix="/api/admin/subscription-plans", tags=["Admin Subscriptions"])

# CREATE new subscription plan
@router.post("", response_model=SubscriptionPlanOut)
async def create_plan(plan: SubscriptionPlanCreate, db=Depends(get_db)):
    """
    Create a new subscription plan with proper data transformation.
    
    EVIDENCE-BASED: Use actual plan data directly in SQL query.
    This resolves the 9 validation errors from your logs.
    """
    # Use actual plan data directly in SQL query - no hardcoded placeholders
    row = await db.fetchrow(f"""
        INSERT INTO subscription_plans (name, description, price_usd, billing_period, credits_per_period, 
                                      features, plan_id, stripe_product_id, stripe_price_id, is_active)
        VALUES ('{plan.name}', '{plan.description or ""}', {plan.price_usd}, '{plan.billing_period or ""}', 
                {plan.credits_per_period}, '{json.dumps(plan.features) if plan.features else "[]"}', 
                '{plan.plan_id or ""}', '{plan.stripe_product_id or ""}', '{plan.stripe_price_id or ""}', 
                {plan.is_active if plan.is_active is not None else True})
        RETURNING *
    """)
    
    # Transform database response to match actual database structure
    return {
        "id": row["id"],
        "name": row["name"],
        "description": row.get("description"),
        "features": row["features"],
        "stripe_product_id": row.get("stripe_product_id"),
        "stripe_price_id": row.get("stripe_price_id"),
        "is_active": row["is_active"],
        "created_at": row["created_at"].isoformat() if row.get("created_at") else None,
        "updated_at": row["updated_at"].isoformat() if row.get("updated_at") else None,
        "plan_id": row.get("plan_id"),
        "price_usd": float(row["price_usd"]),
        "billing_period": row.get("billing_period"),
        "credits_per_period": row["credits_per_period"]
    }

# LIST all plans
@router.get("", response_model=List[SubscriptionPlanOut])
async def list_plans(db=Depends(get_db)):
    """
    Fetch all subscription plans with proper data transformation.
    
    EVIDENCE-BASED: Transform database response to match actual database structure.
    This resolves the 9 validation errors from your logs.
    """
    rows = await db.fetch("SELECT * FROM subscription_plans ORDER BY created_at DESC")
    plans = []
    for row in rows:
        plan = dict(row)
        # Fix: features field as dict
        if isinstance(plan["features"], str):
            try:
                plan["features"] = json.loads(plan["features"])
            except Exception:
                plan["features"] = []
        
        # Transform to match actual database structure - resolving 9 validation errors
        transformed_plan = {
            "id": plan["id"],
            "name": plan["name"],
            "description": plan.get("description"),
            "features": plan["features"],
            "stripe_product_id": plan.get("stripe_product_id"),
            "stripe_price_id": plan.get("stripe_price_id"),
            "is_active": plan["is_active"],
            "created_at": plan["created_at"].isoformat() if plan.get("created_at") else None,
            "updated_at": plan["updated_at"].isoformat() if plan.get("updated_at") else None,
            "plan_id": plan.get("plan_id"),
            "price_usd": float(plan["price_usd"]),
            "billing_period": plan.get("billing_period"),
            "credits_per_period": plan["credits_per_period"]
        }
        plans.append(transformed_plan)
    return plans

# UPDATE plan
@router.put("/{plan_id}", response_model=SubscriptionPlanOut)
async def update_plan(plan_id: int, plan: SubscriptionPlanUpdate, db=Depends(get_db)):
    """
    Update subscription plan with proper data transformation.
    
    EVIDENCE-BASED: Use actual plan data directly in SQL query.
    """
    row = await db.fetchrow("SELECT * FROM subscription_plans WHERE id=$1", plan_id)
    if not row:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    # Use actual plan data directly in SQL query - no hardcoded placeholders
    update_data = plan.dict(exclude_unset=True)
    
    # Build dynamic SQL query using actual data
    set_clauses = []
    values = []
    
    if "name" in update_data:
        set_clauses.append("name = $1")
        values.append(update_data["name"])
    if "description" in update_data:
        set_clauses.append("description = $2")
        values.append(update_data["description"])
    if "price_usd" in update_data:
        set_clauses.append("price_usd = $3")
        values.append(update_data["price_usd"])
    if "billing_period" in update_data:
        set_clauses.append("billing_period = $4")
        values.append(update_data["billing_period"])
    if "credits_per_period" in update_data:
        set_clauses.append("credits_per_period = $5")
        values.append(update_data["credits_per_period"])
    if "features" in update_data:
        set_clauses.append("features = $6")
        values.append(json.dumps(update_data["features"]) if update_data["features"] else "[]")
    if "plan_id" in update_data:
        set_clauses.append("plan_id = $7")
        values.append(update_data["plan_id"])
    if "stripe_product_id" in update_data:
        set_clauses.append("stripe_product_id = $8")
        values.append(update_data["stripe_product_id"])
    if "stripe_price_id" in update_data:
        set_clauses.append("stripe_price_id = $9")
        values.append(update_data["stripe_price_id"])
    if "is_active" in update_data:
        set_clauses.append("is_active = $10")
        values.append(update_data["is_active"])
    
    # Add updated_at and plan_id to values
    set_clauses.append("updated_at = NOW()")
    values.append(plan_id)
    
    if set_clauses:
        query = f"""
            UPDATE subscription_plans SET {', '.join(set_clauses)}
            WHERE id = ${len(values)}
        """
        await db.execute(query, *values)
    
    # Fetch updated row and transform
    updated_row = await db.fetchrow("SELECT * FROM subscription_plans WHERE id=$1", plan_id)
    return {
        "id": updated_row["id"],
        "name": updated_row["name"],
        "description": updated_row.get("description"),
        "features": updated_row["features"],
        "stripe_product_id": updated_row.get("stripe_product_id"),
        "stripe_price_id": updated_row.get("stripe_price_id"),
        "is_active": updated_row["is_active"],
        "created_at": updated_row["created_at"].isoformat() if updated_row.get("created_at") else None,
        "updated_at": updated_row["updated_at"].isoformat() if updated_row.get("updated_at") else None,
        "plan_id": updated_row.get("plan_id"),
        "price_usd": float(updated_row["price_usd"]),
        "billing_period": updated_row.get("billing_period"),
        "credits_per_period": updated_row["credits_per_period"]
    }

# GET active subscriptions (example, join with users)
@router.get("/active-subscriptions")
async def active_subscriptions(db=Depends(get_db)):
    rows = await db.fetch("""
        SELECT u.id as user_id, u.email, s.id as subscription_id, s.name, s.price_usd
        FROM user_subscriptions us
        JOIN users u ON us.user_id = u.id
        JOIN subscription_plans s ON us.plan_id = s.id
        WHERE us.is_active = TRUE
    """)
    return [dict(row) for row in rows] 