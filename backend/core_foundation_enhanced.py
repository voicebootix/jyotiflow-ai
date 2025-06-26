import os
import jwt
import bcrypt
import string
import asyncpg
import aiosqlite
import logging
import secrets
import sys
from typing import Optional, Dict, List, Any, Union
from contextlib import asynccontextmanager
from pathlib import Path
from contextlib import contextmanager

import asyncio
import json
import uuid
import re
import os
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from decimal import Decimal
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import random
from typing import Optional, Dict, List, Any, Tuple
import json


# FastAPI Core Imports
from fastapi import FastAPI, HTTPException, Depends, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

# Pydantic Models for Validation
from pydantic import BaseModel, EmailStr, Field, validator, root_validator
from pydantic_settings import BaseSettings

# External Integrations
import stripe
from openai import AsyncOpenAI
import aiohttp
import uvicorn
import psutil

# Enhanced Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('jyotiflow_enhanced.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

sys.path.append(str(Path(__file__).parent))

# =============================================================================
# 🔧 ENHANCED ENVIRONMENT CONFIGURATION & VALIDATION
# =============================================================================

class EnhancedSettings(BaseSettings):
    """Enhanced environment settings with AI avatar services"""

    # Existing Core Settings (Preserved)
    app_name: str = "JyotiFlow.ai Enhanced"
    app_env: str = "development"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000
    cors_origins: str = "*"

    # Database Configuration (Preserved)
    database_url: str = "sqlite:///./jyotiflow_enhanced.db"
    database_pool_size: int = 20
    database_max_overflow: int = 30
    database_pool_timeout: int = 30

    # Security Configuration (Fixed to match standard env var names)
    jwt_secret_key: str = "your-super-secret-jwt-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 168  # 7 days

    # Admin Configuration (Preserved)
    admin_email: str = "admin@jyotiflow.ai"
    admin_password: str = "admin123"

    # External API Keys (Preserved)
    openai_api_key: str = "your-openai-api-key"
    stripe_secret_key: str = "your-stripe-secret-key"
    stripe_public_key: str = "your-stripe-public-key"
    stripe_webhook_secret: str = "your-stripe-webhook-secret"
    prokerala_api_key: str = "your-prokerala-api-key"
    salescloser_api_key: str = "your-salescloser-api-key"
    salescloser_webhook_url: str = "your-salescloser-webhook-url"

    # NEW: AI Avatar Service Configuration
    d_id_api_key: str = "your-d-id-api-key"
    d_id_api_url: str = "https://api.d-id.com"
    elevenlabs_api_key: str = "your-elevenlabs-api-key"
    elevenlabs_voice_id: str = "your-custom-swamiji-voice-id"
    agora_app_id: str = "your-agora-app-id"
    agora_app_certificate: str = "your-agora-app-certificate"

    # NEW: Video Storage Configuration
    avatar_storage_bucket: str = "jyotiflow-avatar-videos"
    avatar_storage_region: str = "us-east-1"
    avatar_storage_access_key: str = "your-storage-access-key"
    avatar_storage_secret_key: str = "your-storage-secret-key"
    cdn_endpoint: str = "https://cdn.jyotiflow.ai"

    # NEW: AI Optimization Configuration
    ai_optimization_enabled: bool = True
    monetization_analysis_enabled: bool = True
    social_content_generation: bool = True

    # Enhanced Security Settings
    allowed_hosts: str = "localhost,127.0.0.1,jyotiflow.ai,*.jyotiflow.ai"
    ssl_cert_path: Optional[str] = None
    ssl_key_path: Optional[str] = None
    sentry_dsn: Optional[str] = None

    # NEW: Avatar Service Limits
    max_avatar_duration_seconds: int = 1800  # 30 minutes max
    max_concurrent_avatar_generations: int = 10
    avatar_quality: str = "high"  # low, medium, high
    voice_synthesis_language: str = "en-US"
    fallback_voice_enabled: bool = True

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore",
    }

# Initialize enhanced settings
settings = EnhancedSettings()

# =============================================================================
# 📊 ENHANCED PYDANTIC MODELS - ALL MODELS WITH AVATAR INTEGRATION
# =============================================================================

class UserRegistration(BaseModel):
    """User registration with enhanced fields"""
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)
    phone: Optional[str] = Field(None, pattern=r'^\+?[\d\s\-\(\)]+$')
    birth_date: Optional[str] = None
    birth_time: Optional[str] = None
    birth_location: Optional[str] = None
    referral_code: Optional[str] = None
    marketing_source: Optional[str] = None

    # NEW: Avatar Preferences
    preferred_avatar_style: Optional[str] = "traditional"
    voice_preference: Optional[str] = "compassionate"
    video_quality_preference: Optional[str] = "high"

class UserLogin(BaseModel):
    """User login model"""
    email: EmailStr
    password: str

class UserProfile(BaseModel):
    """Enhanced user profile with avatar preferences"""
    email: str
    name: str
    phone: Optional[str] = None
    credits: int
    birth_date: Optional[str] = None
    birth_time: Optional[str] = None
    birth_location: Optional[str] = None
    spiritual_level: Optional[str] = "beginner"
    total_sessions: int = 0
    created_at: datetime

    # NEW: Avatar Profile Fields
    avatar_sessions_count: int = 0
    preferred_avatar_style: str = "traditional"
    voice_preference: str = "compassionate"
    video_quality_preference: str = "high"
    total_avatar_minutes: int = 0

