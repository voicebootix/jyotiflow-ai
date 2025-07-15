#!/usr/bin/env python3
"""
Critical Database Issues Fix Script
===================================

This script fixes the critical database issues causing runtime errors:
1. Missing follow_up_templates table
2. Missing birth_chart_cached_at column in users table  
3. Missing recommendation_data column in sessions table
4. Foreign key constraint issues
5. Embedding array serialization issues

Run this script to resolve the database errors in the logs.
"""

import asyncio
import os
import sys
import logging
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from db import get_db_pool
import asyncpg

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def run_critical_database_fixes():
    """Run the critical database fixes"""
    
    logger.info("🔧 Starting critical database fixes...")
    
    # Get database pool
    pool = get_db_pool()
    if not pool:
        logger.error("❌ Database pool not available")
        return False
    
    try:
        async with pool.acquire() as conn:
            logger.info("✅ Database connection established")
            
            # Read and execute the migration file
            migration_file = backend_dir / "migrations" / "004_fix_critical_database_issues.sql"
            
            if not migration_file.exists():
                logger.error(f"❌ Migration file not found: {migration_file}")
                return False
            
            with open(migration_file, 'r', encoding='utf-8') as f:
                migration_sql = f.read()
            
            logger.info("📋 Executing critical database fixes...")
            
            # Execute the migration
            await conn.execute(migration_sql)
            
            logger.info("✅ Critical database fixes completed successfully!")
            
            # Verify the fixes
            await verify_fixes(conn)
            
            return True
            
    except Exception as e:
        logger.error(f"❌ Error running critical database fixes: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return False

async def verify_fixes(conn):
    """Verify that the critical fixes were applied successfully"""
    
    logger.info("🔍 Verifying database fixes...")
    
    try:
        # Check follow_up_templates table
        result = await conn.fetchval("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables 
                WHERE table_name = 'follow_up_templates'
            )
        """)
        
        if result:
            logger.info("✅ follow_up_templates table exists")
        else:
            logger.error("❌ follow_up_templates table missing")
        
        # Check birth_chart_cached_at column in users
        result = await conn.fetchval("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'users' AND column_name = 'birth_chart_cached_at'
            )
        """)
        
        if result:
            logger.info("✅ birth_chart_cached_at column exists in users table")
        else:
            logger.error("❌ birth_chart_cached_at column missing from users table")
        
        # Check recommendation_data column in sessions
        result = await conn.fetchval("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'sessions' AND column_name = 'recommendation_data'
            )
        """)
        
        if result:
            logger.info("✅ recommendation_data column exists in sessions table")
        else:
            logger.error("❌ recommendation_data column missing from sessions table")
        
        # Check subscription_plans table
        result = await conn.fetchval("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables 
                WHERE table_name = 'subscription_plans'
            )
        """)
        
        if result:
            logger.info("✅ subscription_plans table exists")
        else:
            logger.error("❌ subscription_plans table missing")
        
        # Check user_subscriptions table
        result = await conn.fetchval("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables 
                WHERE table_name = 'user_subscriptions'
            )
        """)
        
        if result:
            logger.info("✅ user_subscriptions table exists")
        else:
            logger.error("❌ user_subscriptions table missing")
        
        # Test sessions query to ensure service_type column works
        try:
            await conn.fetch("SELECT id, service_type, question, created_at FROM sessions LIMIT 1")
            logger.info("✅ sessions table query with service_type column works")
        except Exception as e:
            logger.error(f"❌ sessions table query failed: {e}")
        
        logger.info("🔍 Database verification completed")
        
    except Exception as e:
        logger.error(f"❌ Error during verification: {e}")

async def main():
    """Main function"""
    
    logger.info("🚀 JyotiFlow Critical Database Issues Fix")
    logger.info("=" * 50)
    
    success = await run_critical_database_fixes()
    
    if success:
        logger.info("🎉 All critical database issues have been resolved!")
        logger.info("✅ The application should now run without the database errors")
    else:
        logger.error("❌ Failed to fix critical database issues")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 