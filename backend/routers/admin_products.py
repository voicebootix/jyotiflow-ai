from fastapi import APIRouter, Body, Depends, HTTPException
import uuid

router = APIRouter(prefix="/api/admin/products", tags=["Admin Products"])

# --- SERVICE TYPES ENDPOINTS (must be above product_id endpoints) ---
@router.post("/service-types")
async def create_service_type(service_type: dict = Body(...)):
    print("SERVICE TYPE POST CALLED")
    return {"success": True, "debug": "service-types endpoint hit"}

@router.get("/service-types")
async def get_service_types():
    print("SERVICE TYPE GET CALLED")
    return []

@router.put("/service-types/{service_type_id}")
async def update_service_type(service_type_id: str, service_type: dict = Body(...)):
    print("SERVICE TYPE PUT CALLED")
    return {"success": True, "debug": "service-types update endpoint hit"}

@router.delete("/service-types/{service_type_id}")
async def delete_service_type(service_type_id: str):
    print("SERVICE TYPE DELETE CALLED")
    return {"success": True, "debug": "service-types delete endpoint hit"}

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