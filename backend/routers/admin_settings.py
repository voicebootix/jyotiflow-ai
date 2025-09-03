from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
from ..db import get_db
import uuid

router = APIRouter(prefix="/api/admin", tags=["Admin Settings"])

@router.get("/platform-settings")
async def get_platform_settings(db=Depends(get_db)):
    rows = await db.fetch("SELECT * FROM platform_settings")
    return [dict(row) for row in rows]

@router.put("/platform-settings")
async def update_platform_settings(key: str, value: dict, db=Depends(get_db)):
    await db.execute("UPDATE platform_settings SET value=$1, updated_at=NOW() WHERE key=$2", value, key)
    return {"success": True}

@router.get("/ai-model-config")
async def get_ai_model_config(db=Depends(get_db)):
    row = await db.fetchrow("SELECT value FROM platform_settings WHERE key='ai_model_config'")
    return row["value"] if row else {}

@router.put("/ai-model-config")
async def update_ai_model_config(value: dict, db=Depends(get_db)):
    await db.execute("UPDATE platform_settings SET value=$1, updated_at=NOW() WHERE key='ai_model_config'", value)
    return {"success": True} 