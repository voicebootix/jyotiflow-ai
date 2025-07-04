from fastapi import APIRouter, Body, Depends
from db import get_db

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
async def update_service_type(service_type_id: str, service_type: dict = Body(...), db=Depends(get_db)):
    print("SERVICE TYPE PUT CALLED")
    enabled = service_type.get("enabled", service_type.get("is_active", True))
    await db.execute(
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
        service_type_id
    )
    return {"success": True}

@router.delete("/service-types/{service_type_id}")
async def delete_service_type(service_type_id: str, db=Depends(get_db)):
    print("SERVICE TYPE DELETE CALLED")
    await db.execute(
        "UPDATE service_types SET enabled=FALSE WHERE id=$1",
        service_type_id
    )
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