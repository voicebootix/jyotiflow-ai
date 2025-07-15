from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import asyncpg
from datetime import datetime
import os
import asyncio

# Sentry initialization - Enhanced version with comprehensive integrations
import sentry_sdk

sentry_dsn = os.getenv("SENTRY_DSN")
if sentry_dsn:
    # Initialize integrations list as empty, then add integrations individually
    integrations = []
    
    # Add base integrations with error handling
    try:
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        integrations.append(FastApiIntegration(auto_error=True))
    except ImportError:
        print("⚠️ FastAPI integration not available")
    
    try:
        from sentry_sdk.integrations.starlette import StarletteIntegration
        integrations.append(StarletteIntegration(auto_error=True))
    except ImportError:
        print("⚠️ Starlette integration not available")
    
    # Add optional database integrations
    try:
        from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration  # type: ignore
        integrations.append(SqlalchemyIntegration())
    except ImportError:
        print("⚠️ SQLAlchemy integration not available")
    
    try:
        from sentry_sdk.integrations.asyncpg import AsyncPGIntegration  # type: ignore
        integrations.append(AsyncPGIntegration())
    except ImportError:
        print("⚠️ AsyncPG integration not available")

    # Parse traces_sample_rate with error handling
    sample_rate_env = os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.1")
    try:
        traces_sample_rate = float(sample_rate_env)
    except ValueError:
        print(f"⚠️ Invalid SENTRY_TRACES_SAMPLE_RATE value: '{sample_rate_env}', falling back to 0.1")
        traces_sample_rate = 0.1

    try:
        sentry_sdk.init(
            dsn=sentry_dsn,
            environment=os.getenv("APP_ENV", "development"),
            integrations=integrations,
            traces_sample_rate=traces_sample_rate,
            send_default_pii=True,
        )
        print(f"✅ Sentry initialized successfully with {len(integrations)} integrations, traces_sample_rate={traces_sample_rate}")
    except Exception as e:
        print(f"❌ Failed to initialize Sentry: {e}")
        print("⚠️ Continuing without Sentry - application will run normally")
else:
    print("⚠️ Sentry DSN not configured - skipping Sentry initialization")

# Import routers
from routers import auth, user, spiritual, sessions, followup, donations, credits, services
from routers import admin_products, admin_subscriptions, admin_credits, admin_analytics, admin_content, admin_settings
from routers import admin_overview, admin_integrations
from routers import content, ai, community, session_analytics
import db

# Import the migration runner
from run_migrations import MigrationRunner

# Import enhanced spiritual guidance router
try:
    from enhanced_spiritual_guidance_router import router as enhanced_spiritual_router
    ENHANCED_ROUTER_AVAILABLE = True
except ImportError:
    ENHANCED_ROUTER_AVAILABLE = False
    print("⚠️ Enhanced spiritual guidance router not available")

# Import additional routers
try:
    from routers.universal_pricing_router import router as universal_pricing_router
    UNIVERSAL_PRICING_AVAILABLE = True
except ImportError:
    UNIVERSAL_PRICING_AVAILABLE = False
    print("⚠️ Universal pricing router not available")

try:
    from routers.avatar_generation_router import router as avatar_generation_router
    AVATAR_GENERATION_AVAILABLE = True
except ImportError:
    AVATAR_GENERATION_AVAILABLE = False
    print("⚠️ Avatar generation router not available")

try:
    from routers.social_media_marketing_router import social_marketing_router
    SOCIAL_MEDIA_AVAILABLE = True
except ImportError:
    SOCIAL_MEDIA_AVAILABLE = False
    print("⚠️ Social media marketing router not available")

try:
    from routers.livechat import router as livechat_router
    LIVECHAT_AVAILABLE = True
except ImportError:
    LIVECHAT_AVAILABLE = False
    print("⚠️ Live chat router not available")

# Surgical auth router - REMOVED (conflicting authentication system)
SURGICAL_AUTH_AVAILABLE = False
print("⚠️ Surgical auth router disabled - using main auth system only")

# Debug router for testing
try:
    from debug_auth_endpoint import debug_router
    DEBUG_ROUTER_AVAILABLE = True
except ImportError:
    DEBUG_ROUTER_AVAILABLE = False
    print("⚠️ Debug router not available")

