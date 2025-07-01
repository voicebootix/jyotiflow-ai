from fastapi import APIRouter, Request

router = APIRouter(prefix="/api/credits", tags=["Credits"])

@router.post("/purchase")
async def purchase_credits(request: Request):
    data = await request.json()
    # TODO: Replace with real purchase logic
    return {"success": True, "message": "Credits purchased", "data": data} 