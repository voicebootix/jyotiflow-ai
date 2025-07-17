"""
🧪 TEST MONITORING SYSTEM - Verify monitoring is working correctly
Run this after setting up the monitoring system.
"""

import asyncio
import os
import sys
from datetime import datetime, timezone

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set environment variables for testing
# Only set DATABASE_URL if it exists in environment
if not os.getenv("DATABASE_URL"):
    print("⚠️ DATABASE_URL not set - database tests will be skipped")
    os.environ["DATABASE_URL"] = "skip"  # Placeholder to prevent empty string errors
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "test-key")

async def test_monitoring_system():
    """Test the monitoring system components"""
    print("\n🧪 Testing JyotiFlow Monitoring System\n")
    
    results = {
        "database_migration": False,
        "monitoring_import": False,
        "validator_import": False,
        "integration_test": False,
        "dashboard_import": False
    }
    
    # Test 1: Check if database tables exist
    try:
        from core_foundation_enhanced import get_db
        
        db = await get_db()
conn = await db.get_connection()
try:
            # Check validation_sessions table
            table_exists = await db.fetchval("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'validation_sessions'
                )
            """)
            
            if table_exists:
                print("✅ Database tables created successfully")
                results["database_migration"] = True
            else:
                print("❌ Database tables not found - run migration first")
                
    except Exception as e:
        print(f"❌ Database connection error: {e}")
    
    # Test 2: Import monitoring components
    try:
        from monitoring.integration_monitor import integration_monitor, IntegrationPoint
        from monitoring.business_validator import BusinessLogicValidator
        from monitoring.context_tracker import ContextTracker
        print("✅ Core monitoring components imported successfully")
        results["monitoring_import"] = True
    except Exception as e:
        print(f"❌ Failed to import monitoring components: {e}")
    
    # Test 3: Import validators
    try:
        from validators.prokerala_validator import ProkeralaValidator
        from validators.rag_validator import RAGValidator
        from validators.openai_validator import OpenAIValidator
        from validators.social_media_validator import SocialMediaValidator
        print("✅ All validators imported successfully")
        results["validator_import"] = True
    except Exception as e:
        print(f"❌ Failed to import validators: {e}")
    
    # Test 4: Test integration monitoring
    if results["monitoring_import"]:
        try:
            from monitoring.integration_monitor import integration_monitor
            
            # Start a test session
            test_session_id = f"test_{datetime.now(timezone.utc).timestamp()}"
            
            result = await integration_monitor.start_session_monitoring(
                session_id=test_session_id,
                user_id=0,
                birth_details={"date": "1990-01-15", "time": "14:30", "location": "Chennai"},
                spiritual_question="What is my career future?",
                service_type="test"
            )
            
            if result["success"]:
                print("✅ Integration monitoring test passed")
                results["integration_test"] = True
                
                # Clean up test session
                await integration_monitor.complete_session_monitoring(test_session_id)
            else:
                print(f"❌ Integration monitoring test failed: {result}")
                
        except Exception as e:
            print(f"❌ Integration test error: {e}")
    
    # Test 5: Import dashboard
    try:
        from monitoring.dashboard import monitoring_dashboard, router
        print("✅ Monitoring dashboard imported successfully")
        results["dashboard_import"] = True
    except Exception as e:
        print(f"❌ Failed to import dashboard: {e}")
    
    # Summary
    print("\n📊 Test Results Summary:")
    print("=" * 40)
    
    total_tests = len(results)
    passed_tests = sum(1 for v in results.values() if v)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    print("=" * 40)
    print(f"Total: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("\n🎉 All tests passed! Monitoring system is ready.")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
    
    # Test specific validations
    if results["validator_import"]:
        print("\n🔍 Testing specific validators:")
        
        # Test RAG validator
        try:
            from validators.rag_validator import RAGValidator
            validator = RAGValidator()
            
            test_result = await validator.validate(
                input_data={"question": "What is my career future?"},
                output_data={"knowledge": "Career guidance based on astrology..."},
                session_context={"spiritual_question": "What is my career future?"}
            )
            
            print(f"✅ RAG Validator test: relevance score = {test_result.get('overall_relevance', 0):.2f}")
            
        except Exception as e:
            print(f"❌ RAG Validator test error: {e}")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    # Run the test
    success = asyncio.run(test_monitoring_system())
    sys.exit(0 if success else 1)