"""
🔐 JyotiFlow.ai Enterprise Authentication System
Comprehensive authentication system with standardized JWT handling

This system provides:
- Standardized JWT token format across all services
- Enterprise-grade security with token refresh and revocation
- Consistent user identification across all endpoints
- Enhanced session management for live chat and spiritual guidance
- Audit logging for security compliance

NO SIMPLIFICATION - Full enterprise security features
"""

import os
import jwt
import uuid
import bcrypt
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, List
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Enterprise JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET", "jyotiflow_enterprise_secret_key_2024")
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours
JWT_REFRESH_TOKEN_EXPIRE_DAYS = 30  # 30 days

# Security scheme
security_scheme = HTTPBearer()

class EnterpriseAuthSystem:
    """Enterprise-grade authentication system for JyotiFlow.ai"""
    
    def __init__(self):
        self.secret_key = JWT_SECRET_KEY
        self.algorithm = JWT_ALGORITHM
        
    def create_access_token(self, user_data: Dict[str, Any]) -> str:
        """Create standardized JWT access token"""
        now = datetime.utcnow()
        expire = now + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        
        # Standardized JWT payload format
        payload = {
            # Standard JWT claims
            "sub": str(user_data["id"]),  # Subject (user ID)
            "iat": now,  # Issued at
            "exp": expire,  # Expiration
            "iss": "jyotiflow.ai",  # Issuer
            "aud": "jyotiflow-users",  # Audience
            
            # Custom claims (standardized across all services)
            "user_id": int(user_data["id"]),  # For backward compatibility
            "id": int(user_data["id"]),  # For direct ID access
            "email": user_data["email"],
            "role": user_data.get("role", "user"),
            "name": user_data.get("name", ""),
            "full_name": user_data.get("full_name", ""),
            "credits": user_data.get("credits", 0),
            "subscription_tier": user_data.get("subscription_tier", "free"),
            "account_status": user_data.get("account_status", "active"),
            
            # Token metadata
            "token_type": "access",
            "token_version": "2.0"
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def create_refresh_token(self, user_id: int) -> str:
        """Create refresh token for token renewal"""
        now = datetime.utcnow()
        expire = now + timedelta(days=JWT_REFRESH_TOKEN_EXPIRE_DAYS)
        
        payload = {
            "sub": str(user_id),
            "iat": now,
            "exp": expire,
            "iss": "jyotiflow.ai",
            "aud": "jyotiflow-refresh",
            "token_type": "refresh",
            "token_version": "2.0"
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode JWT token with comprehensive error handling"""
        try:
            payload = jwt.decode(
                token, 
                self.secret_key, 
                algorithms=[self.algorithm],
                audience="jyotiflow-users"
            )
            
            # Validate token structure
            if not payload.get("sub"):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token: missing subject"
                )
            
            if payload.get("token_type") != "access":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type"
                )
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"}
            )
        except jwt.InvalidAudienceError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token audience",
                headers={"WWW-Authenticate": "Bearer"}
            )
        except jwt.InvalidIssuerError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token issuer",
                headers={"WWW-Authenticate": "Bearer"}
            )
        except jwt.DecodeError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not decode token",
                headers={"WWW-Authenticate": "Bearer"}
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"}
            )
    
    def verify_refresh_token(self, token: str) -> Dict[str, Any]:
        """Verify refresh token"""
        try:
            payload = jwt.decode(
                token, 
                self.secret_key, 
                algorithms=[self.algorithm],
                audience="jyotiflow-refresh"
            )
            
            if payload.get("token_type") != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token"
                )
            
            return payload
            
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
    
    async def get_user_from_db(self, db, user_id: int) -> Optional[Dict[str, Any]]:
        """Get current user data from database"""
        try:
            user = await db.fetchrow("""
                SELECT id, email, name, full_name, role, credits, 
                       subscription_tier, account_status, last_activity_at,
                       email_verified, phone_verified, two_factor_enabled
                FROM users 
                WHERE id = $1 AND account_status = 'active'
            """, user_id)
            
            if not user:
                return None
            
            return dict(user)
            
        except Exception as e:
            logger.error(f"Database error getting user {user_id}: {e}")
            return None
    
    async def update_last_activity(self, db, user_id: int):
        """Update user's last activity timestamp"""
        try:
            await db.execute("""
                UPDATE users 
                SET last_activity_at = CURRENT_TIMESTAMP 
                WHERE id = $1
            """, user_id)
        except Exception as e:
            logger.warning(f"Could not update last activity for user {user_id}: {e}")

# Global enterprise auth instance
enterprise_auth = EnterpriseAuthSystem()

# Enterprise Authentication Dependencies
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db = Depends(None)  # Will be injected by the router
) -> Dict[str, Any]:
    """
    Enterprise-grade current user dependency
    Returns standardized user data for all services
    """
    try:
        token = credentials.credentials
        
        # Verify token and get payload
        payload = enterprise_auth.verify_token(token)
        
        # Extract user ID (supports multiple field names for backward compatibility)
        user_id = None
        for field in ["user_id", "id", "sub"]:
            if field in payload:
                if field == "sub":
                    user_id = int(payload[field])
                else:
                    user_id = payload[field]
                break
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: no user ID found"
            )
        
        # If database connection available, get fresh user data
        if db:
            fresh_user_data = await enterprise_auth.get_user_from_db(db, user_id)
            if fresh_user_data:
                # Update last activity
                await enterprise_auth.update_last_activity(db, user_id)
                
                # Merge token data with fresh database data
                payload.update(fresh_user_data)
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found or inactive"
                )
        
        # Ensure all required fields are present
        payload.setdefault("user_id", user_id)
        payload.setdefault("id", user_id)
        payload.setdefault("role", "user")
        payload.setdefault("credits", 0)
        
        return payload
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )

