from fastapi import APIRouter, Body, Depends
from db import get_db
import uuid

router = APIRouter(prefix="/api/admin/products", tags=["Admin Products"])

# --- SERVICE TYPES ENDPOINTS (with real DB logic) ---
@router.post("/service-types")
async def create_service_type(service_type: dict = Body(...), db=Depends(get_db)):
    print("SERVICE TYPE POST CALLED")
    enabled = service_type.get("enabled", service_type.get("is_active", True))
    await db.execute(
        """
        INSERT INTO service_types (name, display_name, description, credits_required, duration_minutes, 
                                 price_usd, service_category, avatar_video_enabled, live_chat_enabled, 
                                 icon, color_gradient, enabled, created_at)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, NOW())
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
        enabled
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
            "created_at": row["created_at"].isoformat() if row["created_at"] else None
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
                               color_gradient=$11, enabled=$12, updated_at=NOW()
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
        enabled,
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
    result = await db.fetch("SELECT * FROM pricing_config ORDER BY config_key")
    return [
        {
            "id": str(row["id"]),
            "config_key": row["config_key"],
            "config_value": row["config_value"],
            "config_type": row["config_type"],
            "description": row["description"],
            "is_active": row["is_active"],
            "created_at": row["created_at"].isoformat() if row["created_at"] else None
        }
        for row in result
    ]

@router.post("/pricing-config")
async def create_pricing_config(config: dict = Body(...), db=Depends(get_db)):
    print("PRICING CONFIG POST CALLED")
    await db.execute(
        """
        INSERT INTO pricing_config (config_key, config_value, config_type, description, is_active, created_at)
        VALUES ($1, $2, $3, $4, $5, NOW())
        """,
        config.get("config_key"),
        config.get("config_value"),
        config.get("config_type", "string"),
        config.get("description"),
        config.get("is_active", True)
    )
    return {"success": True}

@router.put("/pricing-config/{config_key}")
async def update_pricing_config(config_key: str, config: dict = Body(...), db=Depends(get_db)):
    print("PRICING CONFIG PUT CALLED")
    result = await db.execute(
        """
        UPDATE pricing_config SET config_value=$1, config_type=$2, description=$3, 
                                 is_active=$4, updated_at=NOW()
        WHERE config_key=$5
        """,
        config.get("config_value"),
        config.get("config_type", "string"),
        config.get("description"),
        config.get("is_active", True),
        config_key
    )
    if result == "UPDATE 0":
        return {"success": False, "error": "Config not found"}, 404
    return {"success": True}

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
        "UPDATE credit_packages SET enabled=FALSE WHERE id=$1",
        package_id
    )
    if result == "UPDATE 0":
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