"""
🧪 AI Marketing Director Agent Diagnostic Test
Test script to diagnose why the AI agent isn't responding properly
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.append('.')

async def test_ai_agent_imports():
    """Test if we can import the AI agent properly"""
    print("🔍 Testing AI Marketing Director Agent imports...")
    
    try:
        # Test core imports first
        print("1. Testing core_foundation_enhanced import...")
        from core_foundation_enhanced import settings, db_manager, logger
        print("   ✅ Core foundation imports working")
        
        # Test enhanced business logic import
        print("2. Testing enhanced_business_logic import...")
        from enhanced_business_logic import SpiritualAvatarEngine, TamilCulturalIntegration
        print("   ✅ Enhanced business logic imports working")
        
        # Test social media automation import
        print("3. Testing social_media_marketing_automation import...")
        from social_media_marketing_automation import SocialMediaMarketingEngine
        print("   ✅ Social media automation imports working")
        
        # Test AI agent import
        print("4. Testing ai_marketing_director_agent import...")
        from ai_marketing_director_agent import ai_marketing_director
        print("   ✅ AI Marketing Director Agent imported successfully")
        
        return True, ai_marketing_director
        
    except Exception as e:
        print(f"   ❌ Import failed: {e}")
        return False, None

async def test_ai_agent_initialization(agent):
    """Test if the AI agent is properly initialized"""
    print("\n🔧 Testing AI agent initialization...")
    
    try:
        # Check if agent has required attributes
        required_attrs = ['openai_client', 'social_engine', 'avatar_engine', 'cultural_integration']
        
        for attr in required_attrs:
            if hasattr(agent, attr):
                print(f"   ✅ {attr}: Available")
            else:
                print(f"   ❌ {attr}: Missing")
        
        # Test if OpenAI client is working
        if hasattr(agent, 'openai_client'):
            print(f"   📱 OpenAI client type: {type(agent.openai_client)}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Initialization check failed: {e}")
        return False

async def test_ai_agent_response(agent):
    """Test if the AI agent can respond to basic commands"""
    print("\n💬 Testing AI agent responses...")
    
    test_messages = [
        "help",
        "show market analysis",
        "generate content plan",
        "show performance report"
    ]
    
    for message in test_messages:
        try:
            print(f"\n📨 Testing message: '{message}'")
            response = await agent.handle_instruction(message)
            
            if response and isinstance(response, dict):
                reply = response.get('reply', 'No reply field')
                print(f"   ✅ Response received: {reply[:100]}...")
            else:
                print(f"   ❌ Invalid response format: {response}")
                
        except Exception as e:
            print(f"   ❌ Response failed: {e}")

async def test_missing_openai_key():
    """Test if OpenAI API key is configured"""
    print("\n🔑 Testing OpenAI API key configuration...")
    
    try:
        from core_foundation_enhanced import settings
        
        openai_key = settings.openai_api_key
        if openai_key and openai_key != "your-openai-api-key":
            print(f"   ✅ OpenAI API key configured: {openai_key[:10]}...")
            return True
        else:
            print(f"   ❌ OpenAI API key not configured or is default value")
            return False
            
    except Exception as e:
        print(f"   ❌ API key check failed: {e}")
        return False

async def test_database_connection():
    """Test if database connection is working"""
    print("\n🗄️ Testing database connection...")
    
    try:
        from core_foundation_enhanced import db_manager
        
        # Test database connection
        health = await db_manager.health_check()
        
        if health.get('status') == 'healthy':
            print(f"   ✅ Database connection: {health}")
            return True
        else:
            print(f"   ❌ Database connection unhealthy: {health}")
            return False
            
    except Exception as e:
        print(f"   ❌ Database connection test failed: {e}")
        return False

async def fix_ai_agent_response():
    """Provide fixes for common AI agent issues"""
    print("\n🔧 RECOMMENDED FIXES:")
    
    # Check OpenAI key
    openai_working = await test_missing_openai_key()
    if not openai_working:
        print("\n❌ ISSUE: OpenAI API key not configured")
        print("   FIX: Set OPENAI_API_KEY environment variable")
        print("   Example: export OPENAI_API_KEY='sk-your-actual-key'")
    
    # Check database
    db_working = await test_database_connection()
    if not db_working:
        print("\n❌ ISSUE: Database connection not working")
        print("   FIX: Ensure DATABASE_URL is set and database is running")
    
    # Check imports
    import_working, agent = await test_ai_agent_imports()
    if not import_working:
        print("\n❌ ISSUE: Module imports failing")
        print("   FIX: Check if all required modules are installed")
        print("   Run: pip install -r requirements.txt")
    
    if import_working and agent:
        initialization_working = await test_ai_agent_initialization(agent)
        if initialization_working:
            await test_ai_agent_response(agent)

async def main():
    """Main diagnostic function"""
    print("🚀 AI Marketing Director Agent Diagnostic Tool")
    print("=" * 60)
    
    await fix_ai_agent_response()
    
    print("\n" + "=" * 60)
    print("🎯 SUMMARY:")
    print("If you see ❌ issues above, fix them and the AI agent will work!")
    print("If all ✅ checks pass, the AI agent should be responding normally.")

if __name__ == "__main__":
    asyncio.run(main())