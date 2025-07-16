#!/usr/bin/env python3
"""
Comprehensive Test Suite for Unified Startup System
Tests current functionality and validates integration success
"""

import os
import sys
import time
import asyncio
import asyncpg
import logging
from typing import Dict, Any, List
import traceback

# Add backend to path for imports
sys.path.insert(0, 'backend')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UnifiedStartupTester:
    """Comprehensive tester for unified startup system"""
    
    def __init__(self):
        self.test_results = {}
        self.database_url = os.getenv("DATABASE_URL")
        if not self.database_url:
            logger.error("DATABASE_URL not set - tests will fail")
    
    async def test_database_connection(self) -> Dict[str, Any]:
        """Test basic database connection"""
        test_name = "database_connection"
        logger.info(f"🧪 Testing: {test_name}")
        
        try:
            start_time = time.time()
            conn = await asyncpg.connect(self.database_url)
            
            # Test basic query
            result = await conn.fetchval("SELECT 1")
            await conn.close()
            
            duration = time.time() - start_time
            
            return {
                "test": test_name,
                "status": "PASS" if result == 1 else "FAIL",
                "duration_seconds": round(duration, 2),
                "details": f"Connected in {duration:.2f} seconds"
            }
        except Exception as e:
            return {
                "test": test_name,
                "status": "FAIL",
                "error": str(e),
                "details": "Failed to establish database connection"
            }
    
    async def test_unified_startup_import(self) -> Dict[str, Any]:
        """Test unified startup system import and basic functionality"""
        test_name = "unified_startup_import"
        logger.info(f"🧪 Testing: {test_name}")
        
        try:
            # Try to import the unified startup system
            from unified_startup_system import initialize_unified_jyotiflow, cleanup_unified_system
            
            return {
                "test": test_name,
                "status": "PASS",
                "details": "Successfully imported unified startup system"
            }
        except Exception as e:
            return {
                "test": test_name,
                "status": "FAIL",
                "error": str(e),
                "details": "Failed to import unified startup system"
            }
    
    async def test_unified_startup_initialization(self) -> Dict[str, Any]:
        """Test unified startup system initialization"""
        test_name = "unified_startup_initialization"
        logger.info(f"🧪 Testing: {test_name}")
        
        try:
            start_time = time.time()
            
            # Import and initialize
            from unified_startup_system import initialize_unified_jyotiflow, cleanup_unified_system
            
            # Initialize the system (this should work with current implementation)
            db_pool = await initialize_unified_jyotiflow()
            
            # Test the pool
            async with db_pool.acquire() as conn:
                result = await conn.fetchval("SELECT 1")
            
            # Cleanup
            await cleanup_unified_system()
            
            duration = time.time() - start_time
            
            return {
                "test": test_name,
                "status": "PASS" if result == 1 else "FAIL",
                "duration_seconds": round(duration, 2),
                "details": f"Initialized and tested in {duration:.2f} seconds"
            }
        except Exception as e:
            return {
                "test": test_name,
                "status": "FAIL",
                "error": str(e),
                "details": "Failed to initialize unified startup system",
                "traceback": traceback.format_exc()
            }
    
    async def test_required_tables_exist(self) -> Dict[str, Any]:
        """Test that required tables exist in database"""
        test_name = "required_tables_exist"
        logger.info(f"🧪 Testing: {test_name}")
        
        required_tables = [
            'users', 'sessions', 'service_types', 'credit_packages',
            'pricing_config', 'followup_templates'
        ]
        
        try:
            conn = await asyncpg.connect(self.database_url)
            missing_tables = []
            existing_tables = []
            
            for table in required_tables:
                exists = await conn.fetchval("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = $1
                    )
                """, table)
                
                if exists:
                    existing_tables.append(table)
                else:
                    missing_tables.append(table)
            
            await conn.close()
            
            status = "PASS" if len(missing_tables) == 0 else "PARTIAL"
            
            return {
                "test": test_name,
                "status": status,
                "existing_tables": existing_tables,
                "missing_tables": missing_tables,
                "details": f"{len(existing_tables)}/{len(required_tables)} required tables exist"
            }
        except Exception as e:
            return {
                "test": test_name,
                "status": "FAIL",
                "error": str(e),
                "details": "Failed to check table existence"
            }
    
    async def test_enhanced_tables_missing(self) -> Dict[str, Any]:
        """Test that enhanced tables (RAG, cache) are missing (before integration)"""
        test_name = "enhanced_tables_missing"
        logger.info(f"🧪 Testing: {test_name}")
        
        enhanced_tables = [
            'rag_knowledge_base',
            'service_configuration_cache'
        ]
        
        try:
            conn = await asyncpg.connect(self.database_url)
            existing_tables = []
            missing_tables = []
            
            for table in enhanced_tables:
                exists = await conn.fetchval("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = $1
                    )
                """, table)
                
                if exists:
                    existing_tables.append(table)
                else:
                    missing_tables.append(table)
            
            await conn.close()
            
            return {
                "test": test_name,
                "status": "INFO",
                "existing_enhanced_tables": existing_tables,
                "missing_enhanced_tables": missing_tables,
                "details": f"Enhanced tables status: {len(existing_tables)} exist, {len(missing_tables)} missing"
            }
        except Exception as e:
            return {
                "test": test_name,
                "status": "FAIL",
                "error": str(e),
                "details": "Failed to check enhanced table existence"
            }
    
    async def test_health_monitoring_missing(self) -> Dict[str, Any]:
        """Test that health monitoring is not currently integrated"""
        test_name = "health_monitoring_missing"
        logger.info(f"🧪 Testing: {test_name}")
        
        try:
            # Try to import health monitoring components
            try:
                from database_self_healing_system import router as health_router
                health_router_available = True
            except ImportError:
                health_router_available = False
            
            # Check if health endpoints would be available (they shouldn't be in main.py yet)
            with open('backend/main.py', 'r') as f:
                main_content = f.read()
            
            health_integrated = "health_router" in main_content
            
            return {
                "test": test_name,
                "status": "INFO",
                "health_router_importable": health_router_available,
                "health_integrated_in_main": health_integrated,
                "details": f"Health monitoring integration status before unification"
            }
        except Exception as e:
            return {
                "test": test_name,
                "status": "FAIL",
                "error": str(e),
                "details": "Failed to check health monitoring status"
            }
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and return comprehensive results"""
        logger.info("🚀 Starting Unified Startup System Test Suite")
        logger.info("=" * 60)
        
        start_time = time.time()
        
        # Run all tests
        tests = [
            self.test_database_connection(),
            self.test_unified_startup_import(),
            self.test_unified_startup_initialization(),
            self.test_required_tables_exist(),
            self.test_enhanced_tables_missing(),
            self.test_health_monitoring_missing()
        ]
        
        results = await asyncio.gather(*tests, return_exceptions=True)
        
        # Process results
        passed = 0
        failed = 0
        info = 0
        partial = 0
        
        for result in results:
            if isinstance(result, Exception):
                failed += 1
                logger.error(f"❌ Test exception: {result}")
            else:
                status = result.get('status', 'UNKNOWN')
                test_name = result.get('test', 'unknown')
                
                if status == 'PASS':
                    passed += 1
                    logger.info(f"✅ {test_name}: PASSED")
                elif status == 'FAIL':
                    failed += 1
                    logger.error(f"❌ {test_name}: FAILED - {result.get('details', '')}")
                    if 'error' in result:
                        logger.error(f"   Error: {result['error']}")
                elif status == 'PARTIAL':
                    partial += 1
                    logger.warning(f"⚠️ {test_name}: PARTIAL - {result.get('details', '')}")
                elif status == 'INFO':
                    info += 1
                    logger.info(f"ℹ️ {test_name}: INFO - {result.get('details', '')}")
        
        total_time = time.time() - start_time
        
        summary = {
            "total_tests": len(tests),
            "passed": passed,
            "failed": failed,
            "partial": partial,
            "info": info,
            "total_time_seconds": round(total_time, 2),
            "detailed_results": [r for r in results if not isinstance(r, Exception)],
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        logger.info("=" * 60)
        logger.info(f"📊 TEST SUMMARY:")
        logger.info(f"   Total Tests: {summary['total_tests']}")
        logger.info(f"   ✅ Passed: {summary['passed']}")
        logger.info(f"   ❌ Failed: {summary['failed']}")
        logger.info(f"   ⚠️ Partial: {summary['partial']}")
        logger.info(f"   ℹ️ Info: {summary['info']}")
        logger.info(f"   ⏱️ Total Time: {summary['total_time_seconds']} seconds")
        
        return summary

if __name__ == "__main__":
    async def main():
        tester = UnifiedStartupTester()
        results = await tester.run_all_tests()
        
        # Save results to file for evidence
        import json
        with open('test_results_before_integration.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n📄 Test results saved to: test_results_before_integration.json")
    
    asyncio.run(main())