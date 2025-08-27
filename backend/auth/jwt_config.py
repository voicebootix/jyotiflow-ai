import os
from typing import Optional
from fastapi import Request, HTTPException
import jwt
import logging

logger = logging.getLogger(__name__)

# Centralized JWT configuration - SECURITY FIX: No hardcoded fallback
JWT_SECRET = os.getenv("JWT_SECRET")

def validate_jwt_secret_security():
    """
    Validate JWT secret for security requirements
    Raises RuntimeError if security requirements are not met
    """
    if not JWT_SECRET:
        error_msg = "JWT_SECRET environment variable is required for security. Please set it before starting the application."
        logger.critical(error_msg)
        raise RuntimeError(error_msg)

    # Check for common insecure default values
    insecure_defaults = [
        "jyotiflow_secret",
        "secret",
        "jwt_secret",
        "your-secret-key",
        "change-me",
        "default",
        "test",
        "password",
        "123456"
    ]
    
    if JWT_SECRET.lower() in insecure_defaults:
        error_msg = f"JWT_SECRET cannot use predictable default value '{JWT_SECRET}'. Please generate a secure random secret."
        logger.critical(error_msg)
        raise RuntimeError(error_msg)
    
    # Check minimum length for production
    if len(JWT_SECRET) < 32:
        error_msg = f"JWT_SECRET must be at least 32 characters long for security. Current length: {len(JWT_SECRET)}"
        logger.critical(error_msg)
        raise RuntimeError(error_msg)
    
    # Check for environment-specific requirements
    environment = os.getenv("ENVIRONMENT", "development").lower()
    if environment in ["production", "prod", "live"]:
        # Additional production checks
        if JWT_SECRET.isalnum() or JWT_SECRET.isdigit():
            error_msg = "JWT_SECRET in production must contain mixed characters, numbers, and symbols for security."
            logger.critical(error_msg)
            raise RuntimeError(error_msg)
    
    logger.info("JWT_SECRET security validation passed")

# Perform security validation on startup
validate_jwt_secret_security()

JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

class JWTHandler:
    @staticmethod
    def extract_token_from_request(request: Request) -> str:
        """Extract JWT token from Authorization header"""
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            raise HTTPException(status_code=401, detail="Missing authorization header")
        
        # Strip leading/trailing whitespace and split into parts
        parts = auth_header.strip().split(None, 1) 
        
        if len(parts) != 2 or parts[0].lower() != "bearer" or not parts[1]:
            raise HTTPException(status_code=401, detail="Invalid authorization header format. Must be 'Bearer <token>'")
        
        return parts[1]
    
    @staticmethod
    def decode_token(token: str) -> dict:
        """Decode and validate JWT token"""
        try:
            # DEBUG: Log token and secret (redacted)
            logger.debug(f"DEBUG: Decoding token: {token[:10]}...{token[-10:]}")
            logger.debug(f"DEBUG: Using JWT_SECRET (redacted length): {len(JWT_SECRET) if JWT_SECRET else 0}")
            logger.debug(f"DEBUG: Using JWT_ALGORITHM: {JWT_ALGORITHM}")
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token error: {e}")
            raise HTTPException(status_code=401, detail="Invalid token")
    
    @staticmethod
    def get_user_id_from_token(request: Request) -> str:
        """Extract user ID from JWT token with standardized field access"""
        token = JWTHandler.extract_token_from_request(request)
        payload = JWTHandler.decode_token(token)
        
        # Standardized field priority: sub > user_id > id
        user_id = payload.get("sub") or payload.get("user_id") or payload.get("id")
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID not found in token")
        return str(user_id)
    
    @staticmethod
    def get_user_email_from_token(request: Request) -> Optional[str]:
        """Extract user email from JWT token with standardized field access"""
        token = JWTHandler.extract_token_from_request(request)
        payload = JWTHandler.decode_token(token)
        
        # Standardized field priority: email > user_email
        return payload.get("email") or payload.get("user_email")
    
    @staticmethod
    def get_user_role_from_token(request: Request) -> str:
        """Extract user role for admin authentication"""
        token = JWTHandler.extract_token_from_request(request)
        payload = JWTHandler.decode_token(token)
        
        # Standardized field priority: role > user_role
        return payload.get("role", "user")
    
    @staticmethod
    def verify_admin_access(request: Request) -> dict:
        """Verify admin access and return user info"""
        token = JWTHandler.extract_token_from_request(request)
        payload = JWTHandler.decode_token(token)
        
        user_role = payload.get("role", "user")
        if user_role not in ["admin", "super_admin"]:
            raise HTTPException(status_code=403, detail="Admin access required")
        
        return {
            "user_id": JWTHandler.get_user_id_from_token(request),
            "email": JWTHandler.get_user_email_from_token(request),
            "role": user_role
        }
    
    @staticmethod
    def get_full_user_info(request: Request) -> dict:
        """Get complete user information from JWT token"""
        token = JWTHandler.extract_token_from_request(request)
        payload = JWTHandler.decode_token(token)
        
        return {
            "user_id": JWTHandler.get_user_id_from_token(request),
            "email": JWTHandler.get_user_email_from_token(request),
            "role": JWTHandler.get_user_role_from_token(request),
            "payload": payload
        }

# Standalone wrapper functions for backwards compatibility
def get_user_email_from_token(request: Request) -> Optional[str]:
    """Standalone wrapper for JWTHandler.get_user_email_from_token"""
    return JWTHandler.get_user_email_from_token(request)

def get_user_id_from_token(request: Request) -> str:
    """Standalone wrapper for JWTHandler.get_user_id_from_token"""
    return JWTHandler.get_user_id_from_token(request)

def get_user_role_from_token(request: Request) -> str:
    """Standalone wrapper for JWTHandler.get_user_role_from_token"""
    return JWTHandler.get_user_role_from_token(request)