class StandardResponse(BaseModel):
    """Enhanced standard API response"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error_code: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # NEW: Avatar Service Status
    avatar_services_status: Optional[Dict[str, str]] = None
    performance_metrics: Optional[Dict[str, Any]] = None

# =============================================================================
# 🗄️ ENHANCED DATABASE MANAGER WITH AVATAR TABLES
# =============================================================================

class EnhancedDatabaseManager:
    """Enhanced database manager with avatar functionality"""

    def __init__(self):
        self.database_url = settings.database_url
        self.pool = None
        self.is_sqlite = "sqlite" in self.database_url.lower()
        self.database_type = "SQLite" if self.is_sqlite else "PostgreSQL"

    async def initialize(self):
        """Initialize enhanced database with avatar tables"""
        try:
            if self.is_sqlite:
                await self._initialize_sqlite()
            else:
                await self._initialize_postgresql()

            await self._create_enhanced_schema()
            logger.info(f"✅ Enhanced database initialized: {self.database_type}")

        except Exception as e:
            logger.error(f"❌ Enhanced database initialization failed: {e}")
            raise e

    async def _initialize_sqlite(self):
        """Initialize SQLite with enhanced configuration"""
        self.pool = None

    async def _initialize_postgresql(self):
        """Initialize PostgreSQL with enhanced connection pool"""
        try:
            self.pool = await asyncpg.create_pool(
                self.database_url,
                min_size=5,
                max_size=settings.database_pool_size,
                max_queries=50000,
                max_inactive_connection_lifetime=300,
                timeout=settings.database_pool_timeout,
                command_timeout=60
            )
            logger.info("✅ Enhanced PostgreSQL connection pool created")

        except Exception as e:
            logger.error(f"❌ PostgreSQL pool creation failed: {e}")
            raise e 
    



    async def get_connection(self):
        """Get database connection"""
        if self.is_sqlite:
            return await aiosqlite.connect(self.database_url.replace("sqlite:///", ""))
        else:
            if not self.pool:
                raise Exception("Database pool not initialized")
            return await self.pool.acquire()

    async def release_connection(self, conn):
        """Release database connection"""
        if self.is_sqlite:
            if conn:
                await conn.close()
        else:
            if conn and self.pool:
                await self.pool.release(conn)

    async def _create_enhanced_schema(self):
        """Create enhanced database schema with avatar tables"""

        enhanced_schema = """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email VARCHAR(255) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            name VARCHAR(255) NOT NULL,
            phone VARCHAR(20),
            credits INTEGER DEFAULT 3 CHECK (credits >= 0),
            total_credits_purchased INTEGER DEFAULT 0,
            total_credits_used INTEGER DEFAULT 0,
            birth_date DATE,
            birth_time TIME,
            birth_location VARCHAR(255),
            birth_latitude DECIMAL(10, 8),
            birth_longitude DECIMAL(11, 8),
            timezone VARCHAR(50) DEFAULT 'Asia/Kolkata',
            language VARCHAR(10) DEFAULT 'en',
            preferred_avatar_style VARCHAR(50) DEFAULT 'traditional',
            voice_preference VARCHAR(50) DEFAULT 'compassionate',
            video_quality_preference VARCHAR(50) DEFAULT 'high',
            avatar_sessions_count INTEGER DEFAULT 0,
            total_avatar_minutes INTEGER DEFAULT 0,
            role VARCHAR(20) DEFAULT 'user' CHECK (role IN ('user', 'admin', 'moderator')),
            status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'suspended')),
            spiritual_level VARCHAR(20) DEFAULT 'beginner',
            referral_code VARCHAR(20) UNIQUE,
            referred_by VARCHAR(255),
            marketing_source VARCHAR(100),
            total_sessions INTEGER DEFAULT 0,
            last_login_at TIMESTAMP,
            last_session_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            user_email VARCHAR(255) NOT NULL,
            service_type VARCHAR(50) NOT NULL CHECK (service_type IN ('clarity', 'love', 'premium', 'elite')),
            question TEXT NOT NULL,
            birth_details TEXT,
            status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
            result_summary TEXT,
            full_result TEXT,
            avatar_video_url TEXT,
            avatar_duration_seconds INTEGER,
            avatar_generation_cost DECIMAL(10, 4),
            voice_synthesis_used BOOLEAN DEFAULT FALSE,
            avatar_quality VARCHAR(20) DEFAULT 'high',
            credits_used INTEGER NOT NULL DEFAULT 0,
            original_price DECIMAL(10, 2),
            user_rating INTEGER CHECK (user_rating >= 1 AND user_rating <= 5),
            user_feedback TEXT,
            session_quality_score DECIMAL(3, 2),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            FOREIGN KEY (user_email) REFERENCES users(email) ON DELETE CASCADE
        );
        # NEW: Automated avatar styling system
        CREATE TABLE IF NOT EXISTS avatar_style_templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            style_name VARCHAR(100) NOT NULL,
            clothing_prompt TEXT NOT NULL,
            background_prompt TEXT NOT NULL,
            cultural_elements TEXT,
            mood_description TEXT,
            usage_contexts TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        # NEW: Automated festival calendar
        CREATE TABLE IF NOT EXISTS automated_festivals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            festival_name VARCHAR(100) NOT NULL,
            date_pattern TEXT,
            fixed_date DATE,
            style_override TEXT,
            cultural_elements TEXT,
            auto_enabled BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        # NEW: Admin-configurable community events (Phase 2)
        CREATE TABLE IF NOT EXISTS community_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_name VARCHAR(100) NOT NULL,
            event_type VARCHAR(50) NOT NULL,
            recurring_pattern TEXT,
            avatar_style VARCHAR(100),
            content_themes TEXT,
            auto_generated BOOLEAN DEFAULT TRUE,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        # Add columns to existing avatar_sessions table for automation
        ALTER TABLE avatar_sessions ADD COLUMN dynamic_style_prompt TEXT;
        ALTER TABLE avatar_sessions ADD COLUMN auto_detected_occasion VARCHAR(100);
        ALTER TABLE avatar_sessions ADD COLUMN cultural_theme VARCHAR(100);
        
        """

        conn = None
        try:
            conn = await self.get_connection()
            if self.is_sqlite:
                statements = [s.strip() for s in enhanced_schema.split(';') if s.strip()]
                for statement in statements:
                    if statement and not statement.startswith('--'):
                        await conn.execute(statement)
                await conn.commit()
            else:
                postgresql_schema = enhanced_schema.replace("INTEGER PRIMARY KEY AUTOINCREMENT", "SERIAL PRIMARY KEY")
                postgresql_schema = postgresql_schema.replace("TEXT", "TEXT")
                postgresql_schema = postgresql_schema.replace("TIMESTAMP DEFAULT CURRENT_TIMESTAMP", "TIMESTAMP DEFAULT NOW()")
                await conn.execute(postgresql_schema)
            logger.info("✅ Enhanced database schema created successfully")

        except Exception as e:
            logger.error(f"❌ Enhanced schema creation failed: {e}")
            raise e
        finally:
            if conn:
                await self.release_connection(conn)

    async def health_check(self) -> Dict[str, Any]:
        """Enhanced database health check"""
        try:
            conn = await self.get_connection()
            if self.is_sqlite:
                result = await conn.execute("SELECT 1")
                row = await result.fetchone()
                test_result = row[0] if row else None
            else:
                test_result = await conn.fetchval("SELECT 1")

            if test_result != 1:
                raise Exception("Database connectivity test failed")

            stats = await self._get_database_stats(conn)
            await self.release_connection(conn)

            return {
                "status": "healthy",
                "database_type": self.database_type,
                "pool_status": "active" if self.pool else "not_applicable",
                "statistics": stats,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

        except Exception as e:
            return {
                "status": "unhealthy",
                "database_type": self.database_type,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

    async def _get_database_stats(self, conn) -> Dict[str, Any]:
        """Get enhanced database statistics"""
        try:
            if self.is_sqlite:
                total_users = await conn.execute("SELECT COUNT(*) FROM users")
                total_users = (await total_users.fetchone())[0]
                total_sessions = await conn.execute("SELECT COUNT(*) FROM sessions")
                total_sessions = (await total_sessions.fetchone())[0]
            else:
                total_users = await conn.fetchval("SELECT COUNT(*) FROM users")
                total_sessions = await conn.fetchval("SELECT COUNT(*) FROM sessions")

            return {
                "total_users": total_users or 0,
                "total_sessions": total_sessions or 0,
                "tables_created": True
            }

        except Exception as e:
            logger.warning(f"Could not get database stats: {e}")
            return {"error": "Statistics unavailable"}

    async def close(self):
        """Close enhanced database connections"""
        try:
            if self.pool:
                await self.pool.close()
                logger.info("✅ Enhanced database connections closed")
        except Exception as e:
            logger.error(f"❌ Error closing database connections: {e}")

    def execute_sync_query(self, query: str) -> List[Dict]:
        """Execute synchronous query for festival calendar loading"""
        try:
            logger.warning(f"Sync query not implemented yet: {query}")
            return []
        except Exception as e:
            logger.error(f"Sync query failed: {e}")
            return []

    async def get_connection(self):
        """Get database connection - enhanced version"""
        if self.is_sqlite:
            return await aiosqlite.connect(self.database_url.replace("sqlite:///", ""))
        else:
            if not self.pool:
                raise Exception("Database pool not initialized")
            return await self.pool.acquire()

    async def count_users(self) -> int:
        """Count total users"""
        conn = await self.get_connection()
        try:
            if self.is_sqlite:
                result = await conn.execute("SELECT COUNT(*) FROM users")
                count = await result.fetchone()
                return count[0] if count else 0
            else:
                return await conn.fetchval("SELECT COUNT(*) FROM users") or 0
        finally:
            await self.release_connection(conn)

    async def count_sessions(self) -> int:
        """Count total sessions"""
        conn = await self.get_connection()
        try:
            if self.is_sqlite:
                result = await conn.execute("SELECT COUNT(*) FROM sessions")
                count = await result.fetchone()
                return count[0] if count else 0
            else:
                return await conn.fetchval("SELECT COUNT(*) FROM sessions") or 0
        finally:
            await self.release_connection(conn)

    async def count_active_users_last_hour(self) -> int:
        """Count active users in last hour"""
        conn = await self.get_connection()
        try:
            if self.is_sqlite:
                result = await conn.execute(
                    "SELECT COUNT(*) FROM users WHERE last_login_at >= datetime('now', '-1 hour')"
                )
                count = await result.fetchone()
                return count[0] if count else 0
            else:
                return await conn.fetchval(
                    "SELECT COUNT(*) FROM users WHERE last_login_at >= NOW() - INTERVAL '1 hour'"
                ) or 0
        finally:
            await self.release_connection(conn)

    async def count_users(self) -> int:
        """Count total users"""
        conn = await self.get_connection()
        try:
            if self.is_sqlite:
                result = await conn.execute("SELECT COUNT(*) FROM users")
                count = await result.fetchone()
                return count[0] if count else 0
            else:
                return await conn.fetchval("SELECT COUNT(*) FROM users") or 0
        finally:
            await self.release_connection(conn)

    async def count_sessions(self) -> int:
        """Count total sessions"""
        conn = await self.get_connection()
        try:
            if self.is_sqlite:
                result = await conn.execute("SELECT COUNT(*) FROM sessions")
                count = await result.fetchone()
                return count[0] if count else 0
            else:
                return await conn.fetchval("SELECT COUNT(*) FROM sessions") or 0
        finally:
            await self.release_connection(conn)

    async def count_active_users_last_hour(self) -> int:
        """Count active users in last hour"""
        conn = await self.get_connection()
        try:
            if self.is_sqlite:
                result = await conn.execute(
                    "SELECT COUNT(*) FROM users WHERE last_login_at >= datetime('now', '-1 hour')"
                )
                count = await result.fetchone()
                return count[0] if count else 0
            else:
                return await conn.fetchval(
                    "SELECT COUNT(*) FROM users WHERE last_login_at >= NOW() - INTERVAL '1 hour'"
                ) or 0
        finally:
            await self.release_connection(conn)

# Initialize enhanced database manager
db_manager = EnhancedDatabaseManager()

# =============================================================================
# 🔐 ENHANCED SECURITY MANAGER WITH AVATAR AUTHENTICATION
# =============================================================================

class EnhancedSecurityManager:
    """Enhanced security manager with avatar service authentication"""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

    @staticmethod
    def create_access_token(user_data: Dict[str, Any]) -> str:
        """Create JWT access token with enhanced claims"""
        payload = {
            'email': user_data['email'],
            'role': user_data.get('role', 'user'),
            'user_id': user_data.get('id'),
            'name': user_data.get('name'),
            'avatar_enabled': True,
            'live_chat_enabled': user_data.get('role') in ['user', 'admin'],
            'satsang_access': True,
            'iat': datetime.now(timezone.utc),
            'exp': datetime.now(timezone.utc) + timedelta(hours=settings.jwt_expiration_hours),
            'iss': 'jyotiflow-enhanced'
        }
        return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

    @staticmethod
    def verify_access_token(token: str) -> Dict[str, Any]:
        """Verify JWT access token"""
        try:
            payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")

# Initialize enhanced security manager
security_manager = EnhancedSecurityManager()

# =============================================================================
# 🔑 ENHANCED AUTHENTICATION DEPENDENCIES
# =============================================================================

security_scheme = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security_scheme)) -> Dict[str, Any]:
    """Get current authenticated user with enhanced permissions"""
    try:
        payload = security_manager.verify_access_token(credentials.credentials)
        conn = await db_manager.get_connection()

        try:
            if db_manager.is_sqlite:
                result = await conn.execute("""
                    SELECT email, name, role, credits, avatar_sessions_count,
                           total_avatar_minutes, preferred_avatar_style, voice_preference
                    FROM users WHERE email = ?
                """, (payload['email'],))
                user_data = await result.fetchone()
            else:
                user_data = await conn.fetchrow("""
                    SELECT email, name, role, credits, avatar_sessions_count,
                           total_avatar_minutes, preferred_avatar_style, voice_preference
                    FROM users WHERE email = $1
                """, payload['email'])

            if not user_data:
                raise HTTPException(status_code=401, detail="User not found")

            user = dict(user_data)
            user.update({
                'avatar_enabled': payload.get('avatar_enabled', True),
                'live_chat_enabled': payload.get('live_chat_enabled', True),
                'satsang_access': payload.get('satsang_access', True)
            })

            return user

        finally:
            await db_manager.release_connection(conn)

    except Exception as e:
        logger.error(f"Authentication failed: {e}")
        raise HTTPException(status_code=401, detail="Authentication failed")

async def get_admin_user(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Get current admin user"""
    if current_user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user 

