#!/usr/bin/env python3
"""
Deploy Test System Fixes
Applies comprehensive fixes to the self-testing and self-healing system
"""

import asyncio
import asyncpg
import os
import sys
from pathlib import Path

DATABASE_URL = os.getenv("DATABASE_URL")

async def apply_database_schema_fixes():
    """Apply database schema fixes for test execution system"""
    print("🔧 Applying database schema fixes...")
    
    if not DATABASE_URL:
        print("❌ DATABASE_URL not found")
        return False
    
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        
        # Read and execute the schema fix SQL
        schema_sql = Path("backend/fix_test_execution_system.sql").read_text()
        
        # Execute the schema fixes
        await conn.execute(schema_sql)
        print("✅ Database schema fixes applied successfully")
        
        # Verify the changes
        columns = await conn.fetch("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'test_execution_sessions' 
            ORDER BY ordinal_position
        """)
        
        print(f"✅ Verified test_execution_sessions table has {len(columns)} columns:")
        for col in columns:
            print(f"  - {col['column_name']} ({col['data_type']})")
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error applying database fixes: {e}")
        return False

async def apply_authentication_debugging():
    """Apply authentication debugging enhancements"""
    print("🔧 Setting up authentication debugging...")
    
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        
        # Create auth debugging SQL
        auth_sql = """
-- Authentication Debugging and Monitoring
-- Add logging for authentication events

-- Create auth_events table for debugging
CREATE TABLE IF NOT EXISTS auth_events (
    id SERIAL PRIMARY KEY,
    event_type VARCHAR(50) NOT NULL,
    user_id INTEGER,
    email VARCHAR(255),
    ip_address INET,
    user_agent TEXT,
    endpoint VARCHAR(255),
    success BOOLEAN,
    error_message TEXT,
    token_expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create index for performance
CREATE INDEX IF NOT EXISTS idx_auth_events_created_at ON auth_events(created_at);
CREATE INDEX IF NOT EXISTS idx_auth_events_user_id ON auth_events(user_id);
CREATE INDEX IF NOT EXISTS idx_auth_events_success ON auth_events(success);
"""
        
        await conn.execute(auth_sql)
        print("✅ Authentication debugging setup complete")
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error setting up auth debugging: {e}")
        return False

def verify_code_fixes():
    """Verify that code fixes have been applied"""
    print("🔧 Verifying code fixes...")
    
    fixes_verified = []
    
    # Check test execution engine fixes
    try:
        with open('backend/test_execution_engine.py', 'r') as f:
            content = f.read()
            
        if '__import__' in content and '_is_safe_test_module' in content:
            fixes_verified.append("✅ Test execution engine security fixes applied")
        else:
            fixes_verified.append("❌ Test execution engine fixes missing")
            
    except Exception as e:
        fixes_verified.append(f"❌ Error checking test execution engine: {e}")
    
    # Print verification results
    for fix in fixes_verified:
        print(fix)
    
    return all("✅" in fix for fix in fixes_verified)

async def test_system_functionality():
    """Test that the fixes work"""
    print("🧪 Testing system functionality...")
    
    try:
        # Test database connectivity
        conn = await asyncpg.connect(DATABASE_URL)
        
        # Check if we can insert a test session
        test_session_id = "test-deploy-" + str(asyncio.get_event_loop().time())
        
        await conn.execute("""
            INSERT INTO test_execution_sessions (
                session_id, test_type, test_category, environment, 
                status, triggered_by, error_message
            ) VALUES ($1, $2, $3, $4, $5, $6, $7)
        """, test_session_id, "deployment", "system", "production", 
            "completed", "deployment_test", "Test deployment successful")
        
        print("✅ Test session creation successful")
        
        # Clean up test record
        await conn.execute("""
            DELETE FROM test_execution_sessions 
            WHERE session_id = $1
        """, test_session_id)
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f"❌ System functionality test failed: {e}")
        return False

async def create_monitoring_summary():
    """Create a summary of the monitoring system status"""
    print("📊 Creating monitoring system summary...")
    
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        
        # Get system statistics
        stats = {}
        
        # Count test sessions
        stats['total_test_sessions'] = await conn.fetchval("""
            SELECT COUNT(*) FROM test_execution_sessions
        """) or 0
        
        # Count recent sessions (last 24h)
        stats['recent_test_sessions'] = await conn.fetchval("""
            SELECT COUNT(*) FROM test_execution_sessions
            WHERE started_at >= NOW() - INTERVAL '24 hours'
        """) or 0
        
        # Count admin users
        stats['admin_users'] = await conn.fetchval("""
            SELECT COUNT(*) FROM users WHERE role = 'admin'
        """) or 0
        
        # Check table health
        tables_to_check = [
            'test_execution_sessions', 'users', 'integration_validations',
            'business_logic_issues', 'context_snapshots'
        ]
        
        stats['healthy_tables'] = 0
        for table in tables_to_check:
            exists = await conn.fetchval(f"""
                SELECT EXISTS(
                    SELECT 1 FROM information_schema.tables 
                    WHERE table_name = '{table}'
                )
            """)
            if exists:
                stats['healthy_tables'] += 1
        
        await conn.close()
        
        # Print summary
        print("📈 System Health Summary:")
        print(f"  - Total test sessions: {stats['total_test_sessions']}")
        print(f"  - Recent test sessions (24h): {stats['recent_test_sessions']}")
        print(f"  - Admin users: {stats['admin_users']}")
        print(f"  - Healthy database tables: {stats['healthy_tables']}/{len(tables_to_check)}")
        
        return stats
        
    except Exception as e:
        print(f"❌ Error creating monitoring summary: {e}")
        return {}

async def main():
    """Main deployment function"""
    print("🚀 Deploying Test System Fixes\n")
    
    success_count = 0
    total_steps = 5
    
    # Step 1: Apply database schema fixes
    if await apply_database_schema_fixes():
        success_count += 1
    
    # Step 2: Apply authentication debugging
    if await apply_authentication_debugging():
        success_count += 1
    
    # Step 3: Verify code fixes
    if verify_code_fixes():
        success_count += 1
    
    # Step 4: Test system functionality
    if await test_system_functionality():
        success_count += 1
    
    # Step 5: Create monitoring summary
    stats = await create_monitoring_summary()
    if stats:
        success_count += 1
    
    # Final report
    print(f"\n🎯 Deployment Complete: {success_count}/{total_steps} steps successful")
    
    if success_count == total_steps:
        print("✅ All fixes applied successfully!")
        print("\nThe self-testing and self-healing system should now work properly.")
        print("Next steps:")
        print("1. Restart the application to pick up code changes")
        print("2. Test the admin dashboard test execution")
        print("3. Monitor the auth_events table for authentication issues")
    else:
        print("⚠️ Some fixes failed to apply completely")
        print("Please check the error messages above and retry")
    
    return success_count == total_steps

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)