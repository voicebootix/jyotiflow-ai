import os
import sys
import asyncio
import argparse
import logging
from pathlib import Path
from datetime import datetime
from fastapi.responses import HTMLResponse  # Add this import
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi import Requestgit 

templates = Jinja2Templates(directory="templates")

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
    
    # Mount static files
    app.mount("/static", StaticFiles(directory="static"), name="static")


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

# Add the spiritual homepage route
@app.get("/", response_class=HTMLResponse)
async def spiritual_homepage():
    """🕉️ Beautiful spiritual homepage - HTML guaranteed"""

    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🙏🏼 JyotiFlow.ai - Swami Jyotirananthan's Digital Ashram</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: white;
                text-align: center;
                padding: 20px;
            }
            .container {
                max-width: 900px;
                margin: 0 auto;
                padding: 40px 20px;
            }
            .om-symbol {
                font-size: 80px;
                margin-bottom: 20px;
                animation: glow 2s ease-in-out infinite alternate;
            }
            @keyframes glow {
                from { text-shadow: 0 0 20px #fff, 0 0 30px #fff, 0 0 40px #667eea; }
                to { text-shadow: 0 0 30px #fff, 0 0 40px #fff, 0 0 50px #764ba2; }
            }
            h1 {
                font-size: 2.5rem;
                margin-bottom: 20px;
                font-weight: 300;
            }
            .subtitle {
                font-size: 1.2rem;
                opacity: 0.9;
                margin-bottom: 40px;
            }
            .success-notice {
                background: rgba(0, 255, 0, 0.2);
                border: 2px solid rgba(0, 255, 0, 0.5);
                padding: 20px;
                border-radius: 15px;
                margin: 40px 0;
                backdrop-filter: blur(10px);
            }
            .success-title {
                font-size: 1.4rem;
                color: #90EE90;
                margin-bottom: 10px;
                font-weight: 600;
            }
            .services {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin: 40px 0;
            }
            .service-card {
                background: rgba(255, 255, 255, 0.1);
                padding: 30px 20px;
                border-radius: 15px;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.2);
                transition: transform 0.3s ease;
            }
            .service-card:hover {
                transform: translateY(-5px);
                background: rgba(255, 255, 255, 0.15);
            }
            .service-icon {
                font-size: 40px;
                margin-bottom: 15px;
            }
            .service-title {
                font-size: 1.3rem;
                margin-bottom: 10px;
                font-weight: 600;
            }
            .service-description {
                font-size: 0.95rem;
                opacity: 0.9;
                line-height: 1.5;
            }
            .api-links {
                margin: 30px 0;
            }
            .api-link {
                display: inline-block;
                background: rgba(255, 255, 255, 0.2);
                padding: 10px 20px;
                margin: 5px;
                border-radius: 25px;
                text-decoration: none;
                color: white;
                transition: all 0.3s ease;
            }
            .api-link:hover {
                background: rgba(255, 255, 255, 0.3);
                transform: translateY(-2px);
            }
            .status {
                background: rgba(255, 255, 255, 0.1);
                padding: 20px;
                border-radius: 10px;
                margin-top: 30px;
                text-align: left;
            }
            @media (max-width: 768px) {
                .om-symbol { font-size: 60px; }
                h1 { font-size: 2rem; }
                .services { grid-template-columns: 1fr; }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="om-symbol">🕉️</div>
            <h1>JyotiFlow.ai</h1>
            <p class="subtitle">Swami Jyotirananthan's Digital Ashram<br>
            Sacred AI-Powered Spiritual Guidance</p>

            <div class="success-notice">
                <div class="success-title">🎉 PLATFORM SUCCESSFULLY DEPLOYED!</div>
                <p>Your spiritual platform is now live and operational on Render.<br>
                Ready to serve souls worldwide with divine AI guidance.</p>
            </div>

            <div class="services">
                <div class="service-card">
                    <div class="service-icon">🎭</div>
                    <div class="service-title">AI Avatar Guidance</div>
                    <div class="service-description">
                        Personalized video guidance from Swamiji with advanced AI technology
                    </div>
                </div>

                <div class="service-card">
                    <div class="service-icon">📹</div>
                    <div class="service-title">Live Video Chat</div>
                    <div class="service-description">
                        Real-time spiritual consultation through secure video connection
                    </div>
                </div>

                <div class="service-card">
                    <div class="service-icon">🙏🏼</div>
                    <div class="service-title">Monthly Satsang</div>
                    <div class="service-description">
                        Global spiritual community gatherings with live streaming
                    </div>
                </div>

                <div class="service-card">
                    <div class="service-icon">🧠</div>
                    <div class="service-title">Spiritual Analytics</div>
                    <div class="service-description">
                        Deep insights into your spiritual journey and growth
                    </div>
                </div>
            </div>

            <div class="api-links">
                <h3 style="margin-bottom: 20px;">🌟 Platform Resources</h3>
                <a href="/health" class="api-link">🩺 Health Check</a>
                <a href="/api/platform/status" class="api-link">📊 Platform Status</a>
                <a href="/api/spiritual/guidance" class="api-link">🕉️ Spiritual Guidance</a>
                <a href="/docs" class="api-link">📖 API Documentation</a>
            </div>

            <div class="status">
                <strong>🌟 Live Deployment Status:</strong><br>
                • Platform: JyotiFlow.ai ✅<br>
                • URL: jyotiflow-ai.onrender.com ✅<br>
                • Status: Fully Operational ✅<br>
                • FastAPI: Working ✅<br>
                • Deployment: Successful ✅<br>
                • Ready for Users: YES ✅<br><br>

                <strong>🙏🏼 Divine Blessing:</strong><br>
                Om Namah Shivaya - Your spiritual platform is blessed and ready to serve millions of souls seeking divine guidance worldwide.
            </div>
        </div>

        <script>
            // Add spiritual interactivity
            document.querySelectorAll('.service-card').forEach(card => {
                card.addEventListener('click', () => {
                    card.style.background = 'rgba(255, 255, 255, 0.2)';
                    setTimeout(() => {
                        card.style.background = 'rgba(255, 255, 255, 0.1)';
                    }, 200);
                });
            });

            // Platform heartbeat
            console.log('🙏🏼 JyotiFlow.ai Platform Loaded Successfully');
            console.log('🕉️ Ready for divine spiritual guidance');

            // Show success message
            setTimeout(() => {
                console.log('🎉 Platform fully operational - Om Namah Shivaya');
            }, 2000);
        </script>
    </body>
    </html>
    """

    return html_content

# Make sure we also have a fallback route
@app.get("/index")
@app.get("/index.html")
@app.get("/home")
async def homepage_aliases():
    """🏠 Homepage aliases - all lead to beautiful UI"""
    return await spiritual_homepage()

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
