from fastapi import APIRouter, Depends, HTTPException, Request, Body
from datetime import datetime
import uuid
import logging
from db import get_db
from utils.welcome_credits_utils import get_dynamic_welcome_credits, set_dynamic_welcome_credits, validate_welcome_credits

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin/products", tags=["Admin Products"])

# --- ROOT PRODUCTS ENDPOINT ---
@router.get("/")
async def get_products(db=Depends(get_db)):
    """Root endpoint for Products tab - returns all products/services"""
    try:
        # Get all service types
        service_types = await db.fetch("SELECT * FROM service_types WHERE enabled=TRUE ORDER BY name")
        
        # Get all credit packages  
        credit_packages = await db.fetch("SELECT * FROM credit_packages WHERE enabled=TRUE ORDER BY credits_amount")
        
        # Format as products list
        products = []
        
        # Add service types as products
        for row in service_types:
            products.append({
                "id": str(row["id"]),
                "sku_code": f"SVC_{row['name'].upper()}",
                "name": row["display_name"] or row["name"],
                "price": float(row["price_usd"] or 0),
                "credits_allocated": row.get("base_credits") or row.get("credits_required") or 1,
                "is_active": row["enabled"],
                "type": "service",
                "category": row.get("service_category")
            })
        
        # Add credit packages as products
        for row in credit_packages:
            products.append({
                "id": str(row["id"]),
                "sku_code": f"CREDITS_{row['credits_amount']}",
                "name": row["name"],
                "price": float(row["price_usd"]),
                "credits_allocated": row["credits_amount"],
                "is_active": row["enabled"],
                "type": "credit_package",
                "category": "credits"
            })
        
        return {
            "success": True,
            "data": {
                "service_types": [dict(row) for row in service_types],
                "credit_packages": [dict(row) for row in credit_packages],
                "products": products,
                "total_count": len(service_types) + len(credit_packages)
            }
        }
        
    except Exception as e:
        logger.error(f"Products endpoint error: {e}")
        return {"success": False, "error": str(e), "data": []}

