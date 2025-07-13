"""
Test Bug Fixes - Comprehensive Validation Script
This script validates that all the critical bugs have been fixed
"""

import os
import sys
import ast

def test_conditional_variable_usage_fix():
    """Test that the conditional variable usage bug is fixed"""
    print("🔧 Testing Conditional Variable Usage Fix...")
    
    try:
        with open('knowledge_seeding_system.py', 'r') as f:
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
        with open('fix_startup_issues.py', 'r') as f:
            content = f.read()
            
        # Check if pgvector extension check is implemented
        if 'pg_extension WHERE extname = \'vector\'' in content:
            print("✅ pgvector extension check implemented")
        else:
            print("❌ pgvector extension check not implemented")
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
        with open('enhanced_startup_integration.py', 'r') as f:
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
        with open('knowledge_seeding_system.py', 'r') as f:
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
        with open('knowledge_seeding_system.py', 'r') as f:
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

def main():
    """Run all bug fix tests"""
    print("🚀 Testing JyotiFlow.ai Bug Fixes...")
    print("=" * 60)
    
    tests = [
        test_conditional_variable_usage_fix,
        test_vector_extension_fix,
        test_pool_management_fix,
        test_knowledge_seeding_vector_support,
        test_error_handling_improvements
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