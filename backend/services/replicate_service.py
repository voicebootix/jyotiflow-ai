"""
🤖 REPLICATE SERVICE

This service provides a centralized interface for interacting with the Replicate API,
specifically for running predictions with custom LoRA models.
"""

import os
import logging
import replicate
from typing import Optional

logger = logging.getLogger(__name__)

class ReplicateService:
    """A service class to manage interactions with the Replicate API."""

    def __init__(self):
        self.client = None
        self.is_configured = False
        self._initialize_client()

    def _initialize_client(self):
        """Initializes the Replicate client if the API token is available."""
        api_token = os.getenv("REPLICATE_API_TOKEN")
        if api_token:
            self.client = replicate.Client(api_token=api_token)
            self.is_configured = True
            logger.info("✅ Replicate client initialized successfully.")
        else:
            logger.warning("REPLICATE_API_TOKEN is not configured. Replicate service is disabled.")

    def run_lora_prediction(
        self,
        model_name: str,
        model_version: str,
        prompt: str
    ) -> Optional[str]:
        """
        Runs a prediction on a specified LoRA model version on Replicate.

        Args:
            model_name: The name of the model (e.g., 'voicebootix/jyoti_swami').
            model_version: The specific version ID of the LoRA model to use.
            prompt: The text prompt to guide the image generation.

        Returns:
            The URL of the generated image, or None if the prediction fails.
        """
        if not self.is_configured:
            logger.error("Cannot run LoRA prediction, Replicate service is not configured.")
            return None

        try:
            model_string = f"{model_name}:{model_version}"
            input_data = {"prompt": prompt}
            
            logger.info(f"Running Replicate prediction for model: {model_string}")
            
            # The replicate.run() function handles the prediction synchronously
            output = self.client.run(model_string, input=input_data)
            
            # The output is typically a list of URLs
            if output and isinstance(output, list) and len(output) > 0:
                generated_image_url = output[0]
                logger.info(f"✅ Successfully generated image from Replicate: {generated_image_url}")
                return generated_image_url
            else:
                logger.error(f"Replicate prediction returned an unexpected output: {output}")
                return None

        except Exception as e:
            logger.error(f"Failed to run Replicate LoRA prediction: {e}", exc_info=True)
            return None

# --- FastAPI Dependency Injection ---
_replicate_service_instance = None

def get_replicate_service() -> ReplicateService:
    """
    FastAPI dependency that provides a singleton instance of the ReplicateService.
    """
    global _replicate_service_instance
    if _replicate_service_instance is None:
        _replicate_service_instance = ReplicateService()
    return _replicate_service_instance
