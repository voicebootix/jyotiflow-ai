from fastapi import APIRouter, Depends, HTTPException, status, Body
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

@router.get("/donations")
async def get_donations(db=Depends(get_db)):
    """Get all enabled donation options"""
    try:
        result = await db.fetch("SELECT * FROM donations WHERE enabled=TRUE ORDER BY price_usd")
        return [
            {
                "id": str(row["id"]),
                "name": row["name"],
                "tamil_name": row.get("tamil_name", ""),
                "description": row["description"],
                "price_usd": float(row["price_usd"]),
                "icon": row.get("icon", ""),
                "enabled": row["enabled"],
                "created_at": row["created_at"].isoformat() if row["created_at"] else None
            }
            for row in result
        ]
    except Exception as e:
        logger.error(f"Error fetching donations: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch donations")

@router.post("/donations")
async def create_donation(donation: dict = Body(...), db=Depends(get_db)):
    """Create a new donation option"""
    try:
        await db.execute(
            """
            INSERT INTO donations (name, tamil_name, description, price_usd, icon, enabled, created_at)
            VALUES ($1, $2, $3, $4, $5, $6, NOW())
            """,
            donation.get("name"),
            donation.get("tamil_name"),
            donation.get("description"),
            float(donation.get("price_usd", 0)),
            donation.get("icon", ""),
            donation.get("enabled", True)
        )
        return {"success": True}
    except Exception as e:
        logger.error(f"Error creating donation: {e}")
        raise HTTPException(status_code=500, detail="Failed to create donation")

@router.put("/donations/{donation_id}")
async def update_donation(donation_id: str, donation: dict = Body(...), db=Depends(get_db)):
    """Update an existing donation option"""
    try:
        await db.execute(
            """
            UPDATE donations SET name=$1, tamil_name=$2, description=$3, price_usd=$4, icon=$5, enabled=$6 WHERE id=$7
            """,
            donation.get("name"),
            donation.get("tamil_name"),
            donation.get("description"),
            float(donation.get("price_usd", 0)),
            donation.get("icon", ""),
            donation.get("enabled", True),
            donation_id
        )
        return {"success": True}
    except Exception as e:
        logger.error(f"Error updating donation: {e}")
        raise HTTPException(status_code=500, detail="Failed to update donation")

@router.delete("/donations/{donation_id}")
async def delete_donation(donation_id: str, db=Depends(get_db)):
    """Disable (soft delete) a donation option"""
    try:
        await db.execute(
            "UPDATE donations SET enabled=FALSE WHERE id=$1",
            donation_id
        )
        return {"success": True}
    except Exception as e:
        logger.error(f"Error deleting donation: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete donation")

# Service Types Management
@router.get("/service-types")
async def get_service_types(db=Depends(get_db)):
    """Get all service types"""
    try:
        result = await db.fetch("SELECT * FROM service_types ORDER BY credits_required")
        return [
            {
                "id": str(row["id"]),
                "name": row["name"],
                "display_name": row["display_name"],
                "description": row["description"],
                "credits_required": row["credits_required"],
                "duration_minutes": row["duration_minutes"],
                "price_usd": float(row["price_usd"]),
                "is_active": row["is_active"],
                "service_category": row["service_category"],
                "avatar_video_enabled": row["avatar_video_enabled"],
                "live_chat_enabled": row["live_chat_enabled"],
                "icon": row["icon"],
                "color_gradient": row["color_gradient"],
                "created_at": row["created_at"].isoformat() if row["created_at"] else None
            }
            for row in result
        ]
    except Exception as e:
        logger.error(f"Error fetching service types: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch service types")

@router.post("/service-types")
async def create_service_type(service_type: dict = Body(...), db=Depends(get_db)):
    """Create a new service type"""
    try:
        await db.execute(
            """
            INSERT INTO service_types (name, display_name, description, credits_required, duration_minutes, 
                                     price_usd, service_category, avatar_video_enabled, live_chat_enabled, 
                                     icon, color_gradient, created_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, NOW())
            """,
            service_type.get("name"),
            service_type.get("display_name"),
            service_type.get("description"),
            int(service_type.get("credits_required", 1)),
            int(service_type.get("duration_minutes", 5)),
            float(service_type.get("price_usd", 0)),
            service_type.get("service_category", "guidance"),
            service_type.get("avatar_video_enabled", False),
            service_type.get("live_chat_enabled", False),
            service_type.get("icon", "🔮"),
            service_type.get("color_gradient", "from-purple-500 to-indigo-600")
        )
        return {"success": True}
    except Exception as e:
        logger.error(f"Error creating service type: {e}")
        raise HTTPException(status_code=500, detail="Failed to create service type")