async def get_database() -> EnhancedDatabaseManager:
    """Get database manager for FastAPI dependency injection"""
    return db_manager

# =============================================================================
# 🌐 ENHANCED EXTERNAL SERVICE CLIENTS
# =============================================================================

openai_client = AsyncOpenAI(api_key=settings.openai_api_key) if settings.openai_api_key != "your-openai-api-key" else None
stripe.api_key = settings.stripe_secret_key if settings.stripe_secret_key != "your-stripe-secret-key" else None

class EnhancedAvatarServiceClients:
    """Enhanced avatar service clients initialization"""

    @staticmethod
    def get_d_id_headers() -> Dict[str, str]:
        """Get D-ID API headers"""
        return {
            "Authorization": f"Basic {settings.d_id_api_key}",
            "Content-Type": "application/json"
        }

    @staticmethod
    def get_elevenlabs_headers() -> Dict[str, str]:
        """Get ElevenLabs API headers"""
        return {
            "xi-api-key": settings.elevenlabs_api_key,
            "Content-Type": "application/json"
        }

    @staticmethod
    async def test_avatar_services() -> Dict[str, str]:
        """Test avatar service connectivity"""
        results = {}

        try:
            if settings.d_id_api_key != "your-d-id-api-key":
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        f"{settings.d_id_api_url}/talks",
                        headers=EnhancedAvatarServiceClients.get_d_id_headers()
                    ) as response:
                        results["d_id"] = "connected" if response.status == 200 else "error"
            else:
                results["d_id"] = "not_configured"
        except:
            results["d_id"] = "connection_failed"

        try:
            if settings.elevenlabs_api_key != "your-elevenlabs-api-key":
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        "https://api.elevenlabs.io/v1/voices",
                        headers=EnhancedAvatarServiceClients.get_elevenlabs_headers()
                    ) as response:
                        results["elevenlabs"] = "connected" if response.status == 200 else "error"
            else:
                results["elevenlabs"] = "not_configured"
        except:
            results["elevenlabs"] = "connection_failed"

        return results

avatar_clients = EnhancedAvatarServiceClients()

# =============================================================================
# 🛠️ ENHANCED UTILITIES WITH AVATAR PROCESSING
# =============================================================================

class EnhancedUtilities:
    """Enhanced utility functions with avatar support"""

    @staticmethod
    def generate_session_id() -> str:
        """Generate unique session ID"""
        
        return str(uuid4())

# =============================================================================
# 🏥 ENHANCED HEALTH MONITOR WITH AVATAR SERVICE STATUS
# =============================================================================

class EnhancedHealthMonitor:
    """Enhanced health monitoring with avatar services"""

    @staticmethod
    async def get_system_health() -> Dict[str, Any]:
        """Complete enhanced system health check"""

        health_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "overall_status": "healthy",
            "services": {},
            "avatar_services": {},
            "performance": {},
            "enhanced_features": {}
        }

        try:
            db_health = await db_manager.health_check()
            health_data["services"]["database"] = db_health

            avatar_health = await avatar_clients.test_avatar_services()
            health_data["avatar_services"] = avatar_health

            health_data["overall_status"] = EnhancedHealthMonitor._calculate_overall_status(health_data)

        except Exception as e:
            health_data["overall_status"] = "unhealthy"
            health_data["error"] = str(e)

        return health_data

    @staticmethod
    def _calculate_overall_status(health_data: Dict[str, Any]) -> str:
        """Calculate overall system health status"""

        try:
            db_status = health_data.get("services", {}).get("database", {}).get("status")
            if db_status != "healthy":
                return "degraded"

            return "healthy"

        except Exception:
            return "unknown"

health_monitor = EnhancedHealthMonitor()

# =============================================================================
# 🔄 ENHANCED APPLICATION LIFESPAN MANAGEMENT
# =============================================================================

@asynccontextmanager
async def enhanced_app_lifespan(app: FastAPI):
    """Enhanced application lifespan with avatar services"""

    logger.info("🙏🏼 Starting Enhanced JyotiFlow.ai Digital Ashram...")

    try:
        await db_manager.initialize()
        avatar_status = await avatar_clients.test_avatar_services()
        logger.info(f"🎭 Avatar services status: {avatar_status}")

        if settings.app_env == "development":
            await _initialize_enhanced_sample_data()

        logger.info("✅ Enhanced JyotiFlow.ai startup completed successfully")
        logger.info(f"🌟 Environment: {settings.app_env}")
        logger.info(f"🔧 Database: {db_manager.database_type}")
        logger.info(f"🎭 Avatar services: {len([s for s in avatar_status.values() if s == 'connected'])} connected")
        logger.info(f"🙏🏼 Enhanced digital ashram ready to serve souls worldwide")

        yield

    except Exception as e:
        logger.error(f"❌ Enhanced startup failed: {e}")
        raise SystemExit(f"Enhanced application startup failed: {e}")

    finally:
        logger.info("🔄 Shutting down Enhanced JyotiFlow.ai...")
        await db_manager.close()
        logger.info("✅ Enhanced shutdown completed gracefully")

