"""
📦 SUPABASE STORAGE SERVICE

This service provides a centralized interface for interacting with Supabase Storage.
It handles file uploads, retrievals, and management in a standardized way.
"""

import os
import logging
from supabase import create_client, Client

logger = logging.getLogger(__name__)

class SupabaseStorageService:
    """A service class to manage interactions with Supabase Storage."""

    def __init__(self):
        self.supabase: Client = None
        self.is_configured = False
        self._initialize_client()

    def _initialize_client(self):
        """Initializes the Supabase client if credentials are available."""
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

        if supabase_url and supabase_key:
            try:
                self.supabase = create_client(supabase_url, supabase_key)
                self.is_configured = True
                logger.info("✅ Supabase client initialized successfully.")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Supabase client: {e}", exc_info=True)
        else:
            logger.warning("Supabase URL or Key is not configured. Storage service is disabled.")

    def upload_file(self, bucket_name: str, file_path_in_bucket: str, file_content: bytes, content_type: str) -> str:
        """
        Uploads a file to a specified Supabase bucket.

        Args:
            bucket_name: The name of the bucket to upload to.
            file_path_in_bucket: The desired path and filename within the bucket.
            file_content: The file content in bytes.
            content_type: The MIME type of the file.

        Returns:
            The public URL of the uploaded file.
        
        Raises:
            Exception: If the upload fails or the service is not configured.
        """
        if not self.is_configured:
            raise Exception("Supabase Storage is not configured on the server.")

        try:
            # The 'file_options' dictionary is crucial for setting the MIME type.
            # 'upsert=True' means it will overwrite the file if it already exists.
            self.supabase.storage.from_(bucket_name).upload(
                path=file_path_in_bucket,
                file=file_content,
                file_options={"content-type": content_type, "upsert": "true"}
            )
            logger.info(f"Successfully uploaded file to Supabase bucket '{bucket_name}' at path '{file_path_in_bucket}'.")
            
            # After uploading, get the public URL.
            public_url = self.get_public_url(bucket_name, file_path_in_bucket)
            return public_url

        except Exception as e:
            # The Supabase client might raise various exceptions. We catch them broadly.
            logger.error(f"Failed to upload file to Supabase: {e}", exc_info=True)
            raise Exception(f"Could not upload file to storage: {e}")

    def get_public_url(self, bucket_name: str, file_path_in_bucket: str) -> str:
        """
        Retrieves the public URL for a file in a bucket.
        """
        if not self.is_configured:
            raise Exception("Supabase Storage is not configured on the server.")
        
        try:
            response = self.supabase.storage.from_(bucket_name).get_public_url(file_path_in_bucket)
            return response
        except Exception as e:
            logger.error(f"Failed to get public URL from Supabase for path '{file_path_in_bucket}': {e}", exc_info=True)
            raise Exception(f"Could not retrieve file URL: {e}")


# --- FastAPI Dependency Injection ---
# Use a singleton pattern to avoid re-initializing the client on every request.
_storage_service_instance = None

def get_storage_service() -> SupabaseStorageService:
    """
    FastAPI dependency that provides a singleton instance of the SupabaseStorageService.
    """
    global _storage_service_instance
    if _storage_service_instance is None:
        _storage_service_instance = SupabaseStorageService()
    return _storage_service_instance 