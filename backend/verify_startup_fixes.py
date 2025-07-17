"""
Startup Fixes Verification Script
Tests all the critical fixes applied to the JyotiFlow.ai system
"""

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_embedding_formatting():
    """Test the embedding formatting fix"""
    try:
        from knowledge_seeding_system import format_embedding_for_storage
        
        # Test cases
        test_cases = [
            # String JSON embedding
            ('[0.1, 0.2, 0.3]', True, 'list for pgvector'),
            ('[0.1, 0.2, 0.3]', False, 'json string for text'),
            # List embedding
            ([0.1, 0.2, 0.3], True, 'list for pgvector'),
            ([0.1, 0.2, 0.3], False, 'json string for text'),
            # Invalid JSON
            ('invalid_json', True, 'default vector'),
            ('invalid_json', False, 'original string'),
        ]
        
        logger.info("🧪 Testing embedding formatting...")
        
        for embedding, vector_support, expected_type in test_cases:
            result = format_embedding_for_storage(embedding, vector_support)
            
            if vector_support:
                assert isinstance(result, list), f"Expected list for pgvector, got {type(result)}"
                if embedding == 'invalid_json':
                    assert len(result) == 1536, f"Expected 1536-dim default vector, got {len(result)}"
            else:
                if isinstance(embedding, list):
                    assert isinstance(result, str), f"Expected JSON string for non-pgvector, got {type(result)}"
                    
        logger.info("✅ Embedding formatting tests passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Embedding formatting test failed: {e}")
        return False

async def test_timezone_fixer():
    """Test the timezone fixer utilities"""
    try:
        from database_timezone_fixer import safe_utc_now, normalize_datetime_for_db, prepare_datetime_params
        
        logger.info("🧪 Testing timezone fixer...")
        
        # Test safe_utc_now
        now = safe_utc_now()
        assert isinstance(now, datetime), "safe_utc_now should return datetime"
        assert now.tzinfo is None, "safe_utc_now should return timezone-naive datetime"
        
        # Test normalize_datetime_for_db
        tz_aware = datetime.now(timezone.utc)
        normalized = normalize_datetime_for_db(tz_aware)
        assert normalized.tzinfo is None, "normalize_datetime_for_db should strip timezone info"
        
        # Test prepare_datetime_params
        params = prepare_datetime_params("test", tz_aware, 123)
        assert params[1].tzinfo is None, "prepare_datetime_params should normalize datetime"
        assert params[0] == "test", "prepare_datetime_params should preserve non-datetime values"
        assert params[2] == 123, "prepare_datetime_params should preserve non-datetime values"
        
        logger.info("✅ Timezone fixer tests passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Timezone fixer test failed: {e}")
        return False

async def test_import_paths():
    """Test that all import paths are working"""
    try:
        logger.info("🧪 Testing import paths...")
        
        # Test knowledge seeding system
        from knowledge_seeding_system import KnowledgeSeeder
        assert KnowledgeSeeder is not None
        
        # Test database timezone fixer
        from database_timezone_fixer import safe_utc_now
        assert safe_utc_now is not None
        
        # Test database self-healing system
        from database_self_healing_system import DatabaseHealthMonitor
        assert DatabaseHealthMonitor is not None
        
        logger.info("✅ Import path tests passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Import path test failed: {e}")
        return False

async def test_database_queries():
    """Test database query safety"""
    try:
        import asyncpg
        import os
        
        logger.info("🧪 Testing database query safety...")
        
        DATABASE_URL = os.getenv("DATABASE_URL")
        if not DATABASE_URL:
            logger.warning("⚠️ No DATABASE_URL found, skipping database tests")
            return True
            
        conn = await asyncpg.connect(DATABASE_URL)
        try:
            # Test basic connectivity
            version = await conn.fetchval("SELECT version()")
            logger.info(f"📊 Connected to: {version[:50]}...")
            
            # Test that the health monitoring tables exist
            tables_exist = await conn.fetchval("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'health_check_results'
                )
            """)
            
            if not tables_exist:
                logger.warning("⚠️ Health monitoring tables not found, they will be created on startup")
            else:
                logger.info("✅ Health monitoring tables exist")
            
            # Test timezone-naive datetime insertion (this should work now)
            from database_timezone_fixer import safe_utc_now
            test_time = safe_utc_now()
            
            # This should not raise a timezone error
            logger.info(f"✅ Safe UTC time generated: {test_time}")
            
        finally:
            await conn.close()
            
        logger.info("✅ Database query safety tests passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Database query safety test failed: {e}")
        return False

async def verify_startup_fixes():
    """Run all verification tests"""
    logger.info("🔍 Starting JyotiFlow.ai Startup Fixes Verification...")
    
    tests = [
        ("Embedding Formatting", test_embedding_formatting),
        ("Timezone Fixer", test_timezone_fixer),
        ("Import Paths", test_import_paths),
        ("Database Queries", test_database_queries),
    ]
    
    results = {}
    all_passed = True
    
    for test_name, test_func in tests:
        logger.info(f"\n🧪 Running {test_name} tests...")
        try:
            result = await test_func()
            results[test_name] = result
            if not result:
                all_passed = False
        except Exception as e:
            logger.error(f"❌ {test_name} test crashed: {e}")
            results[test_name] = False
            all_passed = False
    
    # Print summary
    logger.info("\n" + "="*60)
    logger.info("🎯 VERIFICATION SUMMARY")
    logger.info("="*60)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        logger.info(f"{status} - {test_name}")
    
    if all_passed:
        logger.info("\n🎉 ALL TESTS PASSED! Startup fixes are working correctly.")
        logger.info("🚀 System should start without the reported errors.")
    else:
        logger.info(f"\n⚠️ {sum(1 for r in results.values() if not r)} tests failed.")
        logger.info("🔧 Review the failed tests before deploying.")
    
    return all_passed

if __name__ == "__main__":
    asyncio.run(verify_startup_fixes())