# --- SERVICE TYPES ENDPOINTS (with real DB logic) ---
@router.post("/service-types")
async def create_service_type(service_type: dict = Body(...), db=Depends(get_db)):
    print("SERVICE TYPE POST CALLED")
    enabled = service_type.get("enabled", service_type.get("is_active", True))
    await db.execute(
        """
        INSERT INTO service_types (name, display_name, description, credits_required, duration_minutes, 
                                 price_usd, service_category, avatar_video_enabled, live_chat_enabled, 
                                 icon, color_gradient, enabled, dynamic_pricing_enabled, knowledge_domains,
                                 persona_modes, comprehensive_reading_enabled, birth_chart_enabled,
                                 remedies_enabled, voice_enabled, video_enabled, created_at)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20, NOW())
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
        enabled,
        service_type.get("dynamic_pricing_enabled", False),
        service_type.get("knowledge_domains", []),
        service_type.get("persona_modes", []),
        service_type.get("comprehensive_reading_enabled", False),
        service_type.get("birth_chart_enabled", False),
        service_type.get("remedies_enabled", False),
        service_type.get("voice_enabled", False),
        service_type.get("video_enabled", False)
    )
    return {"success": True}

@router.get("/service-types")
async def get_service_types(db=Depends(get_db)):
    print("SERVICE TYPE GET CALLED")
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
            "enabled": row["enabled"],
            "is_active": row["enabled"],
            "service_category": row["service_category"],
            "avatar_video_enabled": row["avatar_video_enabled"],
            "live_chat_enabled": row["live_chat_enabled"],
            "icon": row["icon"],
            "color_gradient": row["color_gradient"],
            "created_at": row["created_at"].isoformat() if row["created_at"] else None,
            # Enhanced fields
            "dynamic_pricing_enabled": row.get("dynamic_pricing_enabled", False),
            "knowledge_domains": row.get("knowledge_domains", []),
            "persona_modes": row.get("persona_modes", []),
            "comprehensive_reading_enabled": row.get("comprehensive_reading_enabled", False),
            "birth_chart_enabled": row.get("birth_chart_enabled", False),
            "remedies_enabled": row.get("remedies_enabled", False),
            "voice_enabled": row.get("voice_enabled", False),
            "video_enabled": row.get("video_enabled", False)
        }
        for row in result
    ]

@router.put("/service-types/{service_type_id}")
async def update_service_type(service_type_id: int, service_type: dict = Body(...), db=Depends(get_db)):
    print("SERVICE TYPE PUT CALLED")
    enabled = service_type.get("enabled", service_type.get("is_active", True))
    result = await db.execute(
        """
        UPDATE service_types SET name=$1, display_name=$2, description=$3, credits_required=$4, 
                               duration_minutes=$5, price_usd=$6, service_category=$7, 
                               avatar_video_enabled=$8, live_chat_enabled=$9, icon=$10, 
                               color_gradient=$11, enabled=$12, dynamic_pricing_enabled=$13,
                               knowledge_domains=$14, persona_modes=$15, comprehensive_reading_enabled=$16,
                               birth_chart_enabled=$17, remedies_enabled=$18, voice_enabled=$19,
                               video_enabled=$20, updated_at=NOW()
        WHERE id=$21
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
        enabled,
        service_type.get("dynamic_pricing_enabled", False),
        service_type.get("knowledge_domains", []),
        service_type.get("persona_modes", []),
        service_type.get("comprehensive_reading_enabled", False),
        service_type.get("birth_chart_enabled", False),
        service_type.get("remedies_enabled", False),
        service_type.get("voice_enabled", False),
        service_type.get("video_enabled", False),
        int(service_type_id)
    )
    # Optionally, check if any row was updated and return 404 if not
    if result == "UPDATE 0":
        return {"success": False, "error": "Service type not found"}, 404
    return {"success": True}

@router.delete("/service-types/{service_type_id}")
async def delete_service_type(service_type_id: int, db=Depends(get_db)):
    print("SERVICE TYPE DELETE CALLED")
    result = await db.execute(
        "UPDATE service_types SET enabled=FALSE WHERE id=$1",
        int(service_type_id)
    )
    if result == "UPDATE 0":
        return {"success": False, "error": "Service type not found"}, 404
    return {"success": True}

# --- PRICING CONFIG ENDPOINTS ---
@router.get("/pricing-config")
async def get_pricing_config(db=Depends(get_db)):
    print("PRICING CONFIG GET CALLED")
    result = await db.fetch("SELECT * FROM pricing_config ORDER BY id ASC")
    return [
        {
            "id": str(row["id"]),
            "config_key": row.get("config_key") or row.get("key"),
            "config_value": row.get("config_value") or row.get("value"),
            "config_type": row.get("config_type") or row.get("type"),
            "description": row["description"],
            "is_active": row["is_active"],
            "updated_at": row["updated_at"].isoformat() if row["updated_at"] else None
        }
        for row in result
    ]

@router.post("/pricing-config")
async def create_pricing_config(config: dict = Body(...), db=Depends(get_db)):
    print("PRICING CONFIG POST CALLED")
    await db.execute(
        """
        INSERT INTO pricing_config (key, value, type, description, is_active, updated_at)
        VALUES ($1, $2, $3, $4, $5, NOW())
        """,
        config.get("config_key") or config.get("key"),
        config.get("config_value") or config.get("value"),
        config.get("config_type") or config.get("type"),
        config.get("description"),
        config.get("is_active", True)
    )
    return {"success": True}

