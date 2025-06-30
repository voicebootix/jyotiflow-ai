from fastapi import APIRouter

router = APIRouter(prefix="/api/content", tags=["Content"])

@router.get("/daily-wisdom")
async def get_daily_wisdom():
    # Dummy data, replace with real DB fetch
    return {"wisdom": "Be kind. Be present. Be grateful."}

@router.get("/satsang-schedule")
async def get_satsang_schedule():
    # Dummy data, replace with real DB fetch
    return {"schedule": [
        {"date": "2024-07-01", "topic": "Meditation"},
        {"date": "2024-07-08", "topic": "Bhakti Yoga"}
    ]} 