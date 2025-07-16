#!/usr/bin/env python3
"""
Integration Progress Test
Verifies that the unified startup system now includes integrated functionality
"""

import os
import sys
import json
import time
from typing import Dict, Any

# Add backend to path for imports
sys.path.insert(0, 'backend')

def test_unified_system_functions() -> Dict[str, Any]:
    """Test that new functions are present in unified system"""
    try:
        import unified_startup_system
        
        # Check for newly integrated functions
        new_functions = [
            '_ensure_knowledge_base_seeded',
            '_validate_database_structure',
            '_validate_required_tables',
            '_fix_missing_columns',
            '_get_missing_columns',
            '_ensure_required_data'
        ]
        
        found_functions = []
        missing_functions = []
        
        for func_name in new_functions:
            if hasattr(unified_startup_system.UnifiedJyotiFlowStartup, func_name):
                found_functions.append(func_name)
            else:
                missing_functions.append(func_name)
        
        return {
            "test": "unified_system_functions",
            "status": "PASS" if len(missing_functions) == 0 else "PARTIAL",
            "found_functions": found_functions,
            "missing_functions": missing_functions,
            "details": f"{len(found_functions)}/{len(new_functions)} integrated functions found"
        }
        
    except Exception as e:
        return {
            "test": "unified_system_functions",
            "status": "FAIL",
            "error": str(e),
            "details": "Failed to test unified system functions"
        }

def test_enhanced_tables_functionality() -> Dict[str, Any]:
    """Test that enhanced tables (RAG) are included"""
    try:
        with open('backend/unified_startup_system.py', 'r') as f:
            content = f.read()
        
        rag_features = {
            "rag_knowledge_base_table": "rag_knowledge_base" in content,
            "service_configuration_cache": "service_configuration_cache" in content,
            "knowledge_seeding": "_ensure_knowledge_base_seeded" in content,
            "embedding_vector_support": "embedding_vector" in content,
            "knowledge_seeder_import": "KnowledgeSeeder" in content
        }
        
        implemented_count = sum(rag_features.values())
        
        return {
            "test": "enhanced_tables_functionality",
            "status": "PASS" if implemented_count >= 4 else "PARTIAL",
            "rag_features": rag_features,
            "details": f"{implemented_count}/{len(rag_features)} RAG features implemented"
        }
        
    except Exception as e:
        return {
            "test": "enhanced_tables_functionality",
            "status": "FAIL",
            "error": str(e),
            "details": "Failed to check enhanced tables functionality"
        }

def test_database_validation_integration() -> Dict[str, Any]:
    """Test that database validation features are integrated"""
    try:
        with open('backend/unified_startup_system.py', 'r') as f:
            content = f.read()
        
        validation_features = {
            "structure_validation": "_validate_database_structure" in content,
            "table_validation": "_validate_required_tables" in content,
            "column_fixing": "_fix_missing_columns" in content,
            "missing_column_detection": "_get_missing_columns" in content,
            "required_data_check": "_ensure_required_data" in content,
            "validation_in_sequence": "Step 3.1: Validating critical database structure" in content
        }
        
        implemented_count = sum(validation_features.values())
        
        return {
            "test": "database_validation_integration",
            "status": "PASS" if implemented_count >= 5 else "PARTIAL",
            "validation_features": validation_features,
            "details": f"{implemented_count}/{len(validation_features)} validation features integrated"
        }
        
    except Exception as e:
        return {
            "test": "database_validation_integration",
            "status": "FAIL",
            "error": str(e),
            "details": "Failed to check database validation integration"
        }