@router.put("/pricing-config/{config_key}")
async def update_pricing_config(config_key: str, config: dict = Body(...), db=Depends(get_db)):
    print("PRICING CONFIG PUT CALLED")
    result = await db.execute(
        """
        UPDATE pricing_config SET value=$1, type=$2, description=$3, 
                                 is_active=$4, updated_at=NOW()
        WHERE key=$5
        """,
        config.get("config_value") or config.get("value"),
        config.get("config_type") or config.get("type"),
        config.get("description"),
        config.get("is_active", True),
        config_key
    )
    if result == "UPDATE 0":
        return {"success": False, "error": "Config not found"}, 404
    return {"success": True}

@router.get("/pricing/welcome-credits")
async def get_welcome_credits_config(db=Depends(get_db)):
    """Get current welcome credits configuration"""
    try:
        # Use shared utility function
        welcome_credits = await get_dynamic_welcome_credits()
        
        return {
            "success": True,
            "welcome_credits": welcome_credits
        }
        
    except Exception as e:
        logger.error(f"Error getting welcome credits config: {e}")
        raise HTTPException(status_code=500, detail="Failed to get welcome credits configuration")

@router.put("/pricing/welcome-credits")
async def update_welcome_credits_config(request: Request, db=Depends(get_db)):
    """Update welcome credits configuration"""
    try:
        data = await request.json()
        welcome_credits = data.get("welcome_credits", 20)
        
        # Validate welcome credits using shared utility
        if not validate_welcome_credits(welcome_credits):
            raise HTTPException(status_code=400, detail="Invalid welcome credits value")
        
        # Use shared utility function
        success = await set_dynamic_welcome_credits(welcome_credits)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update welcome credits")
        
        logger.info(f"Welcome credits updated to: {welcome_credits}")
        
        return {
            "success": True,
            "message": f"Welcome credits updated to {welcome_credits}",
            "welcome_credits": welcome_credits
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating welcome credits config: {e}")
        raise HTTPException(status_code=500, detail="Failed to update welcome credits configuration")

# --- DONATIONS ENDPOINTS ---
@router.get("/donations")
async def get_donations(db=Depends(get_db)):
    print("DONATIONS GET CALLED")
    result = await db.fetch("SELECT * FROM donations ORDER BY price_usd")
    return [
        {
            "id": str(row["id"]),
            "name": row["name"],
            "tamil_name": row["tamil_name"],
            "description": row["description"],
            "price_usd": float(row["price_usd"]),
            "icon": row["icon"],
            "category": row["category"],
            "enabled": row["enabled"],
            "created_at": row["created_at"].isoformat() if row["created_at"] else None
        }
        for row in result
    ]

@router.post("/donations")
async def create_donation(donation: dict = Body(...), db=Depends(get_db)):
    print("DONATION POST CALLED")
    await db.execute(
        """
        INSERT INTO donations (name, tamil_name, description, price_usd, icon, category, enabled, created_at)
        VALUES ($1, $2, $3, $4, $5, $6, $7, NOW())
        """,
        donation.get("name"),
        donation.get("tamil_name"),
        donation.get("description"),
        float(donation.get("price_usd", 0)),
        donation.get("icon", "🪔"),
        donation.get("category", "offering"),
        donation.get("enabled", True)
    )
    return {"success": True}

@router.put("/donations/{donation_id}")
async def update_donation(donation_id: str, donation: dict = Body(...), db=Depends(get_db)):
    print("DONATION PUT CALLED")
    result = await db.execute(
        """
        UPDATE donations SET name=$1, tamil_name=$2, description=$3, price_usd=$4, 
                            icon=$5, category=$6, enabled=$7, updated_at=NOW()
        WHERE id=$8
        """,
        donation.get("name"),
        donation.get("tamil_name"),
        donation.get("description"),
        float(donation.get("price_usd", 0)),
        donation.get("icon", "🪔"),
        donation.get("category", "offering"),
        donation.get("enabled", True),
        donation_id
    )
    if result == "UPDATE 0":
        return {"success": False, "error": "Donation not found"}, 404
    return {"success": True}

@router.delete("/donations/{donation_id}")
async def delete_donation(donation_id: str, db=Depends(get_db)):
    print("DONATION DELETE CALLED")
    result = await db.execute(
        "UPDATE donations SET enabled=FALSE WHERE id=$1",
        donation_id
    )
    if result == "UPDATE 0":
        return {"success": False, "error": "Donation not found"}, 404
    return {"success": True}

# --- CREDIT PACKAGES ENDPOINTS ---
@router.get("/credit-packages")
async def get_credit_packages(db=Depends(get_db)):
    print("CREDIT PACKAGES GET CALLED")
    result = await db.fetch("SELECT * FROM credit_packages ORDER BY credits_amount")
    return [
        {
            "id": str(row["id"]),
            "name": row["name"],
            "credits_amount": row["credits_amount"],
            "price_usd": float(row["price_usd"]),
            "bonus_credits": row["bonus_credits"],
            "stripe_product_id": row["stripe_product_id"],
            "stripe_price_id": row["stripe_price_id"],
            "enabled": row["enabled"],
            "created_at": row["created_at"].isoformat() if row["created_at"] else None
        }
        for row in result
    ]

@router.post("/credit-packages")
async def create_credit_package(package: dict = Body(...), db=Depends(get_db)):
    print("CREDIT PACKAGE POST CALLED")
    await db.execute(
        """
        INSERT INTO credit_packages (name, credits_amount, price_usd, bonus_credits, 
                                   stripe_product_id, stripe_price_id, enabled, created_at)
        VALUES ($1, $2, $3, $4, $5, $6, $7, NOW())
        """,
        package.get("name"),
        int(package.get("credits_amount", 0)),
        float(package.get("price_usd", 0)),
        int(package.get("bonus_credits", 0)),
        package.get("stripe_product_id"),
        package.get("stripe_price_id"),
        package.get("enabled", True)
    )
    return {"success": True}

@router.put("/credit-packages/{package_id}")
async def update_credit_package(package_id: str, package: dict = Body(...), db=Depends(get_db)):
    print("CREDIT PACKAGE PUT CALLED")
    result = await db.execute(
        """
        UPDATE credit_packages SET name=$1, credits_amount=$2, price_usd=$3, bonus_credits=$4,
                                 stripe_product_id=$5, stripe_price_id=$6, enabled=$7, updated_at=NOW()
        WHERE id=$8
        """,
        package.get("name"),
        int(package.get("credits_amount", 0)),
        float(package.get("price_usd", 0)),
        int(package.get("bonus_credits", 0)),
        package.get("stripe_product_id"),
        package.get("stripe_price_id"),
        package.get("enabled", True),
        package_id
    )
    if result == "UPDATE 0":
        return {"success": False, "error": "Credit package not found"}, 404
    return {"success": True}

@router.delete("/credit-packages/{package_id}")
async def delete_credit_package(package_id: str, db=Depends(get_db)):
    print("CREDIT PACKAGE DELETE CALLED")
    result = await db.execute(
        "DELETE FROM credit_packages WHERE id=$1",
        package_id
    )
    if result == "DELETE 0":
        return {"success": False, "error": "Credit package not found"}, 404
    return {"success": True}

# --- PRODUCT ENDPOINTS (must be below service-types endpoints) ---
@router.post("/{product_id}")
async def update_product_post(product_id: uuid.UUID, product: dict = Body(...)):
    print("PRODUCT POST CALLED")
    return {"success": True, "debug": f"product endpoint hit for {product_id}"}

@router.put("/{product_id}")
async def update_product(product_id: uuid.UUID, product: dict = Body(...)):
    print("PRODUCT PUT CALLED")
    return {"success": True, "debug": f"product endpoint hit for {product_id}"}

@router.delete("/{product_id}")
async def delete_product(product_id: uuid.UUID):
    print("PRODUCT DELETE CALLED")
    return {"success": True, "debug": f"product endpoint hit for {product_id}"} 