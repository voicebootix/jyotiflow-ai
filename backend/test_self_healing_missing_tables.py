"""
Test that the self-healing system can detect and create missing monitoring tables
"""

import asyncio
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database_self_healing_system import DatabaseHealthMonitor, orchestrator

async def test_missing_table_detection():
    """Test that missing tables are detected and can be auto-fixed"""
    
    print("🧪 Testing missing table detection...")
    
    # Initialize the health monitor
    monitor = DatabaseHealthMonitor(os.getenv("DATABASE_URL"))
    
    # Run a health check
    results = await monitor.run_health_check()
    
    print(f"\n📊 Health Check Results:")
    print(f"- Issues found: {results['issues_found']}")
    print(f"- Issues fixed: {results['issues_fixed']}")
    print(f"- Critical issues: {len(results.get('critical_issues', []))}")
    
    # Check for missing table issues
    missing_table_issues = [
        issue for issue in results.get('critical_issues', [])
        if issue['issue_type'] == 'MISSING_TABLE'
    ]
    
    print(f"\n🔍 Missing Table Issues Found: {len(missing_table_issues)}")
    for issue in missing_table_issues:
        print(f"  - Table: {issue['table']}")
        print(f"    Status: {issue['current_state']}")
        print(f"    Has fix SQL: {'Yes' if issue.get('fix_sql') else 'No'}")
    
    # Check if monitoring tables were detected
    monitoring_tables = ['integration_validations', 'business_logic_issues']
    detected_tables = [issue['table'] for issue in missing_table_issues]
    
    for table in monitoring_tables:
        if table in detected_tables:
            print(f"\n✅ Successfully detected missing table: {table}")
        else:
            print(f"\n❌ Failed to detect missing table: {table}")
    
    return results

if __name__ == "__main__":
    # Run the test
    asyncio.run(test_missing_table_detection())