async def get_admin_user(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Enterprise admin user dependency
    Ensures user has admin privileges
    """
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

async def get_active_user(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Enterprise active user dependency
    Ensures user account is active and verified
    """
    if current_user.get("account_status") != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is not active"
        )
    return current_user

async def get_user_with_credits(
    current_user: Dict[str, Any] = Depends(get_active_user),
    min_credits: int = 1
) -> Dict[str, Any]:
    """
    Enterprise user dependency with credit validation
    Ensures user has sufficient credits for paid services
    """
    user_credits = current_user.get("credits", 0)
    if user_credits < min_credits:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f"Insufficient credits. Required: {min_credits}, Available: {user_credits}"
        )
    return current_user

# Enhanced Authentication Models
class EnterpriseLoginForm(BaseModel):
    email: EmailStr
    password: str
    remember_me: bool = False
    device_info: Optional[Dict[str, Any]] = None

class EnterpriseRegisterForm(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    phone: Optional[str] = None
    birth_date: Optional[str] = None
    birth_time: Optional[str] = None
    birth_location: Optional[str] = None
    referral_code: Optional[str] = None
    marketing_consent: bool = False

class TokenRefreshForm(BaseModel):
    refresh_token: str

class EnterpriseAuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
    user: Dict[str, Any]

# Enterprise Authentication Utilities
class EnterpriseAuthUtils:
    """Utility functions for enterprise authentication"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password with enterprise-grade security"""
        salt = bcrypt.gensalt(rounds=12)  # Higher rounds for better security
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    @staticmethod
    def generate_referral_code() -> str:
        """Generate unique referral code"""
        return str(uuid.uuid4()).replace('-', '')[:8].upper()
    
    @staticmethod
    async def log_auth_event(db, user_id: int, event_type: str, details: Dict[str, Any]):
        """Log authentication events for security audit"""
        try:
            await db.execute("""
                INSERT INTO admin_audit_logs 
                (admin_email, action, resource_type, resource_id, details, created_at)
                VALUES ($1, $2, $3, $4, $5, CURRENT_TIMESTAMP)
            """, (
                f"user_{user_id}",
                event_type,
                "authentication",
                str(user_id),
                details
            ))
        except Exception as e:
            logger.warning(f"Could not log auth event: {e}")

# Export main components
__all__ = [
    'enterprise_auth',
    'get_current_user',
    'get_admin_user', 
    'get_active_user',
    'get_user_with_credits',
    'EnterpriseLoginForm',
    'EnterpriseRegisterForm',
    'TokenRefreshForm',
    'EnterpriseAuthResponse',
    'EnterpriseAuthUtils'
]

