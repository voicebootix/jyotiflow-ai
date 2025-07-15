#!/usr/bin/env python3
"""
Test script to verify connection handling fixes across backend modules.
Tests all the bugs mentioned in the user query to ensure they are resolved.
"""

import asyncio
import sys
import os
import logging
from datetime import datetime

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConnectionHandlingTestSuite:
    """Test suite for connection handling fixes"""
    
    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
    
    def log_test_result(self, test_name: str, passed: bool, details: str = ""):
        """Log test result"""
        self.total_tests += 1
        if passed:
            self.passed_tests += 1
            logger.info(f"✅ PASS: {test_name}")
        else:
            logger.error(f"❌ FAIL: {test_name} - {details}")
        
        self.test_results.append({
            'test': test_name,
            'passed': passed,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
    
    async def test_spiritual_router_connection_handling(self):
        """Test spiritual.py router connection handling fixes"""
        try:
            # Import the module to check for syntax errors
            from routers.spiritual import router
            
            # Check if the file contains proper connection handling patterns
            with open('backend/routers/spiritual.py', 'r') as f:
                content = f.read()
            
            # Check for proper connection handling patterns
            has_proper_release = 'await db_manager.release_connection(conn)' in content
            has_try_finally = 'try:' in content and 'finally:' in content
            has_conn_none_init = 'conn = None' in content
            
            # Check for absence of improper patterns
            no_improper_close = 'await conn.close()' not in content
            
            all_patterns_correct = has_proper_release and has_try_finally and has_conn_none_init and no_improper_close
            
            self.log_test_result(
                "Spiritual Router Connection Handling",
                all_patterns_correct,
                f"Patterns: release={has_proper_release}, try_finally={has_try_finally}, conn_none={has_conn_none_init}, no_improper_close={no_improper_close}"
            )
            
        except Exception as e:
            self.log_test_result(
                "Spiritual Router Connection Handling",
                False,
                f"Import error: {str(e)}"
            )
    
    async def test_enhanced_registration_connection_handling(self):
        """Test enhanced_registration.py connection handling fixes"""
        try:
            # Import the module to check for syntax errors
            from routers.enhanced_registration import router
            
            # Check if the file contains proper connection handling patterns
            with open('backend/routers/enhanced_registration.py', 'r') as f:
                content = f.read()
            
            # Check for proper connection handling patterns
            has_proper_release = 'await db_manager.release_connection(conn)' in content
            has_try_finally = 'try:' in content and 'finally:' in content
            has_conn_none_init = 'conn = None' in content
            uses_db_manager = 'await db_manager.get_connection()' in content
            
            # Check for absence of improper patterns
            no_improper_close = 'await conn.close()' not in content
            no_improper_get_connection = 'await db.get_connection()' not in content
            
            all_patterns_correct = (has_proper_release and has_try_finally and 
                                  has_conn_none_init and uses_db_manager and 
                                  no_improper_close and no_improper_get_connection)
            
            self.log_test_result(
                "Enhanced Registration Connection Handling",
                all_patterns_correct,
                f"Patterns: release={has_proper_release}, try_finally={has_try_finally}, conn_none={has_conn_none_init}, db_manager={uses_db_manager}, no_improper_close={no_improper_close}, no_improper_get={no_improper_get_connection}"
            )
            
        except Exception as e:
            self.log_test_result(
                "Enhanced Registration Connection Handling",
                False,
                f"Import error: {str(e)}"
            )
    
    async def test_dynamic_pricing_connection_handling(self):
        """Test dynamic_comprehensive_pricing.py connection handling fixes"""
        try:
            # Import the module to check for syntax errors
            from dynamic_comprehensive_pricing import DynamicComprehensivePricing
            
            # Check if the file contains proper connection handling patterns
            with open('backend/dynamic_comprehensive_pricing.py', 'r') as f:
                content = f.read()
            
            # Check for proper connection handling patterns
            has_pool_lock = 'self._pool_lock = asyncio.Lock()' in content
            has_pool_initialized = 'self._pool_initialized = False' in content
            has_proper_initialize = 'async with self._pool_lock:' in content
            uses_connection_pool = 'await self.get_connection()' in content
            uses_release_connection = 'await self.release_connection(conn)' in content
            
            # Check for absence of improper patterns
            no_direct_asyncpg = 'await asyncpg.connect(' not in content
            no_improper_close = 'await conn.close()' not in content
            no_race_condition = 'asyncio.create_task(self.initialize_pool())' not in content
            
            all_patterns_correct = (has_pool_lock and has_pool_initialized and 
                                  has_proper_initialize and uses_connection_pool and 
                                  uses_release_connection and no_direct_asyncpg and 
                                  no_improper_close and no_race_condition)
            
            self.log_test_result(
                "Dynamic Pricing Connection Handling",
                all_patterns_correct,
                f"Patterns: pool_lock={has_pool_lock}, pool_initialized={has_pool_initialized}, proper_initialize={has_proper_initialize}, uses_pool={uses_connection_pool}, uses_release={uses_release_connection}, no_direct_asyncpg={no_direct_asyncpg}, no_improper_close={no_improper_close}, no_race_condition={no_race_condition}"
            )
            
        except Exception as e:
            self.log_test_result(
                "Dynamic Pricing Connection Handling",
                False,
                f"Import error: {str(e)}"
            )
    
    async def test_enhanced_birth_chart_service_connection_handling(self):
        """Test enhanced_birth_chart_cache_service.py connection handling fixes"""
        try:
            # Import the module to check for syntax errors
            from services.enhanced_birth_chart_cache_service import EnhancedBirthChartCacheService
            
            # Check if the file contains proper connection handling patterns
            with open('backend/services/enhanced_birth_chart_cache_service.py', 'r') as f:
                content = f.read()
            
            # Check for proper connection handling patterns
            has_try_finally = 'try:' in content and 'finally:' in content
            has_conn_none_init = 'conn = None' in content
            has_proper_close = 'await conn.close()' in content  # This service uses direct connections
            
            # Check for async method call fix
            has_async_prompt = 'await self._build_swamiji_prompt(' in content
            
            all_patterns_correct = has_try_finally and has_conn_none_init and has_proper_close and has_async_prompt
            
            self.log_test_result(
                "Enhanced Birth Chart Service Connection Handling",
                all_patterns_correct,
                f"Patterns: try_finally={has_try_finally}, conn_none={has_conn_none_init}, proper_close={has_proper_close}, async_prompt={has_async_prompt}"
            )
            
        except Exception as e:
            self.log_test_result(
                "Enhanced Birth Chart Service Connection Handling",
                False,
                f"Import error: {str(e)}"
            )
    
    async def test_connection_pool_initialization(self):
        """Test connection pool initialization race condition fix"""
        try:
            from dynamic_comprehensive_pricing import DynamicComprehensivePricing
            
            # Create instance and test initialization
            pricing = DynamicComprehensivePricing()
            
            # Test that pool initialization is properly handled
            conn = await pricing.get_connection()
            if conn:
                await pricing.release_connection(conn)
                self.log_test_result(
                    "Connection Pool Initialization",
                    True,
                    "Pool initialization and connection acquisition successful"
                )
            else:
                self.log_test_result(
                    "Connection Pool Initialization",
                    False,
                    "Failed to acquire connection from pool"
                )
                
        except Exception as e:
            self.log_test_result(
                "Connection Pool Initialization",
                False,
                f"Pool initialization error: {str(e)}"
            )
    
    async def test_async_method_call_fix(self):
        """Test that async methods are properly awaited"""
        try:
            from services.enhanced_birth_chart_cache_service import EnhancedBirthChartCacheService
            
            # Check if the async method call is properly awaited
            with open('backend/services/enhanced_birth_chart_cache_service.py', 'r') as f:
                content = f.read()
            
            # Look for the specific line that was fixed
            has_async_await = 'prompt = await self._build_swamiji_prompt(' in content
            
            self.log_test_result(
                "Async Method Call Fix",
                has_async_await,
                f"Async method properly awaited: {has_async_await}"
            )
            
        except Exception as e:
            self.log_test_result(
                "Async Method Call Fix",
                False,
                f"Test error: {str(e)}"
            )
    
    async def run_all_tests(self):
        """Run all connection handling tests"""
        logger.info("🧪 Starting Connection Handling Test Suite...")
        logger.info("=" * 60)
        
        # Run all tests
        await self.test_spiritual_router_connection_handling()
        await self.test_enhanced_registration_connection_handling()
        await self.test_dynamic_pricing_connection_handling()
        await self.test_enhanced_birth_chart_service_connection_handling()
        await self.test_connection_pool_initialization()
        await self.test_async_method_call_fix()
        
        # Print summary
        logger.info("=" * 60)
        logger.info(f"📊 Test Summary: {self.passed_tests}/{self.total_tests} tests passed")
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        logger.info(f"🎯 Success Rate: {success_rate:.1f}%")
        
        # Print failed tests
        failed_tests = [test for test in self.test_results if not test['passed']]
        if failed_tests:
            logger.error("❌ Failed Tests:")
            for test in failed_tests:
                logger.error(f"   - {test['test']}: {test['details']}")
        else:
            logger.info("✅ All tests passed!")
        
        return success_rate == 100.0

async def main():
    """Main test runner"""
    test_suite = ConnectionHandlingTestSuite()
    success = await test_suite.run_all_tests()
    
    if success:
        logger.info("🎉 All connection handling bugs have been successfully fixed!")
        return 0
    else:
        logger.error("⚠️ Some connection handling issues remain. Please review the failed tests.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 