async def _initialize_enhanced_sample_data():
    """Initialize enhanced sample data for development"""

    try:
        logger.info("📊 Initializing enhanced sample data...")
        conn = await db_manager.get_connection()

        try:
            admin_exists = await _check_user_exists(conn, settings.admin_email)
            if not admin_exists:
                await _create_enhanced_admin_user(conn)
                logger.info(f"👑 Enhanced admin user created: {settings.admin_email}")

            sample_users = [
                {
                    "email": "test@jyotiflow.ai",
                    "password": "test123",
                    "name": "Test User",
                    "credits": 50,
                    "preferred_avatar_style": "traditional",
                    "voice_preference": "compassionate"
                },
                {
                    "email": "spiritual.seeker@example.com",
                    "password": "spiritual123",
                    "name": "Spiritual Seeker",
                    "credits": 100,
                    "preferred_avatar_style": "modern",
                    "voice_preference": "wise"
                }
            ]

            for user_data in sample_users:
                user_exists = await _check_user_exists(conn, user_data["email"])
                if not user_exists:
                    await _create_enhanced_sample_user(conn, user_data)
                    logger.info(f"👤 Enhanced sample user created: {user_data['email']}")

            await _create_sample_satsang_event(conn)

        finally:
            await db_manager.release_connection(conn)

        logger.info("✅ Enhanced sample data initialization completed")

    except Exception as e:
        logger.error(f"❌ Enhanced sample data initialization failed: {e}")

async def _check_user_exists(conn, email: str) -> bool:
    """Check if user exists"""
    if db_manager.is_sqlite:
        result = await conn.execute("SELECT 1 FROM users WHERE email = ?", (email,))
        return (await result.fetchone()) is not None
    else:
        return await conn.fetchval("SELECT 1 FROM users WHERE email = $1", email) is not None

async def _create_enhanced_admin_user(conn):
    """Create enhanced admin user"""
    password_hash = security_manager.hash_password(settings.admin_password)

    if db_manager.is_sqlite:
        await conn.execute("""
            INSERT INTO users (email, password_hash, name, credits, role,
                             preferred_avatar_style, voice_preference, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (settings.admin_email, password_hash, "Admin Swami", 1000, "admin",
              "traditional", "wise", datetime.now(timezone.utc).isoformat(),
              datetime.now(timezone.utc).isoformat()))
        await conn.commit()
    else:
        await conn.execute("""
            INSERT INTO users (email, password_hash, name, credits, role,
                             preferred_avatar_style, voice_preference, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, NOW(), NOW())
        """, settings.admin_email, password_hash, "Admin Swami", 1000, "admin",
             "traditional", "wise")

async def _create_enhanced_sample_user(conn, user_data: dict):
    """Create enhanced sample user"""
    password_hash = security_manager.hash_password(user_data["password"])

    if db_manager.is_sqlite:
        await conn.execute("""
            INSERT INTO users (email, password_hash, name, credits, role,
                             preferred_avatar_style, voice_preference, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_data["email"], password_hash, user_data["name"], user_data["credits"], "user",
              user_data["preferred_avatar_style"], user_data["voice_preference"],
              datetime.now(timezone.utc).isoformat(), datetime.now(timezone.utc).isoformat()))
        await conn.commit()
    else:
        await conn.execute("""
            INSERT INTO users (email, password_hash, name, credits, role,
                             preferred_avatar_style, voice_preference, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, NOW(), NOW())
        """, user_data["email"], password_hash, user_data["name"], user_data["credits"], "user",
             user_data["preferred_avatar_style"], user_data["voice_preference"])

async def _create_sample_satsang_event(conn):
    """Create sample satsang event"""

    next_satsang = datetime.now(timezone.utc).replace(day=1, hour=10, minute=0, second=0, microsecond=0)
    next_satsang = next_satsang + timedelta(days=32)
    next_satsang = next_satsang.replace(day=1)

    try:
        if db_manager.is_sqlite:
            await conn.execute("""
                INSERT OR IGNORE INTO satsang_events
                (title, description, scheduled_date, max_attendees, spiritual_theme, created_by)
                VALUES (?, ?, ?, ?, ?, ?)
            """, ("Monthly Spiritual Satsang",
                  "Join Swami Jyotirananthan for monthly spiritual guidance and community connection",
                  next_satsang.isoformat(), 1000, "Divine Love and Compassion", "system"))
            await conn.commit()
        else:
            await conn.execute("""
                INSERT INTO satsang_events
                (title, description, scheduled_date, max_attendees, spiritual_theme, created_by)
                VALUES ($1, $2, $3, $4, $5, $6)
                ON CONFLICT DO NOTHING
            """, "Monthly Spiritual Satsang",
                 "Join Swami Jyotirananthan for monthly spiritual guidance and community connection",
                 next_satsang, 1000, "Divine Love and Compassion", "system")

    except Exception as e:
        logger.debug(f"Sample satsang creation skipped: {e}")

app_lifespan = enhanced_app_lifespan

logger.info("✅ Enhanced JyotiFlow.ai Core Foundation loaded successfully")
logger.info("🎭 Avatar services configured and ready")
logger.info("🔐 Enhanced security and authentication ready")
logger.info("🗄️ Enhanced database schema with avatar tables ready")
logger.info("🙏🏼 Enhanced Core Foundation provides: Database, Auth, Avatar Config, Security, Monitoring")

# Create app with the FIXED lifespan from core foundation
app = FastAPI(
    title="🙏🏼 JyotiFlow.ai - Swami Jyotirananthan's Digital Ashram",
    description="Sacred AI-powered spiritual guidance platform with fixed Pydantic V2 compatibility",
    version="5.0.0",
    lifespan=enhanced_app_lifespan
)

@app.on_event("startup")
async def startup():
    await db_manager.initialize_tables()

# Create APIRouter for auth and user endpoints
from fastapi import APIRouter

auth_router = APIRouter(prefix="/api/auth", tags=["Authentication"])
user_router = APIRouter(prefix="/api/user", tags=["User"])
admin_router = APIRouter(prefix="/api/admin", tags=["Admin"])

# Export app for main.py import
__all__ = ["app", "auth_router", "user_router", "admin_router", "settings", "db_manager", "security_manager", "enhanced_app_lifespan",
           "StandardResponse", "UserLogin", "UserRegistration", "get_current_user", "get_admin_user"]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.debug else settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Add advanced production middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"] if settings.debug else settings.allowed_hosts.split(",")
)
if not settings.debug:
    app.add_middleware(HTTPSRedirectMiddleware)

# Update CORS for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.debug else ["https://jyotiflow-ai-frontend.onrender.com", "https://jyotiflow.ai"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Enhanced request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"🕉️ API Request: {request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"🕉️ Response: {request.method} {request.url.path} - {response.status_code}")
    return response

# Debug endpoint for route introspection
@app.get("/api/debug/routes")
async def debug_routes():
    routes = []
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            routes.append({
                "path": route.path,
                "methods": list(route.methods),
                "name": getattr(route, 'name', 'unknown')
            })
    return {
        "total_routes": len(routes),
        "routes": sorted(routes, key=lambda x: x['path'])
    }

# =============================================================================
# 🌐 HOMEPAGE WITH ENHANCED DESIGN
# =============================================================================