# Missing endpoints router for 404 fixes
try:
    from missing_endpoints import ai_router, user_router as missing_user_router, sessions_router, community_router
    MISSING_ENDPOINTS_AVAILABLE = True
except ImportError:
    MISSING_ENDPOINTS_AVAILABLE = False
    print("⚠️ Missing endpoints router not available")

# Environment debug router
try:
    from debug_env_check import env_debug_router
    ENV_DEBUG_ROUTER_AVAILABLE = True
except ImportError:
    ENV_DEBUG_ROUTER_AVAILABLE = False
    print("⚠️ Environment debug router not available")

# Import database initialization
from init_database import initialize_jyotiflow_database

# Import enhanced startup integration
from enhanced_startup_integration import initialize_enhanced_jyotiflow

# Import comprehensive startup fixes
try:
    from fix_startup_issues import JyotiFlowStartupFixer
    STARTUP_FIXER_AVAILABLE = True
except ImportError:
    STARTUP_FIXER_AVAILABLE = False
    print("⚠️ Startup fixer not available")

# Import database schema fix
from db_schema_fix import fix_database_schema

async def ensure_base_credits_column():
    DB_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:password@localhost:5432/jyotiflow')
    conn = await asyncpg.connect(DB_URL)
    try:
        col_exists = await conn.fetchval("""
            SELECT 1 FROM information_schema.columns 
            WHERE table_name='service_types' AND column_name='base_credits'
        """)
        if not col_exists:
            print("[AUTO-FIX] Adding missing column: base_credits to service_types...")
            await conn.execute("ALTER TABLE service_types ADD COLUMN base_credits INTEGER DEFAULT 1;")
            print("[AUTO-FIX] base_credits column added!")
        else:
            print("[AUTO-FIX] base_credits column already exists.")
    finally:
        await conn.close()

async def apply_migrations():
    """Apply database migrations using the migration runner"""
    try:
        print("🔄 Applying database migrations...")
        migration_runner = MigrationRunner(DATABASE_URL)
        success = await migration_runner.run_migrations()
        
        if success:
            print("✅ Database migrations applied successfully")
            return True
        else:
            print("⚠️ Some migrations failed but continuing startup")
            return False
            
    except Exception as e:
        print(f"❌ Migration system failed: {e}")
        return False

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/yourdb")

