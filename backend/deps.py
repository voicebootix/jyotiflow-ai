from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any
from auth.jwt_config import JWTHandler
from auth.auth_helpers import AuthenticationHelper
from db import get_db
from datetime import datetime, timezone
import os

# Security scheme for JWT tokens
security_scheme = HTTPBearer()


# JWT configuration - SECURITY FIX: Require environment variable
JWT_SECRET_KEY = os.getenv("JWT_SECRET")
if not JWT_SECRET_KEY:
    raise RuntimeError("JWT_SECRET environment variable is required for security. Please set it before starting the application.")
JWT_ALGORITHM = "HS256"

# Environment configuration for admin access control
APP_ENV = os.getenv("APP_ENV", "production").lower()
ALLOW_ADMIN_BYPASS = os.getenv("ALLOW_ADMIN_BYPASS", "false").lower() == "true"

async def get_current_user(request: Request) -> Dict[str, Any]:
    """
    Dependency to get current authenticated user using centralized JWT handler
    """
    return AuthenticationHelper.get_user_info_strict(request)

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

async def get_current_admin(request: Request, db=Depends(get_db)) -> Dict[str, Any]:
    """
    Dependency to get current authenticated admin using centralized JWT handler
"""
    return await AuthenticationHelper.verify_admin_access_strict(request, db)

async def get_current_admin_dependency(request: Request, db=Depends(get_db)) -> Dict[str, Any]:
    """
    FastAPI dependency to get current authenticated admin
    """
    return await AuthenticationHelper.verify_admin_access_strict(request, db)

async def get_current_user_optional(request: Request) -> Dict[str, Any] | None:
    """
    Optional authentication - returns None if not authenticated
    """
    return AuthenticationHelper.get_user_info_optional(request)

async def get_admin_user(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """

    Verify that current user is an admin (legacy method)

    """
    user_role = current_user.get("role")
    user_id = current_user.get("sub")
    user_email = current_user.get("email", "unknown")
    
    # SECURITY FIX: Strict admin role verification in production
    if APP_ENV == "production":
        # Production: First check for missing/empty role
        if not user_role:
            print(f"SECURITY: Missing role for user {user_email}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid admin credentials"
            )
        
        # Production: Second check for non-admin role
        if user_role != "admin":
            print(f"SECURITY: Access denied for user {user_email} (role: {user_role}) - admin role required")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. Admin privileges required."
            )
            
        print(f"SECURITY: Admin access granted to {user_email} in production")
        
    elif APP_ENV in ["development", "dev", "local"]:
        # Development: Allow bypass only if explicitly enabled via environment variable
        if ALLOW_ADMIN_BYPASS and user_role != "admin":
            print(f"DEV WARNING: Admin bypass enabled for user {user_email} (role: {user_role})")
            print(f"DEV WARNING: This bypass is ONLY allowed in development. Set ALLOW_ADMIN_BYPASS=false for production.")
            
            # Add admin role to user for development purposes
            current_user["role"] = "admin"
            current_user["_dev_bypass"] = True
            
        elif user_role != "admin":
            print(f"SECURITY: Access denied for user {user_email} (role: {user_role}) - admin role required")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. Admin privileges required."
            )
            
        print(f"DEV: Admin access granted to {user_email} in development")
        
    else:
        # Unknown environment: Default to strict security
        print(f"SECURITY: Unknown environment '{APP_ENV}' - defaulting to production security")
        if user_role != "admin":
            print(f"SECURITY: Access denied for user {user_email} (role: {user_role}) - admin role required")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. Admin privileges required."
            )
    
    # Final verification: Ensure user has admin role
    if current_user.get("role") != "admin":
        print(f"SECURITY: Final admin role check failed for user {user_email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role verification failed"
        )
    
    return current_user

def verify_admin_environment():
    """
    Verify admin access configuration on startup
    """
    if APP_ENV == "production":
        if ALLOW_ADMIN_BYPASS:
            raise RuntimeError(
                "SECURITY ERROR: ALLOW_ADMIN_BYPASS=true is not permitted in production. "
                "Set ALLOW_ADMIN_BYPASS=false or remove the environment variable."
            )
        print("✅ SECURITY: Production admin access properly configured - strict role checking enabled")
    
    elif APP_ENV in ["development", "dev", "local"]:
        if ALLOW_ADMIN_BYPASS:
            print("⚠️  DEV WARNING: Admin bypass is enabled in development mode")
            print("⚠️  DEV WARNING: Ensure ALLOW_ADMIN_BYPASS=false in production")
        else:
            print("✅ DEV: Strict admin role checking enabled in development")
    
    else:
        print(f"⚠️  WARNING: Unknown APP_ENV '{APP_ENV}' - defaulting to production security")

# Verify configuration on import
verify_admin_environment() 