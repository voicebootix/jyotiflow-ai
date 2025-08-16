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
            
            logger.info(f"Received output from Replicate: {output}")

            # The output can be a list, a string, or a dictionary.
            if isinstance(output, list):
                if output:
                    generated_image_url = str(output[0])
                    logger.info(f"✅ Successfully extracted image URL from list: {generated_image_url}")
                    return generated_image_url
                else:
                    logger.warning("Replicate output was an empty list.")
                    return None
            elif isinstance(output, str):
                logger.info(f"✅ Successfully received image URL string: {output}")
                return output
            elif isinstance(output, dict):
                # Common keys where the result might be found
                for key in ["image", "output", "result", "url"]:
                    if key in output and output[key]:
                        # Handle cases where the value is a list or a direct string
                        value = output[key]
                        if isinstance(value, list) and value:
                            url = str(value[0])
                            logger.info(f"✅ Successfully extracted image URL from dict key '{key}': {url}")
                            return url
                        elif isinstance(value, str):
                            logger.info(f"✅ Successfully extracted image URL from dict key '{key}': {value}")
                            return value
                logger.error(f"Replicate prediction returned a dictionary with no recognized image URL key: {output}")
                return None
            else:
                logger.error(f"Replicate prediction returned an unexpected output type: {type(output)} - {output}")
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
