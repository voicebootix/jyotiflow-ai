"""
📊 REGISTER MONITORING - Adds monitoring router to main app
This file should be imported in main.py to enable monitoring
"""

from fastapi import FastAPI
from .dashboard import router as monitoring_router

def register_monitoring_system(app: FastAPI):
    """Register the monitoring system with the FastAPI app"""
    try:
        # Include monitoring router
        app.include_router(monitoring_router)
        print("✅ Monitoring system registered successfully")
        
        # Add startup event to initialize monitoring
        @app.on_event("startup")
        async def init_monitoring():
            print("🚀 Initializing JyotiFlow monitoring system...")
            # Any initialization logic here
            
        return True
    except Exception as e:
        print(f"❌ Failed to register monitoring system: {e}")
        return False

# Export for easy import
__all__ = ['register_monitoring_system', 'monitoring_router']