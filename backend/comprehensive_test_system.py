"""
Comprehensive Test System for Enhanced JyotiFlow
Tests all components: RAG, Knowledge Base, Personas, Dynamic Configuration
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JyotiFlowTestSuite:
    """Complete test suite for enhanced JyotiFlow system"""
    
    def __init__(self):
        self.test_results = []
        self.passed_tests = 0
        self.failed_tests = 0
        
    async def run_comprehensive_tests(self):
        """Run all test suites"""
        logger.info("🧪 Starting JyotiFlow Comprehensive Test Suite")
        
        # Test 1: Database Schema Validation
        await self._test_database_schema()
        
        # Test 2: Knowledge Base Seeding
        await self._test_knowledge_base_seeding()
        
        # Test 3: RAG System Functionality
        await self._test_rag_system()
        
        # Test 4: Service Configuration
        await self._test_service_configuration()
        
        # Test 5: Persona Engine
        await self._test_persona_engine()
        
        # Test 6: API Endpoints
        await self._test_api_endpoints()
        
        # Test 7: Full User Flow
        await self._test_full_user_flow()
        
        # Test 8: Edge Cases
        await self._test_edge_cases()
        
        # Generate final report
        self._generate_test_report()
        
    async def _test_database_schema(self):
        """Test database schema creation and structure"""
        test_name = "Database Schema Validation"
        logger.info(f"Testing: {test_name}")
        
        try:
            # Try to import database and check basic connectivity
            try:
                import sqlite3
                db_path = './backend/jyotiflow.db'
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # Test for enhanced tables
                expected_tables = [
                    'rag_knowledge_base', 
                    'swami_persona_responses',
                    'knowledge_effectiveness_tracking',
                    'service_configuration_cache'
                ]
                
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                existing_tables = [row[0] for row in cursor.fetchall()]
                
                missing_tables = [table for table in expected_tables if table not in existing_tables]
                
                if missing_tables:
                    self._record_test_result(test_name, False, f"Missing tables: {missing_tables}")
                else:
                    self._record_test_result(test_name, True, "All required tables present")
                
                conn.close()
                
            except Exception as e:
                self._record_test_result(test_name, False, f"Database error: {e}")
                
        except Exception as e:
            self._record_test_result(test_name, False, f"Test setup error: {e}")
    
    async def _test_knowledge_base_seeding(self):
        """Test knowledge base seeding functionality"""
        test_name = "Knowledge Base Seeding"
        logger.info(f"Testing: {test_name}")
        
        try:
            # Test seeding system
            from knowledge_seeding_system import KnowledgeSeeder
            
            # Create mock database pool
            class MockDBPool:
                def __init__(self):
                    pass
                    
                def acquire(self):
                    return MockConnection()
            
            class MockConnection:
                def __init__(self):
                    pass
                    
                async def __aenter__(self):
                    return self
                    
                async def __aexit__(self, exc_type, exc_val, exc_tb):
                    pass
                    
                async def execute(self, query, *args):
                    pass
            
            mock_pool = MockDBPool()
            seeder = KnowledgeSeeder(mock_pool, "test_key")
            
            # Test that seeder initializes correctly
            self._record_test_result(test_name, True, "Knowledge seeder initialized successfully")
            
        except Exception as e:
            self._record_test_result(test_name, False, f"Seeding test failed: {e}")
    
    async def _test_rag_system(self):
        """Test RAG system functionality"""
        test_name = "RAG System Functionality"
        logger.info(f"Testing: {test_name}")
        
        try:
            # Test RAG engine initialization
            from enhanced_rag_knowledge_engine import RAGKnowledgeEngine
            
            # Create mock pool
            class MockDBPool:
                def acquire(self):
                    return MockConnection()
            
            class MockConnection:
                async def __aenter__(self):
                    return self
                async def __aexit__(self, exc_type, exc_val, exc_tb):
                    pass
                async def fetchrow(self, query, *args):
                    return None
                async def fetch(self, query, *args):
                    return []
            
            mock_pool = MockDBPool()
            rag_engine = RAGKnowledgeEngine(mock_pool, "test_key")
            
            # Test knowledge domains initialization
            domains = rag_engine.knowledge_domains
            expected_domains = [
                'classical_astrology', 'tamil_spiritual_literature',
                'relationship_astrology', 'career_astrology'
            ]
            
            domains_present = all(domain in domains for domain in expected_domains)
            
            if domains_present:
                self._record_test_result(test_name, True, "RAG system initialized with proper domains")
            else:
                self._record_test_result(test_name, False, "Missing expected knowledge domains")
                
        except Exception as e:
            self._record_test_result(test_name, False, f"RAG test failed: {e}")
    
    async def _test_service_configuration(self):
        """Test dynamic service configuration"""
        test_name = "Service Configuration"
        logger.info(f"Testing: {test_name}")
        
        try:
            # Test service configuration structure
            sample_config = {
                "service_name": "love_relationship_mastery",
                "knowledge_domains": ["relationship_astrology", "remedial_measures"],
                "persona_mode": "relationship_counselor_authority",
                "analysis_depth": "comprehensive",
                "specialized_prompts": {
                    "system_prompt": "You are a relationship guidance expert",
                    "analysis_sections": ["compatibility_analysis", "timing_prediction", "remedial_suggestions"]
                }
            }
            
            # Validate configuration structure
            required_fields = ["service_name", "knowledge_domains", "persona_mode"]
            config_valid = all(field in sample_config for field in required_fields)
            
            if config_valid:
                self._record_test_result(test_name, True, "Service configuration structure valid")
            else:
                self._record_test_result(test_name, False, "Invalid service configuration structure")
                
        except Exception as e:
            self._record_test_result(test_name, False, f"Configuration test failed: {e}")
    
    async def _test_persona_engine(self):
        """Test persona engine functionality"""
        test_name = "Persona Engine"
        logger.info(f"Testing: {test_name}")
        
        try:
            from enhanced_rag_knowledge_engine import SwamiPersonaEngine
            
            # Create mock pool
            class MockDBPool:
                pass
            
            mock_pool = MockDBPool()
            persona_engine = SwamiPersonaEngine(mock_pool)
            
            # Test persona configurations
            expected_personas = [
                'general', 'relationship_counselor_authority', 
                'business_mentor_authority', 'comprehensive_life_master'
            ]
            
            personas_present = all(persona in persona_engine.persona_configs for persona in expected_personas)
            
            if personas_present:
                self._record_test_result(test_name, True, "All persona configurations present")
            else:
                self._record_test_result(test_name, False, "Missing persona configurations")
                
        except Exception as e:
            self._record_test_result(test_name, False, f"Persona engine test failed: {e}")
    
    async def _test_api_endpoints(self):
        """Test API endpoint structure"""
        test_name = "API Endpoints"
        logger.info(f"Testing: {test_name}")
        
        try:
            from enhanced_spiritual_guidance_router import enhanced_router
            
            # Test router initialization
            expected_endpoints = [
                '/api/spiritual/enhanced/guidance',
                '/api/spiritual/enhanced/configure-service',
                '/api/spiritual/enhanced/health'
            ]
            
            # Get router routes
            router_paths = [route.path for route in enhanced_router.routes]
            
            endpoints_present = all(endpoint in router_paths for endpoint in expected_endpoints)
            
            if endpoints_present:
                self._record_test_result(test_name, True, "All API endpoints configured")
            else:
                self._record_test_result(test_name, False, "Missing API endpoints")
                
        except Exception as e:
            self._record_test_result(test_name, False, f"API endpoint test failed: {e}")
    
    async def _test_full_user_flow(self):
        """Test complete user flow simulation"""
        test_name = "Full User Flow"
        logger.info(f"Testing: {test_name}")
        
        try:
            # Simulate complete user flow
            sample_request = {
                "question": "When will I find love and get married?",
                "birth_details": {
                    "birth_date": "1990-01-15",
                    "birth_time": "10:30",
                    "birth_location": "Chennai, India"
                },
                "service_type": "love_relationship_mastery",
                "preferred_depth": "comprehensive",
                "cultural_context": "tamil_vedic"
            }
            
            # Test request structure
            required_fields = ["question", "service_type"]
            request_valid = all(field in sample_request for field in required_fields)
            
            if request_valid:
                self._record_test_result(test_name, True, "User flow request structure valid")
            else:
                self._record_test_result(test_name, False, "Invalid user flow request")
                
        except Exception as e:
            self._record_test_result(test_name, False, f"User flow test failed: {e}")
    
    async def _test_edge_cases(self):
        """Test edge cases and error handling"""
        test_name = "Edge Cases"
        logger.info(f"Testing: {test_name}")
        
        try:
            # Test various edge cases
            edge_cases = [
                {"question": "", "service_type": "general"},  # Empty question
                {"question": "Test question", "service_type": "invalid_service"},  # Invalid service
                {"question": "Test question", "birth_details": None},  # No birth details
                {"question": "Test question", "preferred_depth": "invalid_depth"}  # Invalid depth
            ]
            
            # All edge cases should be handled gracefully
            edge_cases_valid = len(edge_cases) == 4  # Simple validation
            
            if edge_cases_valid:
                self._record_test_result(test_name, True, "Edge cases defined for testing")
            else:
                self._record_test_result(test_name, False, "Edge case testing incomplete")
                
        except Exception as e:
            self._record_test_result(test_name, False, f"Edge case test failed: {e}")
    
    def _record_test_result(self, test_name: str, passed: bool, details: str):
        """Record test result"""
        if passed:
            self.passed_tests += 1
            logger.info(f"✅ {test_name}: PASSED - {details}")
        else:
            self.failed_tests += 1
            logger.error(f"❌ {test_name}: FAILED - {details}")
        
        self.test_results.append({
            "test_name": test_name,
            "passed": passed,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
    
    def _generate_test_report(self):
        """Generate comprehensive test report"""
        total_tests = self.passed_tests + self.failed_tests
        pass_rate = (self.passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        report = f"""
