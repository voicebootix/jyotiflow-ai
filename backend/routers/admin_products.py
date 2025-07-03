from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from schemas.product import ProductCreate, ProductUpdate, ProductOut
from db import get_db
from utils.stripe_utils import create_stripe_product
import uuid
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin/products", tags=["Admin Products"])

# CREATE new product (frontend expects POST /api/admin/products)
@router.post("", response_model=ProductOut)
async def create_product(product: ProductCreate, db=Depends(get_db)):
    exists = await db.fetchval("SELECT 1 FROM products WHERE sku_code=$1", product.sku_code)
    if exists:
        raise HTTPException(status_code=400, detail="SKU already exists")
    stripe_product_id, stripe_price_id = await create_stripe_product(product.name, product.price)
    row = await db.fetchrow("""
        INSERT INTO products (sku_code, name, description, price, credits_allocated, stripe_product_id, stripe_price_id, is_active)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        RETURNING *
    """, product.sku_code, product.name, product.description, product.price, product.credits_allocated, stripe_product_id, stripe_price_id, product.is_active)
    return dict(row)

# UPDATE product (frontend expects POST /api/admin/products/{product_id})
@router.post("/{product_id}", response_model=ProductOut)
async def update_product_post(product_id: uuid.UUID, product: ProductUpdate, db=Depends(get_db)):
    row = await db.fetchrow("SELECT * FROM products WHERE id=$1", product_id)
    if not row:
        raise HTTPException(status_code=404, detail="Product not found")
    updated = row.copy()
    for field, value in product.dict(exclude_unset=True).items():
        updated[field] = value
    await db.execute("""
        UPDATE products SET name=$1, description=$2, price=$3, credits_allocated=$4, is_active=$5, updated_at=NOW()
        WHERE id=$6
    """, updated["name"], updated["description"], updated["price"], updated["credits_allocated"], updated["is_active"], product_id)
    return updated

# Also keep PUT for backward compatibility
@router.put("/{product_id}", response_model=ProductOut)
async def update_product(product_id: uuid.UUID, product: ProductUpdate, db=Depends(get_db)):
    row = await db.fetchrow("SELECT * FROM products WHERE id=$1", product_id)
    if not row:
        raise HTTPException(status_code=404, detail="Product not found")
    updated = row.copy()
    for field, value in product.dict(exclude_unset=True).items():
        updated[field] = value
    await db.execute("""
        UPDATE products SET name=$1, description=$2, price=$3, credits_allocated=$4, is_active=$5, updated_at=NOW()
        WHERE id=$6
    """, updated["name"], updated["description"], updated["price"], updated["credits_allocated"], updated["is_active"], product_id)
    return updated

# DELETE product (frontend expects DELETE /api/admin/products/{product_id})
@router.delete("/{product_id}")
async def delete_product(product_id: uuid.UUID, db=Depends(get_db)):
    row = await db.fetchrow("SELECT * FROM products WHERE id=$1", product_id)
    if not row:
        raise HTTPException(status_code=404, detail="Product not found")
    await db.execute("DELETE FROM products WHERE id=$1", product_id)
    return {"success": True}

# LIST products (frontend expects GET /api/admin/products)
@router.get("", response_model=List[dict])
async def list_products(db=Depends(get_db)):
    rows = await db.fetch("SELECT * FROM products ORDER BY created_at DESC")
    return [dict(row) for row in rows]

# SYNC with Stripe (frontend expects POST /api/admin/stripe/sync-products)
from fastapi import APIRouter as MainAPIRouter
main_router = MainAPIRouter()

@main_router.post("/api/admin/stripe/sync-products")
async def sync_stripe_products(db=Depends(get_db)):
    rows = await db.fetch("SELECT id, name, price FROM products WHERE stripe_product_id IS NULL")
    for row in rows:
        stripe_product_id, stripe_price_id = await create_stripe_product(row["name"], row["price"])
        await db.execute("UPDATE products SET stripe_product_id=$1, stripe_price_id=$2 WHERE id=$3", stripe_product_id, stripe_price_id, row["id"])
    return {"success": True, "message": "Stripe sync complete"}

@router.get("/credit-packages")
async def get_credit_packages(db=Depends(get_db)):
    """Get all credit packages"""
    try:
        result = await db.fetch("SELECT * FROM credit_packages ORDER BY price_usd")
        return [
            {
                "id": str(row["id"]),
                "name": row["name"],
                "description": row["description"],
                "price_usd": float(row["price_usd"]),
                "credits_amount": row["credits_amount"],
                "bonus_credits": row["bonus_credits"],
                "enabled": row["enabled"],
                "created_at": row["created_at"].isoformat() if row["created_at"] else None
            }
            for row in result
        ]
    except Exception as e:
        logger.error(f"Error fetching credit packages: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch credit packages") 