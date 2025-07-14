import os
from typing import Optional
from fastapi import Request, HTTPException
import jwt
import logging

logger = logging.getLogger(__name__)

# Centralized JWT configuration
JWT_SECRET = os.getenv("JWT_SECRET", "jyotiflow_secret")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

class JWTHandler:
    @staticmethod
    def extract_token_from_request(request: Request) -> str:
        """Extract JWT token from Authorization header"""
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
        return auth_header.split(" ")[1]
    
    @staticmethod
    def decode_token(token: str) -> dict:
        """Decode and validate JWT token"""
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.InvalidTokenError:
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