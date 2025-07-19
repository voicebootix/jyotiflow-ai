"""
Test the self-healing system's ability to discover and fix missing tables
"""

import asyncio
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database_self_healing_system import DatabaseHealthMonitor

async def test_discovery_flow():
    """Test the complete discovery and fix flow"""
    
    print("🧪 Testing self-healing discovery flow...")
    
    # Initialize monitor
    monitor = DatabaseHealthMonitor(os.getenv("DATABASE_URL"))
    
    # 1. Test schema discovery
    print("\n1️⃣ Testing schema discovery...")
    discovered_schemas = await monitor._discover_table_schemas()
    
    print(f"Discovered {len(discovered_schemas)} table schemas:")
    for table_name in sorted(discovered_schemas.keys()):
        if table_name in ['integration_validations', 'business_logic_issues', 'validation_sessions']:
            print(f"  ✅ {table_name}")
    
    # 2. Test migration search
    print("\n2️⃣ Testing migration search...")
    integration_schema = await monitor._find_create_table_in_migrations('integration_validations')
    if integration_schema:
        print(f"  ✅ Found integration_validations in migrations")
        print(f"  Schema length: {len(integration_schema)} chars")
        print(f"  Has indexes: {'CREATE INDEX' in integration_schema}")
    else:
        print(f"  ❌ Failed to find integration_validations in migrations")
    
    # 3. Test missing table detection
    print("\n3️⃣ Testing missing table detection...")
    
    # Get current schema
    import db
    pool = db.get_db_pool()
    if not pool:
        print("  ❌ No database pool available")
        return
        
    async with pool.acquire() as conn:
        # Get current tables
        tables = await conn.fetch("""
            SELECT tablename FROM pg_tables 
            WHERE schemaname = 'public'
        """)
        current_tables = {t['tablename'] for t in tables}
        
        print(f"  Current tables in DB: {len(current_tables)}")
        
        # Check if monitoring tables exist
        monitoring_tables = ['integration_validations', 'business_logic_issues', 
                           'validation_sessions', 'context_snapshots']
        
        missing = [t for t in monitoring_tables if t not in current_tables]
        if missing:
            print(f"  ⚠️  Missing tables: {missing}")
        else:
            print(f"  ✅ All monitoring tables exist")
    
    # 4. Run health check to see if issues are detected
    print("\n4️⃣ Running health check...")
    results = await monitor.run_health_check()
    
    print(f"  Total issues found: {results['issues_found']}")
    print(f"  Issues auto-fixed: {results['issues_fixed']}")
    
    # Check for MISSING_TABLE issues
    missing_table_issues = [
        issue for issue in results.get('critical_issues', [])
        if issue['issue_type'] == 'MISSING_TABLE'
    ]
    
    if missing_table_issues:
        print(f"  📋 Missing table issues detected: {len(missing_table_issues)}")
        for issue in missing_table_issues:
            has_fix = 'Yes' if issue.get('fix_sql') else 'No'
            print(f"    - {issue['table']} (has fix SQL: {has_fix})")
    
    return results

if __name__ == "__main__":
    asyncio.run(test_discovery_flow())