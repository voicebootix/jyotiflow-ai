from fastapi import APIRouter

router = APIRouter(
    prefix="/api/content",
    tags=["content"]
)

@router.get("/daily-wisdom")
async def get_daily_wisdom():
    return {"wisdom": "Today is a great day for spiritual growth!"}

@router.get("/satsang-schedule")
async def get_satsang_schedule():
    return {"schedule": "Every Sunday at 10am"} 