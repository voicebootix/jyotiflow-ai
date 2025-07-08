from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import aiosqlite
import os
from datetime import datetime

app = FastAPI(title="JyotiFlow AI", version="1.0.0")

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database path
DB_PATH = "jyotiflow.db"

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "🕉️ Welcome to JyotiFlow AI - Divine Digital Guidance",
        "status": "active",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Check application health"""
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("SELECT 1")
        
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.now().isoformat()
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

@app.get("/api/auth/me")
async def get_current_user():
    """Mock endpoint for current user"""
    return {
        "success": True,
        "user": {
            "id": "demo-user",
            "name": "Demo User",
            "email": "demo@jyotiflow.ai",
            "is_admin": False
        }
    }

@app.post("/api/auth/login")
async def login():
    """Mock login endpoint"""
    return {
        "success": True,
        "message": "Login successful",
        "token": "demo-token",
        "user": {
            "id": "demo-user",
            "name": "Demo User",
            "email": "demo@jyotiflow.ai",
            "is_admin": False
        }
    }

@app.post("/api/auth/register")
async def register():
    """Mock register endpoint"""
    return {
        "success": True,
        "message": "Registration successful",
        "user": {
            "id": "demo-user",
            "name": "Demo User",
            "email": "demo@jyotiflow.ai"
        }
    }

@app.get("/api/spiritual/guidance")
async def get_spiritual_guidance():
    """Mock spiritual guidance endpoint"""
    return {
        "success": True,
        "guidance": "🕉️ Welcome to JyotiFlow. Your spiritual journey begins with mindfulness and compassion. Every challenge is an opportunity for growth.",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/admin/dashboard")
async def admin_dashboard():
    """Mock admin dashboard endpoint"""
    return {
        "success": True,
        "data": {
            "total_users": 150,
            "active_sessions": 12,
            "total_revenue": 5000,
            "pending_approvals": 3
        }
    }

@app.get("/api/credits/packages")
async def get_credit_packages():
    """Mock credit packages endpoint"""
    return {
        "success": True,
        "packages": [
            {
                "id": "basic",
                "name": "Basic Package",
                "credits": 10,
                "price": 299,
                "description": "Perfect for beginners"
            },
            {
                "id": "premium",
                "name": "Premium Package", 
                "credits": 25,
                "price": 599,
                "description": "Advanced spiritual guidance"
            }
        ]
    }

if __name__ == "__main__":
    import uvicorn
    print("🕉️ Starting JyotiFlow AI Backend (SQLite Mode)")
    uvicorn.run(app, host="0.0.0.0", port=8000)