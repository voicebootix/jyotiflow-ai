from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import asyncpg
from datetime import datetime
import os
import asyncio

# Import routers
from routers import auth, user, spiritual, sessions, followup, donations, credits, services
from routers import admin_products, admin_subscriptions, admin_credits, admin_analytics, admin_content, admin_settings
from routers import content
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

try:
    from surgical_frontend_auth_fix import surgical_auth_router
    SURGICAL_AUTH_AVAILABLE = True
except ImportError:
    SURGICAL_AUTH_AVAILABLE = False
    print("⚠️ Surgical auth router not available")

# Debug router for testing
try:
    from debug_auth_endpoint import debug_router
    DEBUG_ROUTER_AVAILABLE = True
except ImportError:
    DEBUG_ROUTER_AVAILABLE = False
    print("⚠️ Debug router not available")

# Import database initialization
from init_database import initialize_jyotiflow_database

# Import enhanced startup integration
from enhanced_startup_integration import initialize_enhanced_jyotiflow

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
        await apply_migrations()
        
        # Initialize database connection pool
        global db_pool
        db_pool = await asyncpg.create_pool(
            DATABASE_URL,
            min_size=5,
            max_size=20,
            command_timeout=60
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
        
        # Ensure base credits column exists
        try:
            await ensure_base_credits_column()
            print("✅ Base credits column check completed")
        except Exception as e:
            print(f"⚠️ Base credits column check failed: {e}")
        
        # Apply database schema fixes
        try:
            print("🔧 Applying database schema fixes...")
            schema_fix_success = await fix_database_schema()
            if schema_fix_success:
                print("✅ Database schema fixes applied successfully")
            else:
                print("⚠️ Database schema fixes had issues but will continue")
        except Exception as e:
            print(f"⚠️ Database schema fix failed: {e}")
        
        # Initialize database with comprehensive reset (ONE-SHOT SOLUTION)
        try:
            print("🚀 Starting comprehensive database reset...")
            from comprehensive_database_reset import ComprehensiveDatabaseReset
            reset = ComprehensiveDatabaseReset()
            await reset.execute_reset()
            print("✅ Comprehensive database reset completed - ALL TABLES CREATED!")
        except Exception as e:
            print(f"❌ Comprehensive reset failed: {e}")
            # Fallback to original initialization
            try:
                print("🔄 Falling back to original database initialization...")
                success = await initialize_jyotiflow_database()
                if success:
                    print("✅ Fallback database initialization completed")
                else:
                    print("⚠️ Fallback initialization had issues but will continue")
            except Exception as fallback_error:
                print(f"⚠️ Fallback initialization also failed: {fallback_error}")
        
        # Surgical fix for admin user authentication
        try:
            print("🔧 Applying surgical admin authentication fix...")
            from surgical_admin_auth_fix import surgical_admin_auth_fix
            admin_auth_success = await surgical_admin_auth_fix()
            if admin_auth_success:
                print("✅ Surgical admin authentication fix completed successfully")
            else:
                print("⚠️ Surgical admin authentication fix had issues but will continue")
        except Exception as e:
            print(f"⚠️ Surgical admin authentication fix failed: {e}")
        
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
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://jyotiflow-ai-frontend.onrender.com",
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
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

# Admin routers
app.include_router(admin_products.router)
app.include_router(admin_subscriptions.router)
app.include_router(admin_credits.router)
app.include_router(admin_analytics.router)
app.include_router(admin_content.router)
app.include_router(admin_settings.router)

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

# Surgical auth router for frontend authentication fix
if SURGICAL_AUTH_AVAILABLE:
    app.include_router(surgical_auth_router)
    print("✅ Surgical auth router registered")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)





