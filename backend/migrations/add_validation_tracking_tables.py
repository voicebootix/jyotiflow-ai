"""
📊 ADD VALIDATION TRACKING TABLES
Adds tables for monitoring integration validation results
"""

import asyncio
import asyncpg
import os
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def run_migration():
    """Add validation tracking tables to database"""
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        logger.error("DATABASE_URL not set")
        return False
    
    try:
        conn = await asyncpg.connect(database_url)
        
        logger.info("🚀 Adding validation tracking tables...")
        
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
                created_at TIMESTAMP DEFAULT NOW(),
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
        """)
        logger.info("✅ Created validation_sessions table")
        
        # Create integration_validations table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS integration_validations (
                id SERIAL PRIMARY KEY,
                session_id VARCHAR(255) NOT NULL,
                integration_name VARCHAR(100) NOT NULL,
                validation_type VARCHAR(100),
                status VARCHAR(50),
                expected_value TEXT,
                actual_value TEXT,
                error_message TEXT,
                validation_time TIMESTAMP DEFAULT NOW(),
                auto_fixed BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (session_id) REFERENCES validation_sessions(session_id)
            );
        """)
        logger.info("✅ Created integration_validations table")
        
        # Create index for performance
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_integration_validations_session 
            ON integration_validations(session_id);
        """)
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_integration_validations_time 
            ON integration_validations(validation_time);
        """)
        
        # Create business_logic_issues table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS business_logic_issues (
                id SERIAL PRIMARY KEY,
                session_id VARCHAR(255),
                issue_type VARCHAR(100),
                severity VARCHAR(50),
                description TEXT,
                auto_fixable BOOLEAN DEFAULT FALSE,
                fixed BOOLEAN DEFAULT FALSE,
                user_impact TEXT,
                created_at TIMESTAMP DEFAULT NOW(),
                FOREIGN KEY (session_id) REFERENCES validation_sessions(session_id)
            );
        """)
        logger.info("✅ Created business_logic_issues table")
        
        # Create context_snapshots table for debugging
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
        logger.info("✅ Created context_snapshots table")
        
        # Create monitoring_alerts table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS monitoring_alerts (
                id SERIAL PRIMARY KEY,
                alert_type VARCHAR(50) NOT NULL,
                severity VARCHAR(50) NOT NULL,
                message TEXT NOT NULL,
                details JSONB,
                acknowledged BOOLEAN DEFAULT FALSE,
                acknowledged_by VARCHAR(255),
                acknowledged_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT NOW()
            );
        """)
        logger.info("✅ Created monitoring_alerts table")
        
        # Create social_media_validation_log table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS social_media_validation_log (
                id SERIAL PRIMARY KEY,
                platform VARCHAR(50) NOT NULL,
                validation_type VARCHAR(100) NOT NULL,
                status VARCHAR(50) NOT NULL,
                details JSONB,
                created_at TIMESTAMP DEFAULT NOW()
            );
        """)
        logger.info("✅ Created social_media_validation_log table")
        
        # Add columns to existing tables if they don't exist
        try:
            # Add validation_score to sessions table if not exists
            await conn.execute("""
                ALTER TABLE sessions 
                ADD COLUMN IF NOT EXISTS validation_score DECIMAL(5,2);
            """)
            logger.info("✅ Added validation_score column to sessions")
        except Exception as e:
            logger.warning(f"Could not add validation_score column: {e}")
        
        # Create views for monitoring dashboard
        await conn.execute("""
            CREATE OR REPLACE VIEW validation_summary AS
            SELECT 
                DATE(started_at) as date,
                COUNT(*) as total_sessions,
                COUNT(CASE WHEN overall_status = 'success' THEN 1 END) as successful_sessions,
                COUNT(CASE WHEN overall_status = 'failed' THEN 1 END) as failed_sessions,
                AVG(CASE WHEN overall_status = 'success' THEN 1 ELSE 0 END) * 100 as success_rate
            FROM validation_sessions
            WHERE started_at > NOW() - INTERVAL '30 days'
            GROUP BY DATE(started_at)
            ORDER BY date DESC;
        """)
        logger.info("✅ Created validation_summary view")
        
        await conn.execute("""
            CREATE OR REPLACE VIEW integration_health AS
            SELECT 
                integration_name,
                COUNT(*) as total_calls,
                COUNT(CASE WHEN status = 'success' THEN 1 END) as successful_calls,
                AVG(CASE WHEN status = 'success' THEN 1 ELSE 0 END) * 100 as success_rate,
                COUNT(CASE WHEN auto_fixed = true THEN 1 END) as auto_fixed_count
            FROM integration_validations
            WHERE validation_time > NOW() - INTERVAL '24 hours'
            GROUP BY integration_name;
        """)
        logger.info("✅ Created integration_health view")
        
        # Record migration
        await conn.execute("""
            INSERT INTO schema_migrations (migration_name, checksum)
            VALUES ($1, $2)
            ON CONFLICT (migration_name) DO NOTHING
        """, 'add_validation_tracking_tables', 'v1.0')
        
        await conn.close()
        
        logger.info("✅ Validation tracking tables migration completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {str(e)}")
        return False

if __name__ == "__main__":
    asyncio.run(run_migration())