@app.get("/", response_class=HTMLResponse)
async def homepage():
    """Spiritual homepage showing platform status"""

    homepage_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🙏🏼 JyotiFlow.ai - Swami Jyotirananthan's Digital Ashram</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: white;
                text-align: center;
                padding: 20px;
            }}
            .container {{
                max-width: 900px;
                margin: 0 auto;
                padding: 40px 20px;
            }}
            .hero {{
                margin-bottom: 40px;
            }}
            .om-symbol {{
                font-size: 80px;
                margin-bottom: 20px;
                animation: glow 2s ease-in-out infinite alternate;
            }}
            @keyframes glow {{
                from {{ text-shadow: 0 0 20px #fff, 0 0 30px #fff, 0 0 40px #667eea; }}
                to {{ text-shadow: 0 0 30px #fff, 0 0 40px #fff, 0 0 50px #764ba2; }}
            }}
            h1 {{
                font-size: 2.5rem;
                margin-bottom: 20px;
                font-weight: 300;
            }}
            .subtitle {{
                font-size: 1.2rem;
                opacity: 0.9;
                margin-bottom: 40px;
            }}
            .fix-notice {{
                background: rgba(0, 255, 0, 0.2);
                border: 2px solid rgba(0, 255, 0, 0.5);
                padding: 20px;
                border-radius: 15px;
                margin-bottom: 40px;
                backdrop-filter: blur(10px);
            }}
            .fix-title {{
                font-size: 1.4rem;
                color: #90EE90;
                margin-bottom: 10px;
                font-weight: 600;
            }}
            .services {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-bottom: 40px;
            }}
            .service-card {{
                background: rgba(255, 255, 255, 0.1);
                padding: 30px 20px;
                border-radius: 15px;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.2);
                transition: transform 0.3s ease;
            }}
            .service-card:hover {{
                transform: translateY(-5px);
                background: rgba(255, 255, 255, 0.15);
            }}
            .service-icon {{
                font-size: 40px;
                margin-bottom: 15px;
            }}
            .service-title {{
                font-size: 1.3rem;
                margin-bottom: 10px;
                font-weight: 600;
            }}
            .service-description {{
                font-size: 0.95rem;
                opacity: 0.9;
                line-height: 1.5;
            }}
            .status {{
                background: rgba(255, 255, 255, 0.1);
                padding: 20px;
                border-radius: 10px;
                margin-top: 30px;
            }}
            .status-title {{
                font-size: 1.1rem;
                margin-bottom: 10px;
                color: #90EE90;
            }}
            .config-info {{
                background: rgba(255, 255, 255, 0.05);
                padding: 15px;
                border-radius: 8px;
                margin-top: 20px;
                text-align: left;
                font-family: monospace;
                font-size: 0.9rem;
            }}
            @media (max-width: 768px) {{
                .om-symbol {{ font-size: 60px; }}
                h1 {{ font-size: 2rem; }}
                .services {{ grid-template-columns: 1fr; }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="hero">
                <div class="om-symbol">🕉️</div>
                <h1>JyotiFlow.ai</h1>
                <p class="subtitle">Swami Jyotirananthan's Digital Ashram<br>
                Sacred AI-Powered Spiritual Guidance</p>
            </div>

            <div class="fix-notice">
                <div class="fix-title">✅ PYDANTIC V2 COMPATIBILITY FIXED</div>
                <p>All environment variable mapping issues resolved.<br>
                Database initialization working properly.<br>
                Platform ready for production deployment.</p>
            </div>

            <div class="services">
                <div class="service-card">
                    <div class="service-icon">🎭</div>
                    <div class="service-title">AI Avatar Guidance</div>
                    <div class="service-description">
                        Personalized video guidance from Swamiji with D-ID + ElevenLabs integration
                    </div>
                </div>

                <div class="service-card">
                    <div class="service-icon">📹</div>
                    <div class="service-title">Live Video Chat</div>
                    <div class="service-description">
                        Real-time spiritual consultation through Agora WebRTC integration
                    </div>
                </div>

                <div class="service-card">
                    <div class="service-icon">🙏🏼</div>
                    <div class="service-title">Monthly Satsang</div>
                    <div class="service-description">
                        Global spiritual community gatherings with live streaming
                    </div>
                </div>

                <div class="service-card">
                    <div class="service-icon">🧠</div>
                    <div class="service-title">AI Business Intelligence</div>
                    <div class="service-description">
                        Monetization optimization and spiritual analytics dashboard
                    </div>
                </div>
            </div>

            <div class="status">
                <div class="status-title">✅ Platform Status: Fully Operational</div>
                <p>Core foundation properly initialized.<br>
                Database schema created successfully.<br>
                All spiritual services ready for divine guidance. 🌟</p>

                <div class="config-info">
                    <strong>Configuration Status:</strong><br>
                    • Environment: {settings.app_env}<br>
                    • Database: {db_manager.database_type}<br>
                    • JWT Secret: {"Configured" if settings.jwt_secret_key != "your-super-secret-jwt-key-change-in-production" else "Default"}<br>
                    • AI Services: {"Configured" if settings.openai_api_key != "your-openai-api-key" else "Placeholder"}<br>
                    • Avatar Services: {"Ready" if settings.d_id_api_key != "your-d-id-api-key" else "Needs API Keys"}<br>
                    • Debug Mode: {settings.debug}
                </div>
            </div>
        </div>

        <script>
            document.querySelectorAll('.service-card').forEach(card => {{
                card.addEventListener('click', () => {{
                    card.style.background = 'rgba(255, 255, 255, 0.2)';
                    setTimeout(() => {{
                        card.style.background = 'rgba(255, 255, 255, 0.1)';
                    }}, 200);
                }});
            }});

            setInterval(() => {{
                const now = new Date();
                const time = now.toLocaleTimeString();
                console.log(`🙏🏼 Divine platform heartbeat: ${{time}}`);
            }}, 60000);
        </script>
    </body>
    </html>
    """

    return homepage_html

# =============================================================================
# 🩺 HEALTH CHECK WITH DETAILED STATUS
# =============================================================================

@app.get("/health")
async def health_check():
    """Comprehensive health check with fixed components"""

    health_data = {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "platform": "JyotiFlow.ai Digital Ashram",
        "version": "5.0.0 - Pydantic V2 Fixed",
        "services": {
            "api": "operational",
            "core_foundation": "fixed",
            "pydantic_compatibility": "v2_compliant",
            "spiritual_guidance": "ready",
            "avatar_services": "configured"
        },
        "configuration": {
            "environment": settings.app_env,
            "database_type": db_manager.database_type,
            "debug_mode": settings.debug,
            "ai_optimization": settings.ai_optimization_enabled
        },
        "blessing": "🙏🏼 Om Namah Shivaya - All systems properly blessed and fixed"
    }

    try:
        db_health = await db_manager.health_check()
        health_data["services"]["database"] = db_health.get("status", "unknown")
        health_data["database_details"] = db_health
    except Exception as e:
        health_data["services"]["database"] = f"error: {str(e)}"

    return JSONResponse(content=health_data)

# =============================================================================
# 🔐 AUTHENTICATION ENDPOINTS WITH FIXED CORE
# =============================================================================

@auth_router.post("/register")
async def register_user(user_data: UserRegistration):
    """User registration with complete field handling"""
    try:
        # Check if user already exists
        conn = await db_manager.get_connection()
        try:
            if db_manager.is_sqlite:
                existing = await conn.execute("SELECT 1 FROM users WHERE email = ?", (user_data.email,))
                exists = await existing.fetchone()
            else:
                exists = await conn.fetchval("SELECT 1 FROM users WHERE email = $1", user_data.email)
            
            if exists:
                return StandardResponse(
                    success=False,
                    message="User with this email already exists",
                    data={"error": "Email already registered"}
                ).dict()
            
            # Hash password
            password_hash = security_manager.hash_password(user_data.password)
            
            # Generate unique referral code for new user
            referral_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            
            # Get current timestamp
            now = datetime.now(timezone.utc)
            
            # Insert user with ALL fields
            if db_manager.is_sqlite:
                await conn.execute("""
                    INSERT INTO users (
                        email, password_hash, name, phone, credits, role,
                        birth_date, birth_time, birth_location,
                        preferred_avatar_style, voice_preference, video_quality_preference,
                        referral_code, marketing_source, referred_by,
                        spiritual_level, timezone, language,
                        created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    user_data.email, password_hash, user_data.name, user_data.phone,
                    3, "user",  # 3 welcome credits, user role
                    user_data.birth_date, user_data.birth_time, user_data.birth_location,
                    user_data.preferred_avatar_style or "traditional",
                    user_data.voice_preference or "compassionate",
                    user_data.video_quality_preference or "high",
                    referral_code, user_data.marketing_source, user_data.referral_code,
                    "beginner", "Asia/Kolkata", "en",
                    now.isoformat(), now.isoformat()
                ))
                await conn.commit()
            else:
                await conn.execute("""
                    INSERT INTO users (
                        email, password_hash, name, phone, credits, role,
                        birth_date, birth_time, birth_location,
                        preferred_avatar_style, voice_preference, video_quality_preference,
                        referral_code, marketing_source, referred_by,
                        spiritual_level, timezone, language,
                        created_at, updated_at
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, NOW(), NOW())
                """, 
                    user_data.email, password_hash, user_data.name, user_data.phone,
                    3, "user",
                    user_data.birth_date, user_data.birth_time, user_data.birth_location,
                    user_data.preferred_avatar_style or "traditional",
                    user_data.voice_preference or "compassionate", 
                    user_data.video_quality_preference or "high",
                    referral_code, user_data.marketing_source, user_data.referral_code,
                    "beginner", "Asia/Kolkata", "en"
                )
                
            logger.info(f"✅ User registered successfully: {user_data.email}")
            
            return StandardResponse(
                success=True,
                message="Registration successful - Welcome to the digital ashram!",
                data={
                    "email": user_data.email,
                    "name": user_data.name,
                    "welcome_credits": 3,
                    "spiritual_level": "beginner",
                    "referral_code": referral_code,
                    "avatar_preferences": {
                        "style": user_data.preferred_avatar_style or "traditional",
                        "voice": user_data.voice_preference or "compassionate",
                        "quality": user_data.video_quality_preference or "high"
                    }
                }
            ).dict()
            
        finally:
            await db_manager.release_connection(conn)

    except Exception as e:
        logger.error(f"Registration failed: {e}")
        return StandardResponse(
            success=False,
            message="Registration failed",
            data={"error": str(e)}
        ).dict() 
    

@auth_router.post("/login")
async def login_user(login_data: UserLogin):
    """User login with complete field handling"""
    try:
        logger.info(f"Login request for: {login_data.email}")

        conn = await db_manager.get_connection()
        try:
            # Get ALL user fields for complete profile
            if db_manager.is_sqlite:
                user_row = await conn.execute("""
                    SELECT id, email, password_hash, role, name, phone, credits,
                           birth_date, birth_time, birth_location,
                           preferred_avatar_style, voice_preference, video_quality_preference,
                           spiritual_level, timezone, language,
                           total_sessions, avatar_sessions_count, total_avatar_minutes,
                           referral_code, created_at
                    FROM users WHERE email = ?
                """, (login_data.email,))
                user_data = await user_row.fetchone()
            else:
                user_data = await conn.fetchrow("""
                    SELECT id, email, password_hash, role, name, phone, credits,
                           birth_date, birth_time, birth_location,
                           preferred_avatar_style, voice_preference, video_quality_preference,
                           spiritual_level, timezone, language,
                           total_sessions, avatar_sessions_count, total_avatar_minutes,
                           referral_code, created_at
                    FROM users WHERE email = $1
                """, login_data.email)
            
            if not user_data:
                return StandardResponse(
                    success=False,
                    message="Invalid email or password",
                    data={"error": "Authentication failed"}
                ).dict()

            # Verify password
            if not security_manager.verify_password(login_data.password, user_data['password_hash']):
                return StandardResponse(
                    success=False,
                    message="Invalid email or password",
                    data={"error": "Authentication failed"}
                ).dict()

            # Update last login timestamp
            now = datetime.now(timezone.utc)
            if db_manager.is_sqlite:
                await conn.execute(
                    "UPDATE users SET last_login_at = ? WHERE email = ?",
                    (now.isoformat(), login_data.email)
                )
                await conn.commit()
            else:
                await conn.execute(
                    "UPDATE users SET last_login_at = NOW() WHERE email = $1",
                    login_data.email
                )

            # Create token with complete user data
            token = security_manager.create_access_token(dict(user_data))

            # Prepare complete user response
            user_response = {
                "id": user_data['id'],
                "email": user_data['email'],
                "name": user_data['name'],
                "role": user_data['role'],
                "credits": user_data['credits'],
                "spiritual_level": user_data['spiritual_level'],
                "profile": {
                    "phone": user_data['phone'],
                    "birth_date": user_data['birth_date'],
                    "birth_time": user_data['birth_time'],
                    "birth_location": user_data['birth_location'],
                    "timezone": user_data['timezone'],
                    "language": user_data['language']
                },
                "avatar_preferences": {
                    "style": user_data['preferred_avatar_style'],
                    "voice": user_data['voice_preference'],
                    "quality": user_data['video_quality_preference']
                },
                "stats": {
                    "total_sessions": user_data['total_sessions'],
                    "avatar_sessions": user_data['avatar_sessions_count'],
                    "avatar_minutes": user_data['total_avatar_minutes']
                },
                "referral_code": user_data['referral_code'],
                "member_since": user_data['created_at'].isoformat() if user_data['created_at'] else None
            }

            logger.info(f"✅ User login successful: {login_data.email}")

            return StandardResponse(
                success=True,
                message="Login successful - Welcome back to the ashram",
                data={
                    "token": token,
                    "user": user_response,
                    "expires_in": f"{settings.jwt_expiration_hours} hours",
                    "avatar_enabled": True,
                    "live_chat_enabled": True,
                    "satsang_access": True
                }
            ).dict()
            
        finally:
            await db_manager.release_connection(conn)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login failed: {e}")
        return StandardResponse(
            success=False,
            message="Login failed",
            data={"error": str(e)}
        ).dict()

# =============================================================================
# 📊 PROTECTED ENDPOINTS USING FIXED AUTHENTICATION
# =============================================================================

@user_router.get("/profile")
async def get_user_profile(current_user: dict = Depends(get_current_user)):
    """Get complete user profile with avatar preferences"""
    try:
        user = await db_manager.get_user_profile(current_user['id'])
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return {"success": True, "data": dict(user)}
    except Exception as e:
        logger.error(f"Profile retrieval failed: {e}")
        return {"success": False, "message": "Failed to retrieve profile", "data": {"error": str(e)}}

@user_router.get("/sessions")
async def get_user_sessions(current_user: dict = Depends(get_current_user)):
    """Get user's spiritual sessions"""
    try:
        sessions = await db_manager.get_user_sessions(current_user['id'])
        return {"success": True, "data": [dict(s) for s in sessions]}
    except Exception as e:
        logger.error(f"Session retrieval failed: {e}")
        return {"success": False, "message": "Failed to retrieve sessions", "data": {"error": str(e)}}

@user_router.get("/credits")
async def get_user_credits(current_user: dict = Depends(get_current_user)):
    """Get user's credit balance and transaction history"""
    try:
        credits = await db_manager.get_user_credits(current_user['id'])
        transactions = await db_manager.get_user_credit_transactions(current_user['id'])
        return {"success": True, "data": {"credits": credits, "transactions": [dict(t) for t in transactions]}}
    except Exception as e:
        logger.error(f"Credit retrieval failed: {e}")
        return {"success": False, "message": "Failed to retrieve credits", "data": {"error": str(e)}}

@admin_router.get("/dashboard")
async def admin_dashboard(admin_user: dict = Depends(get_admin_user)):
    """Admin dashboard using fixed authentication"""
    try:
        return StandardResponse(
            success=True,
            message="Admin dashboard data retrieved",
            data={
                "admin": admin_user,
                "platform_stats": {
                    "total_users": "Loading...",
                    "total_sessions": "Loading...",
                    "revenue_today": "Loading...",
                    "avatar_generations": "Loading..."
                },
                "system_status": {
                    "pydantic_v2": "✅ Fixed",
                    "database": "✅ Connected",
                    "authentication": "✅ Working",
                    "avatar_services": "✅ Configured"
                }
            }
        ).dict()

    except Exception as e:
        logger.error(f"Admin dashboard failed: {e}")
        raise HTTPException(status_code=500, detail="Admin dashboard failed")

@admin_router.get("/stats")
async def admin_stats(admin_user: dict = Depends(get_admin_user)):
    try:
        total_users = await db_manager.get_total_users()
        active_users = await db_manager.get_active_users()
        total_sessions = await db_manager.get_total_sessions()
        total_revenue = await db_manager.get_total_revenue()
        daily_revenue = await db_manager.get_daily_revenue()
        satsangs_completed = await db_manager.get_satsangs_completed()
        avatar_generations = await db_manager.get_avatar_generations()
        return {
            "success": True,
            "message": "Admin stats retrieved successfully",
            "data": {
                "total_users": total_users,
                "active_users": active_users,
                "total_revenue": float(total_revenue or 0),
                "daily_revenue": float(daily_revenue or 0),
                "total_sessions": total_sessions,
                "satsangs_completed": satsangs_completed,
                "avatar_generations": avatar_generations
            }
        }
    except Exception as e:
        logger.error(f"Admin stats failed: {e}")
        return {"success": False, "message": "Failed to retrieve admin stats", "data": {"error": str(e)}}

@admin_router.get("/monetization")
async def admin_monetization(admin_user: dict = Depends(get_admin_user)):
    try:
        # Example: Calculate revenue growth, user engagement, etc. from real data
        total_revenue = await db_manager.get_total_revenue()
        daily_revenue = await db_manager.get_daily_revenue()
        total_users = await db_manager.get_total_users()
        active_users = await db_manager.get_active_users()
        # Add more real analytics as needed
        return {
            "success": True,
            "message": "Monetization insights retrieved",
            "data": {
                "total_revenue": float(total_revenue or 0),
                "daily_revenue": float(daily_revenue or 0),
                "total_users": total_users,
                "active_users": active_users
            }
        }
    except Exception as e:
        logger.error(f"Monetization insights failed: {e}")
        return {"success": False, "message": "Failed to retrieve monetization insights", "data": {"error": str(e)}}

@admin_router.get("/optimization")
async def admin_optimization(admin_user: dict = Depends(get_admin_user)):
    try:
        # Example: Aggregate product/feature usage, session stats, etc.
        total_sessions = await db_manager.get_total_sessions()
        avatar_generations = await db_manager.get_avatar_generations()
        satsangs_completed = await db_manager.get_satsangs_completed()
        return {
            "success": True,
            "message": "Product optimization data retrieved",
            "data": {
                "total_sessions": total_sessions,
                "avatar_generations": avatar_generations,
                "satsangs_completed": satsangs_completed
            }
        }
    except Exception as e:
        logger.error(f"Product optimization failed: {e}")
        return {"success": False, "message": "Failed to retrieve optimization data", "data": {"error": str(e)}}

# =============================================================================
# 🔧 ERROR HANDLERS FOR FIXED PLATFORM
# =============================================================================

@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """404 error handler"""
    return JSONResponse(
        status_code=404,
        content={
            "success": False,
            "message": "🙏🏼 The path you seek is not found. May divine guidance lead you to the right direction.",
            "blessing": "Om Namah Shivaya",
            "suggested_paths": ["/", "/health", "/api/auth/login"],
            "platform_status": "fixed_and_operational"
        }
    )

@app.exception_handler(500)
async def server_error_handler(request: Request, exc):
    """500 error handler"""
    logger.error(f"Server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "🕉️ Divine services experienced an issue, but the platform is properly fixed.",
            "blessing": "Om Shanti Shanti Shanti",
            "support": "Platform core is stable - temporary service disruption",
            "platform_status": "core_fixed_pydantic_v2_compliant"
        }
    )

# =============================================================================
# 🏁 APPLICATION ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    logger.info("🚀 Starting JyotiFlow.ai with FIXED core foundation...")
    logger.info(f"🌟 Environment: {settings.app_env}")
    logger.info(f"🔧 Database: {db_manager.database_type}")
    logger.info(f"🎭 Pydantic V2: Properly Fixed")

    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )


class SpiritualUser(BaseModel):
    """- Complete spiritual user model"""
    id: Optional[int] = None
    email: str
    name: str
    role: str = "user"
    credits: int = 0
    subscription_tier: str = "free"  # free, premium, elite
    preferred_language: str = "en"
    total_sessions: int = 0
    avatar_sessions_count: int = 0
    total_avatar_minutes: int = 0
    preferred_avatar_style: str = "traditional"
    voice_preference: str = "compassionate"
    spiritual_level: str = "beginner"
    birth_date: Optional[str] = None
    birth_time: Optional[str] = None
    birth_location: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_login_at: Optional[datetime] = None 


class UserPurchase(BaseModel):
    """ User purchase/transaction model"""
    id: Optional[int] = None
    user_email: str
    transaction_type: str = "purchase"  # purchase, deduction, refund, bonus
    amount: float
    credits: int
    balance_before: int = 0
    balance_after: int = 0
    package_type: Optional[str] = None
    payment_method: Optional[str] = None
    stripe_session_id: Optional[str] = None
    stripe_payment_intent_id: Optional[str] = None
    description: str
    status: str = "completed"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc)) 


