import os
import httpx
from typing import Optional, Dict, Any, List
import asyncio

from backend.config.logging_config import get_logger

logger = get_logger(__name__)

REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
REPLICATE_BASE_URL = "https://api.replicate.com/v1"

class ReplicateService:
    def __init__(self, api_token: str = REPLICATE_API_TOKEN):
        if not api_token:
            raise ValueError("REPLICATE_API_TOKEN is not set.")
        self.api_token = api_token
        self.headers = {
            "Authorization": f"Token {self.api_token}",
            "Content-Type": "application/json",
        }

    async def run_prediction(self, model_name: str, input_data: Dict[str, Any], version: Optional[str] = None) -> Optional[str]:
        """
        Starts a prediction on Replicate and returns the URL to check for results.
        Note: This is an asynchronous operation on Replicate's side.
        For simplicity in this service, we will poll for the result.
        """
        # Find the latest version of the model if not specified
        if not version:
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    model_url = f"{REPLICATE_BASE_URL}/models/{model_name}"
                    response = await client.get(model_url, headers=self.headers)
                    response.raise_for_status()
                    model_details = response.json()
                    version = model_details.get("latest_version", {}).get("id")
                    if not version:
                        logger.error(f"Could not automatically determine the latest version for model {model_name}.")
                        return None
            except Exception as e:
                logger.error(f"Failed to fetch model version for {model_name}: {e}", exc_info=True)
                return None

        prediction_payload = {
            "version": version,
            "input": input_data,
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                predictions_url = f"{REPLICATE_BASE_URL}/predictions"
                logger.info(f"Starting prediction for model version: {version}")
                
                response = await client.post(predictions_url, headers=self.headers, json=prediction_payload)
                response.raise_for_status()
                
                prediction_data = response.json()
                status_check_url = prediction_data.get("urls", {}).get("get")

                # Polling for the result
                for _ in range(60): # Poll for up to 5 minutes (60 * 5s)
                    await asyncio.sleep(5)
                    status_response = await client.get(status_check_url, headers=self.headers)
                    status_data = status_response.json()
                    
                    if status_data["status"] == "succeeded":
                        output = status_data.get("output")
                        # The output can be a list or a single item
                        if isinstance(output, list) and output:
                            return output[0]
                        return output
                    elif status_data["status"] in ["failed", "canceled"]:
                        logger.error(f"Prediction failed or was canceled: {status_data.get('error')}")
                        return None
                
                logger.warning("Prediction timed out after 5 minutes.")
                return None

        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to start prediction. Status: {e.response.status_code}, Response: {e.response.text}", exc_info=True)
            return None
        except Exception as e:
            logger.error(f"An unexpected error occurred during prediction: {e}", exc_info=True)
            return None

    async def download_image(self, url: str) -> Optional[bytes]:
        """Downloads an image from a given URL."""
        if not url:
            return None
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.get(url)
                response.raise_for_status()
                return response.content
        except Exception as e:
            logger.error(f"Failed to download image from {url}: {e}", exc_info=True)
            return None

# Dependency injector
def get_replicate_service() -> ReplicateService:
    return ReplicateService()
