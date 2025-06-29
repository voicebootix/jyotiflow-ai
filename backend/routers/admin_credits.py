from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from schemas.credit import CreditPackageCreate, CreditPackageUpdate, CreditPackageOut
from db import get_db
from utils.stripe_utils import create_stripe_credit_package
import uuid

router = APIRouter(prefix="/api/admin/credit-packages", tags=["Admin Credits"])

# CREATE new credit package
@router.post("", response_model=CreditPackageOut)
async def create_package(pkg: CreditPackageCreate, db=Depends(get_db)):
    row = await db.fetchrow("""
        INSERT INTO credit_packages (name, credits_amount, price, bonus_credits, is_active)
        VALUES ($1, $2, $3, $4, $5)
        RETURNING *
    """, pkg.name, pkg.credits_amount, pkg.price, pkg.bonus_credits, pkg.is_active)
    return dict(row)

# LIST all packages
@router.get("", response_model=List[CreditPackageOut])
async def list_packages(db=Depends(get_db)):
    rows = await db.fetch("SELECT * FROM credit_packages ORDER BY created_at DESC")
    return [dict(row) for row in rows]

# UPDATE package
@router.put("/{package_id}", response_model=CreditPackageOut)
async def update_package(package_id: uuid.UUID, pkg: CreditPackageUpdate, db=Depends(get_db)):
    row = await db.fetchrow("SELECT * FROM credit_packages WHERE id=$1", package_id)
    if not row:
        raise HTTPException(status_code=404, detail="Package not found")
    updated = row.copy()
    for field, value in pkg.dict(exclude_unset=True).items():
        updated[field] = value
    await db.execute("""
        UPDATE credit_packages SET name=$1, credits_amount=$2, price=$3, bonus_credits=$4, is_active=$5, updated_at=NOW()
        WHERE id=$6
    """, updated["name"], updated["credits_amount"], updated["price"], updated["bonus_credits"], updated["is_active"], package_id)
    return updated

# GET credit transactions
@router.get("/credit-transactions")
async def credit_transactions(db=Depends(get_db)):
    rows = await db.fetch("SELECT * FROM credit_transactions ORDER BY created_at DESC")
    return [dict(row) for row in rows] 