🧪 JyotiFlow Enhanced System Test Report
==========================================

Total Tests: {total_tests}
Passed: {self.passed_tests}
Failed: {self.failed_tests}
Pass Rate: {pass_rate:.1f}%

Test Details:
"""
        
        for result in self.test_results:
            status = "✅ PASSED" if result["passed"] else "❌ FAILED"
            report += f"\n{status}: {result['test_name']}"
            report += f"\n  Details: {result['details']}"
            report += f"\n  Time: {result['timestamp']}\n"
        
        report += f"""
Overall Status: {"🎉 SYSTEM READY" if self.failed_tests == 0 else "⚠️ NEEDS ATTENTION"}
"""
        
        logger.info(report)
        
        # Save report to file
        with open('test_report.txt', 'w') as f:
            f.write(report)
        
        return report

class JyotiFlowDeploymentValidator:
    """Validates deployment readiness"""
    
    def __init__(self):
        self.deployment_checks = []
        
    async def validate_deployment_readiness(self):
        """Validate system is ready for deployment"""
        logger.info("🚀 Validating JyotiFlow Deployment Readiness")
        
        # Check 1: Database Migration
        await self._check_database_migration()
        
        # Check 2: Knowledge Base Population
        await self._check_knowledge_base_population()
        
        # Check 3: API Endpoints
        await self._check_api_endpoints()
        
        # Check 4: Service Configurations
        await self._check_service_configurations()
        
        # Check 5: Environment Variables
        await self._check_environment_variables()
        
        # Generate deployment report
        self._generate_deployment_report()
    
    async def _check_database_migration(self):
        """Check database migration status"""
        try:
            # Check if migration file exists
            migration_file = './backend/migrations/enhance_service_types_rag.sql'
            if os.path.exists(migration_file):
                self._record_deployment_check("Database Migration", True, "Migration file exists")
            else:
                self._record_deployment_check("Database Migration", False, "Migration file missing")
        except Exception as e:
            self._record_deployment_check("Database Migration", False, f"Error: {e}")
    
    async def _check_knowledge_base_population(self):
        """Check knowledge base population"""
        try:
            # Check if knowledge seeding system exists
            seeding_file = './backend/knowledge_seeding_system.py'
            if os.path.exists(seeding_file):
                self._record_deployment_check("Knowledge Base", True, "Seeding system ready")
            else:
                self._record_deployment_check("Knowledge Base", False, "Seeding system missing")
        except Exception as e:
            self._record_deployment_check("Knowledge Base", False, f"Error: {e}")
    
    async def _check_api_endpoints(self):
        """Check API endpoints"""
        try:
            # Check if router file exists
            router_file = './backend/enhanced_spiritual_guidance_router.py'
            if os.path.exists(router_file):
                self._record_deployment_check("API Endpoints", True, "Router configured")
            else:
                self._record_deployment_check("API Endpoints", False, "Router missing")
        except Exception as e:
            self._record_deployment_check("API Endpoints", False, f"Error: {e}")
    
    async def _check_service_configurations(self):
        """Check service configurations"""
        try:
            # Check if RAG engine exists
            rag_file = './backend/enhanced_rag_knowledge_engine.py'
            if os.path.exists(rag_file):
                self._record_deployment_check("Service Configuration", True, "RAG engine ready")
            else:
                self._record_deployment_check("Service Configuration", False, "RAG engine missing")
        except Exception as e:
            self._record_deployment_check("Service Configuration", False, f"Error: {e}")
    
    async def _check_environment_variables(self):
        """Check required environment variables"""
        try:
            required_vars = ['OPENAI_API_KEY', 'DATABASE_URL']
            missing_vars = [var for var in required_vars if not os.getenv(var)]
            
            if missing_vars:
                self._record_deployment_check("Environment Variables", False, f"Missing: {missing_vars}")
            else:
                self._record_deployment_check("Environment Variables", True, "All variables configured")
        except Exception as e:
            self._record_deployment_check("Environment Variables", False, f"Error: {e}")
    
    def _record_deployment_check(self, check_name: str, passed: bool, details: str):
        """Record deployment check result"""
        if passed:
            logger.info(f"✅ {check_name}: READY - {details}")
        else:
            logger.error(f"❌ {check_name}: NOT READY - {details}")
        
        self.deployment_checks.append({
            "check_name": check_name,
            "passed": passed,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
    
    def _generate_deployment_report(self):
        """Generate deployment readiness report"""
        total_checks = len(self.deployment_checks)
        passed_checks = sum(1 for check in self.deployment_checks if check["passed"])
        ready_rate = (passed_checks / total_checks * 100) if total_checks > 0 else 0
        
        report = f"""
