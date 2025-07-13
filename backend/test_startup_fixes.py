"""
Test Startup Fixes - Simple Validation Script
This script validates that the startup fixes are properly implemented
"""

import os
import sys

def test_knowledge_seeding_fix():
    """Test that knowledge seeding fix is implemented"""
    print("🧠 Testing Knowledge Base Seeding Fix...")
    
    # Check if the enhanced startup integration has the fix
    try:
        with open('enhanced_startup_integration.py', 'r') as f:
            content = f.read()
            
        if 'from knowledge_seeding_system import KnowledgeSeeder' in content:
            print("✅ Knowledge seeding import found")
        else:
            print("❌ Knowledge seeding import missing")
            return False
            
        if 'await seeder.seed_complete_knowledge_base()' in content:
            print("✅ Knowledge seeding call found")
        else:
            print("❌ Knowledge seeding call missing")
            return False
            
        print("✅ Knowledge base seeding fix is properly implemented")
        return True
        
    except FileNotFoundError:
        print("❌ enhanced_startup_integration.py not found")
        return False

def test_service_configuration_cache_fix():
    """Test that service configuration cache fix is implemented"""
    print("🔧 Testing Service Configuration Cache Fix...")
    
    # Check if the fix files exist
    fix_files = [
        'fix_service_configuration_cache.py',
        'fix_startup_issues.py'
    ]
    
    for file in fix_files:
        if os.path.exists(file):
            print(f"✅ {file} exists")
        else:
            print(f"❌ {file} missing")
            return False
    
    # Check if enhanced startup integration has schema validation
    try:
        with open('enhanced_startup_integration.py', 'r') as f:
            content = f.read()
            
        if '_fix_service_configuration_cache_schema' in content:
            print("✅ Schema validation method found")
        else:
            print("❌ Schema validation method missing")
            return False
            
        if 'cached_at' in content and 'expires_at' in content:
            print("✅ Column validation found")
        else:
            print("❌ Column validation missing")
            return False
            
        print("✅ Service configuration cache fix is properly implemented")
        return True
        
    except FileNotFoundError:
        print("❌ enhanced_startup_integration.py not found")
        return False

def test_sentry_configuration_guide():
    """Test that Sentry configuration guide exists"""
    print("📖 Testing Sentry Configuration Guide...")
    
    if os.path.exists('sentry_configuration_guide.md'):
        print("✅ Sentry configuration guide exists")
        
        # Check if it has useful content
        with open('sentry_configuration_guide.md', 'r') as f:
            content = f.read()
            
        if 'SENTRY_DSN' in content and 'sentry.io' in content:
            print("✅ Sentry guide has proper content")
            return True
        else:
            print("❌ Sentry guide content incomplete")
            return False
    else:
        print("❌ Sentry configuration guide missing")
        return False

def test_main_integration():
    """Test that main.py has the fixes integrated"""
    print("🔗 Testing Main Integration...")
    
    try:
        with open('main.py', 'r') as f:
            content = f.read()
            
        if 'JyotiFlowStartupFixer' in content:
            print("✅ Startup fixer import found")
        else:
            print("❌ Startup fixer import missing")
            return False
            
        if 'await startup_fixer.fix_all_issues()' in content:
            print("✅ Startup fixer call found")
        else:
            print("❌ Startup fixer call missing")
            return False
            
        print("✅ Main integration is properly implemented")
        return True
        
    except FileNotFoundError:
        print("❌ main.py not found")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing JyotiFlow.ai Startup Fixes...")
    print("=" * 50)
    
    tests = [
        test_knowledge_seeding_fix,
        test_service_configuration_cache_fix,
        test_sentry_configuration_guide,
        test_main_integration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All startup fixes are properly implemented!")
        return True
    else:
        print("⚠️ Some fixes need attention")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)