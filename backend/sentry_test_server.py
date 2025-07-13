#!/usr/bin/env python3
"""
Simplified FastAPI server for testing Sentry integration with secure configuration
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

# Configure CORS based on environment - EXACTLY MATCHING backend/main.py
def get_cors_origins():
    """Get CORS origins based on environment - matches main.py exactly"""
    app_env = os.getenv("APP_ENV", "development").lower()
    
    if app_env == "production":
        # Production: Only allow specific trusted origins - MATCHES main.py
        cors_origins = os.getenv(
            "CORS_ORIGINS", 
            "https://jyotiflow.ai,https://www.jyotiflow.ai,https://jyotiflow-ai-frontend.onrender.com"
        ).split(",")
    elif app_env == "staging":
        # Staging: Allow staging and development origins - MATCHES main.py
        cors_origins = os.getenv(
            "CORS_ORIGINS",
            "https://staging.jyotiflow.ai,https://dev.jyotiflow.ai,https://jyotiflow-ai-frontend.onrender.com,http://localhost:3000,http://localhost:5173"
        ).split(",")
    else:
        # Development: Allow common development origins - MATCHES main.py
        cors_origins = os.getenv(
            "CORS_ORIGINS",
            "http://localhost:3000,http://localhost:5173,http://localhost:8080,http://127.0.0.1:3000,http://127.0.0.1:5173,https://jyotiflow-ai-frontend.onrender.com"
        ).split(",")
    
    # Clean up any whitespace from split
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

# Add CORS middleware with environment-based configuration
cors_origins = get_cors_origins()
cors_methods = get_cors_methods()

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=cors_methods,
    allow_headers=["*"],  # Headers can remain flexible for API usage
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

@app.get("/test-exception-handler")
async def test_exception_handler():
    """Test endpoint to verify secure error handling without exposing sensitive information"""
    try:
        # Simulate a real error that might contain sensitive information
        sensitive_data = "SECRET_DATABASE_PASSWORD_123"
        internal_path = "/internal/admin/secrets"
        
        # This would normally be a database connection or similar operation
        raise ValueError(f"Database connection failed with credentials: {sensitive_data} at path: {internal_path}")
        
    except Exception as e:
        # Log the full exception details to Sentry for internal tracking
        sentry_sdk.capture_exception(e)
        
        # Return a secure, generic response without exposing sensitive details
        return JSONResponse(
            status_code=500,
            content={
                "message": "An internal server error occurred. Please try again later.",
                "timestamp": datetime.now().isoformat(),
                "error_id": "Please contact support if this issue persists",
                "note": "Full error details have been logged for investigation"
            }
        )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Secure global exception handler that captures errors for Sentry
    without exposing sensitive information to the client
    """
    # Log the full exception details to Sentry for internal tracking
    sentry_sdk.capture_exception(exc)
    
    # Return a generic, user-friendly error message without sensitive details
    return JSONResponse(
        status_code=500,
        content={
            "message": "An internal server error occurred. Please try again later.",
            "timestamp": datetime.now().isoformat(),
            "error_id": "Please contact support if this issue persists"
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)