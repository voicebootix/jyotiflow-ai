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
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

# Pydantic Models for Validation
from pydantic import BaseModel, EmailStr, Field, validator, root_validator
from pydantic_settings import BaseSettings

# External Integrations
import stripe
from openai import AsyncOpenAI
import aiohttp

# তমিল - Enhanced Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('jyotiflow_enhanced.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# =============================================================================
# 🔧 ENHANCED ENVIRONMENT CONFIGURATION & VALIDATION
# 
# =============================================================================

class EnhancedSettings(BaseSettings):
    """Enhanced environment settings with AI avatar services"""
   
    # Existing Core Settings (Preserved)
    app_name: str = "JyotiFlow.ai Enhanced"
    app_env: str = "development"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000
   
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
    openai_api_key: str = "your-openai-api-key"  # Will auto-map to OPENAI_API_KEY
    stripe_secret_key: str = "your-stripe-secret-key"  # Will auto-map to STRIPE_SECRET_KEY
    stripe_public_key: str = "your-stripe-public-key"  # Will auto-map to STRIPE_PUBLIC_KEY
    stripe_webhook_secret: str = "your-stripe-webhook-secret"  # Will auto-map to STRIPE_WEBHOOK_SECRET
    prokerala_api_key: str = "your-prokerala-api-key"  # Will auto-map to PROKERALA_API_KEY
    salescloser_api_key: str = "your-salescloser-api-key"  # Will auto-map to SALESCLOSER_API_KEY
    salescloser_webhook_url: str = "your-salescloser-webhook-url"
   
    # NEW: AI Avatar Service Configuration
    d_id_api_key: str = "your-d-id-api-key"  # Will auto-map to D_ID_API_KEY
    d_id_api_url: str = "https://api.d-id.com"
    elevenlabs_api_key: str = "your-elevenlabs-api-key"  # Will auto-map to ELEVENLABS_API_KEY
    elevenlabs_voice_id: str = "your-custom-swamiji-voice-id"  # Will auto-map to ELEVENLABS_VOICE_ID
    agora_app_id: str = "your-agora-app-id"  # Will auto-map to AGORA_APP_ID
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
    cors_origins: str = "http://localhost:3000,https://jyotiflow.ai"
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
        "extra": "ignore",  # This prevents "extra inputs not permitted" errors
        "validate_default": True,
    }
    
    #class config that was removed
    

# Initialize enhanced settings
settings = EnhancedSettings()

# =============================================================================
# 📊 ENHANCED PYDANTIC MODELS - ALL MODELS WITH AVATAR INTEGRATION
# তমিল - উন্নত Pydantic মডেল - অবতার ইন্টিগ্রেশন সহ সব মডেল
# =============================================================================

# Existing Models (Preserved and Enhanced)
class UserRegistration(BaseModel):
    """তমিল - User registration with enhanced fields"""
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)
    phone: Optional[str] = Field(None, regex=r'^\+?[\d\s\-\(\)]+$')
    birth_date: Optional[str] = None
    birth_time: Optional[str] = None
    birth_location: Optional[str] = None
    referral_code: Optional[str] = None
    marketing_source: Optional[str] = None
    
    # NEW: Avatar Preferences
    preferred_avatar_style: Optional[str] = "traditional"  # traditional, modern, casual
    voice_preference: Optional[str] = "compassionate"  # compassionate, wise, gentle
    video_quality_preference: Optional[str] = "high"  # low, medium, high

class UserLogin(BaseModel):
    """তমিল - User login model"""
    email: EmailStr
    password: str

class UserProfile(BaseModel):
    """তমিল - Enhanced user profile with avatar preferences"""
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

# NEW: Avatar-Specific Models
class AvatarGenerationRequest(BaseModel):
    """তমিল - Avatar video generation request"""
    user_email: str
    session_id: str
    guidance_text: str
    service_type: str = Field(..., regex=r'^(clarity|love|premium|elite)$')
    
    # Avatar Customization
    avatar_style: Optional[str] = "traditional"
    voice_tone: Optional[str] = "compassionate"
    video_duration: Optional[int] = Field(default=300, le=1800)  # Max 30 minutes
    include_subtitles: bool = True
    video_quality: str = "high"
    
    # Spiritual Context
    user_birth_details: Optional[Dict[str, Any]] = None
    astrological_context: Optional[Dict[str, Any]] = None
    emotional_tone: Optional[str] = "supportive"

class AvatarGenerationResponse(BaseModel):
    """তমিল - Avatar generation response"""
    success: bool
    avatar_id: str
    video_url: Optional[str] = None
    duration_seconds: Optional[int] = None
    generation_time_seconds: Optional[float] = None
    cost_usd: Optional[float] = None
    quality_score: Optional[float] = None
    message: str
    error_details: Optional[str] = None

class LiveChatSessionRequest(BaseModel):
    """তমিল - Live video chat session request"""
    user_email: str
    service_type: str = Field(..., regex=r'^(premium|elite)$')
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

