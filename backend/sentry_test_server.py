#!/usr/bin/env python3
"""
Simplified FastAPI server for testing Sentry integration
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import os
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

# Initialize Sentry
sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN", "https://576bf026f026fecadcd12bef7f020e18@o4509655767056384.ingest.us.sentry.io/4509655863132160"),
    environment=os.getenv("APP_ENV", "development"),
    integrations=[
        FastApiIntegration(),
    ],
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
    send_default_pii=True,
)

app = FastAPI(title="Sentry Test API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Sentry Test API is running",
        "timestamp": datetime.now().isoformat(),
        "sentry_enabled": True
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "sentry_configured": True
    }

@app.get("/test-sentry")
async def test_sentry():
    """Test endpoint to verify Sentry error tracking is working"""
    # Log the error to Sentry
    sentry_sdk.capture_exception(Exception("Test backend error for Sentry integration - this should appear in Sentry dashboard"))
    
    return JSONResponse(
        status_code=500,
        content={
            "message": "Test error sent to Sentry",
            "error": "Test backend error for Sentry integration - this should appear in Sentry dashboard",
            "timestamp": datetime.now().isoformat()
        }
    )

@app.get("/test-sentry-message")
async def test_sentry_message():
    """Test endpoint to send a message to Sentry"""
    sentry_sdk.capture_message("Test message from backend - Sentry integration working!")
    
    return {
        "message": "Test message sent to Sentry",
        "timestamp": datetime.now().isoformat()
    }

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler that sends errors to Sentry"""
    sentry_sdk.capture_exception(exc)
    
    return JSONResponse(
        status_code=500,
        content={
            "message": "Internal server error",
            "error": str(exc),
            "path": str(request.url)
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)