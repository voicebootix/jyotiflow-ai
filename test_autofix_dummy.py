#!/usr/bin/env python3
"""
Safe Auto-Fix Testing Script
Creates a dummy table with intentional issues to test the auto-fix system
"""

import asyncio
import asyncpg
import os
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL")

async def create_test_scenario():
    """Create a safe test scenario for auto-fix testing"""
    if not DATABASE_URL:
        print("❌ DATABASE_URL not found")
        return False
    
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        
        # Create a test table with intentional issues
        print("🧪 Creating test table 'autofix_test_dummy'...")
        
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS autofix_test_dummy (
                id SERIAL PRIMARY KEY,
                test_name VARCHAR(100),
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        
        # Insert test data
        await conn.execute("""
            INSERT INTO autofix_test_dummy (test_name) VALUES ('test1'), ('test2')
        """)
        
        # Now drop a column to create a "missing column" issue
        print("🔧 Creating intentional issue: dropping 'status' column that code expects...")
        
        # First add the column
        await conn.execute("""
            ALTER TABLE autofix_test_dummy ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'active'
        """)
        
        # Update test data
        await conn.execute("""
            UPDATE autofix_test_dummy SET status = 'test_status'
        """)
        
        # Now drop it to create an issue
        await conn.execute("""
            ALTER TABLE autofix_test_dummy DROP COLUMN IF EXISTS status
        """)
        
        print("✅ Test scenario created successfully")
        print("📊 Test table 'autofix_test_dummy' now has a missing 'status' column")
        print("🎯 Auto-fix system should detect this as a missing column issue")
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Failed to create test scenario: {e}")
        return False

async def cleanup_test_scenario():
    """Clean up the test scenario"""
    if not DATABASE_URL:
        print("❌ DATABASE_URL not found")
        return False
    
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        
        print("🧹 Cleaning up test table...")
        await conn.execute("DROP TABLE IF EXISTS autofix_test_dummy")
        
        print("✅ Test scenario cleaned up successfully")
        await conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Failed to cleanup test scenario: {e}")
        return False

async def verify_fix_applied():
    """Verify if the auto-fix was applied correctly"""
    if not DATABASE_URL:
        print("❌ DATABASE_URL not found")
        return False
    
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        
        # Check if status column exists
        result = await conn.fetchval("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'autofix_test_dummy' 
            AND column_name = 'status'
        """)
        
        if result:
            print("✅ Auto-fix SUCCESS: 'status' column has been restored!")
            
            # Check data integrity
            data = await conn.fetch("SELECT * FROM autofix_test_dummy")
            print(f"📊 Data integrity check: {len(data)} rows found")
            for row in data:
                print(f"   Row: {dict(row)}")
                
        else:
            print("❌ Auto-fix NOT APPLIED: 'status' column still missing")
        
        await conn.close()
        return bool(result)
        
    except Exception as e:
        print(f"❌ Failed to verify fix: {e}")
        return False

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "create":
            success = asyncio.run(create_test_scenario())
            sys.exit(0 if success else 1)
        elif sys.argv[1] == "cleanup":
            success = asyncio.run(cleanup_test_scenario())
            sys.exit(0 if success else 1)
        elif sys.argv[1] == "verify":
            success = asyncio.run(verify_fix_applied())
            sys.exit(0 if success else 1)
    
    print("Usage:")
    print("  python3 test_autofix_dummy.py create   # Create test scenario")
    print("  python3 test_autofix_dummy.py verify   # Verify if fix was applied")
    print("  python3 test_autofix_dummy.py cleanup  # Clean up test scenario")