@router.put("/service-types/{service_type_id}")
async def update_service_type(service_type_id: str, service_type: dict = Body(...), db=Depends(get_db)):
    """Update an existing service type"""
    try:
        await db.execute(
            """
            UPDATE service_types SET name=$1, display_name=$2, description=$3, credits_required=$4, 
                                   duration_minutes=$5, price_usd=$6, service_category=$7, 
                                   avatar_video_enabled=$8, live_chat_enabled=$9, icon=$10, 
                                   color_gradient=$11, is_active=$12, updated_at=NOW()
            WHERE id=$13
            """,
            service_type.get("name"),
            service_type.get("display_name"),
            service_type.get("description"),
            int(service_type.get("credits_required", 1)),
            int(service_type.get("duration_minutes", 5)),
            float(service_type.get("price_usd", 0)),
            service_type.get("service_category", "guidance"),
            service_type.get("avatar_video_enabled", False),
            service_type.get("live_chat_enabled", False),
            service_type.get("icon", "🔮"),
            service_type.get("color_gradient", "from-purple-500 to-indigo-600"),
            service_type.get("is_active", True),
            service_type_id
        )
        return {"success": True}
    except Exception as e:
        logger.error(f"Error updating service type: {e}")
        raise HTTPException(status_code=500, detail="Failed to update service type")

@router.delete("/service-types/{service_type_id}")
async def delete_service_type(service_type_id: str, db=Depends(get_db)):
    """Disable (soft delete) a service type"""
    try:
        await db.execute(
            "UPDATE service_types SET is_active=FALSE WHERE id=$1",
            service_type_id
        )
        return {"success": True}
    except Exception as e:
        logger.error(f"Error deleting service type: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete service type")

# Pricing Configuration Management
@router.get("/pricing-config")
async def get_pricing_config(db=Depends(get_db)):
    """Get all pricing configuration variables"""
    try:
        result = await db.fetch("SELECT * FROM pricing_config WHERE is_active=TRUE ORDER BY config_key")
        return [
            {
                "id": str(row["id"]),
                "config_key": row["config_key"],
                "config_value": row["config_value"],
                "config_type": row["config_type"],
                "description": row["description"],
                "created_at": row["created_at"].isoformat() if row["created_at"] else None
            }
            for row in result
        ]
    except Exception as e:
        logger.error(f"Error fetching pricing config: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch pricing config")

@router.post("/pricing-config")
async def create_pricing_config(config: dict = Body(...), db=Depends(get_db)):
    """Create a new pricing configuration variable"""
    try:
        await db.execute(
            """
            INSERT INTO pricing_config (config_key, config_value, config_type, description, created_at)
            VALUES ($1, $2, $3, $4, NOW())
            """,
            config.get("config_key"),
            config.get("config_value"),
            config.get("config_type", "string"),
            config.get("description")
        )
        return {"success": True}
    except Exception as e:
        logger.error(f"Error creating pricing config: {e}")
        raise HTTPException(status_code=500, detail="Failed to create pricing config")

@router.put("/pricing-config/{config_key}")
async def update_pricing_config(config_key: str, config: dict = Body(...), db=Depends(get_db)):
    """Update an existing pricing configuration variable"""
    try:
        await db.execute(
            """
            UPDATE pricing_config SET config_value=$1, config_type=$2, description=$3, updated_at=NOW()
            WHERE config_key=$4
            """,
            config.get("config_value"),
            config.get("config_type", "string"),
            config.get("description"),
            config_key
        )
        return {"success": True}
    except Exception as e:
        logger.error(f"Error updating pricing config: {e}")
        raise HTTPException(status_code=500, detail="Failed to update pricing config") 