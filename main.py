import os
import sys
import asyncio
import argparse
import logging
from pathlib import Path

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

# তমিল - Import all enhanced artifacts
try:
    # Artifact 1: Enhanced Core Foundation
    from core_foundation_enhanced import (
        EnhancedSettings, 
        EnhancedJyotiFlowDatabase,
        logger
    )
    
    # Artifact 2: Enhanced API Layer  
    from enhanced_api_layer import enhanced_router, original_router
    
    # Artifact 3: Enhanced Business Logic
    from enhanced_business_logic import (
        SpiritualAvatarEngine,
        MonetizationOptimizer,
        SatsangManager,
        SocialContentEngine
    )
    
    # Artifact 4: Enhanced Frontend Integration
    from enhanced_frontend_integration import setup_template_filters
    
    # Artifact 5: Enhanced Production Deployment
    from enhanced_production_deployment import enhanced_app
    
    # Artifact 6: Main Integration Hub
    from main_integration_hub import JyotiFlowIntegrationHub, JyotiFlowRunner
    
    print("✅ All 6 enhanced artifacts imported successfully!")
    
except ImportError as e:
    print(f"❌ Error importing artifacts: {e}")
    print("Please ensure all 6 artifact files are in the same directory as main.py")
    sys.exit(1)

# =============================================================================
# 🌟 MAIN APPLICATION SETUP
# তমিল - প্রধান অ্যাপ্লিকেশন সেটআপ
# =============================================================================

def setup_logging(debug_mode=False):
    """Setup comprehensive logging for the platform"""
    log_level = logging.DEBUG if debug_mode else logging.INFO
    
    # Create logs directory
    Path("logs").mkdir(exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - 🙏🏼 JyotiFlow.ai - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('logs/jyotiflow_complete.log', encoding='utf-8'),
            logging.FileHandler('logs/jyotiflow_error.log', level=logging.ERROR, encoding='utf-8')
        ]
    )
    
    # Set external library log levels
    logging.getLogger('uvicorn').setLevel(logging.INFO)
    logging.getLogger('asyncio').setLevel(logging.WARNING)

def validate_environment():
    """Validate all required environment variables"""
    required_vars = [
        'OPENAI_API_KEY',
        'STRIPE_SECRET_KEY', 
        'JWT_SECRET'
    ]
    
    optional_vars = [
        'D_ID_API_KEY',
        'ELEVENLABS_API_KEY', 
        'AGORA_APP_ID',
        'DATABASE_URL'
    ]
    
    missing_required = []
    missing_optional = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_required.append(var)
    
    for var in optional_vars:
        if not os.getenv(var):
            missing_optional.append(var)
    
    if missing_required:
        print(f"❌ Missing required environment variables: {', '.join(missing_required)}")
        print("Please set these variables in your .env file or environment")
        return False
    
    if missing_optional:
        print(f"⚠️ Missing optional environment variables: {', '.join(missing_optional)}")
        print("Some features may be limited without these variables")
    
    print("✅ Environment validation passed!")
    return True

async def initialize_platform():
    """Initialize the complete JyotiFlow platform"""
    print("\n🕉️ ===== JYOTIFLOW.AI PLATFORM INITIALIZATION =====")
    print("🙏🏼 Swami Jyotirananthan's Digital Ashram")
    print("✨ Version 5.0 - Complete AI Avatar Spiritual Platform")
    print("=" * 60)
    
    try:
        # Create integration hub
        integration_hub = JyotiFlowIntegrationHub()
        
        # Initialize complete platform
        result = await integration_hub.initialize_complete_platform()
        
        print("\n🌟 Platform Initialization Complete!")
        print(f"   Status: {result['status']}")
        print(f"   Startup Time: {result['initialization_duration']}")
        print("\n🎭 Available Features:")
        for feature, status in result['platform_features'].items():
            print(f"   {feature.replace('_', ' ').title()}: {status}")
        
        print(f"\n{result['divine_blessing']}")
        print("=" * 60)
        
        return integration_hub
        
    except Exception as e:
        print(f"❌ Platform initialization failed: {e}")
        raise

def run_development_server():
    """Run the platform in development mode"""
    import uvicorn
    
    settings = EnhancedSettings()
    
    print("🚀 Starting JyotiFlow.ai in DEVELOPMENT mode...")
    print(f"🌐 Server will be available at: http://localhost:{settings.port}")
    print("📝 API Documentation: http://localhost:8000/sacred-docs")
    print("🔄 Auto-reload enabled for development")
    
    uvicorn.run(
        "enhanced_production_deployment:enhanced_app",
        host="0.0.0.0",
        port=settings.port,
        reload=True,
        log_level="debug",
        access_log=True
    )

def run_production_server():
    """Run the platform in production mode"""
    print("🚀 Starting JyotiFlow.ai in PRODUCTION mode...")
    
    runner = JyotiFlowRunner()
    runner.run_production_server()

async def run_test_suite():
    """Run the complete platform test suite"""
    print("🧪 Running JyotiFlow.ai Test Suite...")
    
    try:
        # Import test function from integration hub
        from main_integration_hub import test_complete_platform
        
        # Run comprehensive tests
        test_result = await test_complete_platform()
        
        if test_result:
            print("✅ All tests PASSED! Platform is ready for deployment.")
            return True
        else:
            print("❌ Some tests FAILED! Please check the logs.")
            return False
            
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        return False

