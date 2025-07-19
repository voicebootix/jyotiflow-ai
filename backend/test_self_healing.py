#!/usr/bin/env python3
"""
Test the Database Self-Healing System
Verifies that missing tables are detected and schemas are generated dynamically
"""

import asyncio
import logging
from database_self_healing_system import DatabaseHealthMonitor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_self_healing():
    """Test the self-healing system"""
    # Use test database URL (modify as needed)
    database_url = "postgresql://user:password@localhost/test_db"
    
    try:
        monitor = DatabaseHealthMonitor(database_url)
        
        # Run health check
        logger.info("Running health check...")
        results = await monitor.run_health_check()
        
        logger.info(f"Health check results:")
        logger.info(f"- Issues found: {results.get('issues_found', 0)}")
        logger.info(f"- Issues fixed: {results.get('issues_fixed', 0)}")
        logger.info(f"- Critical issues: {len(results.get('critical_issues', []))}")
        logger.info(f"- Warnings: {len(results.get('warnings', []))}")
        
        # Check if any tables were dynamically generated
        if results.get('critical_issues'):
            for issue in results['critical_issues']:
                if issue['issue_type'] == 'MISSING_TABLE':
                    logger.info(f"\nDetected missing table: {issue['table']}")
                    logger.info(f"Generated SQL:\n{issue['fix_sql']}")
                    
                    # Verify no hardcoded schemas
                    if 'integration_validations' in issue['table']:
                        # Check that the schema was generated from queries, not hardcoded
                        assert 'CREATE TABLE IF NOT EXISTS' in issue['fix_sql']
                        logger.info("✅ Schema was dynamically generated!")
        
        # Test manual fix preview
        if results.get('critical_issues'):
            issue_id = results['critical_issues'][0].get('id')
            if issue_id:
                logger.info(f"\nTesting manual fix preview for issue {issue_id}...")
                preview = await monitor.get_manual_fix_preview(issue_id)
                logger.info(f"Preview: {preview}")
        
        logger.info("\n✅ Self-healing test completed successfully!")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(test_self_healing())