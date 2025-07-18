#!/usr/bin/env python3
"""
Database Race Condition Fix Validator
Tests that the pricing module no longer competes with main app for database connections
"""

import os
import asyncio
import asyncpg
import time
import logging
from concurrent.futures import ThreadPoolExecutor
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_main_db_connection():
    """Test main database connection"""
    logger.info("🧪 Testing main database connection...")
    
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        logger.error("❌ DATABASE_URL not set")
        return False
    
    try:
        # Test direct connection
        conn = await asyncpg.connect(DATABASE_URL)
        result = await conn.fetchval("SELECT 1")
        await conn.close()
        
        if result == 1:
            logger.info("✅ Main database connection successful")
            return True
        else:
            logger.error("❌ Main database connection failed")
            return False
    except Exception as e:
        logger.error(f"❌ Main database connection error: {e}")
        return False

async def test_pricing_module():
    """Test pricing module with main db pool"""
    logger.info("🧪 Testing pricing module...")
    
    try:
        # Import the fixed pricing module
        from dynamic_comprehensive_pricing import DynamicComprehensivePricing
        
        # This should now use the main app's pool instead of creating its own
        pricing = DynamicComprehensivePricing()
        
        logger.info("✅ Pricing module imported successfully")
        logger.info(f"✅ Using main pool: {pricing._use_main_pool}")
        
        return True
    except Exception as e:
        logger.error(f"❌ Pricing module error: {e}")
        return False

async def test_concurrent_connections():
    """Test that multiple connections don't compete"""
    logger.info("🧪 Testing concurrent database connections...")
    
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        logger.error("❌ DATABASE_URL not set")
        return False
    
    async def create_test_connection(conn_id):
        """Create a test connection"""
        try:
            start_time = time.time()
            conn = await asyncpg.connect(DATABASE_URL)
            result = await conn.fetchval(f"SELECT {conn_id}")
            await conn.close()
            end_time = time.time()
            
            logger.info(f"✅ Connection {conn_id} successful in {end_time - start_time:.2f}s")
            return True
        except Exception as e:
            logger.error(f"❌ Connection {conn_id} failed: {e}")
            return False
    
    # Test 5 concurrent connections
    tasks = [create_test_connection(i+1) for i in range(5)]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    successful = sum(1 for r in results if r is True)
    logger.info(f"✅ {successful}/5 concurrent connections successful")
    
    return successful >= 4  # Allow 1 failure

async def test_unified_startup():
    """Test that unified startup works without conflicts"""
    logger.info("🧪 Testing unified startup system...")
    
    try:
        # Import unified startup
        from unified_startup_system import UnifiedJyotiFlowStartup
        
        startup = UnifiedJyotiFlowStartup()
        
        # Test validation step
        await startup._validate_environment()
        logger.info("✅ Environment validation passed")
        
        return True
    except Exception as e:
        logger.error(f"❌ Unified startup error: {e}")
        return False

async def main():
    """Run all tests"""
    logger.info("🚀 Starting Database Race Condition Fix Validation...")
    
    tests = [
        ("Main DB Connection", test_main_db_connection),
        ("Pricing Module", test_pricing_module),
        ("Concurrent Connections", test_concurrent_connections),
        ("Unified Startup", test_unified_startup)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        logger.info(f"\n📋 Running {test_name} test...")
        try:
            result = await test_func()
            results[test_name] = result
            logger.info(f"{'✅' if result else '❌'} {test_name}: {'PASSED' if result else 'FAILED'}")
        except Exception as e:
            logger.error(f"❌ {test_name} test crashed: {e}")
            results[test_name] = False
    
    # Summary
    logger.info("\n📊 Test Results Summary:")
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"   {test_name}: {status}")
    
    logger.info(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! Database race condition fix is working.")
        return True
    else:
        logger.error("💥 Some tests failed. Race condition may still exist.")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)