# Global database pool
db_pool = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan manager for startup and shutdown"""
    # Startup
    try:
        print("🚀 Starting JyotiFlow.ai backend...")
        
        # Apply database migrations first
        # await apply_migrations()
        print("⏭️ Skipping migrations - Database already set up")
        
        # Initialize database connection pool with enhanced settings
        global db_pool
        db_pool = await asyncpg.create_pool(
            DATABASE_URL,
            min_size=5,
            max_size=20,
            command_timeout=60,
            server_settings={
                'application_name': 'jyotiflow_main_pool',
                'tcp_keepalives_idle': '600',
                'tcp_keepalives_interval': '60',
                'tcp_keepalives_count': '5'
            }
        )
        
        # Set the pool in the db module for all routers to use
        db.set_db_pool(db_pool)
        
        print("✅ Database connection pool initialized")
        
        # Test database connection
        if db_pool is not None:
            async with db_pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
            print("✅ Database connection test successful")
        else:
            raise Exception("Database pool is not initialized.")
        
        # Skip column checks - they use ALTER TABLE
        print("⏭️ Skipping column checks - Database already configured")
        
        # Skip schema fixes - they use ALTER TABLE
        print("⏭️ Skipping schema fixes - Database already fixed")
        
        # Safe database initialization might be OK if it only INSERTs data
        try:
            print("🚀 Checking if safe database initialization is needed...")
            from safe_database_init import safe_initialize_database
            # This should only INSERT data, not create/alter tables
            success = await safe_initialize_database()
            if success:
                print("✅ Safe database initialization completed!")
        except Exception as e:
            print(f"⚠️ Safe initialization skipped: {e}")
            # This is OK - tables exist, just might be missing some seed data
        
        # Surgical fix for admin user authentication - DISABLED
        # This is now handled by safe_database_init.py with consistent bcrypt hashing
        print("⏭️ Skipping surgical admin authentication fix - handled by safe_database_init.py")
        
        # Initialize enhanced system if available
        if ENHANCED_ROUTER_AVAILABLE:
            try:
                from enhanced_startup_integration import initialize_enhanced_jyotiflow
                success = await initialize_enhanced_jyotiflow()
                if success:
                    print("✅ Enhanced JyotiFlow system initialized successfully")
                else:
                    print("⚠️ Enhanced system initialization had issues but will continue in fallback mode")
            except Exception as e:
                print(f"⚠️ Enhanced system initialization failed: {e}")
        
        # Run comprehensive startup fixes if available
        if STARTUP_FIXER_AVAILABLE:
            try:
                from fix_startup_issues import JyotiFlowStartupFixer
                startup_fixer = JyotiFlowStartupFixer()
                await startup_fixer.fix_all_issues()
                print("✅ Comprehensive startup fixes applied successfully")
            except Exception as e:
                print(f"⚠️ Comprehensive startup fixes failed: {e}")
        
        print("🎉 JyotiFlow.ai backend startup completed successfully!")
        
    except Exception as e:
        print(f"❌ Backend startup failed: {e}")
        raise
    
    # Yield control to the application
    yield
    
    # Shutdown
    try:
        print("🛑 Shutting down JyotiFlow.ai backend...")
        if db_pool is not None:
            await db_pool.close()
            print("✅ Database connections closed")
        print("👋 JyotiFlow.ai backend shutdown completed")
    except Exception as e:
        print(f"❌ Backend shutdown error: {e}")

# Create FastAPI app with lifespan manager
app = FastAPI(
    title="🕉️ JyotiFlow.ai - Divine Digital Guidance API", 
    description="Spiritual guidance platform with AI-powered insights and live consultations",
    version="2.0.0",
    lifespan=lifespan
)

# --- CORS Middleware (English & Tamil) ---
# எப்போதும் frontend deploy domain-ஐ allow செய்ய வேண்டும் (CORS fix)
ALWAYS_ALLOW_ORIGINS = ["https://jyotiflow-ai-frontend.onrender.com"]

def get_cors_origins():
    """Get CORS origins based on environment"""
    app_env = os.getenv("APP_ENV", "development").lower()
    
    if app_env == "production":
        cors_origins = os.getenv(
            "CORS_ORIGINS", 
            "https://jyotiflow.ai,https://www.jyotiflow.ai,https://jyotiflow-ai-frontend.onrender.com"
        ).split(",")
    elif app_env == "staging":
        cors_origins = os.getenv(
            "CORS_ORIGINS",
            "https://staging.jyotiflow.ai,https://dev.jyotiflow.ai,https://jyotiflow-ai-frontend.onrender.com,http://localhost:3000,http://localhost:5173"
        ).split(",")
    else:
        cors_origins = os.getenv(
            "CORS_ORIGINS",
            "http://localhost:3000,http://localhost:5173,http://localhost:8080,http://127.0.0.1:3000,http://127.0.0.1:5173,https://jyotiflow-ai-frontend.onrender.com"
        ).split(",")
    # எப்போதும் frontend deploy domain-ஐ சேர்க்கவும்
    for origin in ALWAYS_ALLOW_ORIGINS:
        if origin not in cors_origins:
            cors_origins.append(origin)
    return [origin.strip() for origin in cors_origins if origin.strip()]

def get_cors_methods():
    """Get allowed CORS methods based on environment"""
    app_env = os.getenv("APP_ENV", "development").lower()
    
    if app_env == "production":
        # Production: Only allow necessary methods
        return ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    else:
        # Development/Staging: Allow all methods for flexibility
        return ["*"]

def get_cors_headers():
    """Get allowed CORS headers based on environment"""
    app_env = os.getenv("APP_ENV", "development").lower()
    
    if app_env == "production":
        # Production: Only allow necessary headers
        return [
            "Accept",
            "Accept-Language",
            "Content-Language",
            "Content-Type",
            "Authorization",
            "X-Requested-With",
            "X-CSRF-Token",
            "Cache-Control"
        ]
    else:
        # Development/Staging: Allow all headers for flexibility
        return ["*"]

# Add CORS middleware with simplified configuration for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Global Exception Handler ---
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions with user-friendly messages"""
    print(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "சேவை தற்காலிகமாக கிடைக்கவில்லை - தயவுசெய்து சிறிது நேரம் கழித்து முயற்சிக்கவும்",
            "error": "Internal server error"
        }
    )

