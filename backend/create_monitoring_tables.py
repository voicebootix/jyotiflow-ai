#!/usr/bin/env python3
"""
Create monitoring system database tables
Run this to set up the Integration Monitoring System tables
"""

import asyncio
import os
import asyncpg
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL")

async def create_monitoring_tables():
    """Create all monitoring system tables"""
    if not DATABASE_URL:
        print("❌ DATABASE_URL environment variable is required")
        return False
    
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        
        # Create validation_sessions table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS validation_sessions (
                session_id VARCHAR(255) PRIMARY KEY,
                user_id INTEGER NOT NULL,
                service_type VARCHAR(100),
                spiritual_question TEXT,
                birth_details JSONB,
                started_at TIMESTAMP DEFAULT NOW(),
                completed_at TIMESTAMP,
                overall_status VARCHAR(50),
                issues_found INTEGER DEFAULT 0,
                auto_fixes_applied INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        print("✅ Created validation_sessions table")
        
        # Create integration_validations table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS integration_validations (
                id SERIAL PRIMARY KEY,
                session_id VARCHAR(255) NOT NULL,
                integration_point VARCHAR(100) NOT NULL,
                validation_time TIMESTAMP DEFAULT NOW(),
                status VARCHAR(50),
                response_time_ms INTEGER,
                validation_score NUMERIC(5,2),
                issues JSONB,
                auto_fixed BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT NOW(),
                FOREIGN KEY (session_id) REFERENCES validation_sessions(session_id)
            )
        """)
        print("✅ Created integration_validations table")
        
        # Create business_logic_issues table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS business_logic_issues (
                id SERIAL PRIMARY KEY,
                session_id VARCHAR(255) NOT NULL,
                issue_type VARCHAR(100),
                severity VARCHAR(20),
                description TEXT,
                context JSONB,
                resolved BOOLEAN DEFAULT FALSE,
                resolution_details TEXT,
                created_at TIMESTAMP DEFAULT NOW(),
                FOREIGN KEY (session_id) REFERENCES validation_sessions(session_id)
            )
        """)
        print("✅ Created business_logic_issues table")
        
        # Create context_snapshots table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS context_snapshots (
                id SERIAL PRIMARY KEY,
                session_id VARCHAR(255) NOT NULL,
                integration_point VARCHAR(100),
                snapshot_data JSONB,
                created_at TIMESTAMP DEFAULT NOW(),
                FOREIGN KEY (session_id) REFERENCES validation_sessions(session_id)
            )
        """)
        print("✅ Created context_snapshots table")
        
        # Create monitoring_alerts table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS monitoring_alerts (
                id SERIAL PRIMARY KEY,
                alert_type VARCHAR(100),
                severity VARCHAR(20),
                title VARCHAR(255),
                description TEXT,
                context JSONB,
                acknowledged BOOLEAN DEFAULT FALSE,
                acknowledged_by INTEGER,
                acknowledged_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        print("✅ Created monitoring_alerts table")
        
        # Create social_media_validation_log table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS social_media_validation_log (
                id SERIAL PRIMARY KEY,
                session_id VARCHAR(255),
                platform VARCHAR(50),
                validation_type VARCHAR(100),
                status VARCHAR(50),
                details JSONB,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        print("✅ Created social_media_validation_log table")
        
        # Create indexes for performance
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_integration_validations_session
            ON integration_validations(session_id);
        """)
        
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_integration_validations_time
            ON integration_validations(validation_time);
        """)
        
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_validation_sessions_user_id
            ON validation_sessions(user_id);
        """)
        
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_validation_sessions_created_at
            ON validation_sessions(created_at DESC);
        """)
        
        print("✅ Created performance indexes")
        
        await conn.close()
        print("\n✅ All monitoring tables created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating monitoring tables: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(create_monitoring_tables())