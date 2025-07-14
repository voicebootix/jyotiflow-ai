from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any
from auth.jwt_config import JWTHandler
from datetime import datetime, timezone
import os

# Security scheme for JWT tokens
security_scheme = HTTPBearer()

async def get_current_user(request: Request) -> Dict[str, Any]:
    """
    Dependency to get current authenticated user using centralized JWT handler
    """
    return JWTHandler.get_full_user_info(request)

async def get_current_user_legacy(credentials: HTTPAuthorizationCredentials = Depends(security_scheme)) -> Dict[str, Any]:
    """
    Legacy method for backward compatibility - uses HTTPBearer scheme
    """
    try:
        # Create a mock request object with the Authorization header
        class MockRequest:
            def __init__(self, token):
                self.headers = {"Authorization": f"Bearer {token}"}
        
        mock_request = MockRequest(credentials.credentials)
        return JWTHandler.get_full_user_info(mock_request)
    except HTTPException:
        # Re-raise JWT handler exceptions
        raise
    except Exception as e:
        print(f"Unexpected JWT error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_admin(request: Request) -> Dict[str, Any]:
    """
    Dependency to get current authenticated admin using centralized JWT handler
    """
    return JWTHandler.verify_admin_access(request)

async def get_current_admin_dependency(request: Request) -> Dict[str, Any]:
    """
    FastAPI dependency to get current authenticated admin
    """
    return JWTHandler.verify_admin_access(request)

async def get_current_user_optional(request: Request) -> Dict[str, Any] | None:
    """
    Optional authentication - returns None if not authenticated
    """
    try:
        return JWTHandler.get_full_user_info(request)
    except HTTPException:
        return None

async def get_admin_user(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Verify that current user is an admin (legacy method)
    """
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access admin endpoints"
        )
    return current_user 