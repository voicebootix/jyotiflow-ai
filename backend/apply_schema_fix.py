#!/usr/bin/env python3
"""
Apply schema fix migration for service_types table
This fixes the is_premium column issue and other missing columns
"""

import asyncio
import asyncpg
import os
from pathlib import Path

async def apply_schema_fix():
    """Apply the schema fix migration"""
    try:
        # Connect to database
        DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:password@localhost:5432/jyotiflow')
        conn = await asyncpg.connect(DATABASE_URL)
        
        print("🔧 Applying schema fix migration...")
        
        # Read the migration file
        migration_file = Path(__file__).parent / "migrations" / "001_align_service_types_schema.sql"
        if not migration_file.exists():
            print(f"❌ Migration file not found: {migration_file}")
            return False
        
        with open(migration_file, 'r') as f:
            migration_sql = f.read()
        
        # Apply the migration
        await conn.execute(migration_sql)
        print("✅ Schema fix migration applied successfully!")
        
        # Verify the fix by checking for is_premium column
        has_is_premium = await conn.fetchval("""
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'service_types' AND column_name = 'is_premium'
        """)
        
        if has_is_premium:
            print("✅ is_premium column now exists")
        else:
            print("❌ is_premium column still missing")
        
        # Check service_types count
        service_count = await conn.fetchval("SELECT COUNT(*) FROM service_types")
        print(f"📊 Service types count: {service_count}")
        
        # Check for display_name issues
        null_display_names = await conn.fetchval("""
            SELECT COUNT(*) FROM service_types WHERE display_name IS NULL
        """)
        print(f"🔍 Service types with null display_name: {null_display_names}")
        
        if null_display_names == 0:
            print("✅ All service types have display_name")
        else:
            print("⚠️ Some service types still have null display_name")
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Schema fix migration failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(apply_schema_fix())
    if success:
        print("🎉 Schema fix completed successfully!")
    else:
        print("💥 Schema fix failed!")