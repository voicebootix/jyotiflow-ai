#!/usr/bin/env python3
"""
🚨 RUN CRITICAL MIGRATION
Automatically fixes platform_settings table schema on app startup
"""

import os
import asyncio
import asyncpg
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def run_critical_migration():
    """Run the critical platform_settings schema fix migration"""
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        logger.warning("⚠️ DATABASE_URL not set - skipping migration")
        return False
    
    try:
        logger.info("🔗 Connecting to database for migration...")
        conn = await asyncpg.connect(database_url)
        
        # Read the migration file
        migration_file = Path(__file__).parent / "migrations" / "002_fix_platform_settings_schema.sql"
        
        if not migration_file.exists():
            logger.error(f"❌ Migration file not found: {migration_file}")
            return False
        
        logger.info("📝 Reading migration script...")
        with open(migration_file, 'r', encoding='utf-8') as f:
            migration_sql = f.read()
        
        logger.info("🔧 Applying critical schema fix migration...")
        
        # Execute migration (PostgreSQL can handle multiple statements)
        await conn.execute(migration_sql)
        
        # Verify the fix worked
        logger.info("🧪 Verifying migration...")
        
        # Test the exact query used by the backend
        test_row = await conn.fetchrow(
            "SELECT value FROM platform_settings WHERE key = $1",
            "youtube_credentials"
        )
        
        if test_row:
            logger.info("✅ Migration verification: Backend query works!")
        else:
            logger.warning("⚠️ youtube_credentials not found, but query structure is correct")
        
        # Check table structure
        columns = await conn.fetch("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'platform_settings'
            ORDER BY ordinal_position
        """)
        
        has_key = any(col['column_name'] == 'key' for col in columns)
        has_value = any(col['column_name'] == 'value' for col in columns)
        
        if has_key and has_value:
            logger.info("✅ Migration successful: Table has correct key/value structure")
        else:
            logger.error("❌ Migration failed: Table still has wrong structure")
            return False
        
        await conn.close()
        
        logger.info("🎉 CRITICAL MIGRATION COMPLETED SUCCESSFULLY!")
        logger.info("🎯 Social media platform configuration save should now work!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Critical migration failed: {e}")
        return False

async def check_if_migration_needed():
    """Check if the migration is needed"""
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        return False
    
    try:
        conn = await asyncpg.connect(database_url)
        
        # Check if table exists and has correct structure
        has_key_column = await conn.fetchval("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'platform_settings' 
                AND column_name = 'key'
            )
        """)
        
        has_platform_name = await conn.fetchval("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'platform_settings' 
                AND column_name = 'platform_name'
            )
        """)
        
        await conn.close()
        
        if has_platform_name and not has_key_column:
            logger.info("🚨 MIGRATION NEEDED: Wrong table structure detected")
            return True
        elif has_key_column:
            logger.info("✅ MIGRATION NOT NEEDED: Table already has correct structure")
            return False
        else:
            logger.info("🆕 NEW INSTALLATION: Table doesn't exist, migration will create it")
            return True
            
    except Exception as e:
        logger.warning(f"⚠️ Could not check migration status: {e}")
        return True  # Assume migration is needed if we can't check

if __name__ == "__main__":
    print("🚨 CRITICAL DATABASE MIGRATION CHECK")
    print("=" * 50)
    
    # Check if migration is needed
    migration_needed = asyncio.run(check_if_migration_needed())
    
    if migration_needed:
        print("\n🔧 RUNNING MIGRATION...")
        print("-" * 30)
        success = asyncio.run(run_critical_migration())
        
        if success:
            print("\n✅ MIGRATION COMPLETED SUCCESSFULLY!")
            print("🎯 Social media configuration save is now fixed!")
        else:
            print("\n❌ MIGRATION FAILED!")
            print("💡 Try manual fix using RENDER_DATABASE_FIX_GUIDE.md")
    else:
        print("\n✅ NO MIGRATION NEEDED")
        print("🎯 Database already has correct structure") 