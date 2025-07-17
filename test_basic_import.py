#!/usr/bin/env python3
"""
Basic Import Test for Unified Startup System
Tests basic functionality without requiring external database connection
"""

import os
import sys
import json
import time
from typing import Dict, Any

# Add backend to path for imports
sys.path.insert(0, 'backend')

def test_unified_startup_import() -> Dict[str, Any]:
    """Test unified startup system import"""
    try:
        from unified_startup_system import initialize_unified_jyotiflow, cleanup_unified_system
        return {
            "test": "unified_startup_import",
            "status": "PASS",
            "details": "Successfully imported unified startup system functions"
        }
    except Exception as e:
        return {
            "test": "unified_startup_import",
            "status": "FAIL",
            "error": str(e),
            "details": "Failed to import unified startup system"
        }

def test_separate_systems_import() -> Dict[str, Any]:
    """Test importing the separate systems that need integration"""
    systems = {
        "integrate_self_healing": "backend/integrate_self_healing.py",
        "enhanced_startup_integration": "backend/enhanced_startup_integration.py",
        "fix_startup_issues": "backend/fix_startup_issues.py",
        "startup_database_validator": "backend/startup_database_validator.py"
    }
    
    results = {}
    
    for system_name, filepath in systems.items():
        try:
            # Check if file exists
            if not os.path.exists(filepath):
                results[system_name] = {
                    "status": "MISSING",
                    "details": f"File {filepath} does not exist"
                }
                continue
            
            # Try to import the module
            if system_name == "integrate_self_healing":
                from integrate_self_healing import integrate_self_healing
                results[system_name] = {"status": "PASS", "details": "Import successful"}
            elif system_name == "enhanced_startup_integration":
                from enhanced_startup_integration import EnhancedJyotiFlowStartup
                results[system_name] = {"status": "PASS", "details": "Import successful"}
            elif system_name == "fix_startup_issues":
                from fix_startup_issues import JyotiFlowStartupFixer
                results[system_name] = {"status": "PASS", "details": "Import successful"}
            elif system_name == "startup_database_validator":
                from startup_database_validator import StartupDatabaseValidator
                results[system_name] = {"status": "PASS", "details": "Import successful"}
                
        except Exception as e:
            results[system_name] = {
                "status": "FAIL",
                "error": str(e),
                "details": f"Failed to import {system_name}"
            }
    
    return {
        "test": "separate_systems_import",
        "results": results,
        "summary": f"{sum(1 for r in results.values() if r['status'] == 'PASS')}/{len(systems)} systems importable"
    }

def test_main_py_integration() -> Dict[str, Any]:
    """Test what's currently integrated in main.py"""
    try:
        with open('backend/main.py', 'r') as f:
            main_content = f.read()
        
        integrations = {
            "unified_startup_system": "initialize_unified_jyotiflow" in main_content,
            "self_healing": "integrate_self_healing" in main_content,
            "enhanced_startup": "EnhancedJyotiFlowStartup" in main_content,
            "startup_fixer": "JyotiFlowStartupFixer" in main_content,
            "database_validator": "StartupDatabaseValidator" in main_content,
            "health_router": "health_router" in main_content
        }
        
        integrated_count = sum(integrations.values())
        
        return {
            "test": "main_py_integration",
            "status": "INFO",
            "integrations": integrations,
            "details": f"{integrated_count}/{len(integrations)} systems integrated in main.py"
        }
    except Exception as e:
        return {
            "test": "main_py_integration",
            "status": "FAIL",
            "error": str(e),
            "details": "Failed to analyze main.py integration"
        }

def test_critical_files_exist() -> Dict[str, Any]:
    """Test that all critical files exist"""
    critical_files = [
        "backend/unified_startup_system.py",
        "backend/integrate_self_healing.py",
        "backend/enhanced_startup_integration.py",
        "backend/fix_startup_issues.py",
        "backend/startup_database_validator.py",
        "backend/database_self_healing_system.py",
        "backend/knowledge_seeding_system.py",
        "backend/main.py"
    ]
    
    existing_files = []
    missing_files = []
    
    for filepath in critical_files:
        if os.path.exists(filepath):
            existing_files.append(filepath)
        else:
            missing_files.append(filepath)
    
    return {
        "test": "critical_files_exist",
        "status": "PASS" if len(missing_files) == 0 else "PARTIAL",
        "existing_files": existing_files,
        "missing_files": missing_files,
        "details": f"{len(existing_files)}/{len(critical_files)} critical files exist"
    }

def run_all_basic_tests() -> Dict[str, Any]:
    """Run all basic tests"""
    print("🧪 BASIC FUNCTIONALITY TEST SUITE")
    print("=" * 50)
    
    start_time = time.time()
    
    tests = [
        test_unified_startup_import(),
        test_separate_systems_import(),
        test_main_py_integration(),
        test_critical_files_exist()
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
        
        # Print additional details for some tests
        if test_name == 'separate_systems_import' and 'results' in result:
            for system, sys_result in result['results'].items():
                status_emoji = "✅" if sys_result['status'] == 'PASS' else "❌" if sys_result['status'] == 'FAIL' else "⚠️"
                print(f"     {status_emoji} {system}: {sys_result['status']}")
        
        if test_name == 'main_py_integration' and 'integrations' in result:
            for integration, integrated in result['integrations'].items():
                status_emoji = "✅" if integrated else "❌"
                print(f"     {status_emoji} {integration}: {'INTEGRATED' if integrated else 'NOT INTEGRATED'}")
    
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
    print(f"📊 BASIC TEST SUMMARY:")
    print(f"   Total Tests: {summary['total_tests']}")
    print(f"   ✅ Passed: {summary['passed']}")
    print(f"   ❌ Failed: {summary['failed']}")
    print(f"   ⚠️ Partial: {summary['partial']}")
    print(f"   ℹ️ Info: {summary['info']}")
    print(f"   ⏱️ Total Time: {summary['total_time_seconds']} seconds")
    
    return summary

if __name__ == "__main__":
    results = run_all_basic_tests()
    
    # Save results to file for evidence
    with open('basic_test_results_before_integration.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Basic test results saved to: basic_test_results_before_integration.json")