# Enhanced Existing Models
class SessionRequest(BaseModel):
    """তমিল - Enhanced session request with avatar options"""
    service_type: str = Field(..., regex=r'^(clarity|love|premium|elite)$')
    question: str = Field(..., min_length=10, max_length=2000)
    birth_details: Optional[Dict[str, Any]] = None
    
    # NEW: Avatar Enhancement Options
    include_avatar_video: bool = True
    avatar_duration_preference: Optional[int] = None  # Let service determine if None
    request_live_chat: bool = False  # For premium/elite only
    voice_tone_preference: Optional[str] = "compassionate"

class SessionResponse(BaseModel):
    """তমিল - Enhanced session response with avatar content"""
    success: bool
    session_id: str
    guidance_text: str
    credits_used: int
    service_name: str
    
    # NEW: Avatar Content
    avatar_video_url: Optional[str] = None
    avatar_duration_seconds: Optional[int] = None
    live_chat_available: bool = False
    live_chat_url: Optional[str] = None
    
    # Enhanced Metadata
    astrological_insights: Optional[Dict[str, Any]] = None
    estimated_completion_time: datetime
    session_quality_score: Optional[float] = None

class MonetizationRecommendation(BaseModel):
    """তমিল - AI-powered business optimization recommendation"""
    recommendation_id: str
    recommendation_type: str  # pricing, product, marketing, optimization
    title: str
    description: str
    
    # Impact Projections
    projected_revenue_increase_percent: float
    projected_user_impact: str
    confidence_score: float  # 0.0 to 1.0
    
    # Implementation Details
    implementation_effort: str  # low, medium, high
    timeframe_days: int
    risk_level: str  # low, medium, high
    
    # Supporting Data
    data_points: List[Dict[str, Any]]
    created_at: datetime
    expires_at: Optional[datetime] = None

class StandardResponse(BaseModel):
    """তমিল - Enhanced standard API response"""
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
# তমিল - অবতার টেবিল সহ উন্নত ডেটাবেস ম্যানেজার
# =============================================================================