def test_startup_sequence_updated() -> Dict[str, Any]:
    """Test that startup sequence includes new steps"""
    try:
        with open('backend/unified_startup_system.py', 'r') as f:
            content = f.read()
        
        sequence_features = {
            "knowledge_seeding_step": "Step 5/6: Ensuring knowledge base is seeded" in content,
            "validation_step": "Step 3.1: Validating critical database structure" in content,
            "six_step_sequence": "Step 6/6:" in content,
            "knowledge_seeding_function_called": "await self._ensure_knowledge_base_seeded()" in content,
            "validation_function_called": "await self._validate_database_structure()" in content
        }
        
        implemented_count = sum(sequence_features.values())
        
        return {
            "test": "startup_sequence_updated",
            "status": "PASS" if implemented_count >= 4 else "PARTIAL",
            "sequence_features": sequence_features,
            "details": f"{implemented_count}/{len(sequence_features)} sequence updates implemented"
        }
        
    except Exception as e:
        return {
            "test": "startup_sequence_updated",
            "status": "FAIL",
            "error": str(e),
            "details": "Failed to check startup sequence updates"
        }

def test_original_systems_still_exist() -> Dict[str, Any]:
    """Test that original separate systems still exist for reference"""
    systems = {
        "integrate_self_healing": "backend/integrate_self_healing.py",
        "enhanced_startup_integration": "backend/enhanced_startup_integration.py",
        "fix_startup_issues": "backend/fix_startup_issues.py",
        "startup_database_validator": "backend/startup_database_validator.py"
    }
    
    existing_systems = {}
    
    for system_name, filepath in systems.items():
        existing_systems[system_name] = os.path.exists(filepath)
    
    existing_count = sum(existing_systems.values())
    
    return {
        "test": "original_systems_still_exist",
        "status": "INFO",
        "existing_systems": existing_systems,
        "details": f"{existing_count}/{len(systems)} original systems still exist for reference"
    }

def run_integration_tests() -> Dict[str, Any]:
    """Run all integration tests"""
    print("🧪 INTEGRATION PROGRESS TEST SUITE")
    print("=" * 50)
    
    start_time = time.time()
    
    tests = [
        test_unified_system_functions(),
        test_enhanced_tables_functionality(),
        test_database_validation_integration(),
        test_startup_sequence_updated(),
        test_original_systems_still_exist()
    ]
    
    passed = 0
    failed = 0
    info = 0
    partial = 0
    
    for result in tests:
        status = result.get('status', 'UNKNOWN')
        test_name = result.get('test', 'unknown')
        
        if status == 'PASS':
            passed += 1
            print(f"✅ {test_name}: PASSED - {result.get('details', '')}")
        elif status == 'FAIL':
            failed += 1
            print(f"❌ {test_name}: FAILED - {result.get('details', '')}")
            if 'error' in result:
                print(f"   Error: {result['error']}")
        elif status == 'PARTIAL':
            partial += 1
            print(f"⚠️ {test_name}: PARTIAL - {result.get('details', '')}")
        elif status == 'INFO':
            info += 1
            print(f"ℹ️ {test_name}: INFO - {result.get('details', '')}")
        
        # Print detailed results for some tests
        if 'found_functions' in result:
            print(f"     Functions found: {', '.join(result['found_functions'])}")
            if result.get('missing_functions'):
                print(f"     Missing functions: {', '.join(result['missing_functions'])}")
        
        if 'rag_features' in result:
            for feature, implemented in result['rag_features'].items():
                status_emoji = "✅" if implemented else "❌"
                print(f"     {status_emoji} {feature}: {'IMPLEMENTED' if implemented else 'MISSING'}")
    
    total_time = time.time() - start_time
    
    summary = {
        "total_tests": len(tests),
        "passed": passed,
        "failed": failed,
        "partial": partial,
        "info": info,
        "total_time_seconds": round(total_time, 2),
        "detailed_results": tests,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    print("=" * 50)
    print(f"📊 INTEGRATION TEST SUMMARY:")
    print(f"   Total Tests: {summary['total_tests']}")
    print(f"   ✅ Passed: {summary['passed']}")
    print(f"   ❌ Failed: {summary['failed']}")
    print(f"   ⚠️ Partial: {summary['partial']}")
    print(f"   ℹ️ Info: {summary['info']}")
    print(f"   ⏱️ Total Time: {summary['total_time_seconds']} seconds")
    
    return summary

if __name__ == "__main__":
    results = run_integration_tests()
    
    # Save results to file for evidence
    with open('integration_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Integration test results saved to: integration_test_results.json")