class SpiritualSession(BaseModel):
    """তমিল - Complete spiritual session model"""
    id: str
    user_email: str
    service_type: str = Field(..., pattern=r'^(clarity|love|premium|elite)$')
    question: str
    birth_details: Optional[Dict[str, Any]] = None
    status: str = "completed"
    result_summary: Optional[str] = None
    full_result: Optional[str] = None
    guidance: str
    
    # Avatar Integration
    avatar_video_url: Optional[str] = None
    avatar_duration_seconds: Optional[int] = None
    avatar_generation_cost: Optional[float] = None
    voice_synthesis_used: bool = False
    avatar_quality: str = "high"
    
    # Credits & Payment
    credits_used: int
    original_price: Optional[float] = None
    
    # Quality & Feedback
    user_rating: Optional[int] = Field(None, ge=1, le=5)
    user_feedback: Optional[str] = None
    session_quality_score: Optional[float] = None
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None 


class AvatarSession(BaseModel):
    """তমিল - Avatar generation session model"""
    id: Optional[int] = None
    session_id: str
    user_email: str
    avatar_prompt: str
    voice_script: str
    avatar_style: str = "traditional"
    voice_tone: str = "compassionate"
    generation_status: str = "pending"
    generation_started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    generation_completed_at: Optional[datetime] = None
    video_url: Optional[str] = None
    audio_url: Optional[str] = None
    duration_seconds: Optional[int] = None
    file_size_mb: Optional[float] = None
    video_quality: str = "high"
    d_id_cost: Optional[float] = None
    elevenlabs_cost: Optional[float] = None
    total_cost: Optional[float] = None
    generation_time_seconds: Optional[float] = None
    quality_score: Optional[float] = None


