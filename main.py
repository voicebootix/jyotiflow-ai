import os
import sys
import asyncio
import argparse
import logging
from pathlib import Path
from datetime import datetime

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

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

    # Use the enhanced app instead of creating a new one
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

    # Mock settings for fallback
    class MockSettings:
        debug = True
        port = int(os.environ.get("PORT", 8000))
        host = "0.0.0.0"
        app_env = "fallback"

    settings = MockSettings()

# =============================================================================
# PART 2: ADD AFTER THE IMPORT SECTION
if ENHANCED_MODE:
    # Enhanced routes are already included with the enhanced_app
    print("🌟 Enhanced routes active - Full JyotiFlow.ai functionality available")

    @app.get("/api/platform/status")
    async def enhanced_platform_status():
        """Enhanced platform status with full feature list"""
        return {
            "success": True,
            "platform": "JyotiFlow.ai - Enhanced Mode",
            "mode": "full_featured",
            "features": {
                "avatar_guidance": "✅ Available",
                "live_video_chat": "✅ Available",
                "monthly_satsang": "✅ Available",
                "ai_business_intelligence": "✅ Available",
                "social_automation": "✅ Available",
                "admin_dashboard": "✅ Available"
            },
            "services": {
                "clarity_plus": {"price": 9, "credits": 1},
                "astrolove_whisper": {"price": 19, "credits": 3},
                "r3_live_premium": {"price": 39, "credits": 6},
                "daily_astrocoach": {"price": 149, "credits": 12}
            },
            "blessing": "🙏🏼 Full digital ashram operational"
        }
else:
    # Keep existing simple routes if they exist
    print("⚡ Simple mode active - Basic functionality")

    @app.get("/api/platform/status")
    async def simple_platform_status():
        """Simple platform status"""
        return {
            "success": True,
            "platform": "JyotiFlow.ai - Simple Mode",
            "mode": "basic",
            "message": "Platform deployed successfully, enhanced features loading...",
            "blessing": "🙏🏼 Basic ashram operational"
        }

# Import other modules with fallbacks
try:
    from enhanced_business_logic import (
        SpiritualAvatarEngine,
        MonetizationOptimizer,
        SatsangManager,
        SocialContentEngine
    )
    print("✅ Business logic imported")
except ImportError as e:
    print(f"⚠️ Business logic import issue: {e}")
    # Create placeholder classes
    class SpiritualAvatarEngine:
        pass
    class MonetizationOptimizer:
        pass
    class SatsangManager:
        pass
    class SocialContentEngine:
        pass

try:
    from enhanced_production_deployment import enhanced_app
    print("✅ Production app imported")
except ImportError as e:
    print(f"⚠️ Production app import issue: {e}")
    # Use fallback app
    enhanced_app = app

try:
    from main_integration_hub import JyotiFlowIntegrationHub, JyotiFlowRunner
    print("✅ Integration hub imported")
except ImportError as e:
    print(f"⚠️ Integration hub import issue: {e}")
    # Create basic classes
    class JyotiFlowIntegrationHub:
        async def initialize_complete_platform(self):
            return {"status": "basic_mode"}

    class JyotiFlowRunner:
        def run_production_server(self):
            import uvicorn
            uvicorn.run(enhanced_app, host="0.0.0.0", port=settings.port)

print("✅ All imports handled successfully!")

# =============================================================================
# 🌟 MAIN APPLICATION SETUP
# =============================================================================

def validate_environment():
    """Validate environment variables"""
    required_vars = ['OPENAI_API_KEY', 'STRIPE_SECRET_KEY', 'JWT_SECRET']
    missing = [var for var in required_vars if not os.getenv(var)]

    if missing:
        print(f"❌ Missing environment variables: {', '.join(missing)}")
        print("💡 Create .env file with these variables")
        return False

    print("✅ Environment validation passed!")
    return True

def create_sample_env():
    """Create sample .env file"""
    env_content = '''# 🙏🏼 JyotiFlow.ai Environment Configuration

# Required Settings
OPENAI_API_KEY=sk-your-openai-key-here
STRIPE_SECRET_KEY=sk_test_your-stripe-key
JWT_SECRET=your-super-secret-jwt-key-om-namah-shivaya

# Optional Avatar Services
D_ID_API_KEY=your-d-id-api-key
ELEVENLABS_API_KEY=your-elevenlabs-api-key
AGORA_APP_ID=your-agora-app-id

# Database
DATABASE_URL=sqlite:///./jyotiflow_enhanced.db

# Admin
ADMIN_EMAIL=admin@jyotiflow.ai
ADMIN_PASSWORD=your-secure-admin-password
'''

    with open('.env.sample', 'w') as f:
        f.write(env_content)
    print("✅ Sample .env file created: .env.sample")

async def initialize_platform():
    """Initialize the platform"""
    print("\n🕉️ ===== JYOTIFLOW.AI PLATFORM INITIALIZATION =====")
    print("🙏🏼 Swami Jyotirananthan's Digital Ashram")
    print("✨ Version 5.0 - Enhanced Spiritual Platform")
    print("=" * 60)

    try:
        integration_hub = JyotiFlowIntegrationHub()
        result = await integration_hub.initialize_complete_platform()

        print("\n🌟 Platform Initialization Complete!")
        print(f"   Status: {result.get('status', 'operational')}")
        print("\n🙏🏼 Digital ashram ready to serve souls worldwide")
        print("=" * 60)

        return integration_hub

    except Exception as e:
        print(f"❌ Platform initialization failed: {e}")
        print("⚠️ Running in basic mode...")
        return None

def run_development_server():
    """Run development server"""
    import uvicorn

    print("🚀 Starting JyotiFlow.ai in DEVELOPMENT mode...")
    print(f"🌐 Server: http://localhost:{settings.port}")

    uvicorn.run(
        enhanced_app,
        host="0.0.0.0",
        port=settings.port,
        reload=True,
        log_level="info"
    )

def run_production_server():
    """Run production server"""
    runner = JyotiFlowRunner()
    runner.run_production_server()

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='🙏🏼 JyotiFlow.ai Platform')
    parser.add_argument('--dev', action='store_true', help='Run in development mode')
    parser.add_argument('--create-env', action='store_true', help='Create sample .env file')
    parser.add_argument('--validate-env', action='store_true', help='Validate environment')

    args = parser.parse_args()

    # Handle special commands
    if args.create_env:
        create_sample_env()
        return

    if args.validate_env:
        validate_environment()
        return

    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ Environment variables loaded")
    except ImportError:
        print("⚠️ python-dotenv not installed")
    except Exception as e:
        print(f"⚠️ Could not load .env file: {e}")

    # Validate environment
    if not validate_environment():
        print("\n💡 Tip: Run 'python main.py --create-env' to create .env file")
        print("💡 Then copy .env.sample to .env and update with your API keys")
        return

    try:
        if args.dev:
            # Run development server
            run_development_server()
        else:
            # Run production server
            print("🚀 Starting JyotiFlow.ai platform...")

            # Initialize platform
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            integration_hub = loop.run_until_complete(initialize_platform())

            # Start server
            run_production_server()

    except KeyboardInterrupt:
        print("\n🙏🏼 Graceful shutdown...")
        if ENHANCED_MODE:
            logger.info("Platform shutdown by user")

    except Exception as e:
        print(f"\n❌ Critical error: {e}")
        if ENHANCED_MODE:
            logger.error(f"Critical error: {e}")
        sys.exit(1)

if __name__ != "__main__":
    app = enhanced_app  # Export for Render deployment
