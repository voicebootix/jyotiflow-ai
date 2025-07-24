"""
📝 RESPONSE SCHEMAS

Standard response models for consistent API responses across the system.
"""

from pydantic import BaseModel
from typing import Optional, Any, Dict, List


class StandardResponse(BaseModel):
    """Standard API response format used across all JyotiFlow endpoints"""
    success: bool
    message: Optional[str] = None
    data: Optional[Any] = None
    error: Optional[str] = None
    error_code: Optional[str] = None
    timestamp: Optional[str] = None
    request_id: Optional[str] = None
    
    class Config:
        json_encoders = {
            # Add any custom encoders if needed
        }
    
    def set_success_from_status(self) -> 'StandardResponse':
        """Auto-set success field based on error presence"""
        self.success = self.error is None
        return self


class PaginatedResponse(StandardResponse):
    """Paginated response for list endpoints"""
    total: Optional[int] = None
    page: Optional[int] = None
    page_size: Optional[int] = None
    total_pages: Optional[int] = None


class ErrorResponse(StandardResponse):
    """Error response with additional error details"""
    success: bool = False
    error_details: Optional[Dict[str, Any]] = None
    validation_errors: Optional[List[Dict[str, str]]] = None
    
    
class SuccessResponse(StandardResponse):
    """Success response with data"""
    success: bool = True 