def create_sample_env_file():
    """Create a sample .env file for users"""
    env_content = """# 🙏🏼 JyotiFlow.ai Environment Configuration
# Swami Jyotirananthan's Digital Ashram

# =============================================================================
# 🔧 CORE SETTINGS
# =============================================================================
APP_NAME="JyotiFlow.ai Enhanced"
APP_ENV="development"
DEBUG=true
HOST="0.0.0.0"
PORT=8000

# =============================================================================
# 🔐 SECURITY SETTINGS  
# =============================================================================
JWT_SECRET="your-super-secret-jwt-key-change-in-production-om-namah-shivaya"
JWT_ALGORITHM="HS256"
JWT_EXPIRATION_HOURS=168

# =============================================================================
# 🗄️ DATABASE CONFIGURATION
# =============================================================================
DATABASE_URL="sqlite:///./jyotiflow_enhanced.db"
# For PostgreSQL: DATABASE_URL="postgresql://user:password@localhost/jyotiflow"

# =============================================================================
# 👤 ADMIN CONFIGURATION
# =============================================================================
ADMIN_EMAIL="admin@jyotiflow.ai"
ADMIN_PASSWORD="admin123"

# =============================================================================
# 🤖 AI SERVICES
# =============================================================================
OPENAI_API_KEY="your-openai-api-key-here"

# =============================================================================
# 🎭 AVATAR SERVICES
# =============================================================================
D_ID_API_KEY="your-d-id-api-key-here"
D_ID_API_URL="https://api.d-id.com"
ELEVENLABS_API_KEY="your-elevenlabs-api-key-here"
ELEVENLABS_VOICE_ID="your-custom-swamiji-voice-id"

# =============================================================================
# 📹 LIVE VIDEO SERVICES
# =============================================================================
AGORA_APP_ID="your-agora-app-id-here"
AGORA_APP_CERTIFICATE="your-agora-certificate-here"

# =============================================================================
# 💳 PAYMENT PROCESSING
# =============================================================================
STRIPE_SECRET_KEY="your-stripe-secret-key-here"
STRIPE_PUBLIC_KEY="your-stripe-public-key-here"
STRIPE_WEBHOOK_SECRET="your-stripe-webhook-secret-here"

# =============================================================================
# 📊 ANALYTICS & MONITORING
# =============================================================================
PROKERALA_API_KEY="your-prokerala-api-key-here"

# =============================================================================
# 🌐 EXTERNAL INTEGRATIONS
# =============================================================================
SALESCLOSER_API_KEY="your-salescloser-api-key-here"
SALESCLOSER_WEBHOOK_URL="your-salescloser-webhook-url-here"

# =============================================================================
# 📱 SOCIAL MEDIA AUTOMATION
# =============================================================================
INSTAGRAM_ACCESS_TOKEN="your-instagram-token-here"
TWITTER_API_KEY="your-twitter-api-key-here"
LINKEDIN_ACCESS_TOKEN="your-linkedin-token-here"
YOUTUBE_API_KEY="your-youtube-api-key-here"

# =============================================================================
# 🙏🏼 DIVINE BLESSING
# =============================================================================
# Om Namah Shivaya - May divine blessings flow through this platform
"""
    
    with open('.env.sample', 'w') as f:
        f.write(env_content)
    
    print("✅ Sample .env file created: .env.sample")
    print("📝 Copy this to .env and update with your actual API keys")

def main():
    """Main entry point for JyotiFlow.ai platform"""
    parser = argparse.ArgumentParser(description='🙏🏼 JyotiFlow.ai - Complete Spiritual Platform')
    parser.add_argument('--dev', action='store_true', help='Run in development mode')
    parser.add_argument('--test', action='store_true', help='Run test suite')
    parser.add_argument('--create-env', action='store_true', help='Create sample .env file')
    parser.add_argument('--validate-env', action='store_true', help='Validate environment variables')
    
    args = parser.parse_args()
    
    # Handle special commands
    if args.create_env:
        create_sample_env_file()
        return
    
    if args.validate_env:
        validate_environment()
        return
    
    # Setup logging
    setup_logging(debug_mode=args.dev)
    
    # Load environment variables from .env file
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ Environment variables loaded from .env file")
    except ImportError:
        print("⚠️ python-dotenv not installed. Loading environment variables from system.")
    except Exception as e:
        print(f"⚠️ Could not load .env file: {e}")
    
    # Validate environment
    if not validate_environment():
        print("\n💡 Tip: Run 'python main.py --create-env' to create a sample .env file")
        sys.exit(1)
    
    try:
        if args.test:
            # Run test suite
            result = asyncio.run(run_test_suite())
            sys.exit(0 if result else 1)
        
        elif args.dev:
            # Run development server
            run_development_server()
        
        else:
            # Run production server with full platform initialization
            print("🚀 Starting complete JyotiFlow.ai platform...")
            
            # Initialize platform first
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            integration_hub = loop.run_until_complete(initialize_platform())
            
            # Then run production server
            run_production_server()
    
    except KeyboardInterrupt:
        print("\n🙏🏼 Graceful shutdown initiated...")
        logger.info("Platform shutdown by user request")
    
    except Exception as e:
        print(f"\n❌ Critical error: {e}")
        logger.error(f"Critical platform error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()