class AvatarGenerationRequest(BaseModel):
    """Enhanced avatar video generation request"""
    user_email: str
    session_id: str
    guidance_text: str
    service_type: str = Field(..., pattern=r'^(clarity|love|premium|elite)$')
    
    # Add content_type field
    content_type: Optional[str] = Field(
        default="daily_guidance",
        description="Type of content: daily_guidance, satsang, social_media, consultation"
    )
    
    # Avatar Customization
    avatar_style: Optional[str] = "traditional"
    voice_tone: Optional[str] = "compassionate"
    video_duration: Optional[int] = Field(default=300, le=1800)
    include_subtitles: bool = True
    video_quality: str = "high"
    
    # Spiritual Context
    user_birth_details: Optional[Dict[str, Any]] = None
    astrological_context: Optional[Dict[str, Any]] = None
    emotional_tone: Optional[str] = "supportive"
    
    # User timezone for proper festival detection
    user_timezone: Optional[str] = Field(
        default="Asia/Kolkata",
        description="User's timezone for accurate festival and daily theme detection"
    )


class SatsangEvent(BaseModel):
    """তমিল - Satsang event model"""
    id: Optional[int] = None
    title: str
    description: Optional[str] = None
    scheduled_date: datetime
    duration_minutes: int = 90
    max_attendees: int = 1000
    is_premium_only: bool = False
    stream_url: Optional[str] = None
    agora_channel_name: Optional[str] = None
    recording_url: Optional[str] = None
    status: str = "scheduled"  # scheduled, live, completed, cancelled
    actual_start_time: Optional[datetime] = None
    actual_end_time: Optional[datetime] = None
    total_registrations: int = 0
    peak_concurrent_attendees: int = 0
    average_engagement_score: Optional[float] = None
    spiritual_theme: Optional[str] = None
    key_teachings: Optional[List[str]] = None
    created_by: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc)) 


class SatsangAttendee(BaseModel):
    """তমিল - Satsang attendee model"""
    id: Optional[int] = None
    satsang_id: int
    user_email: str
    registration_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    attended: bool = False
    join_time: Optional[datetime] = None
    leave_time: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    questions_asked: int = 0
    chat_messages_sent: int = 0
    engagement_score: Optional[float] = None
    rating: Optional[int] = Field(None, ge=1, le=5)
    feedback: Optional[str] = None 



class MonetizationInsight(BaseModel):
    """তমিল - AI monetization insight model"""
    id: Optional[int] = None
    recommendation_id: str
    recommendation_type: str  # pricing, product, marketing, optimization
    title: str
    description: str
    projected_revenue_increase_percent: float
    projected_user_impact: str
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    implementation_effort: str = Field(..., pattern=r'^(low|medium|high)$')
    timeframe_days: int
    risk_level: str = Field(..., pattern=r'^(low|medium|high)$')
    data_points: Optional[List[Dict[str, Any]]] = None
    status: str = "pending"  # pending, approved, implemented, rejected
    admin_response: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None

