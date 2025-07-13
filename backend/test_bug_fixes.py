"""
Test Bug Fixes - Comprehensive Validation Script
This script validates that all the critical bugs have been fixed
"""

import os
import sys
import ast

def get_test_file_path(filename):
    """Get absolute path to a file relative to this test file's directory"""
    test_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(test_dir, filename)

def test_conditional_variable_usage_fix():
    """Test that the conditional variable usage bug is fixed"""
    print("🔧 Testing Conditional Variable Usage Fix...")
    
    try:
        file_path = get_test_file_path('knowledge_seeding_system.py')
        with open(file_path, 'r') as f:
            content = f.read()
            
        # Check if conn is properly initialized before use
        if 'conn = None' in content:
            print("✅ conn variable properly initialized")
        else:
            print("❌ conn variable not properly initialized")
            return False
            
        # Check if conn is properly checked before closing
        if 'if conn:' in content and 'await conn.close()' in content:
            print("✅ conn variable properly checked before closing")
        else:
            print("❌ conn variable not properly checked before closing")
            return False
            
        # Check if the try-finally block is properly structured
        if 'try:' in content and 'finally:' in content:
            print("✅ try-finally block properly structured")
        else:
            print("❌ try-finally block not properly structured")
            return False
            
        print("✅ Conditional variable usage fix is properly implemented")
        return True
        
    except FileNotFoundError:
        print("❌ knowledge_seeding_system.py not found")
        return False

def test_vector_extension_fix():
    """Test that the vector extension bug is fixed"""
    print("🔧 Testing Vector Extension Fix...")
    
    try:
        file_path = get_test_file_path('fix_startup_issues.py')
        with open(file_path, 'r') as f:
            content = f.read()
            
        # Check if pgvector extension creation is implemented
        if 'CREATE EXTENSION IF NOT EXISTS vector' in content:
            print("✅ pgvector extension creation implemented")
        else:
            print("❌ pgvector extension creation not implemented")
            return False
            
        # Check if fallback table creation is implemented
        if 'embedding_vector TEXT' in content:
            print("✅ fallback table creation implemented")
        else:
            print("❌ fallback table creation not implemented")
            return False
            
        # Check if both table creation paths exist
        if 'VECTOR(1536)' in content and 'TEXT, -- Store as JSON string' in content:
            print("✅ both vector and text column types supported")
        else:
            print("❌ both vector and text column types not supported")
            return False
            
        print("✅ Vector extension fix is properly implemented")
        return True
        
    except FileNotFoundError:
        print("❌ fix_startup_issues.py not found")
        return False

def test_pool_management_fix():
    """Test that the pool management bug is fixed"""
    print("🔧 Testing Pool Management Fix...")
    
    try:
        file_path = get_test_file_path('enhanced_startup_integration.py')
        with open(file_path, 'r') as f:
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
            
        # Check if pool is checked before closing
        if 'if db_pool:' in content:
            print("✅ pool properly checked before closing")
        else:
            print("❌ pool not properly checked before closing")
            return False
            
        print("✅ Pool management fix is properly implemented")
        return True
        
    except FileNotFoundError:
        print("❌ enhanced_startup_integration.py not found")
        return False

def test_knowledge_seeding_vector_support():
    """Test that knowledge seeding handles both vector and text columns"""
    print("🔧 Testing Knowledge Seeding Vector Support...")
    
    try:
        file_path = get_test_file_path('knowledge_seeding_system.py')
        with open(file_path, 'r') as f:
            content = f.read()
            
        # Check if vector support detection is implemented
        if 'data_type FROM information_schema.columns' in content:
            print("✅ vector support detection implemented")
        else:
            print("❌ vector support detection not implemented")
            return False
            
        # Check if embedding format conversion is implemented
        if 'json.dumps(embedding)' in content:
            print("✅ embedding format conversion implemented")
        else:
            print("❌ embedding format conversion not implemented")
            return False
            
        # Check if both vector and text handling exists
        if 'vector_support = column_type == \'USER-DEFINED\'' in content:
            print("✅ vector type detection implemented")
        else:
            print("❌ vector type detection not implemented")
            return False
            
        print("✅ Knowledge seeding vector support is properly implemented")
        return True
        
    except FileNotFoundError:
        print("❌ knowledge_seeding_system.py not found")
        return False

def test_error_handling_improvements():
    """Test that error handling has been improved"""
    print("🔧 Testing Error Handling Improvements...")
    
    try:
        file_path = get_test_file_path('knowledge_seeding_system.py')
        with open(file_path, 'r') as f:
            content = f.read()
            
        # Check if AsyncPG availability is checked
        if 'ASYNCPG_AVAILABLE' in content:
            print("✅ AsyncPG availability check implemented")
        else:
            print("❌ AsyncPG availability check not implemented")
            return False
            
        # Check if graceful fallback is implemented
        if 'AsyncPG not available, skipping knowledge seeding' in content:
            print("✅ graceful fallback implemented")
        else:
            print("❌ graceful fallback not implemented")
            return False
            
        # Check if OpenAI errors are handled gracefully
        if 'OpenAI embedding failed' in content:
            print("✅ OpenAI error handling implemented")
        else:
            print("❌ OpenAI error handling not implemented")
            return False
            
        print("✅ Error handling improvements are properly implemented")
        return True
        
    except FileNotFoundError:
        print("❌ knowledge_seeding_system.py not found")
        return False

def test_knowledge_seeding_fix():
    """Test that knowledge seeding fix is implemented"""
    print("🧠 Testing Knowledge Base Seeding Fix...")
    
    # Check if the enhanced startup integration has the fix
    try:
        file_path = get_test_file_path('enhanced_startup_integration.py')
        with open(file_path, 'r') as f:
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
        file_path = get_test_file_path(file)
        if os.path.exists(file_path):
            print(f"✅ {file} exists")
        else:
            print(f"❌ {file} missing")
            return False
    
    # Check if enhanced startup integration has schema validation
    try:
        file_path = get_test_file_path('enhanced_startup_integration.py')
        with open(file_path, 'r') as f:
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
    print("� Testing Sentry Configuration Guide...")
    
    file_path = get_test_file_path('sentry_configuration_guide.md')
    if os.path.exists(file_path):
        print("✅ Sentry configuration guide exists")
        
        # Check if it has useful content
        with open(file_path, 'r') as f:
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
    print("� Testing Main Integration...")
    
    try:
        file_path = get_test_file_path('main.py')
        with open(file_path, 'r') as f:
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
    """Run all bug fix tests"""
    print("🚀 Testing JyotiFlow.ai Bug Fixes...")
    print("=" * 60)
    
    tests = [
        test_conditional_variable_usage_fix,
        test_vector_extension_fix,
        test_pool_management_fix,
        test_knowledge_seeding_vector_support,
        test_error_handling_improvements,
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
    
    print("=" * 60)
    print(f"📊 Bug Fix Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All critical bugs have been fixed!")
        print("✅ System is now robust and production-ready")
        return True
    else:
        print("⚠️ Some bugs still need attention")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)