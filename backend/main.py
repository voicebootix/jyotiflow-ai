import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add backend directory to path
sys.path.append(str(Path(__file__).parent))

# Import routers
from routers import (
    admin_products, admin_subscriptions, admin_credits,
    admin_analytics, admin_content, admin_settings,
    auth, user
)

# Create FastAPI app
app = FastAPI(
    title="JyotiFlow.ai Admin API",
    description="Spiritual AI Platform Admin Dashboard API",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(admin_products.router, prefix="/api/admin")
app.include_router(admin_subscriptions.router, prefix="/api/admin")
app.include_router(admin_credits.router, prefix="/api/admin")
app.include_router(admin_analytics.router, prefix="/api/admin")
app.include_router(admin_content.router, prefix="/api/admin")
app.include_router(admin_settings.router, prefix="/api/admin")
app.include_router(auth.router)
app.include_router(user.router)

@app.get("/")
async def root():
    return {"message": "🕉️ JyotiFlow.ai Admin API - Spiritual Intelligence Platform"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Admin API is running"}