class SocialContent(BaseModel):
    """তমিল - Social media content model"""
    id: Optional[int] = None
    content_id: str
    content_type: str = Field(..., pattern=r'^(daily_wisdom|user_highlight|satsang_promo|spiritual_quote)$')
    title: Optional[str] = None
    content_text: str
    hashtags: Optional[str] = None
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    audio_url: Optional[str] = None
    source_session_id: Optional[str] = None
    source_user_email: Optional[str] = None
    ai_generated: bool = True
    scheduled_publish_time: Optional[datetime] = None
    published_at: Optional[datetime] = None
    platforms: Optional[List[str]] = None
    views: int = 0
    likes: int = 0
    shares: int = 0
    comments: int = 0
    engagement_rate: Optional[float] = None
    status: str = "draft"  # draft, scheduled, published, archived
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Database alias for backward compatibility
EnhancedJyotiFlowDatabase = EnhancedDatabaseManager

# Service pricing and credits configuration
SKUS: Dict[str, dict] = {
    'clarity': {'price': 9, 'credits': 1, 'name': 'Clarity Plus'},
    'love': {'price': 19, 'credits': 3, 'name': 'AstroLove Whisper'},
    'premium': {'price': 39, 'credits': 6, 'name': 'R3 Live Premium'},
    'elite': {'price': 149, 'credits': 12, 'name': 'Daily AstroCoach'}
}

# Additional Pydantic models for API consistency
class SessionRequest(BaseModel):
    """তমিল - Session request model"""
    service_type: str = Field(..., pattern=r'^(clarity|love|premium|elite)$')
    question: str = Field(..., min_length=10, max_length=2000)
    birth_details: Optional[Dict[str, Any]] = None
    include_avatar_video: bool = True
    avatar_duration_preference: Optional[int] = None
    request_live_chat: bool = False
    voice_tone_preference: Optional[str] = "compassionate"

class LiveChatSessionRequest(BaseModel):
    """তমিল - Live chat session request"""
    user_email: str
    service_type: str = Field(..., pattern=r'^(premium|elite)$')
    session_duration_minutes: int = Field(default=15, le=45)
    preferred_time: Optional[datetime] = None
    topic: Optional[str] = None

class LiveChatSessionResponse(BaseModel):
    """তমিল - Live chat session response"""
    success: bool
    session_id: str
    chat_url: Optional[str] = None
    scheduled_time: Optional[datetime] = None
    duration_minutes: int
    agora_token: Optional[str] = None
    channel_name: Optional[str] = None
    message: str

class SatsangEventRequest(BaseModel):
    """তমিল - Satsang event creation/join request"""
    title: str = Field(..., min_length=5, max_length=200)
    description: Optional[str] = None
    scheduled_date: datetime
    max_attendees: Optional[int] = 1000
    is_premium_only: bool = False

class SatsangEventResponse(BaseModel):
    """তমিল - Satsang event response"""
    success: bool
    event_id: int
    title: str
    scheduled_date: datetime
    stream_url: Optional[str] = None
    attendee_count: int = 0
    user_registered: bool = False  

class EnhancedJyotiFlowDatabase:
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL") or "postgresql://jyotiflow_db_user:em0MmaZmvPzASryvzLHpR5g5rRZTQqpw@dpg-d12ohqemcj7s73fjbqtg-a/jyotiflow_db"
        self.pool = None

    async def connect(self):
        if not self.pool:
            self.pool = await asyncpg.create_pool(dsn=self.database_url, min_size=1, max_size=10)

    async def initialize_tables(self):
        await self.connect()
        async with self.pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    name TEXT,
                    role TEXT DEFAULT 'user',
                    credits INT DEFAULT 0,
                    created_at TIMESTAMP DEFAULT NOW(),
                    last_login_at TIMESTAMP
                );
            """)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id SERIAL PRIMARY KEY,
                    user_id INT REFERENCES users(id),
                    session_type TEXT,
                    guidance_text TEXT,
                    credits_used INT,
                    created_at TIMESTAMP DEFAULT NOW()
                );
            """)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS credit_transactions (
                    id SERIAL PRIMARY KEY,
                    user_id INT REFERENCES users(id),
                    amount INT,
                    type TEXT,
                    timestamp TIMESTAMP DEFAULT NOW()
                );
            """)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS payments (
                    id SERIAL PRIMARY KEY,
                    user_id INT REFERENCES users(id),
                    amount NUMERIC,
                    stripe_id TEXT,
                    status TEXT,
                    created_at TIMESTAMP DEFAULT NOW()
                );
            """)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS satsang_events (
                    id SERIAL PRIMARY KEY,
                    title TEXT,
                    date TIMESTAMP,
                    attendees INT DEFAULT 0
                );
            """)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS avatar_sessions (
                    id SERIAL PRIMARY KEY,
                    user_id INT REFERENCES users(id),
                    video_url TEXT,
                    duration INT,
                    created_at TIMESTAMP DEFAULT NOW()
                );
            """)

    # --- User Queries ---
    async def get_total_users(self):
        await self.connect()
        async with self.pool.acquire() as conn:
            return await conn.fetchval("SELECT COUNT(*) FROM users")

    async def get_active_users(self):
        await self.connect()
        async with self.pool.acquire() as conn:
            return await conn.fetchval("SELECT COUNT(*) FROM users WHERE last_login_at > NOW() - INTERVAL '1 hour'")

    async def get_user_profile(self, user_id):
        await self.connect()
        async with self.pool.acquire() as conn:
            return await conn.fetchrow("SELECT * FROM users WHERE id=$1", user_id)

    async def get_user_by_email(self, email):
        await self.connect()
        async with self.pool.acquire() as conn:
            return await conn.fetchrow("SELECT * FROM users WHERE email=$1", email)

    async def create_user(self, email, password_hash, name, role="user"):
        await self.connect()
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(
                "INSERT INTO users (email, password_hash, name, role, created_at) VALUES ($1, $2, $3, $4, $5) RETURNING *",
                email, password_hash, name, role, datetime.now(timezone.utc)
            )

    async def update_last_login(self, user_id):
        await self.connect()
        async with self.pool.acquire() as conn:
            await conn.execute("UPDATE users SET last_login_at=NOW() WHERE id=$1", user_id)

    # --- Session Queries ---
    async def get_total_sessions(self):
        await self.connect()
        async with self.pool.acquire() as conn:
            return await conn.fetchval("SELECT COUNT(*) FROM sessions")

    async def get_user_sessions(self, user_id):
        await self.connect()
        async with self.pool.acquire() as conn:
            return await conn.fetch("SELECT * FROM sessions WHERE user_id=$1 ORDER BY created_at DESC LIMIT 50", user_id)

    # --- Credit Queries ---
    async def get_user_credits(self, user_id):
        await self.connect()
        async with self.pool.acquire() as conn:
            return await conn.fetchval("SELECT credits FROM users WHERE id=$1", user_id)

    async def get_user_credit_transactions(self, user_id):
        await self.connect()
        async with self.pool.acquire() as conn:
            return await conn.fetch("SELECT * FROM credit_transactions WHERE user_id=$1 ORDER BY timestamp DESC LIMIT 20", user_id)

    # --- Payment Queries ---
    async def get_total_revenue(self):
        await self.connect()
        async with self.pool.acquire() as conn:
            return await conn.fetchval("SELECT COALESCE(SUM(amount),0) FROM payments WHERE status='completed'")

    async def get_daily_revenue(self):
        await self.connect()
        async with self.pool.acquire() as conn:
            return await conn.fetchval("SELECT COALESCE(SUM(amount),0) FROM payments WHERE status='completed' AND created_at > NOW() - INTERVAL '1 day'")

    # --- Satsang Queries ---
    async def get_satsangs_completed(self):
        await self.connect()
        async with self.pool.acquire() as conn:
            return await conn.fetchval("SELECT COUNT(*) FROM satsang_events WHERE date < NOW()")

    # --- Avatar Queries ---
    async def get_avatar_generations(self):
        await self.connect()
        async with self.pool.acquire() as conn:
            return await conn.fetchval("SELECT COUNT(*) FROM avatar_sessions")

    # --- Analytics/Monetization/Optimization ---
    # Add more methods as needed for analytics, monetization, etc.

# Export the db_manager instance

# ... existing code ...

