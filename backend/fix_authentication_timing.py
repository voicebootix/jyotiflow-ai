#!/usr/bin/env python3
"""
Fix Authentication Timing Issues
Investigates and fixes intermittent 401 errors in the monitoring system
"""

import asyncio
import asyncpg
import os
import json
from datetime import datetime, timezone, timedelta

DATABASE_URL = os.getenv("DATABASE_URL")

async def investigate_auth_timing_issues():
    """
    Investigate authentication timing issues that cause intermittent 401 errors
    """
    print("🔍 Investigating authentication timing issues...")
    
    if not DATABASE_URL:
        print("❌ DATABASE_URL not found")
        return
    
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        
        # Check JWT token expiration settings
        print("\n1. Checking JWT configuration...")
        
        # Look for users with admin role
        admin_users = await conn.fetch("""
            SELECT id, email, role, created_at, 
                   CASE WHEN is_active THEN 'Active' ELSE 'Inactive' END as status
            FROM users 
            WHERE role = 'admin'
            ORDER BY created_at DESC
        """)
        
        print(f"Found {len(admin_users)} admin users:")
        for user in admin_users:
            print(f"  - {user['email']} (ID: {user['id']}) - {user['status']}")
        
        # Check for any session or token tracking tables
        print("\n2. Checking for session tracking...")
        
        tables = await conn.fetch("""
            SELECT tablename FROM pg_tables 
            WHERE tablename ILIKE '%session%' OR tablename ILIKE '%token%'
            AND schemaname = 'public'
        """)
        
        for table in tables:
            count = await conn.fetchval(f"SELECT COUNT(*) FROM {table['tablename']}")
            print(f"  - {table['tablename']}: {count} records")
        
        # Check test execution sessions timing
        print("\n3. Analyzing test execution patterns...")
        
        # Check if test_execution_sessions table exists and has recent activity
        table_exists = await conn.fetchval("""
            SELECT EXISTS(
                SELECT 1 FROM information_schema.tables 
                WHERE table_name = 'test_execution_sessions'
            )
        """)
        
        if table_exists:
            recent_sessions = await conn.fetch("""
                SELECT session_id, test_type, status, started_at, 
                       triggered_by, environment
                FROM test_execution_sessions 
                WHERE started_at >= NOW() - INTERVAL '24 hours'
                ORDER BY started_at DESC
                LIMIT 10
            """)
            
            print(f"Recent test sessions (last 24h): {len(recent_sessions)}")
            for session in recent_sessions:
                print(f"  - {session['test_type']} ({session['status']}) at {session['started_at']}")
        else:
            print("  - test_execution_sessions table does not exist")
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ Error investigating auth issues: {e}")

async def create_auth_debugging_endpoint():
    """
    Create SQL for adding auth debugging capabilities
    """
    
    sql_script = """
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

-- Function to log auth events
CREATE OR REPLACE FUNCTION log_auth_event(
    p_event_type VARCHAR(50),
    p_user_id INTEGER DEFAULT NULL,
    p_email VARCHAR(255) DEFAULT NULL,
    p_ip_address INET DEFAULT NULL,
    p_user_agent TEXT DEFAULT NULL,
    p_endpoint VARCHAR(255) DEFAULT NULL,
    p_success BOOLEAN DEFAULT NULL,
    p_error_message TEXT DEFAULT NULL,
    p_token_expires_at TIMESTAMP DEFAULT NULL
) RETURNS VOID AS $$
BEGIN
    INSERT INTO auth_events (
        event_type, user_id, email, ip_address, user_agent, 
        endpoint, success, error_message, token_expires_at
    ) VALUES (
        p_event_type, p_user_id, p_email, p_ip_address, p_user_agent,
        p_endpoint, p_success, p_error_message, p_token_expires_at
    );
END;
$$ LANGUAGE plpgsql;

-- View for recent auth events
CREATE OR REPLACE VIEW recent_auth_events AS
SELECT 
    event_type,
    email,
    endpoint,
    success,
    error_message,
    created_at,
    CASE 
        WHEN token_expires_at IS NULL THEN 'No expiry'
        WHEN token_expires_at < NOW() THEN 'Expired'
        ELSE 'Valid'
    END as token_status
FROM auth_events 
WHERE created_at >= NOW() - INTERVAL '24 hours'
ORDER BY created_at DESC;

-- Check for authentication patterns
SELECT 
    event_type,
    COUNT(*) as count,
    AVG(CASE WHEN success THEN 1 ELSE 0 END) * 100 as success_rate
FROM auth_events 
WHERE created_at >= NOW() - INTERVAL '24 hours'
GROUP BY event_type
ORDER BY count DESC;
"""
    
    print("📝 Created SQL script for authentication debugging:")
    print(sql_script)
    
    # Save to file
    with open('backend/auth_debugging.sql', 'w') as f:
        f.write(sql_script)
    
    print("✅ Saved to backend/auth_debugging.sql")

async def fix_jwt_token_expiration():
    """
    Investigate JWT token expiration settings
    """
    print("\n🔧 Analyzing JWT token configuration...")
    
    # Check auth.py for JWT settings
    try:
        with open('backend/routers/auth.py', 'r') as f:
            auth_content = f.read()
            
        if 'JWT_EXPIRY_MINUTES = 60 * 24' in auth_content:
            print("✅ JWT tokens expire after 24 hours")
        else:
            print("⚠️ JWT expiration setting not found or different")
            
        # Look for token refresh logic
        if 'refresh' in auth_content.lower():
            print("✅ Token refresh logic may be present")
        else:
            print("⚠️ No token refresh logic found")
            
    except Exception as e:
        print(f"❌ Error reading auth configuration: {e}")

async def main():
    """Main function to run all investigations"""
    print("🚀 Starting Authentication Issues Investigation\n")
    
    await investigate_auth_timing_issues()
    await create_auth_debugging_endpoint()
    await fix_jwt_token_expiration()
    
    print("\n🎯 Investigation Complete!")
    print("\nRecommendations:")
    print("1. Run the SQL script: backend/auth_debugging.sql")
    print("2. Monitor auth_events table for patterns")
    print("3. Check JWT token expiration times")
    print("4. Implement token refresh mechanism if needed")

if __name__ == "__main__":
    asyncio.run(main())