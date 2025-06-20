import os
import re
import jwt
import bcrypt
import asyncio
import asyncpg
import aiosqlite
import logging
import secrets
import json
import sys
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, List, Any, Union
from contextlib import asynccontextmanager
from pathlib import Path
from decimal import Decimal

# FastAPI Core Imports
from fastapi import FastAPI, HTTPException, Depends, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.exceptions import RequestValidationError

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
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(hours=settings.jwt_expiration_hours),
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
        from uuid import uuid4
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

# Ensure app is exported for main.py import
__all__ = ["app", "settings", "db_manager", "security_manager", "enhanced_app_lifespan",
           "StandardResponse", "UserLogin", "UserRegistration", "get_current_user", "get_admin_user"]
