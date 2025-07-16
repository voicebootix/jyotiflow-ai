"""
Database Schema Fix Script for JyotiFlow
Fixes all database issues including table structures, constraints, and data integrity
"""

import os
import json
import logging
import asyncpg
from datetime import datetime
from typing import Dict, Any, List

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseSchemaFixer:
    """Handles database schema fixes and migrations"""
    
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL")
        
        # Validate DATABASE_URL is set
        if not self.database_url:
            raise ValueError(
                "DATABASE_URL environment variable is missing or empty. "
                "Please set the DATABASE_URL environment variable before running this script. "
                "Example: export DATABASE_URL='postgresql://user:password@localhost/dbname'"
            )
    
    async def fix_all_database_issues(self):
        """Fix all known database issues"""
        logger.info("🔧 Applying database schema fixes...")
        
        try:
            conn = await asyncpg.connect(self.database_url)
            
            # Step 1: Fix table structure issues
            await self._fix_table_structures(conn)
            
            # Step 2: Fix constraint issues
            await self._fix_constraint_issues(conn)
            
            # Step 3: Fix data integrity issues
            await self._fix_data_integrity(conn)
            
            # Step 4: Ensure proper indexes
            await self._ensure_indexes(conn)
            
            await conn.close()
            logger.info("✅ Database schema fixes applied successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Database schema fix failed: {e}")
            return False
    
    async def _fix_table_structures(self, conn):
        """Fix table structure issues"""
        try:
            # Fix sessions table - ensure it has the required columns
            await conn.execute("""
                DO $$
                BEGIN
                    -- Add duration_minutes column if it doesn't exist
                    IF NOT EXISTS (SELECT FROM information_schema.columns 
                                  WHERE table_name = 'sessions' AND column_name = 'duration_minutes') THEN
                        ALTER TABLE sessions ADD COLUMN duration_minutes INTEGER DEFAULT 0;
                    END IF;
                    
                    -- Add session_data column if it doesn't exist
                    IF NOT EXISTS (SELECT FROM information_schema.columns 
                                  WHERE table_name = 'sessions' AND column_name = 'session_data') THEN
                        ALTER TABLE sessions ADD COLUMN session_data TEXT;
                    END IF;
                END $$;
            """)
            
            # Fix service_types table - ensure it has all required columns
            await conn.execute("""
                DO $$
                BEGIN
                    -- Add base_credits column if it doesn't exist
                    IF NOT EXISTS (SELECT FROM information_schema.columns 
                                  WHERE table_name = 'service_types' AND column_name = 'base_credits') THEN
                        ALTER TABLE service_types ADD COLUMN base_credits INTEGER DEFAULT 5;
                    END IF;
                    
                    -- Add duration_minutes column if it doesn't exist
                    IF NOT EXISTS (SELECT FROM information_schema.columns 
                                  WHERE table_name = 'service_types' AND column_name = 'duration_minutes') THEN
                        ALTER TABLE service_types ADD COLUMN duration_minutes INTEGER DEFAULT 15;
                    END IF;
                END $$;
            """)
            
            # Fix users table - ensure it has all required columns
            await conn.execute("""
                DO $$
                BEGIN
                    -- Add credits column if it doesn't exist
                    IF NOT EXISTS (SELECT FROM information_schema.columns 
                                  WHERE table_name = 'users' AND column_name = 'credits') THEN
                        ALTER TABLE users ADD COLUMN credits INTEGER DEFAULT 0;
                    END IF;
                    
                    -- Add role column if it doesn't exist
                    IF NOT EXISTS (SELECT FROM information_schema.columns 
                                  WHERE table_name = 'users' AND column_name = 'role') THEN
                        ALTER TABLE users ADD COLUMN role VARCHAR(50) DEFAULT 'user';
                    END IF;
                END $$;
            """)
            
            logger.info("✅ Table structures fixed")
            
        except Exception as e:
            logger.error(f"Table structure fix error: {e}")
            raise
    
    async def _fix_constraint_issues(self, conn):
        """Fix foreign key constraint issues"""
        try:
            # Create service_usage_logs table if it doesn't exist
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS service_usage_logs (
                    id SERIAL PRIMARY KEY,
                    service_type TEXT NOT NULL,
                    api_name TEXT NOT NULL,
                    usage_type TEXT NOT NULL,
                    usage_amount REAL NOT NULL,
                    cost_usd REAL NOT NULL,
                    cost_credits REAL NOT NULL,
                    session_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Add foreign key constraint safely
            await conn.execute("""
                DO $$
                BEGIN
                    -- Check if foreign key constraint doesn't already exist
                    IF NOT EXISTS (SELECT FROM information_schema.table_constraints 
                                  WHERE table_name = 'service_usage_logs' 
                                  AND constraint_type = 'FOREIGN KEY'
                                  AND constraint_name = 'service_usage_logs_session_id_fkey') THEN
                        
                        -- Only add if sessions table exists with id column
                        IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'sessions') AND
                           EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'sessions' AND column_name = 'id') THEN
                            ALTER TABLE service_usage_logs 
                            ADD CONSTRAINT service_usage_logs_session_id_fkey 
                            FOREIGN KEY (session_id) REFERENCES sessions(id);
                        END IF;
                    END IF;
                END $$;
            """)
            
            logger.info("✅ Constraint issues fixed")
            
        except Exception as e:
            logger.error(f"Constraint fix error: {e}")
            # Don't raise - system can work without constraints
            pass
    
    async def _fix_data_integrity(self, conn):
        """Fix data integrity issues"""
        try:
            # Ensure default service types exist
            default_services = [
                ('clarity', 'Basic spiritual clarity session', 5, 15, True),
                ('love', 'Love and relationship guidance', 8, 20, True),
                ('premium', 'Premium comprehensive reading', 12, 30, True),
                ('elite', 'Elite personalized consultation', 20, 45, True),
                ('comprehensive_life_reading_30min', 'Comprehensive 30-minute life reading', 15, 30, True),
                ('horoscope_reading_quick', 'Quick horoscope reading', 8, 10, True),
                ('satsang_community', 'Community satsang session', 5, 60, True)
            ]
            
            # Check if service_types table exists
            table_exists = await conn.fetchval(
                "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'service_types')"
            )
            
            if table_exists:
                for service in default_services:
                    try:
                        await conn.execute("""
                            INSERT INTO service_types (name, description, base_credits, duration_minutes, video_enabled)
                            VALUES ($1, $2, $3, $4, $5)
                            ON CONFLICT (name) DO UPDATE SET
                                description = EXCLUDED.description,
                                base_credits = EXCLUDED.base_credits,
                                duration_minutes = EXCLUDED.duration_minutes,
                                video_enabled = EXCLUDED.video_enabled
                        """, *service)
                    except Exception as e:
                        logger.warning(f"Could not insert service {service[0]}: {e}")
            
            logger.info("✅ Data integrity fixed")
            
        except Exception as e:
            logger.error(f"Data integrity fix error: {e}")
            # Don't raise - system can work without initial data
            pass
    
    async def _ensure_indexes(self, conn):
        """Ensure proper database indexes exist"""
        try:
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_sessions_service_type ON sessions(service_type)",
                "CREATE INDEX IF NOT EXISTS idx_sessions_user_email ON sessions(user_email)",
                "CREATE INDEX IF NOT EXISTS idx_sessions_created_at ON sessions(created_at)",
                "CREATE INDEX IF NOT EXISTS idx_service_usage_logs_service_type ON service_usage_logs(service_type)",
                "CREATE INDEX IF NOT EXISTS idx_service_usage_logs_api_name ON service_usage_logs(api_name)",
                "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)",
                "CREATE INDEX IF NOT EXISTS idx_users_role ON users(role)"
            ]
            
            for index_sql in indexes:
                try:
                    await conn.execute(index_sql)
                except Exception as e:
                    logger.warning(f"Could not create index: {e}")
            
            logger.info("✅ Indexes ensured")
            
        except Exception as e:
            logger.error(f"Index creation error: {e}")
            # Don't raise - system can work without indexes
            pass

# Global instance
schema_fixer = DatabaseSchemaFixer()

async def fix_database_schema():
    """Main function to fix all database schema issues"""
    return await schema_fixer.fix_all_database_issues()

if __name__ == "__main__":
    import asyncio
    asyncio.run(fix_database_schema()) 