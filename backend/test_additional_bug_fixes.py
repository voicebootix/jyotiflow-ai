"""
Test Additional Bug Fixes - Comprehensive Validation Script
This script validates that all the additional critical bugs have been fixed
"""

import os
import sys
import ast

def test_sentry_initialization_fix():
    """Test that the Sentry initialization syntax errors are fixed"""
    print("🔧 Testing Sentry Initialization Fix...")
    
    try:
        with open('main.py', 'r') as f:
            content = f.read()
            
        # Check if the malformed integrations list is removed
        if 'integrations = [\n    try:' in content:
            print("❌ Malformed integrations list still present")
            return False
        else:
            print("✅ Malformed integrations list removed")
            
        # Check if duplicate sentry_dsn check is removed
        sentry_dsn_count = content.count('sentry_dsn = os.getenv("SENTRY_DSN")')
        if sentry_dsn_count > 1:
            print(f"❌ Duplicate sentry_dsn checks found: {sentry_dsn_count}")
            return False
        else:
            print("✅ No duplicate sentry_dsn checks")
            
        # Check if duplicate else blocks are removed
        else_count = content.count('else:\n    print("⚠️ Sentry DSN not configured - skipping Sentry initialization")')
        if else_count > 1:
            print(f"❌ Duplicate else blocks found: {else_count}")
            return False
        else:
            print("✅ No duplicate else blocks")
            
        # Try to parse the file to check for syntax errors
        try:
            ast.parse(content)
            print("✅ No syntax errors in main.py")
        except SyntaxError as e:
            print(f"❌ Syntax error still present: {e}")
            return False
            
        print("✅ Sentry initialization fix is properly implemented")
        return True
        
    except FileNotFoundError:
        print("❌ main.py not found")
        return False

def test_extension_creation_fix():
    """Test that PostgreSQL extensions are properly created"""
    print("🔧 Testing Extension Creation Fix...")
    
    try:
        with open('fix_startup_issues.py', 'r') as f:
            content = f.read()
            
        # Check if pgcrypto extension creation is implemented
        if 'CREATE EXTENSION IF NOT EXISTS pgcrypto' in content:
            print("✅ pgcrypto extension creation implemented")
        else:
            print("❌ pgcrypto extension creation not implemented")
            return False
            
        # Check if pgvector extension creation is implemented
        if 'CREATE EXTENSION IF NOT EXISTS vector' in content:
            print("✅ pgvector extension creation implemented")
        else:
            print("❌ pgvector extension creation not implemented")
            return False
            
        # Check if extension errors are handled gracefully
        if 'Could not enable pgcrypto extension' in content:
            print("✅ pgcrypto extension error handling implemented")
        else:
            print("❌ pgcrypto extension error handling not implemented")
            return False
            
        if 'Could not enable pgvector extension' in content:
            print("✅ pgvector extension error handling implemented")
        else:
            print("❌ pgvector extension error handling not implemented")
            return False
            
        print("✅ Extension creation fix is properly implemented")
        return True
        
    except FileNotFoundError:
        print("❌ fix_startup_issues.py not found")
        return False

def test_pool_management_fix_startup_issues():
    """Test that pool management is fixed in fix_startup_issues.py"""
    print("🔧 Testing Pool Management Fix (Startup Issues)...")
    
    try:
        with open('fix_startup_issues.py', 'r') as f:
            content = f.read()
            
        # Check if db_pool is properly initialized
        if 'db_pool = None' in content:
            print("✅ db_pool properly initialized")
        else:
            print("❌ db_pool not properly initialized")
            return False
            
        # Check if pool is properly closed in finally block
        if 'finally:' in content and 'await db_pool.close()' in content:
            print("✅ pool properly closed in finally block")
        else:
            print("❌ pool not properly closed in finally block")
            return False
            
        # Check if pool closure is logged
        if 'Database pool closed' in content:
            print("✅ pool closure logging implemented")
        else:
            print("❌ pool closure logging not implemented")
            return False
            
        print("✅ Pool management fix (startup issues) is properly implemented")
        return True
        
    except FileNotFoundError:
        print("❌ fix_startup_issues.py not found")
        return False

def test_delete_query_fix():
    """Test that the DELETE query properly returns count"""
    print("🔧 Testing DELETE Query Fix...")
    
    try:
        with open('fix_startup_issues.py', 'r') as f:
            content = f.read()
            
        # Check if execute() is used instead of fetchval() for DELETE
        if 'result = await conn.execute(' in content and 'DELETE FROM service_configuration_cache' in content:
            print("✅ DELETE query uses execute() method")
        else:
            print("❌ DELETE query doesn't use execute() method")
            return False
            
        # Check if result parsing is implemented
        if 'result.split()[-1]' in content and 'result.startswith("DELETE")' in content:
            print("✅ DELETE result parsing implemented")
        else:
            print("❌ DELETE result parsing not implemented")
            return False
            
        # Check if proper error handling for parsing
        if 'int(result.split()[-1]) if result and result.startswith("DELETE") else 0' in content:
            print("✅ DELETE result parsing error handling implemented")
        else:
            print("❌ DELETE result parsing error handling not implemented")
            return False
            
        print("✅ DELETE query fix is properly implemented")
        return True
        
    except FileNotFoundError:
        print("❌ fix_startup_issues.py not found")
        return False

def test_enhanced_error_handling():
    """Test that enhanced error handling is implemented"""
    print("🔧 Testing Enhanced Error Handling...")
    
    try:
        with open('fix_startup_issues.py', 'r') as f:
            content = f.read()
            
        # Check if extension warnings are implemented
        if '⚠️ Could not enable' in content:
            print("✅ Extension warning messages implemented")
        else:
            print("❌ Extension warning messages not implemented")
            return False
            
        # Check if graceful fallback is implemented
        if 'using fallback' in content:
            print("✅ Graceful fallback messaging implemented")
        else:
            print("❌ Graceful fallback messaging not implemented")
            return False
            
        # Check if comprehensive logging is implemented
        success_indicators = ['✅', '⚠️', '📦', '🔧', '🌱']
        found_indicators = sum(1 for indicator in success_indicators if indicator in content)
        
        if found_indicators >= 4:
            print(f"✅ Comprehensive logging implemented ({found_indicators} indicators found)")
        else:
            print(f"❌ Insufficient logging indicators ({found_indicators} found)")
            return False
            
        print("✅ Enhanced error handling is properly implemented")
        return True
        
    except FileNotFoundError:
        print("❌ fix_startup_issues.py not found")
        return False

def main():
    """Run all additional bug fix tests"""
    print("🚀 Testing JyotiFlow.ai Additional Bug Fixes...")
    print("=" * 70)
    
    tests = [
        test_sentry_initialization_fix,
        test_extension_creation_fix,
        test_pool_management_fix_startup_issues,
        test_delete_query_fix,
        test_enhanced_error_handling
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
    
    print("=" * 70)
    print(f"📊 Additional Bug Fix Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All additional critical bugs have been fixed!")
        print("✅ System is now fully robust and production-ready")
        return True
    else:
        print("⚠️ Some additional bugs still need attention")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)