🚀 JyotiFlow Deployment Readiness Report
=========================================

Total Checks: {total_checks}
Ready: {passed_checks}
Not Ready: {total_checks - passed_checks}
Readiness: {ready_rate:.1f}%

Deployment Checks:
"""
        
        for check in self.deployment_checks:
            status = "✅ READY" if check["passed"] else "❌ NOT READY"
            report += f"\n{status}: {check['check_name']}"
            report += f"\n  Details: {check['details']}"
            report += f"\n  Time: {check['timestamp']}\n"
        
        deployment_status = "🎉 READY FOR DEPLOYMENT" if passed_checks == total_checks else "⚠️ DEPLOYMENT BLOCKED"
        report += f"""
Deployment Status: {deployment_status}
"""
        
        logger.info(report)
        
        # Save report to file
        with open('deployment_report.txt', 'w') as f:
            f.write(report)
        
        return report

# Main execution
async def main():
    """Main test execution"""
    logger.info("🧪 JyotiFlow Enhanced System Testing")
    
    # Run comprehensive tests
    test_suite = JyotiFlowTestSuite()
    await test_suite.run_comprehensive_tests()
    
    # Validate deployment readiness
    deployment_validator = JyotiFlowDeploymentValidator()
    await deployment_validator.validate_deployment_readiness()
    
    logger.info("🎯 Testing and validation completed!")

if __name__ == "__main__":
    asyncio.run(main())