class EnhancedDatabaseManager:
    """তমিল - Enhanced database manager with avatar functionality"""
    
    def __init__(self):
        self.database_url = settings.database_url
        self.pool = None
        self.is_sqlite = "sqlite" in self.database_url.lower()
        self.database_type = "SQLite" if self.is_sqlite else "PostgreSQL"
        
    async def initialize(self):
        """তমিল - Initialize enhanced database with avatar tables"""
        try:
            if self.is_sqlite:
                await self._initialize_sqlite()
            else:
                await self._initialize_postgresql()
            
            # Create enhanced schema with avatar tables
            await self._create_enhanced_schema()
            
            logger.info(f"✅ Enhanced database initialized: {self.database_type}")
            
        except Exception as e:
            logger.error(f"❌ Enhanced database initialization failed: {e}")
            raise e
    
    async def _initialize_sqlite(self):
        """তমিল - Initialize SQLite with enhanced configuration"""
        # SQLite doesn't use connection pools, but we'll maintain compatibility
        self.pool = None
        
    async def _initialize_postgresql(self):
        """তমিল - Initialize PostgreSQL with enhanced connection pool"""
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
        """তমিল - Get database connection"""
        if self.is_sqlite:
            return await aiosqlite.connect(self.database_url.replace("sqlite:///", ""))
        else:
            if not self.pool:
                raise Exception("Database pool not initialized")
            return await self.pool.acquire()
    
    async def release_connection(self, conn):
        """তমিল - Release database connection"""
        if self.is_sqlite:
            if conn:
                await conn.close()
        else:
            if conn and self.pool:
                await self.pool.release(conn)
    
    async def _create_enhanced_schema(self):
        """তমিল - Create enhanced database schema with avatar tables"""
        
        enhanced_schema = """
        -- ============================================================================
        -- Enhanced JyotiFlow.ai Database Schema with AI Avatar Integration
        -- ============================================================================
        
        -- Existing Users Table (Enhanced)
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email VARCHAR(255) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            name VARCHAR(255) NOT NULL,
            phone VARCHAR(20),
            
            -- Credit System (Existing)
            credits INTEGER DEFAULT 3 CHECK (credits >= 0),
            total_credits_purchased INTEGER DEFAULT 0,
            total_credits_used INTEGER DEFAULT 0,
            
            -- Profile & Preferences (Enhanced)
            birth_date DATE,
            birth_time TIME,
            birth_location VARCHAR(255),
            birth_latitude DECIMAL(10, 8),
            birth_longitude DECIMAL(11, 8),
            timezone VARCHAR(50) DEFAULT 'Asia/Kolkata',
            language VARCHAR(10) DEFAULT 'en',
            
            -- NEW: Avatar Preferences
            preferred_avatar_style VARCHAR(50) DEFAULT 'traditional',
            voice_preference VARCHAR(50) DEFAULT 'compassionate',
            video_quality_preference VARCHAR(50) DEFAULT 'high',
            avatar_sessions_count INTEGER DEFAULT 0,
            total_avatar_minutes INTEGER DEFAULT 0,
            
            -- Account Status (Enhanced)
            role VARCHAR(20) DEFAULT 'user' CHECK (role IN ('user', 'admin', 'moderator')),
            status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'suspended')),
            spiritual_level VARCHAR(20) DEFAULT 'beginner',
            
            -- Marketing & Growth
            referral_code VARCHAR(20) UNIQUE,
            referred_by VARCHAR(255),
            marketing_source VARCHAR(100),
            
            -- Metadata
            total_sessions INTEGER DEFAULT 0,
            last_login_at TIMESTAMP,
            last_session_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Existing Sessions Table (Enhanced)
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            user_email VARCHAR(255) NOT NULL,
            service_type VARCHAR(50) NOT NULL CHECK (service_type IN ('clarity', 'love', 'premium', 'elite')),
            question TEXT NOT NULL,
            birth_details TEXT, -- JSON
            
            -- Session Processing (Enhanced)
            status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
            result_summary TEXT,
            full_result TEXT, -- JSON
            
            -- NEW: Avatar Integration
            avatar_video_url TEXT,
            avatar_duration_seconds INTEGER,
            avatar_generation_cost DECIMAL(10, 4),
            voice_synthesis_used BOOLEAN DEFAULT FALSE,
            avatar_quality VARCHAR(20) DEFAULT 'high',
            
            -- Credits & Payment
            credits_used INTEGER NOT NULL DEFAULT 0,
            original_price DECIMAL(10, 2),
            
            -- Quality & Feedback
            user_rating INTEGER CHECK (user_rating >= 1 AND user_rating <= 5),
            user_feedback TEXT,
            session_quality_score DECIMAL(3, 2),
            
            -- Metadata
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            
            FOREIGN KEY (user_email) REFERENCES users(email) ON DELETE CASCADE
        );
        
        -- NEW: Avatar Sessions Table
        CREATE TABLE IF NOT EXISTS avatar_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            user_email VARCHAR(255) NOT NULL,
            
            -- Avatar Generation Details
            avatar_prompt TEXT NOT NULL,
            voice_script TEXT NOT NULL,
            avatar_style VARCHAR(50) DEFAULT 'traditional',
            voice_tone VARCHAR(50) DEFAULT 'compassionate',
            
            -- Generation Process
            d_id_talk_id VARCHAR(255),
            elevenlabs_audio_id VARCHAR(255),
            generation_status VARCHAR(50) DEFAULT 'pending',
            generation_started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            generation_completed_at TIMESTAMP,
            
            -- Results
            video_url TEXT,
            audio_url TEXT,
            duration_seconds INTEGER,
            file_size_mb DECIMAL(10, 2),
            video_quality VARCHAR(20),
            
            -- Costs & Performance
            d_id_cost DECIMAL(10, 4),
            elevenlabs_cost DECIMAL(10, 4),
            total_cost DECIMAL(10, 4),
            generation_time_seconds DECIMAL(10, 2),
            quality_score DECIMAL(3, 2),
            
            -- Metadata
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE,
            FOREIGN KEY (user_email) REFERENCES users(email) ON DELETE CASCADE
        );
        
        -- NEW: Live Chat Sessions Table
        CREATE TABLE IF NOT EXISTS live_chat_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email VARCHAR(255) NOT NULL,
            session_id TEXT,
            
            -- Chat Details
            service_type VARCHAR(50) NOT NULL CHECK (service_type IN ('premium', 'elite')),
            scheduled_duration_minutes INTEGER DEFAULT 15,
            actual_duration_minutes INTEGER,
            
            -- Agora Integration
            agora_channel_name VARCHAR(255) UNIQUE,
            agora_token TEXT,
            agora_uid INTEGER,
            
            -- Session Status
            status VARCHAR(50) DEFAULT 'scheduled' CHECK (status IN ('scheduled', 'active', 'completed', 'cancelled')),
            scheduled_time TIMESTAMP,
            started_at TIMESTAMP,
            ended_at TIMESTAMP,
            
            -- Content & Quality
            topic TEXT,
            session_notes TEXT,
            user_satisfaction INTEGER CHECK (user_satisfaction >= 1 AND user_satisfaction <= 5),
            technical_quality_score DECIMAL(3, 2),
            
            -- Costs
            chat_cost DECIMAL(10, 4),
            credits_used INTEGER,
            
            -- Metadata
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            FOREIGN KEY (user_email) REFERENCES users(email) ON DELETE CASCADE,
            FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE SET NULL
        );
        
        -- NEW: Satsang Events Table
        CREATE TABLE IF NOT EXISTS satsang_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title VARCHAR(255) NOT NULL,
            description TEXT,
            
            -- Event Details
            scheduled_date TIMESTAMP NOT NULL,
            duration_minutes INTEGER DEFAULT 90,
            max_attendees INTEGER DEFAULT 1000,
            is_premium_only BOOLEAN DEFAULT FALSE,
            
            -- Streaming Details
            stream_url TEXT,
            agora_channel_name VARCHAR(255),
            recording_url TEXT,
            
            -- Event Status
            status VARCHAR(50) DEFAULT 'scheduled' CHECK (status IN ('scheduled', 'live', 'completed', 'cancelled')),
            actual_start_time TIMESTAMP,
            actual_end_time TIMESTAMP,
            
            -- Analytics
            total_registrations INTEGER DEFAULT 0,
            peak_concurrent_attendees INTEGER DEFAULT 0,
            average_engagement_score DECIMAL(3, 2),
            
            -- Content
            spiritual_theme VARCHAR(255),
            key_teachings TEXT, -- JSON array
            
            -- Metadata
            created_by VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- NEW: Satsang Attendees Table
        CREATE TABLE IF NOT EXISTS satsang_attendees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            satsang_id INTEGER NOT NULL,
            user_email VARCHAR(255) NOT NULL,
            
            -- Attendance Details
            registration_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            attended BOOLEAN DEFAULT FALSE,
            join_time TIMESTAMP,
            leave_time TIMESTAMP,
            duration_minutes INTEGER,
            
            -- Engagement
            questions_asked INTEGER DEFAULT 0,
            chat_messages_sent INTEGER DEFAULT 0,
            engagement_score DECIMAL(3, 2),
            
            -- Feedback
            rating INTEGER CHECK (rating >= 1 AND rating <= 5),
            feedback TEXT,
            
            FOREIGN KEY (satsang_id) REFERENCES satsang_events(id) ON DELETE CASCADE,
            FOREIGN KEY (user_email) REFERENCES users(email) ON DELETE CASCADE,
            UNIQUE(satsang_id, user_email)
        );
        
        -- Existing Credit Transactions Table (Enhanced)
        CREATE TABLE IF NOT EXISTS credit_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email VARCHAR(255) NOT NULL,
            transaction_type VARCHAR(20) NOT NULL CHECK (transaction_type IN ('purchase', 'deduction', 'refund', 'bonus', 'admin_adjustment')),
            credits INTEGER NOT NULL,
            balance_before INTEGER DEFAULT 0,
            balance_after INTEGER DEFAULT 0,
            
            -- Purchase Details
            package_type VARCHAR(20),
            amount_paid DECIMAL(10, 2),
            currency VARCHAR(3) DEFAULT 'USD',
            
            -- Payment Processing
            payment_method VARCHAR(50),
            stripe_session_id VARCHAR(255),
            stripe_payment_intent_id VARCHAR(255),
            
            -- Session Reference
            session_id TEXT,
            
            -- Admin Actions
            admin_email VARCHAR(255),
            admin_reason TEXT,
            
            -- NEW: Avatar Service Costs
            avatar_generation_cost DECIMAL(10, 4),
            live_chat_cost DECIMAL(10, 4),
            
            -- Metadata
            description TEXT NOT NULL,
            status VARCHAR(20) DEFAULT 'completed',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            FOREIGN KEY (user_email) REFERENCES users(email) ON DELETE CASCADE,
            FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE SET NULL
        );
        
        -- NEW: AI Recommendations Table
        CREATE TABLE IF NOT EXISTS ai_recommendations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recommendation_id TEXT UNIQUE NOT NULL,
            recommendation_type VARCHAR(50) NOT NULL,
            
            -- Recommendation Content
            title VARCHAR(255) NOT NULL,
            description TEXT NOT NULL,
            implementation_details TEXT, -- JSON
            
            -- Impact Analysis
            projected_revenue_increase_percent DECIMAL(5, 2),
            projected_user_impact TEXT,
            confidence_score DECIMAL(3, 2),
            
            -- Implementation
            implementation_effort VARCHAR(20) CHECK (implementation_effort IN ('low', 'medium', 'high')),
            timeframe_days INTEGER,
            risk_level VARCHAR(20) CHECK (risk_level IN ('low', 'medium', 'high')),
            
            -- Status
            status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'implemented', 'rejected')),
            admin_response TEXT,
            
            -- Supporting Data
            data_points TEXT, -- JSON
            analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            -- Metadata
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP
        );
        
        -- NEW: Social Content Table
        CREATE TABLE IF NOT EXISTS social_content (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content_id TEXT UNIQUE NOT NULL,
            content_type VARCHAR(50) NOT NULL CHECK (content_type IN ('daily_wisdom', 'user_highlight', 'satsang_promo', 'spiritual_quote')),
            
            -- Content Details
            title VARCHAR(255),
            content_text TEXT,
            hashtags TEXT, -- Comma-separated
            
            -- Media Assets
            image_url TEXT,
            video_url TEXT,
            audio_url TEXT,
            
            -- Source Information
            source_session_id TEXT,
            source_user_email VARCHAR(255),
            ai_generated BOOLEAN DEFAULT TRUE,
            
            -- Publishing Details
            scheduled_publish_time TIMESTAMP,
            published_at TIMESTAMP,
            platforms TEXT, -- JSON array: instagram, youtube, twitter, etc.
            
            -- Performance Metrics
            views INTEGER DEFAULT 0,
            likes INTEGER DEFAULT 0,
            shares INTEGER DEFAULT 0,
            comments INTEGER DEFAULT 0,
            engagement_rate DECIMAL(5, 2),
            
            -- Status
            status VARCHAR(50) DEFAULT 'draft' CHECK (status IN ('draft', 'scheduled', 'published', 'archived')),
            
            -- Metadata
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            FOREIGN KEY (source_session_id) REFERENCES sessions(id) ON DELETE SET NULL,
            FOREIGN KEY (source_user_email) REFERENCES users(email) ON DELETE SET NULL
        );
        
        -- Existing Admin Logs Table (Enhanced)
        CREATE TABLE IF NOT EXISTS admin_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            admin_email VARCHAR(255) NOT NULL,
            action VARCHAR(100) NOT NULL,
            target_type VARCHAR(50),
            target_id VARCHAR(255),
            target_user VARCHAR(255),
            
            -- Enhanced Action Details
            details TEXT, -- JSON
            old_values TEXT, -- JSON
            new_values TEXT, -- JSON
            
            -- NEW: Avatar-Related Actions
            avatar_actions TEXT, -- JSON for avatar-specific admin actions
            
            -- Request Information
            ip_address VARCHAR(45),
            user_agent TEXT,
            endpoint VARCHAR(255),
            
            -- Status
            status VARCHAR(20) DEFAULT 'success',
            error_message TEXT,
            
            -- Metadata
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            session_id VARCHAR(255)
        );
        
        -- Enhanced Indexes for Performance
        CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
        CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
        CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);
        CREATE INDEX IF NOT EXISTS idx_sessions_user_email ON sessions(user_email);
        CREATE INDEX IF NOT EXISTS idx_sessions_status ON sessions(status);
        CREATE INDEX IF NOT EXISTS idx_sessions_service_type ON sessions(service_type);
        CREATE INDEX IF NOT EXISTS idx_sessions_created_at ON sessions(created_at);
        
        -- NEW: Avatar-Specific Indexes
        CREATE INDEX IF NOT EXISTS idx_avatar_sessions_user_email ON avatar_sessions(user_email);
        CREATE INDEX IF NOT EXISTS idx_avatar_sessions_status ON avatar_sessions(generation_status);
        CREATE INDEX IF NOT EXISTS idx_live_chat_sessions_user_email ON live_chat_sessions(user_email);
        CREATE INDEX IF NOT EXISTS idx_live_chat_sessions_status ON live_chat_sessions(status);
        CREATE INDEX IF NOT EXISTS idx_satsang_events_date ON satsang_events(scheduled_date);
        CREATE INDEX IF NOT EXISTS idx_satsang_attendees_user ON satsang_attendees(user_email);
        CREATE INDEX IF NOT EXISTS idx_ai_recommendations_type ON ai_recommendations(recommendation_type);
        CREATE INDEX IF NOT EXISTS idx_ai_recommendations_status ON ai_recommendations(status);
        CREATE INDEX IF NOT EXISTS idx_social_content_type ON social_content(content_type);
        CREATE INDEX IF NOT EXISTS idx_social_content_status ON social_content(status);
        """
        
        conn = None
        try:
            conn = await self.get_connection()
            
            if self.is_sqlite:
                # Execute SQLite schema
                statements = [s.strip() for s in enhanced_schema.split(';') if s.strip()]
                for statement in statements:
                    if statement and not statement.startswith('--'):
                        await conn.execute(statement)
                await conn.commit()
            else:
                # For PostgreSQL, adapt the schema
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
        """তমিল - Enhanced database health check"""
        try:
            conn = await self.get_connection()
            
            # Test basic connectivity
            if self.is_sqlite:
                result = await conn.execute("SELECT 1")
                row = await result.fetchone()
                test_result = row[0] if row else None
            else:
                test_result = await conn.fetchval("SELECT 1")
            
            if test_result != 1:
                raise Exception("Database connectivity test failed")
            
            # Get enhanced statistics
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
        """তমিল - Get enhanced database statistics"""
        try:
            if self.is_sqlite:
                # SQLite statistics
                total_users = await conn.execute("SELECT COUNT(*) FROM users")
                total_users = (await total_users.fetchone())[0]
                
                total_sessions = await conn.execute("SELECT COUNT(*) FROM sessions")
                total_sessions = (await total_sessions.fetchone())[0]
                
                avatar_sessions = await conn.execute("SELECT COUNT(*) FROM avatar_sessions")
                avatar_sessions = (await avatar_sessions.fetchone())[0]
                
            else:
                # PostgreSQL statistics
                total_users = await conn.fetchval("SELECT COUNT(*) FROM users")
                total_sessions = await conn.fetchval("SELECT COUNT(*) FROM sessions") 
                avatar_sessions = await conn.fetchval("SELECT COUNT(*) FROM avatar_sessions")
            
            return {
                "total_users": total_users or 0,
                "total_sessions": total_sessions or 0,
                "avatar_sessions": avatar_sessions or 0,
                "tables_created": True
            }
            
        except Exception as e:
            logger.warning(f"Could not get database stats: {e}")
            return {"error": "Statistics unavailable"}
    
    async def close(self):
        """তমিল - Close enhanced database connections"""
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
# তমিল - অবতার প্রমাণীকরণ সহ উন্নত নিরাপত্তা ব্যবস্থাপক
# =============================================================================

