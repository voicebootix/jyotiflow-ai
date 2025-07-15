"""
CENTRALIZED AUTHENTICATION HELPERS
Provides consistent authentication patterns across all routers.
Eliminates authentication inconsistencies without duplicating logic.
"""

from fastapi import Request, HTTPException
from auth.jwt_config import JWTHandler
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class AuthenticationHelper:
    """
    Centralized authentication helper that provides consistent patterns
    for all authentication needs across the application.
    """
    
    @staticmethod
    def get_user_id_strict(request: Request) -> str:
        """
        Extract user ID from JWT token - STRICT MODE
        Throws 401 if token is missing or invalid.
        Use for endpoints that require authentication.
        """
        return JWTHandler.get_user_id_from_token(request)
    
    @staticmethod
    def get_user_id_optional(request: Request) -> Optional[str]:
        """
        Extract user ID from JWT token - OPTIONAL MODE
        Returns None if token is missing or invalid.
        Use for endpoints with graceful fallback.
        """
        try:
            return JWTHandler.get_user_id_from_token(request)
        except HTTPException:
            return None
        except Exception as e:
            logger.debug(f"Optional authentication failed: {e}")
            return None
    
    @staticmethod
    def get_user_info_strict(request: Request) -> Dict[str, Any]:
        """
        Get full user information from JWT token - STRICT MODE
        Throws 401 if token is missing or invalid.
        Use for endpoints that require authentication.
        """
        return JWTHandler.get_full_user_info(request)
    
    @staticmethod
    def get_user_info_optional(request: Request) -> Optional[Dict[str, Any]]:
        """
        Get full user information from JWT token - OPTIONAL MODE
        Returns None if token is missing or invalid.
        Use for endpoints with graceful fallback.
        """
        try:
            return JWTHandler.get_full_user_info(request)
        except HTTPException:
            return None
        except Exception as e:
            logger.debug(f"Optional authentication failed: {e}")
            return None
    
    @staticmethod
    def verify_admin_access_strict(request: Request) -> Dict[str, Any]:
        """
        Verify admin access - STRICT MODE
        Throws 401/403 if token is missing, invalid, or not admin.
        Use for admin-only endpoints.
        """
        return JWTHandler.verify_admin_access(request)
    
    @staticmethod
    def convert_user_id_to_int(user_id: Optional[str]) -> Optional[int]:
        """
        Convert string user_id to integer for database queries.
        Returns None if user_id is None or invalid.
        Centralized conversion logic.
        """
        if not user_id:
            return None
        try:
            return int(user_id)
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def get_user_email_strict(request: Request) -> str:
        """
        Extract user email from JWT token - STRICT MODE
        Throws 401 if token is missing or invalid.
        """
        email = JWTHandler.get_user_email_from_token(request)
        if email is None:
            raise HTTPException(status_code=401, detail="User email not found in token")
        return email
    
    @staticmethod
    def get_user_email_optional(request: Request) -> Optional[str]:
        """
        Extract user email from JWT token - OPTIONAL MODE
        Returns None if token is missing or invalid.
        """
        try:
            return JWTHandler.get_user_email_from_token(request)
        except HTTPException:
            return None
        except Exception as e:
            logger.debug(f"Optional email extraction failed: {e}")
            return None

# Legacy compatibility functions for existing code
def get_user_id_from_token_strict(request: Request) -> str:
    """Legacy compatibility - strict mode"""
    return AuthenticationHelper.get_user_id_strict(request)

def get_user_id_from_token_optional(request: Request) -> Optional[str]:
    """Legacy compatibility - optional mode"""
    return AuthenticationHelper.get_user_id_optional(request)

def convert_user_id_to_int(user_id: Optional[str]) -> Optional[int]:
    """Legacy compatibility - user ID conversion"""
    return AuthenticationHelper.convert_user_id_to_int(user_id)