# --- Root Endpoint ---
@app.get("/")
async def root():
    """Root endpoint for JyotiFlow AI Backend"""
    return {
        "message": "🕉️ JyotiFlow AI Backend - Divine Digital Guidance API",
        "status": "active",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "api": "/api/*",
            "docs": "/docs"
        }
    }

# --- Health Check Endpoint ---
@app.get("/health")
async def health_check():
    """Check application health and database connectivity"""
    try:
        # Test database connection
        if db_pool is not None:
            async with db_pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
        else:
            raise Exception("Database pool is not initialized.")
        
        # Get enhanced system status if available
        enhanced_status = {}
        if ENHANCED_ROUTER_AVAILABLE:
            try:
                from enhanced_startup_integration import get_enhancement_status
                enhanced_status = get_enhancement_status()
            except Exception:
                enhanced_status = {"enhanced_system_active": False}
        
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.now().isoformat(),
            "enhanced_features": enhanced_status
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "database": "disconnected",
                "error": str(e)
            }
        )

# --- Sentry Test Endpoint ---
@app.get("/test-sentry")
async def test_sentry():
    """Test endpoint to verify Sentry error tracking is working"""
    try:
        # This will raise an exception to test Sentry integration
        raise Exception("Test backend error for Sentry integration - this should appear in Sentry dashboard")
    except Exception as e:
        # Log the error to Sentry
        sentry_sdk.capture_exception(e)
        
        return JSONResponse(
            status_code=500,
            content={
                "message": "Test error sent to Sentry",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )

# Add API health endpoint for frontend compatibility
@app.get("/api/health")
async def api_health_check():
    """API health check endpoint for frontend compatibility"""
    return await health_check()

# Register routers
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(spiritual.router)
app.include_router(sessions.router)
app.include_router(followup.router)
app.include_router(donations.router)
app.include_router(credits.router)
app.include_router(services.router)
app.include_router(content.router)
app.include_router(ai.router)
app.include_router(community.router)
app.include_router(session_analytics.router)

# Register missing endpoints (avoid duplicates)
try:
    from missing_endpoints import ai_router, user_router as missing_user_router, sessions_router as missing_sessions_router
    app.include_router(ai_router)
    app.include_router(missing_user_router)
    app.include_router(missing_sessions_router)
    # Note: community_router not included to avoid duplicate with community.router above
    print("✅ Missing endpoints registered successfully (excluding duplicate community router)")
except ImportError as e:
    print(f"❌ Failed to register missing endpoints: {e}")

# Admin routers
app.include_router(admin_products.router)
app.include_router(admin_subscriptions.router)
app.include_router(admin_credits.router)
app.include_router(admin_analytics.router)
app.include_router(admin_content.router)
app.include_router(admin_settings.router)
app.include_router(admin_overview.router)
app.include_router(admin_integrations.router)

# Enhanced spiritual guidance router
if ENHANCED_ROUTER_AVAILABLE:
    app.include_router(enhanced_spiritual_router)
    print("✅ Enhanced spiritual guidance router registered")

# Additional enhanced routers
if UNIVERSAL_PRICING_AVAILABLE:
    app.include_router(universal_pricing_router)
    print("✅ Universal pricing router registered")

if AVATAR_GENERATION_AVAILABLE:
    app.include_router(avatar_generation_router)
    print("✅ Avatar generation router registered")

if SOCIAL_MEDIA_AVAILABLE:
    app.include_router(social_marketing_router)
    print("✅ Social media marketing router registered")

if LIVECHAT_AVAILABLE:
    app.include_router(livechat_router)
    print("✅ Live chat router registered")

# Debug router for testing AI Marketing Director
if DEBUG_ROUTER_AVAILABLE:
    app.include_router(debug_router)
    print("✅ Debug router registered")

# Environment debug router for checking environment variables
if ENV_DEBUG_ROUTER_AVAILABLE:
    app.include_router(env_debug_router)
    print("✅ Environment debug router registered")

# Missing endpoints router for 404 fixes
if MISSING_ENDPOINTS_AVAILABLE:
    app.include_router(ai_router)
    app.include_router(missing_user_router)
    app.include_router(sessions_router)
    app.include_router(community_router)
    print("✅ Missing endpoints router registered")

print("🚀 All routers registered successfully!")

# Surgical auth router - REMOVED (conflicting authentication system)
# Using main auth system only (routers/auth.py)
print("⏭️ Surgical auth router disabled - using main auth system only")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)





