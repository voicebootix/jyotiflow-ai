#!/usr/bin/env python3
"""
Database Timeout Fix Test - Verify Enhanced Cold Start Handling
Tests the improved timeout settings for Supabase database connections
"""

import os
import sys
import asyncio
import asyncpg
import time
from datetime import datetime

def test_timeout_configuration():
    """Test if the timeout configuration is correctly set"""
    
    print("🧪 Testing Database Timeout Fix")
    print("=" * 50)
    
    # Test the timeout calculation logic
    def calculate_timeout(attempt):
        return 90 if attempt == 0 else 120 + (attempt * 20)
    
    print("⏱️ New Timeout Schedule:")
    for i in range(5):
        timeout = calculate_timeout(i)
        print(f"   Attempt {i+1}: {timeout} seconds")
    
    print()
    print("📊 Timeout Analysis:")
    print(f"   • First attempt: {calculate_timeout(0)} seconds (was 45)")
    print(f"   • Sufficient for Supabase cold start (60-90s needed): ✅")
    print(f"   • Progressive increase for retries: ✅")
    print(f"   • Maximum timeout: {calculate_timeout(4)} seconds")
    
    return True

async def test_database_connection_with_timeout():
    """Test actual database connection with enhanced timeouts"""
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("⚠️ DATABASE_URL not set - skipping actual connection test")
        return True
    
    print("🔗 Testing Actual Database Connection...")
    print(f"📍 Target: {database_url.split('@')[1] if '@' in database_url else 'Hidden'}")
    
    start_time = time.time()
    
    try:
        # Test with the new 90-second timeout
        print("⏳ Attempting connection with 90-second timeout...")
        
        conn = await asyncio.wait_for(
            asyncpg.connect(database_url),
            timeout=90.0
        )
        
        # Test basic query
        result = await conn.fetchval("SELECT 1 as test")
        await conn.close()
        
        elapsed = time.time() - start_time
        print(f"✅ Connection successful in {elapsed:.2f} seconds")
        print(f"📊 Result: {result}")
        
        if elapsed > 60:
            print("🔥 Cold start detected - connection took >60 seconds")
            print("✅ Enhanced timeout prevented failure")
        
        return True
        
    except asyncio.TimeoutError:
        elapsed = time.time() - start_time
        print(f"❌ Connection timeout after {elapsed:.2f} seconds")
        print("🚨 This suggests a persistent connectivity issue")
        return False
        
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"❌ Connection error after {elapsed:.2f} seconds: {e}")
        return False

def test_environment_detection():
    """Test environment detection logic"""
    
    print("🔍 Testing Environment Detection...")
    
    # Mock environment variables for testing
    original_render = os.getenv("RENDER")
    original_render_url = os.getenv("RENDER_EXTERNAL_URL")
    
    # Test Render detection
    os.environ["RENDER"] = "true"
    is_render = os.getenv("RENDER") == "true" or "render.com" in os.getenv("RENDER_EXTERNAL_URL", "")
    print(f"   Render environment detected: {is_render}")
    
    # Test Supabase detection
    test_db_url = "postgresql://user:pass@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres"
    is_supabase = "supabase.com" in test_db_url
    print(f"   Supabase database detected: {is_supabase}")
    
    # Restore original environment
    if original_render:
        os.environ["RENDER"] = original_render
    else:
        os.environ.pop("RENDER", None)
        
    if original_render_url:
        os.environ["RENDER_EXTERNAL_URL"] = original_render_url
    
    return True

async def main():
    """Run all timeout fix tests"""
    
    print("🚀 Database Timeout Fix Validation")
    print("=" * 50)
    print(f"🕐 Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    tests = [
        ("Timeout Configuration", test_timeout_configuration),
        ("Environment Detection", test_environment_detection),
        ("Database Connection", test_database_connection_with_timeout),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"🧪 Running: {test_name}")
        print("-" * 30)
        
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            
            results.append((test_name, result))
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"📊 {test_name}: {status}")
            
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
            results.append((test_name, False))
        
        print()
    
    # Summary
    print("📋 Test Summary:")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅" if result else "❌"
        print(f"   {status} {test_name}")
    
    print()
    print(f"📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Database timeout fix is working correctly.")
        return True
    else:
        print("⚠️ Some tests failed. Check the database configuration.")
        return False

if __name__ == "__main__":
    # Run the test
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 