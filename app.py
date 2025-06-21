# SURGICAL FIX: Just add these 10 lines at the top of your existing app.py
# ==========================================
# SURGICAL IMPORT FIX - தமிழ் तकनीकी समाधान
# ==========================================
# Core utilities - FIXED IMPORT CHAIN
try:
    from app.utils.logger import get_logger, log_request_response
    logger = get_logger(__name__)
    logger.info("✅ Logger imported successfully")
except ImportError:
    # Fallback logger for deployment
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.warning("⚠️ Using fallback logger - utils.logger not available")
    # Create dummy log_request_response function
    async def log_request_response(*args, **kwargs):
        pass

from app.config import settings, get_settings

# ==========================================
# KEEP ALL YOUR EXISTING CODE AFTER THIS
# ==========================================

import os
import sys
import asyncio
import argparse
import logging
from pathlib import Path
from datetime import datetime

# CRITICAL: Add these FastAPI imports FIRST
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# IMMEDIATELY create the app after imports
app = FastAPI(title="JyotiFlow.ai - Swami Jyotirananthan's Digital Ashram")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Continue with your existing code...
templates = Jinja2Templates(directory="templates")

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

# CRITICAL: Initialize app variable FIRST before any decorators
app = None

# =============================================================================
# PART 1: REPLACE THE IMPORT SECTION
# Import enhanced components with proper error handling
try:
    from core_foundation_enhanced import (
        app as enhanced_app, settings, logger, db_manager,
        SpiritualUser, UserPurchase, SpiritualSession, AvatarSession,
        SatsangEvent, SatsangAttendee, MonetizationInsight, SocialContent,
        EnhancedJyotiFlowDatabase, get_current_user, get_admin_user,
        UserRegistration, UserLogin, StandardResponse
    )
    print("✅ Full enhanced core foundation imported successfully")
    app = enhanced_app
    ENHANCED_MODE = True

except ImportError as e:
    print(f"⚠️ Enhanced import failed: {e}")
    print("🔄 Using existing simple app...")

    # If there's already a simple app.py, import from there
    try:
        from app import app as simple_app
        app = simple_app
        print("✅ Using existing simple app")
    except ImportError:
        # Fallback to basic FastAPI
        from fastapi import FastAPI
        from fastapi.middleware.cors import CORSMiddleware

        app = FastAPI(title="JyotiFlow.ai - Basic Mode")
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"]
        )
        print("✅ Created fallback FastAPI app")

    ENHANCED_MODE = False

    # Mount static files
    app.mount("/static", StaticFiles(directory="static"), name="static")

    # Mock settings for fallback
    class MockSettings:
        debug = True
        port = int(os.environ.get("PORT", 8000))
        host = "0.0.0.0"
        app_env = "fallback"

    settings = MockSettings()

# ALL YOUR SOPHISTICATED IMPORTS STAY THE SAME:
# Route imports - Import all revolutionary features
from app.routes.voice_conversation_router import router as voice_conversation_router
from app.routes.business_intelligence_router import router as business_intelligence_router
from app.routes.dream_router import router as dream_router
from app.routes.debug_router import router as debug_router
from app.routes.github_router import router as github_router
from app.routes.smart_contract_router import router as smart_contract_router
from app.routes.contract_method_router import router as contract_method_router
from app.routes.project_router import router as project_router
from app.routes.auth_router import router as auth_router

# Database manager instance
db_manager = None

# ALL YOUR SOPHISTICATED LIFESPAN MANAGEMENT STAYS THE SAME
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("🚀 Starting AI Debugger Factory...")

    global db_manager
    db_manager = DatabaseManager()

    # Initialize database
    try:
        await db_manager.initialize()
        await db_manager.run_migrations()
        logger.info("✅ Database initialized successfully")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise

    # Initialize other services
    try:
        # Initialize LLM providers
        from app.utils.llm_provider import llm_provider
        await llm_provider.initialize()
        logger.info("✅ LLM providers initialized")

        # Initialize voice processor
        from app.utils.voice_processor import voice_processor
        await voice_processor.initialize()
        logger.info("✅ Voice processor initialized")

        # Initialize GitHub integration
        from app.utils.github_integration import github_manager
        await github_manager.initialize()
        logger.info("✅ GitHub integration initialized")

        logger.info("🎉 AI Debugger Factory startup complete!")

    except Exception as e:
        logger.error(f"❌ Service initialization failed: {e}")
        # Continue startup even if some services fail

    yield

    # Shutdown
    logger.info("🛑 Shutting down AI Debugger Factory...")
    if db_manager:
        await db_manager.close()
    logger.info("✅ Shutdown complete")

# ALL YOUR SOPHISTICATED APP CREATION STAYS THE SAME
app = FastAPI(
    title="AI Debugger Factory",
    description="Revolutionary AI-powered development platform that transforms founder conversations into profitable businesses",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)

# ALL YOUR SOPHISTICATED MIDDLEWARE STAYS THE SAME
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"] if settings.DEBUG else settings.ALLOWED_HOSTS
)

