from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from schemas.credit import CreditPackageCreate, CreditPackageUpdate, CreditPackageOut
from db import get_db
from utils.stripe_utils import create_stripe_credit_package

router = APIRouter(prefix="/api/admin/credit-packages", tags=["Admin Credits"])

# CREATE new credit package
@router.post("", response_model=CreditPackageOut)
async def create_package(pkg: CreditPackageCreate, db=Depends(get_db)):
    # Map is_active to enabled for database
    enabled = pkg.is_active if hasattr(pkg, 'is_active') else True
    row = await db.fetchrow("""
        INSERT INTO credit_packages (name, credits_amount, price_usd, bonus_credits, enabled)
        VALUES ($1, $2, $3, $4, $5)
        RETURNING *
    """, pkg.name, pkg.credits_amount, pkg.price, pkg.bonus_credits, enabled)
    
    # Format the response to match the schema
    return {
        "id": row["id"],
        "name": row["name"],
        "credits_amount": row["credits_amount"],
        "price_usd": float(row["price_usd"]) if row["price_usd"] is not None else 0.0,
        "bonus_credits": row["bonus_credits"] or 0,
        "stripe_product_id": row.get("stripe_product_id"),
        "stripe_price_id": row.get("stripe_price_id"),
        "enabled": bool(row["enabled"]) if row["enabled"] is not None else True,
        "description": row.get("description"),
        "created_at": row["created_at"].isoformat() if row["created_at"] else None
    }

# LIST all packages
@router.get("", response_model=List[CreditPackageOut])
async def list_packages(db=Depends(get_db)):
    rows = await db.fetch("SELECT * FROM credit_packages ORDER BY created_at DESC")
    
    result = []
    for row in rows:
        package = {
            "id": row["id"],
            "name": row["name"],
            "credits_amount": row["credits_amount"],
            "price_usd": float(row["price_usd"]) if row["price_usd"] is not None else 0.0,
            "bonus_credits": row["bonus_credits"] or 0,
            "stripe_product_id": row.get("stripe_product_id"),
            "stripe_price_id": row.get("stripe_price_id"),
            "enabled": bool(row["enabled"]) if row["enabled"] is not None else True,
            "description": row.get("description"),
            "created_at": row["created_at"].isoformat() if row["created_at"] else None
        }
        result.append(package)
    
    return result

# UPDATE package
@router.put("/{package_id}", response_model=CreditPackageOut)
async def update_package(package_id: int, pkg: CreditPackageUpdate, db=Depends(get_db)):
    row = await db.fetchrow("SELECT * FROM credit_packages WHERE id=$1", package_id)
    if not row:
        raise HTTPException(status_code=404, detail="Package not found")
    
    # Build update data, mapping is_active to enabled
    update_data = {}
    for field, value in pkg.dict(exclude_unset=True).items():
        if field == 'is_active':
            update_data['enabled'] = value
        elif field == 'price':
            update_data['price_usd'] = value
        else:
            update_data[field] = value
    
    # Build the update query dynamically
    if update_data:
        set_clause = ", ".join([f"{k}=${i+2}" for i, k in enumerate(update_data.keys())])
        query = f"UPDATE credit_packages SET {set_clause}, updated_at=NOW() WHERE id=$1 RETURNING *"
        values = [package_id] + list(update_data.values())
        row = await db.fetchrow(query, *values)
    
    # Format the response to match the schema
    return {
        "id": row["id"],
        "name": row["name"],
        "credits_amount": row["credits_amount"],
        "price_usd": float(row["price_usd"]) if row["price_usd"] is not None else 0.0,
        "bonus_credits": row["bonus_credits"] or 0,
        "stripe_product_id": row.get("stripe_product_id"),
        "stripe_price_id": row.get("stripe_price_id"),
        "enabled": bool(row["enabled"]) if row["enabled"] is not None else True,
        "description": row.get("description"),
        "created_at": row["created_at"].isoformat() if row["created_at"] else None
    }

# GET credit transactions
@router.get("/credit-transactions")
async def credit_transactions(db=Depends(get_db)):
    rows = await db.fetch("SELECT * FROM credit_transactions ORDER BY created_at DESC")
    return [dict(row) for row in rows] 