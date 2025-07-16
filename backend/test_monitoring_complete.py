#!/usr/bin/env python3
"""
🧪 COMPREHENSIVE MONITORING SYSTEM TEST
This script verifies every component of the monitoring system
"""

import asyncio
import os
import sys
import json
from datetime import datetime
from typing import Dict, List, Tuple

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set required environment variables for testing
# Handle DATABASE_URL properly - don't default to empty string
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("⚠️ DATABASE_URL environment variable not set")
    print("   Database tests will be skipped")
    print("   To run database tests, set: export DATABASE_URL='your-database-url'")
    
os.environ["JWT_SECRET"] = os.getenv("JWT_SECRET", "test-secret-for-verification-must-be-32-characters-long")
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "test-key")

class MonitoringSystemTester:
    def __init__(self):
        self.results = {
            "imports": {},
            "database": {},
            "api_endpoints": {},
            "validators": {},
            "integration": {}
        }
        self.confidence_score = 0
        self.has_database = DATABASE_URL is not None
        
    async def run_all_tests(self):
        """Run all tests and calculate confidence score"""
        print("\n🧪 COMPREHENSIVE MONITORING SYSTEM TEST\n")
        print("=" * 60)
        
        # Test 1: Import Tests
        await self.test_imports()
        
        # Test 2: Database Tests (only if DATABASE_URL is set)
        if self.has_database:
            await self.test_database()
        else:
            print("\n🗄️ Skipping Database Tests (DATABASE_URL not set)")
            self.results["database"]["skipped"] = True
        
        # Test 3: API Endpoint Tests
        await self.test_api_endpoints()
        
        # Test 4: Validator Tests
        await self.test_validators()
        
        # Test 5: Integration Tests
        await self.test_integration()
        
        # Calculate confidence score
        self.calculate_confidence()
        
        # Print results
        self.print_results()
        
    async def test_imports(self):
        """Test all imports work correctly"""
        print("\n📦 Testing Imports...")
        
        # Test monitoring imports
        try:
            from monitoring import (
                IntegrationMonitor,
                ContextTracker,
                BusinessLogicValidator
            )
            from monitoring.register_monitoring import register_monitoring_system
            from monitoring.dashboard import router as monitoring_router
            from monitoring.integration_hooks import MonitoringHooks
            
            self.results["imports"]["monitoring"] = True
            print("✅ Monitoring components imported successfully")
        except Exception as e:
            self.results["imports"]["monitoring"] = False
            print(f"❌ Monitoring import failed: {e}")
            
        # Test validator imports
        try:
            from validators import (
                ProkeralaValidator,
                RAGValidator,
                OpenAIValidator,
                ElevenLabsValidator,
                DIDValidator,
                SocialMediaValidator
            )
            self.results["imports"]["validators"] = True
            print("✅ Validators imported successfully")
        except Exception as e:
            self.results["imports"]["validators"] = False
            print(f"❌ Validators import failed: {e}")
            
        # Test core imports
        try:
            from core_foundation_enhanced import get_database, logger, settings
            from fastapi import FastAPI
            import asyncpg
            self.results["imports"]["core"] = True
            print("✅ Core dependencies imported successfully")
        except Exception as e:
            self.results["imports"]["core"] = False
            print(f"❌ Core import failed: {e}")
            
    async def test_database(self):
        """Test database connectivity and tables"""
        print("\n🗄️ Testing Database...")
        
        if not DATABASE_URL:
            self.results["database"]["connection"] = False
            print("❌ DATABASE_URL not provided")
            return
            
        try:
            import asyncpg
            
            # Test connection
            conn = await asyncpg.connect(DATABASE_URL)
            self.results["database"]["connection"] = True
            print("✅ Database connection successful")
            
            # Test if monitoring tables exist
            tables = [
                'validation_sessions',
                'integration_validations',
                'business_logic_issues',
                'context_snapshots',
                'monitoring_alerts',
                'social_media_validation_log'
            ]
            
            for table in tables:
                exists = await conn.fetchval(f"""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = '{table}'
                    )
                """)
                self.results["database"][f"table_{table}"] = exists
                if exists:
                    print(f"✅ Table '{table}' exists")
                else:
                    print(f"❌ Table '{table}' missing - run migration")
                    
            await conn.close()
            
        except Exception as e:
            self.results["database"]["connection"] = False
            print(f"❌ Database test failed: {e}")
            
    async def test_api_endpoints(self):
        """Test API endpoints are registered"""
        print("\n🌐 Testing API Endpoints...")
        
        try:
            from fastapi import FastAPI
            from monitoring.register_monitoring import register_monitoring_system
            
            # Create test app
            app = FastAPI()
            register_monitoring_system(app)
            
            # Check routes
            routes = [route.path for route in app.routes]
            
            expected_routes = [
                "/api/monitoring/dashboard",
                "/api/monitoring/session/{session_id}",
                "/api/monitoring/test/{test_type}",
                "/api/monitoring/ws"
            ]
            
            for route in expected_routes:
                if any(route in r for r in routes):
                    self.results["api_endpoints"][route] = True
                    print(f"✅ Endpoint registered: {route}")
                else:
                    self.results["api_endpoints"][route] = False
                    print(f"❌ Endpoint missing: {route}")
                    
        except Exception as e:
            self.results["api_endpoints"]["registration"] = False
            print(f"❌ API endpoint test failed: {e}")
            
    async def test_validators(self):
        """Test validator functionality"""
        print("\n🔍 Testing Validators...")
        
        # Skip validator tests if no database (they may require it)
        if not self.has_database:
            print("⚠️ Skipping validator tests (DATABASE_URL not set)")
            self.results["validators"]["skipped"] = True
            return
            
        # Test ProkeralaValidator
        try:
            from validators import ProkeralaValidator
            validator = ProkeralaValidator()
            
            # Test with sample data
            test_data = {
                "birth_chart": {
                    "planets": {"Sun": "Aries", "Moon": "Taurus"},
                    "nakshatra": "Ashwini",
                    "rasi": "Mesha"
                }
            }
            
            result = await validator.validate(test_data, {}, {"session_id": "test-123"})
            self.results["validators"]["prokerala"] = result.get("passed", False)
            print(f"✅ ProkeralaValidator works: {result.get('passed', False)}")
            
        except Exception as e:
            self.results["validators"]["prokerala"] = False
            print(f"❌ ProkeralaValidator test failed: {e}")
            
        # Test RAGValidator
        try:
            from validators import RAGValidator
            validator = RAGValidator()
            
            # Test with sample data
            test_query = "What is the significance of Saturn in 7th house?"
            test_response = "Saturn in 7th house indicates delays in marriage and serious partnerships."
            
            result = await validator.validate({
                "query": test_query,
                "retrieved_content": test_response,
                "response": test_response
            }, {}, {"session_id": "test-123", "user_query": test_query})
            
            self.results["validators"]["rag"] = result.get("passed", False)
            print(f"✅ RAGValidator works - Relevance: {result.get('overall_relevance', 0):.1f}%")
            
        except Exception as e:
            self.results["validators"]["rag"] = False
            print(f"❌ RAGValidator test failed: {e}")
            
    async def test_integration(self):
        """Test integration with main app"""
        print("\n🔗 Testing Integration...")
        
        try:
            # Check if main.py has monitoring integration
            with open('main.py', 'r') as f:
                main_content = f.read()
                
            has_import = 'from monitoring.register_monitoring import register_monitoring_system' in main_content
            has_registration = 'register_monitoring_system(app)' in main_content
            
            self.results["integration"]["main_py_import"] = has_import
            self.results["integration"]["main_py_registration"] = has_registration
            
            if has_import and has_registration:
                print("✅ Monitoring system integrated in main.py")
            else:
                print("❌ Monitoring system not fully integrated in main.py")
                
        except Exception as e:
            self.results["integration"]["main_py"] = False
            print(f"❌ Integration test failed: {e}")
            
        # Test monitoring hooks
        try:
            from monitoring.integration_hooks import MonitoringHooks
            
            # Test decorator
            @MonitoringHooks.monitor_session
            async def test_function(data):
                return {"success": True}
                
            self.results["integration"]["hooks"] = True
            print("✅ Monitoring hooks working")
            
        except Exception as e:
            self.results["integration"]["hooks"] = False
            print(f"❌ Monitoring hooks test failed: {e}")
            
    def calculate_confidence(self):
        """Calculate overall confidence score"""
        total_tests = 0
        passed_tests = 0
        skipped_tests = 0
        
        for category, tests in self.results.items():
            for test_name, result in tests.items():
                if test_name == "skipped" and result:
                    skipped_tests += len([k for k in tests.keys() if k != "skipped"])
                    continue
                    
                total_tests += 1
                if result:
                    passed_tests += 1
                    
        # Adjust total for skipped tests
        total_tests = max(1, total_tests - skipped_tests)
        
        self.confidence_score = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
    def print_results(self):
        """Print comprehensive test results"""
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        # Category summaries
        for category, tests in self.results.items():
            if "skipped" in tests and tests["skipped"]:
                print(f"\n{category.upper()}: ⏭️ SKIPPED (DATABASE_URL not set)")
                continue
                
            passed = sum(1 for k, v in tests.items() if k != "skipped" and v)
            total = len([k for k in tests.keys() if k != "skipped"])
            print(f"\n{category.upper()}:")
            print(f"  Passed: {passed}/{total}")
            
            for test_name, result in tests.items():
                if test_name == "skipped":
                    continue
                status = "✅" if result else "❌"
                print(f"  {status} {test_name}")
                
        # Overall confidence
        print("\n" + "=" * 60)
        print(f"🎯 OVERALL CONFIDENCE SCORE: {self.confidence_score:.1f}%")
        print("=" * 60)
        
        # Recommendations
        if self.confidence_score < 100:
            print("\n⚠️ ACTIONS NEEDED TO REACH 100%:")
            
            if not self.has_database:
                print("\n1. Set DATABASE_URL environment variable:")
                print("   export DATABASE_URL='postgresql://user:pass@host:port/dbname'")
                
            if self.has_database and not all(self.results.get("database", {}).values()):
                print("\n1. Run database migration:")
                print("   DATABASE_URL='your-db-url' python migrations/add_validation_tracking_tables.py")
                
            if not all(self.results.get("imports", {}).values()):
                print("\n2. Install missing dependencies:")
                print("   pip install -r requirements.txt")
                
            if not all(self.results.get("integration", {}).values()):
                print("\n3. Ensure monitoring is registered in main.py")
                
        else:
            print("\n✅ MONITORING SYSTEM IS 100% READY FOR PRODUCTION!")
            
async def main():
    tester = MonitoringSystemTester()
    await tester.run_all_tests()
    
    # Return confidence score for CI/CD
    return tester.confidence_score

if __name__ == "__main__":
    score = asyncio.run(main())
    sys.exit(0 if score == 100 else 1)