# YOUR SOPHISTICATED LOGGING MIDDLEWARE WITH CONDITIONAL CALL
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """Log all requests and responses"""
    start_time = asyncio.get_event_loop().time()

    # Process request
    response = await call_next(request)

    # Calculate processing time
    process_time = asyncio.get_event_loop().time() - start_time

    # Log request/response - CONDITIONALLY CALL BASED ON AVAILABILITY
    try:
        await log_request_response(
            method=request.method,
            url=str(request.url),
            status_code=response.status_code,
            process_time=process_time,
            user_agent=request.headers.get("user-agent"),
            ip_address=request.client.host if request.client else None
        )
    except Exception as e:
        logger.warning(f"Request logging failed: {e}")

    # Add processing time header
    response.headers["X-Process-Time"] = str(process_time)

    return response

# ALL YOUR SOPHISTICATED ERROR HANDLING STAYS THE SAME
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with proper logging"""
    logger.warning(f"HTTP {exc.status_code}: {exc.detail} - {request.method} {request.url}")

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "message": exc.detail,
            "timestamp": asyncio.get_event_loop().time()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    logger.error(f"Unexpected error: {exc}", exc_info=True)

    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "Internal server error" if not settings.DEBUG else str(exc),
            "timestamp": asyncio.get_event_loop().time(),
            "path": str(request.url.path)
        }
    )

# ALL YOUR SOPHISTICATED TEMPLATE AND STATIC FILE HANDLING STAYS THE SAME
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# ALL YOUR SOPHISTICATED API ROUTES STAY THE SAME
API_PREFIX = "/api/v1"

# VoiceBotics AI Cofounder (REVOLUTIONARY - PATENT-WORTHY)
app.include_router(
    voice_conversation_router,
    prefix=f"{API_PREFIX}/voice-conversation",
    tags=["🎤 VoiceBotics AI Cofounder"]
)

# Business Intelligence (INTELLIGENT - OPTIONAL)
app.include_router(
    business_intelligence_router,
    prefix=f"{API_PREFIX}/business-intelligence",
    tags=["🧠 Business Intelligence"]
)

# Layer 1 Build - Dream Engine (CORE GENERATION)
app.include_router(
    dream_router,
    prefix=f"{API_PREFIX}/dreamengine",
    tags=["⚡ Layer 1 Build"]
)

# Layer 2 Debug - Debug Engine (PROFESSIONAL DEBUGGING)
app.include_router(
    debug_router,
    prefix=f"{API_PREFIX}/debug",
    tags=["🔧 Layer 2 Debug"]
)

# GitHub Integration (SEAMLESS WORKFLOW)
app.include_router(
    github_router,
    prefix=f"{API_PREFIX}/github",
    tags=["📤 GitHub Integration"]
)

# Smart Contract Revenue Sharing (PATENT-WORTHY)
app.include_router(
    smart_contract_router,
    prefix=f"{API_PREFIX}/smart-contract",
    tags=["💰 Smart Contract Revenue"]
)

# Contract Method AI Compliance (PATENT-WORTHY)
app.include_router(
    contract_method_router,
    prefix=f"{API_PREFIX}/contract-method",
    tags=["📋 Contract Method Compliance"]
)

# Project Management (CROSS-LAYER COORDINATION)
app.include_router(
    project_router,
    prefix=f"{API_PREFIX}/projects",
    tags=["📁 Project Management"]
)

# Authentication (SECURITY)
app.include_router(
    auth_router,
    prefix=f"{API_PREFIX}/auth",
    tags=["🔐 Authentication"]
)

# ALL YOUR SOPHISTICATED TEMPLATE ROUTES STAY THE SAME
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve main application interface"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Serve login page"""
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Serve user dashboard"""
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/voice-conversation", response_class=HTMLResponse)
async def voice_conversation_page(request: Request):
    """Serve VoiceBotics AI Cofounder interface"""
    return templates.TemplateResponse("voice_conversation.html", {"request": request})

# ALL YOUR SOPHISTICATED HEALTH AND STATUS ENDPOINTS STAY THE SAME
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for Docker and monitoring"""
    try:
        # Test database connection
        db_health = await db_manager.health_check()

        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "environment": settings.ENVIRONMENT,
            "database": db_health["status"],
            "services": {
                "api": "healthy",
                "database": db_health["status"],
                "auth": "healthy"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
        )

@app.get("/api/platform/status")
async def platform_status():
    """Detailed application status"""
    try:
        # Get database stats
        db_stats = {}
        if db_manager:
            db_stats = await db_manager.get_stats()

        return {
            "status": "operational",
            "platform": "AI Debugger Factory",
            "version": "1.0.0",
            "environment": settings.ENVIRONMENT,
            "database": db_stats,
            "services": {
                "voice_conversation": "active",
                "business_intelligence": "active",
                "dream_engine": "active",
                "debug_engine": "active",
                "github_integration": "active",
                "smart_contracts": "active",
                "contract_methods": "active"
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "degraded",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )

# Keep ALL your remaining sophisticated functionality exactly as is!
