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
        print("✅ Monitoring system router registered")
        return True
    except Exception as e:
        print(f"❌ Failed to register monitoring system: {e}")
        return False

async def init_monitoring():
    """Initialize monitoring system - to be called from lifespan"""
    print("🚀 Initializing JyotiFlow monitoring system...")
    # Any initialization logic here
    # This function can be imported and called from main.py's lifespan

# Export for easy import
__all__ = ['register_monitoring_system', 'init_monitoring', 'monitoring_router']