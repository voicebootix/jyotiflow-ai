#!/usr/bin/env python3
"""
Current Testing System Status Check
Verifies the state of the testing system after recent changes
"""

import sys
import os
import asyncio
import requests
from datetime import datetime

# Add backend to path
sys.path.append('/workspace/backend')

def check_production_endpoints():
    """Check the status of production endpoints"""
    print("🌐 CHECKING PRODUCTION ENDPOINTS")
    print("=" * 50)
    
    base_url = "https://jyotiflow-ai.onrender.com"
    endpoints = [
        "/api/monitoring/test-status",
        "/api/monitoring/social-media-status", 
        "/api/monitoring/spiritual-services-status",
        "/api/monitoring/business-logic-validation"
    ]
    
    results = {}
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            data = response.json()
            status = data.get('status', 'unknown')
            message = data.get('message', '')
            
            if 'datetime' in message.lower() or 'timezone' in message.lower():
                results[endpoint] = f"❌ DATETIME ERROR: {message[:100]}"
            elif 'import' in message.lower() or 'module' in message.lower():
                results[endpoint] = f"❌ IMPORT ERROR: {message[:100]}"
            elif status == 'success':
                results[endpoint] = f"✅ SUCCESS: {message[:50]}"
            else:
                results[endpoint] = f"⚠️  {status.upper()}: {message[:100]}"
                
        except Exception as e:
            results[endpoint] = f"❌ CONNECTION ERROR: {str(e)[:50]}"
    
    for endpoint, result in results.items():
        print(f"{endpoint}: {result}")
    
    return results

def check_local_imports():
    """Check if local imports work correctly"""
    print("\n🔧 CHECKING LOCAL IMPORTS")
    print("=" * 50)
    
    results = {}
    
    # Test 1: TestSuiteGenerator
    try:
        from test_suite_generator import TestSuiteGenerator
        generator = TestSuiteGenerator()
        results['TestSuiteGenerator'] = "✅ Import successful"
    except Exception as e:
        results['TestSuiteGenerator'] = f"❌ Import failed: {str(e)[:100]}"
    
    # Test 2: TestExecutionEngine  
    try:
        from test_execution_engine import TestExecutionEngine
        engine = TestExecutionEngine()
        results['TestExecutionEngine'] = "✅ Import successful"
    except Exception as e:
        results['TestExecutionEngine'] = f"❌ Import failed: {str(e)[:100]}"
    
    # Test 3: SocialMediaValidator
    try:
        from validators.social_media_validator import SocialMediaValidator
        validator = SocialMediaValidator()
        results['SocialMediaValidator'] = "✅ Import successful"
    except Exception as e:
        results['SocialMediaValidator'] = f"❌ Import failed: {str(e)[:100]}"
    
    # Test 4: Avatar Engine
    try:
        from spiritual_avatar_generation_engine import avatar_engine, get_avatar_engine
        results['AvatarEngine'] = "✅ Import successful"
    except Exception as e:
        results['AvatarEngine'] = f"❌ Import failed: {str(e)[:100]}"
    
    for component, result in results.items():
        print(f"{component}: {result}")
    
    return results

def check_datetime_handling():
    """Check datetime handling"""
    print("\n📅 CHECKING DATETIME HANDLING")
    print("=" * 50)
    
    try:
        from datetime import datetime, timezone
        
        # Test timezone-naive (should work with PostgreSQL TIMESTAMP)
        naive_dt = datetime.now()
        print(f"✅ Naive datetime: {naive_dt} (tzinfo: {naive_dt.tzinfo})")
        
        # Test timezone-aware (was causing errors)
        aware_dt = datetime.now(timezone.utc)
        print(f"⚠️ Aware datetime: {aware_dt} (tzinfo: {aware_dt.tzinfo})")
        
        # Check if test suite generator uses correct approach
        import inspect
        from test_suite_generator import TestSuiteGenerator
        source = inspect.getsource(TestSuiteGenerator.store_test_suites)
        
        if 'datetime.now()' in source and 'timezone.utc' not in source:
            print("✅ TestSuiteGenerator uses timezone-naive datetime")
            return True
        elif 'timezone.utc' in source:
            print("❌ TestSuiteGenerator still uses timezone-aware datetime")
            return False
        else:
            print("⚠️ Could not determine datetime usage")
            return None
            
    except Exception as e:
        print(f"❌ Datetime check failed: {e}")
        return False

def main():
    print("🚀 TESTING SYSTEM STATUS CHECK - POST RECENT CHANGES")
    print("=" * 80)
    
    # Check production endpoints
    endpoint_results = check_production_endpoints()
    
    # Check local imports
    import_results = check_local_imports()
    
    # Check datetime handling
    datetime_ok = check_datetime_handling()
    
    print("\n📊 SUMMARY")
    print("=" * 50)
    
    # Count successes
    endpoint_success = sum(1 for r in endpoint_results.values() if '✅' in r)
    import_success = sum(1 for r in import_results.values() if '✅' in r)
    
    print(f"Production Endpoints: {endpoint_success}/{len(endpoint_results)} working")
    print(f"Local Imports: {import_success}/{len(import_results)} working")
    print(f"Datetime Handling: {'✅ Fixed' if datetime_ok else '❌ Still broken' if datetime_ok is False else '⚠️ Unknown'}")
    
    # Overall assessment
    total_issues = 0
    datetime_issues = sum(1 for r in endpoint_results.values() if 'DATETIME ERROR' in r)
    import_issues = sum(1 for r in endpoint_results.values() if 'IMPORT ERROR' in r)
    
    print(f"\nRemaining Issues:")
    print(f"- Datetime errors: {datetime_issues}")
    print(f"- Import errors: {import_issues}")
    print(f"- Connection issues: {sum(1 for r in endpoint_results.values() if 'CONNECTION ERROR' in r)}")
    
    if datetime_issues == 0 and import_issues == 0:
        print("\n🎉 TESTING SYSTEM APPEARS TO BE WORKING!")
    elif datetime_issues == 0:
        print("\n✅ Datetime issues resolved, import issues remain")
    elif import_issues == 0:
        print("\n✅ Import issues resolved, datetime issues remain")
    else:
        print("\n❌ Multiple issues still present")

if __name__ == "__main__":
    main()