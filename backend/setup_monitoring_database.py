#!/usr/bin/env python3
"""
🗄️ MONITORING DATABASE SETUP
Sets up monitoring tables in your database
"""

import asyncio
import asyncpg
import os
import sys

async def create_monitoring_tables():
    """Create all monitoring tables"""
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL environment variable not set")
        print("Please set it to your PostgreSQL connection string")
        return False
        
    try:
        print("🚀 Connecting to database...")
        conn = await asyncpg.connect(database_url)
        
        print("📊 Creating monitoring tables...")
        
        # Create validation_sessions table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS validation_sessions (
                id SERIAL PRIMARY KEY,
                session_id VARCHAR(255) UNIQUE NOT NULL,
                user_id INTEGER,
                started_at TIMESTAMP DEFAULT NOW(),
                completed_at TIMESTAMP,
                overall_status VARCHAR(50),
                user_context JSONB,
                validation_results JSONB,
                created_at TIMESTAMP DEFAULT NOW()
            );
        """)
        print("✅ Created validation_sessions table")
        
        # Create integration_validations table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS integration_validations (
                id SERIAL PRIMARY KEY,
                session_id VARCHAR(255) NOT NULL,
                integration_name VARCHAR(100) NOT NULL,
                status VARCHAR(50) NOT NULL,
                response_time_ms INTEGER,
                error_message TEXT,
                validation_data JSONB,
                created_at TIMESTAMP DEFAULT NOW(),
                FOREIGN KEY (session_id) REFERENCES validation_sessions(session_id)
            );
        """)
        print("✅ Created integration_validations table")
        
        # Create business_logic_issues table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS business_logic_issues (
                id SERIAL PRIMARY KEY,
                session_id VARCHAR(255) NOT NULL,
                issue_type VARCHAR(100) NOT NULL,
                severity VARCHAR(20) NOT NULL,
                description TEXT,
                metadata JSONB,
                created_at TIMESTAMP DEFAULT NOW(),
                FOREIGN KEY (session_id) REFERENCES validation_sessions(session_id)
            );
        """)
        print("✅ Created business_logic_issues table")
        
        # Create context_snapshots table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS context_snapshots (
                id SERIAL PRIMARY KEY,
                session_id VARCHAR(255) NOT NULL,
                integration_point VARCHAR(100) NOT NULL,
                context_data JSONB NOT NULL,
                context_hash VARCHAR(64),
                created_at TIMESTAMP DEFAULT NOW(),
                FOREIGN KEY (session_id) REFERENCES validation_sessions(session_id)
            );
        """)
        print("✅ Created context_snapshots table")
        
        # Create monitoring_alerts table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS monitoring_alerts (
                id SERIAL PRIMARY KEY,
                alert_type VARCHAR(100) NOT NULL,
                severity VARCHAR(20) NOT NULL,
                integration_name VARCHAR(100),
                message TEXT NOT NULL,
                metadata JSONB,
                resolved BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT NOW()
            );
        """)
        print("✅ Created monitoring_alerts table")
        
        # Create social_media_validation_log table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS social_media_validation_log (
                id SERIAL PRIMARY KEY,
                platform VARCHAR(50) NOT NULL,
                validation_type VARCHAR(50) NOT NULL,
                status VARCHAR(20) NOT NULL,
                error_message TEXT,
                auto_fix_attempted BOOLEAN DEFAULT FALSE,
                auto_fix_result VARCHAR(50),
                metadata JSONB,
                created_at TIMESTAMP DEFAULT NOW()
            );
        """)
        print("✅ Created social_media_validation_log table")
        
        # Create indexes for performance
        print("\n🔧 Creating indexes...")
        
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_validation_sessions_user_id 
            ON validation_sessions(user_id);
        """)
        
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_validation_sessions_created_at 
            ON validation_sessions(created_at DESC);
        """)
        
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_integration_validations_session_id 
            ON integration_validations(session_id);
        """)
        
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_monitoring_alerts_created_at 
            ON monitoring_alerts(created_at DESC) 
            WHERE resolved = FALSE;
        """)
        
        print("✅ Created performance indexes")
        
        # Verify tables exist
        print("\n🔍 Verifying tables...")
        tables = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND (table_name LIKE '%validation%' 
                 OR table_name LIKE '%monitoring%'
                 OR table_name LIKE '%social_media_validation%')
            ORDER BY table_name;
        """)
        
        print("\n📋 Monitoring tables in database:")
        for table in tables:
            print(f"  ✅ {table['table_name']}")
            
        await conn.close()
        print("\n✅ Monitoring database setup complete!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error setting up database: {e}")
        return False

if __name__ == "__main__":
    # Check if DATABASE_URL is provided as argument
    if len(sys.argv) > 1:
        os.environ["DATABASE_URL"] = sys.argv[1]
        
    success = asyncio.run(create_monitoring_tables())
    sys.exit(0 if success else 1)