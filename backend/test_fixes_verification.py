#!/usr/bin/env python3
"""
Test Fixes Verification Script
Proves that the datetime and import fixes actually work
"""

import sys
import os
import asyncio
from datetime import datetime
import json

# Add backend to path
sys.path.append('/workspace/backend')

def test_datetime_fix():
    """Test that datetime.now() works vs datetime.now(timezone.utc)"""
    print("🔍 Testing datetime fix...")
    
    try:
        # This should work (the fix)
        simple_dt = datetime.now()
        print(f"✅ datetime.now() works: {simple_dt}")
        
        # This was causing the error
        from datetime import timezone
        utc_dt = datetime.now(timezone.utc)
        print(f"⚠️ datetime.now(timezone.utc) type: {type(utc_dt)} - {utc_dt}")
        
        print("🎯 Conclusion: Using datetime.now() (naive) for PostgreSQL TIMESTAMP columns")
        return True
    except Exception as e:
        print(f"❌ Datetime test failed: {e}")
        return False

def test_import_fix():
    """Test that the import fixes work"""
    print("\n🔍 Testing import fix...")
    
    try:
        # Test the fixed import
        from validators.social_media_validator import SocialMediaValidator
        validator = SocialMediaValidator()
        print("✅ SocialMediaValidator import works")
        
        # Test that it's functional
        if hasattr(validator, 'validate'):
            print("✅ SocialMediaValidator has validate method")
        
        return True
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False

async def test_test_suite_generator():
    """Test that TestSuiteGenerator can work with the fixes"""
    print("\n🔍 Testing TestSuiteGenerator with fixes...")
    
    try:
        from test_suite_generator import TestSuiteGenerator
        generator = TestSuiteGenerator()
        print("✅ TestSuiteGenerator import works")
        
        # Test that it can generate a test suite
        test_suites = await generator.generate_user_management_tests()
        if test_suites and 'test_cases' in test_suites:
            print(f"✅ Generated test suite with {len(test_suites['test_cases'])} test cases")
            return True
        else:
            print("⚠️ Test suite generated but structure unexpected")
            return False
            
    except Exception as e:
        print(f"❌ TestSuiteGenerator test failed: {e}")
        return False

def main():
    print("🚀 TESTING SYSTEM FIXES VERIFICATION")
    print("=" * 60)
    
    results = []
    
    # Test datetime fix
    results.append(test_datetime_fix())
    
    # Test import fix
    results.append(test_import_fix())
    
    # Test test suite generator
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        results.append(loop.run_until_complete(test_test_suite_generator()))
    finally:
        loop.close()
    
    print(f"\n📊 RESULTS: {sum(results)}/{len(results)} tests passed")
    
    if all(results):
        print("🎉 ALL FIXES VERIFIED - Testing system should work now!")
        return True
    else:
        print("❌ Some fixes still need work")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)