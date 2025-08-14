"""
🚀 LoRA Model Management API Router
Handles all interactions with the Replicate API for LoRA model training.
"""

import logging
import os
import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Annotated, Literal

from auth.auth_helpers import AuthenticationHelper
from schemas.response import StandardResponse

logger = logging.getLogger(__name__)
lora_router = APIRouter()

REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
REPLICATE_BASE_URL = "https://api.replicate.com/v1"

class CreateModelRequest(BaseModel):
    owner: str = Field(..., description="The Replicate username or organization name that owns the model.")
    model_name: str = Field("swamiji-lora-model", description="The name for the new model.")
    visibility: Literal["public", "private"] = Field("private", description="Visibility of the model ('public' or 'private').")
    hardware: str = Field("gpu-t4", description="Hardware SKU for the model. Changed from gpu-a40-large.")

@lora_router.post("/create-model", response_model=StandardResponse)
async def create_replicate_model(
    request: CreateModelRequest,
    _admin_user: Annotated[dict, Depends(AuthenticationHelper.verify_admin_access_strict)]
):
    """
    Creates a new model placeholder on Replicate to be used as a training destination.
    """
    if not REPLICATE_API_TOKEN:
        raise HTTPException(status_code=500, detail="REPLICATE_API_TOKEN is not configured on the server.")
    
    headers = {
        "Authorization": f"Token {REPLICATE_API_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "owner": request.owner,
        "name": request.model_name,
        "visibility": request.visibility,
        "hardware": request.hardware
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            model_url = f"{REPLICATE_BASE_URL}/models"
            logger.info(f"Attempting to create Replicate model: {request.owner}/{request.model_name}")
            response = await client.post(model_url, headers=headers, json=payload)
            
            # Replicate returns 409 Conflict if model already exists, which is a success case for us.
            if response.status_code == 409:
                logger.warning(f"Replicate model '{request.owner}/{request.model_name}' already exists. This is okay.")
                # We can fetch the existing model data to confirm and return it.
                get_response = await client.get(f"{model_url}/{request.owner}/{request.model_name}", headers=headers)
                get_response.raise_for_status()
                existing_model_data = get_response.json()
                return StandardResponse(success=True, message=f"Model '{request.owner}/{request.model_name}' already exists.", data=existing_model_data)

            response.raise_for_status()
            created_model_data = response.json()
            logger.info(f"Successfully created Replicate model: {created_model_data.get('url')}")
            return StandardResponse(success=True, message=f"Successfully created Replicate model '{request.owner}/{request.model_name}'.", data=created_model_data)

    except httpx.HTTPStatusError as e:
        logger.error(f"Failed to create Replicate model. Status: {e.response.status_code}, Response: {e.response.text}", exc_info=True)
        raise HTTPException(status_code=502, detail=f"Failed to communicate with Replicate API: {e.response.text}") from e
    except Exception as e:
        logger.error(f"An unexpected error occurred while creating Replicate model: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An unexpected error occurred.") from e
