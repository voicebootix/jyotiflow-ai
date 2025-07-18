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
    
    # Add base integrations with error handling (compatible with all Sentry SDK versions)
    try:
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        # Try with auto_error parameter first, fallback to no parameters
        try:
            integrations.append(FastApiIntegration(auto_error=True))
        except TypeError:
            # Fallback for newer Sentry SDK versions
            integrations.append(FastApiIntegration())
        print("✅ FastAPI integration loaded")
    except ImportError:
        print("⚠️ FastAPI integration not available")
    
    try:
        from sentry_sdk.integrations.starlette import StarletteIntegration
        # Try with auto_error parameter first, fallback to no parameters
        try:
            integrations.append(StarletteIntegration(auto_error=True))
        except TypeError:
            # Fallback for newer Sentry SDK versions
            integrations.append(StarletteIntegration())
        print("✅ Starlette integration loaded")
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
        print(f"✅ Sentry initialized successfully with {len(integrations)} integrations")
        print(f"📊 Environment: {os.getenv('APP_ENV', 'development')}")
        print(f"📈 Traces sample rate: {traces_sample_rate}")
        print("🎯 Error monitoring active")
    except Exception as e:
        print(f"❌ Failed to initialize Sentry: {e}")
        print("⚠️ Continuing without Sentry - application will run normally")
        print("💡 App will work fine, just no error monitoring")
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

# Monitoring system
try:
    from monitoring.register_monitoring import register_monitoring_system, init_monitoring
    MONITORING_AVAILABLE = True
except ImportError:
    MONITORING_AVAILABLE = False
    print("⚠️ Monitoring system not available")

# Debug router for testing
try:
    from debug_auth_endpoint import debug_router
    DEBUG_ROUTER_AVAILABLE = True
except ImportError:
    DEBUG_ROUTER_AVAILABLE = False
    print("⚠️ Debug router not available")

# Missing endpoints router for 404 fixes
try:
    from missing_endpoints import ai_router, user_router as missing_user_router, sessions_router as missing_sessions_router, community_router
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

# Health monitoring router
try:
    from database_self_healing_system import router as health_router
    HEALTH_ROUTER_AVAILABLE = True
    print("✅ Health monitoring router available")
except ImportError:
    HEALTH_ROUTER_AVAILABLE = False
    print("⚠️ Health monitoring router not available")

# Import database initialization
from init_database import initialize_jyotiflow_database

# Enhanced startup integration and fixes are now consolidated in unified_startup_system.py

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

@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan manager using unified startup system"""
    # Startup operations
    try:
        print("🚀 Starting JyotiFlow.ai backend with unified system...")
        
        # Import and initialize the unified startup system
        from unified_startup_system import initialize_unified_jyotiflow, cleanup_unified_system
        
        # Initialize everything through the unified system
        db_pool = await initialize_unified_jyotiflow()
        
        # Set the pool in the db module for all routers to use
        db.set_db_pool(db_pool)
        
        print("✅ Database connection pool initialized successfully!")
        print("📊 Pool configuration: connections ready for use")
        
        # Initialize monitoring system if available
        if MONITORING_AVAILABLE:
            try:
                await init_monitoring()
                print("✅ Monitoring system initialized")
            except Exception as monitor_error:
                print(f"⚠️ Failed to initialize monitoring: {monitor_error}")
                # Continue running even if monitoring fails
        
        print("✅ Unified JyotiFlow.ai system ready!")
        print("🎯 Ready to serve API requests with all features enabled")
        
    except Exception as e:
        print(f"❌ Backend startup failed: {str(e)}")
        print("🔧 For debugging, check your Render dashboard and environment variables")
        raise
    
    # Yield control to the application (this runs the app)
    yield
    
    # Shutdown operations (cleanup)
    try:
        print("🔄 Shutting down unified system...")
        await cleanup_unified_system()
        print("✅ Unified system shutdown completed")
    except Exception as e:
        print(f"⚠️ Error during unified system cleanup: {str(e)}")

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
    allow_origins=get_cors_origins(),  # Use proper domain-specific origins
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
        from db import get_db_pool
        db_pool = get_db_pool()
        if db_pool is not None:
            async with db_pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
        else:
            raise Exception("Database pool is not initialized.")
        
        # Get unified system status
        unified_status = {}
        try:
            from unified_startup_system import get_unified_system_status
            unified_status = get_unified_system_status()
        except Exception:
            unified_status = {"system_available": False}
        
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.now().isoformat(),
            "unified_system": unified_status
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

# Health monitoring router integration (health monitoring initialization now handled by unified startup)
if HEALTH_ROUTER_AVAILABLE:
    app.include_router(health_router)
    print("✅ Health monitoring router registered - monitoring endpoints available")

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

# Register monitoring system
if MONITORING_AVAILABLE:
    try:
        register_monitoring_system(app)
        print("✅ Monitoring system registered successfully")
    except Exception as e:
        print(f"❌ Failed to register monitoring system: {e}")

# Surgical auth router - REMOVED (conflicting authentication system)
# Using main auth system only (routers/auth.py)
print("⏭️ Surgical auth router disabled - using main auth system only")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)