class EnhancedSecurityManager:
    """তমিল - Enhanced security manager with avatar service authentication"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """তমিল - Hash password using bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """তমিল - Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    @staticmethod
    def create_access_token(user_data: Dict[str, Any]) -> str:
        """তমিল - Create JWT access token with enhanced claims"""
        payload = {
            'email': user_data['email'],
            'role': user_data.get('role', 'user'),
            'user_id': user_data.get('id'),
            'name': user_data.get('name'),
            
            # NEW: Avatar Service Permissions
            'avatar_enabled': True,
            'live_chat_enabled': user_data.get('role') in ['user', 'admin'],
            'satsang_access': True,
            
            # Token metadata
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(hours=settings.jwt_expiration_hours),
            'iss': 'jyotiflow-enhanced'
        }
        return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    
    @staticmethod
    def verify_access_token(token: str) -> Dict[str, Any]:
        """তমিল - Verify JWT access token"""
        try:
            payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")
    
    @staticmethod
    def generate_agora_token(channel_name: str, uid: int, duration_seconds: int = 3600) -> str:
        """তমিল - Generate Agora RTC token for live video chat"""
        try:
            # This is a simplified version - in production, use Agora's official SDK
            import hmac
            import hashlib
            import base64
            
            # Create a simple token (replace with official Agora token generation)
            message = f"{settings.agora_app_id}:{channel_name}:{uid}:{duration_seconds}"
            signature = hmac.new(
                settings.agora_app_certificate.encode(),
                message.encode(),
                hashlib.sha256
            ).digest()
            
            token_data = {
                'app_id': settings.agora_app_id,
                'channel': channel_name,
                'uid': uid,
                'expires': duration_seconds,
                'signature': base64.b64encode(signature).decode()
            }
            
            return base64.b64encode(json.dumps(token_data).encode()).decode()
            
        except Exception as e:
            logger.error(f"Agora token generation failed: {e}")
            return f"demo_token_{channel_name}_{uid}"

# Initialize enhanced security manager
security_manager = EnhancedSecurityManager()

# =============================================================================
# 🔑 ENHANCED AUTHENTICATION DEPENDENCIES
# তমিল - উন্নত প্রমাণীকরণ নির্ভরতা
# =============================================================================

# HTTP Bearer Security Scheme
security_scheme = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security_scheme)) -> Dict[str, Any]:
    """তমিল - Get current authenticated user with enhanced permissions"""
    try:
        # Verify token
        payload = security_manager.verify_access_token(credentials.credentials)
        
        # Get user from database with enhanced fields
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
            
            # Convert to dict and add permissions
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
    """তমিল - Get current admin user"""
    if current_user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

# =============================================================================
# 🌐 ENHANCED EXTERNAL SERVICE CLIENTS
# তমিল - উন্নত বাহ্যিক সেবা ক্লায়েন্ট
# =============================================================================

# Initialize enhanced external service clients
openai_client = AsyncOpenAI(api_key=settings.openai_api_key) if settings.openai_api_key != "your-openai-api-key" else None
stripe.api_key = settings.stripe_secret_key if settings.stripe_secret_key != "your-stripe-secret-key" else None

class EnhancedAvatarServiceClients:
    """তমিল - Enhanced avatar service clients initialization"""
    
    @staticmethod
    def get_d_id_headers() -> Dict[str, str]:
        """তমিল - Get D-ID API headers"""
        return {
            "Authorization": f"Basic {settings.d_id_api_key}",
            "Content-Type": "application/json"
        }
    
    @staticmethod
    def get_elevenlabs_headers() -> Dict[str, str]:
        """তমিল - Get ElevenLabs API headers"""
        return {
            "xi-api-key": settings.elevenlabs_api_key,
            "Content-Type": "application/json"
        }
    
    @staticmethod
    async def test_avatar_services() -> Dict[str, str]:
        """তমিল - Test avatar service connectivity"""
        results = {}
        
        # Test D-ID
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
        
        # Test ElevenLabs
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
# তমিল - অবতার প্রক্রিয়াকরণ সহ উন্নত ইউটিলিটি
# =============================================================================

class EnhancedUtilities:
    """তমিল - Enhanced utility functions with avatar support"""
    
    @staticmethod
    def generate_session_id() -> str:
        """তমিল - Generate unique session ID"""
        from uuid import uuid4
        return str(uuid4())
    
    @staticmethod
    def generate_agora_channel_name(user_email: str, session_type: str) -> str:
        """তমিল - Generate unique Agora channel name"""
        import hashlib
        data = f"{user_email}_{session_type}_{datetime.now().timestamp()}"
        return hashlib.md5(data.encode()).hexdigest()[:16]
    
    @staticmethod
    def validate_avatar_duration(service_type: str, requested_duration: Optional[int]) -> int:
        """তমিল - Validate and return appropriate avatar duration"""
        service_limits = {
            'clarity': 300,      # 5 minutes
            'love': 600,         # 10 minutes  
            'premium': 1200,     # 20 minutes
            'elite': 1800        # 30 minutes
        }
        
        max_duration = service_limits.get(service_type, 300)
        
        if requested_duration is None:
            return max_duration
        
        return min(requested_duration, max_duration, settings.max_avatar_duration_seconds)
    
    @staticmethod
    def calculate_avatar_cost(duration_seconds: int, quality: str = "high") -> float:
        """তমিল - Calculate estimated avatar generation cost"""
        # D-ID pricing: ~$0.12 per minute
        # ElevenLabs pricing: ~$0.08 per minute for high quality
        
        minutes = duration_seconds / 60.0
        
        quality_multipliers = {
            "low": 0.7,
            "medium": 0.85, 
            "high": 1.0
        }
        
        base_cost_per_minute = 0.20  # Combined D-ID + ElevenLabs
        multiplier = quality_multipliers.get(quality, 1.0)
        
        return round(minutes * base_cost_per_minute * multiplier, 4)
    
    @staticmethod
    def sanitize_spiritual_content(content: str) -> str:
        """তমিল - Sanitize spiritual content for avatar generation"""
        import re
        
        # Remove potentially problematic characters
        content = re.sub(r'[^\w\s\.,!?;:()\'-]', '', content)
        
        # Limit length for voice synthesis
        max_length = 4000  # ElevenLabs character limit
        if len(content) > max_length:
            content = content[:max_length] + "..."
        
        return content.strip()
    
    @staticmethod
    def format_spiritual_response(guidance_text: str, user_name: str) -> str:
        """তমিল - Format spiritual guidance for avatar presentation"""
        
        # Add spiritual greeting
        greeting = f"🙏🏼 Namaste, dear {user_name}."
        
        # Add spiritual closing
        closing = "\n\nMay divine light guide your path. Om Shanti Shanti Shanti. 🕉️"
        
        # Combine with proper formatting
        formatted_response = f"{greeting}\n\n{guidance_text}{closing}"
        
        return EnhancedUtilities.sanitize_spiritual_content(formatted_response)

utilities = EnhancedUtilities()

# =============================================================================
# 🏥 ENHANCED HEALTH MONITOR WITH AVATAR SERVICE STATUS
# তমিল - অবতার সেবা স্থিতি সহ উন্নত স্বাস্থ্য মনিটর
# =============================================================================

class EnhancedHealthMonitor:
    """তমিল - Enhanced health monitoring with avatar services"""
    
    @staticmethod
    async def get_system_health() -> Dict[str, Any]:
        """তমিল - Complete enhanced system health check"""
        
        health_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "overall_status": "healthy",
            "services": {},
            "avatar_services": {},
            "performance": {},
            "enhanced_features": {}
        }
        
        try:
            # Database health (enhanced)
            db_health = await db_manager.health_check()
            health_data["services"]["database"] = db_health
            
            # Avatar services health (new)
            avatar_health = await avatar_clients.test_avatar_services()
            health_data["avatar_services"] = avatar_health
            
            # External services health (enhanced)
            external_health = await EnhancedHealthMonitor._check_external_services()
            health_data["services"].update(external_health)
            
            # Performance metrics (enhanced)
            performance = await EnhancedHealthMonitor._get_performance_metrics()
            health_data["performance"] = performance
            
            # Enhanced features status
            enhanced_status = await EnhancedHealthMonitor._check_enhanced_features()
            health_data["enhanced_features"] = enhanced_status
            
            # Calculate overall status
            health_data["overall_status"] = EnhancedHealthMonitor._calculate_overall_status(health_data)
            
        except Exception as e:
            health_data["overall_status"] = "unhealthy"
            health_data["error"] = str(e)
        
        return health_data
    
    @staticmethod
    async def _check_external_services() -> Dict[str, str]:
        """তমিল - Check external service health"""
        
        services = {}
        
        # OpenAI
        try:
            if openai_client:
                # Simple test - get models list
                models = await openai_client.models.list()
                services["openai"] = "healthy"
            else:
                services["openai"] = "not_configured"
        except:
            services["openai"] = "unhealthy"
        
        # Stripe
        try:
            if stripe.api_key:
                # Simple test - retrieve account
                stripe.Account.retrieve()
                services["stripe"] = "healthy"
            else:
                services["stripe"] = "not_configured"
        except:
            services["stripe"] = "unhealthy"
        
        return services
    
    @staticmethod
    async def _get_performance_metrics() -> Dict[str, Any]:
        """তমিল - Get enhanced performance metrics"""
        
        import psutil
        
        try:
            # System performance
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Application metrics
            conn = await db_manager.get_connection()
            
            try:
                if db_manager.is_sqlite:
                    session_count = await conn.execute("SELECT COUNT(*) FROM sessions WHERE DATE(created_at) = DATE('now')")
                    session_count = (await session_count.fetchone())[0]
                    
                    avatar_count = await conn.execute("SELECT COUNT(*) FROM avatar_sessions WHERE DATE(created_at) = DATE('now')")
                    avatar_count = (await avatar_count.fetchone())[0]
                else:
                    session_count = await conn.fetchval("SELECT COUNT(*) FROM sessions WHERE DATE(created_at) = CURRENT_DATE")
                    avatar_count = await conn.fetchval("SELECT COUNT(*) FROM avatar_sessions WHERE DATE(created_at) = CURRENT_DATE")
                
                return {
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "disk_percent": disk.percent,
                    "daily_sessions": session_count or 0,
                    "daily_avatar_generations": avatar_count or 0
                }
                
            finally:
                await db_manager.release_connection(conn)
                
        except Exception as e:
            logger.error(f"Performance metrics error: {e}")
            return {"error": str(e)}
    
    @staticmethod
    async def _check_enhanced_features() -> Dict[str, str]:
        """তমিল - Check enhanced feature availability"""
        
        features = {}
        
        # AI Optimization
        features["ai_optimization"] = "enabled" if settings.ai_optimization_enabled else "disabled"
        
        # Monetization Analysis
        features["monetization_analysis"] = "enabled" if settings.monetization_analysis_enabled else "disabled"
        
        # Social Content Generation
        features["social_content"] = "enabled" if settings.social_content_generation else "disabled"
        
        # Avatar Quality Settings
        features["avatar_quality"] = settings.avatar_quality
        
        # Live Chat Capability
        features["live_chat"] = "enabled" if settings.agora_app_id != "your-agora-app-id" else "not_configured"
        
        return features
    
    @staticmethod
    def _calculate_overall_status(health_data: Dict[str, Any]) -> str:
        """তমিল - Calculate overall system health status"""
        
        try:
            # Check critical services
            db_status = health_data.get("services", {}).get("database", {}).get("status")
            if db_status != "healthy":
                return "degraded"
            
            # Check avatar services (non-critical but important)
            avatar_services = health_data.get("avatar_services", {})
            avatar_healthy = any(status == "connected" for status in avatar_services.values())
            
            # Check performance
            performance = health_data.get("performance", {})
            cpu_high = performance.get("cpu_percent", 0) > 90
            memory_high = performance.get("memory_percent", 0) > 90
            
            if cpu_high or memory_high:
                return "degraded"
            
            if not avatar_healthy:
                return "limited"  # Core works but avatar features limited
            
            return "healthy"
            
        except Exception:
            return "unknown"

health_monitor = EnhancedHealthMonitor()

# =============================================================================
# 🔄 ENHANCED APPLICATION LIFESPAN MANAGEMENT
# তমিল - উন্নত অ্যাপ্লিকেশন জীবনকাল ব্যবস্থাপনা
# =============================================================================

@asynccontextmanager
async def enhanced_app_lifespan(app: FastAPI):
    """তমিল - Enhanced application lifespan with avatar services"""
    
    # Startup
    logger.info("🙏🏼 Starting Enhanced JyotiFlow.ai Digital Ashram...")
    
    try:
        # Initialize enhanced database
        await db_manager.initialize()
        
        # Test avatar services
        avatar_status = await avatar_clients.test_avatar_services()
        logger.info(f"🎭 Avatar services status: {avatar_status}")
        
        # Initialize sample data in development
        if settings.app_env == "development":
            await _initialize_enhanced_sample_data()
        
        # Log enhanced startup success
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
        # Shutdown cleanup
        logger.info("🔄 Shutting down Enhanced JyotiFlow.ai...")
        await db_manager.close()
        logger.info("✅ Enhanced shutdown completed gracefully")

async def _initialize_enhanced_sample_data():
    """তমিল - Initialize enhanced sample data for development"""
    
    try:
        logger.info("📊 Initializing enhanced sample data...")
        
        conn = await db_manager.get_connection()
        
        try:
            # Create admin user
            admin_exists = await _check_user_exists(conn, settings.admin_email)
            if not admin_exists:
                await _create_enhanced_admin_user(conn)
                logger.info(f"👑 Enhanced admin user created: {settings.admin_email}")
            
            # Create sample users with avatar preferences
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
            
            # Create sample satsang event
            await _create_sample_satsang_event(conn)
            
        finally:
            await db_manager.release_connection(conn)
            
        logger.info("✅ Enhanced sample data initialization completed")
        
    except Exception as e:
        logger.error(f"❌ Enhanced sample data initialization failed: {e}")

async def _check_user_exists(conn, email: str) -> bool:
    """তমিল - Check if user exists"""
    if db_manager.is_sqlite:
        result = await conn.execute("SELECT 1 FROM users WHERE email = ?", (email,))
        return (await result.fetchone()) is not None
    else:
        return await conn.fetchval("SELECT 1 FROM users WHERE email = $1", email) is not None

async def _create_enhanced_admin_user(conn):
    """তমিল - Create enhanced admin user"""
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
    """তমিল - Create enhanced sample user"""
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
    """তমিল - Create sample satsang event"""
    
    # Create next month's satsang
    next_satsang = datetime.now(timezone.utc).replace(day=1, hour=10, minute=0, second=0, microsecond=0)
    next_satsang = next_satsang + timedelta(days=32)  # Next month
    next_satsang = next_satsang.replace(day=1)  # First Saturday logic would go here
    
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

# Export enhanced app lifespan
app_lifespan = enhanced_app_lifespan

# তমিল - Log enhanced core foundation completion
logger.info("✅ Enhanced JyotiFlow.ai Core Foundation loaded successfully")
logger.info("🎭 Avatar services configured and ready")
logger.info("🔐 Enhanced security and authentication ready")
logger.info("🗄️ Enhanced database schema with avatar tables ready")
logger.info("🙏🏼 Enhanced Core Foundation provides: Database, Auth, Avatar Config, Security, Monitoring")