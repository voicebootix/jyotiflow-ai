#!/usr/bin/env python3
"""
🔧 JyotiFlow Database Constraint Fix Script
Fixes all database constraint and schema issues identified in deployment logs
"""

import os
import asyncio
import asyncpg
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseConstraintFixer:
    """Fixes database constraint and schema issues"""
    
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL")
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable is required")
    
    async def fix_all_constraints(self):
        """Fix all database constraint issues"""
        logger.info("🔧 Starting comprehensive database constraint fixes...")
        
        try:
            conn = await asyncpg.connect(self.database_url)
            
            # Fix in order of dependency
            await self._fix_sessions_table_constraints(conn)
            await self._fix_service_types_table(conn)
            await self._fix_service_tables_constraints(conn)
            await self._fix_missing_columns(conn)
            await self._fix_migration_dependencies(conn)
            
            await conn.close()
            logger.info("✅ All database constraint fixes completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Database constraint fix failed: {e}")
            return False
    
    async def _fix_sessions_table_constraints(self, conn):
        """Fix sessions table constraints for foreign key references"""
        logger.info("🔧 Fixing sessions table constraints...")
        
        try:
            # Ensure sessions table exists with proper structure
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    id SERIAL PRIMARY KEY,
                    session_id VARCHAR(100) UNIQUE NOT NULL,
                    user_email VARCHAR(255),
                    user_id TEXT,
                    service_type TEXT NOT NULL,
                    duration_minutes INTEGER DEFAULT 0,
                    credits_used INTEGER DEFAULT 0,
                    session_data TEXT,
                    question TEXT,
                    birth_details JSONB,
                    status VARCHAR(50) DEFAULT 'active',
                    result_summary TEXT,
                    full_result TEXT,
                    guidance TEXT,
                    avatar_video_url VARCHAR(500),
                    avatar_duration_seconds INTEGER,
                    avatar_generation_cost DECIMAL(10,2),
                    voice_synthesis_used BOOLEAN DEFAULT false,
                    avatar_quality VARCHAR(20) DEFAULT 'high',
                    original_price DECIMAL(10,2),
                    user_rating INTEGER CHECK (user_rating >= 1 AND user_rating <= 5),
                    user_feedback TEXT,
                    session_quality_score DECIMAL(3,2),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP
                );
            ''')
            
            # Add unique constraint on id if not exists (for foreign key references)
            await conn.execute('''
                DO $$ 
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM pg_constraint 
                        WHERE conname = 'sessions_id_unique'
                    ) THEN
                        ALTER TABLE sessions ADD CONSTRAINT sessions_id_unique UNIQUE (id);
                    END IF;
                END $$;
            ''')
            
            # Add unique constraint on session_id if not exists
            await conn.execute('''
                DO $$ 
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM pg_constraint 
                        WHERE conname = 'sessions_session_id_unique'
                    ) THEN
                        ALTER TABLE sessions ADD CONSTRAINT sessions_session_id_unique UNIQUE (session_id);
                    END IF;
                END $$;
            ''')
            
            logger.info("✅ Sessions table constraints fixed")
            
        except Exception as e:
            logger.error(f"❌ Failed to fix sessions table constraints: {e}")
    
    async def _fix_service_types_table(self, conn):
        """Fix service_types table ID generation and constraints"""
        logger.info("🔧 Fixing service_types table...")
        
        try:
            # Ensure service_types table exists with proper structure
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS service_types (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) UNIQUE NOT NULL,
                    description TEXT,
                    base_credits INTEGER NOT NULL DEFAULT 10,
                    duration_minutes INTEGER DEFAULT 15,
                    video_enabled BOOLEAN DEFAULT true,
                    knowledge_configuration JSONB DEFAULT '{}',
                    specialized_prompts JSONB DEFAULT '{}',
                    response_behavior JSONB DEFAULT '{}',
                    swami_persona_mode VARCHAR(100) DEFAULT 'general',
                    analysis_depth VARCHAR(50) DEFAULT 'standard',
                    icon VARCHAR(50) DEFAULT '🔮',
                    gradient_class VARCHAR(100) DEFAULT 'from-purple-500 to-indigo-600',
                    is_premium BOOLEAN DEFAULT false,
                    requires_birth_details BOOLEAN DEFAULT false,
                    supports_followup BOOLEAN DEFAULT true,
                    max_followup_questions INTEGER DEFAULT 3,
                    ai_model VARCHAR(50) DEFAULT 'gpt-4',
                    voice_enabled BOOLEAN DEFAULT true,
                    avatar_enabled BOOLEAN DEFAULT true,
                    category VARCHAR(50) DEFAULT 'guidance',
                    metadata JSONB DEFAULT '{}',
                    pricing_config JSONB DEFAULT '{}',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            ''')
            
            # Add unique constraint on name for ON CONFLICT clauses
            await conn.execute('''
                DO $$ 
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM pg_constraint 
                        WHERE conname = 'service_types_name_unique'
                    ) THEN
                        ALTER TABLE service_types ADD CONSTRAINT service_types_name_unique UNIQUE (name);
                    END IF;
                END $$;
            ''')
            
            # Ensure ID sequence exists and is properly set
            await conn.execute('''
                DO $$ 
                BEGIN
                    IF NOT EXISTS (SELECT 1 FROM pg_sequences WHERE sequencename = 'service_types_id_seq') THEN
                        CREATE SEQUENCE service_types_id_seq;
                        ALTER TABLE service_types ALTER COLUMN id SET DEFAULT nextval('service_types_id_seq');
                    END IF;
                END $$;
            ''')
            
            logger.info("✅ Service_types table fixed")
            
        except Exception as e:
            logger.error(f"❌ Failed to fix service_types table: {e}")
    
    async def _fix_service_tables_constraints(self, conn):
        """Fix constraints on all service-related tables"""
        logger.info("🔧 Fixing service tables constraints...")
        
        try:
            # Fix service_configurations table
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS service_configurations (
                    id SERIAL PRIMARY KEY,
                    service_name VARCHAR(100) UNIQUE NOT NULL,
                    base_credits INTEGER NOT NULL DEFAULT 10,
                    duration_minutes INTEGER DEFAULT 15,
                    video_enabled BOOLEAN DEFAULT true,
                    premium_features JSONB DEFAULT '{}',
                    ai_model VARCHAR(50) DEFAULT 'gpt-4',
                    voice_enabled BOOLEAN DEFAULT true,
                    avatar_enabled BOOLEAN DEFAULT true,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            ''')
            
            # Add unique constraint for ON CONFLICT
            await conn.execute('''
                DO $$ 
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM pg_constraint 
                        WHERE conname = 'service_configurations_service_name_unique'
                    ) THEN
                        ALTER TABLE service_configurations ADD CONSTRAINT service_configurations_service_name_unique UNIQUE (service_name);
                    END IF;
                END $$;
            ''')
            
            # Fix other service tables that might need unique constraints
            service_tables = [
                'ai_pricing_recommendations',
                'service_usage_logs', 
                'api_usage_metrics',
                'satsang_events',
                'satsang_donations',
                'satsang_attendees'
            ]
            
            for table in service_tables:
                # Add basic unique constraints where needed
                if table == 'api_usage_metrics':
                    await conn.execute(f'''
                        DO $$ 
                        BEGIN
                            IF NOT EXISTS (
                                SELECT 1 FROM pg_constraint 
                                WHERE conname = '{table}_unique_daily'
                            ) THEN
                                ALTER TABLE {table} ADD CONSTRAINT {table}_unique_daily UNIQUE (api_name, endpoint, date);
                            END IF;
                        EXCEPTION WHEN undefined_table THEN
                            -- Table doesn't exist yet, skip
                            NULL;
                        END $$;
                    ''')
                elif table == 'satsang_attendees':
                    await conn.execute(f'''
                        DO $$ 
                        BEGIN
                            IF NOT EXISTS (
                                SELECT 1 FROM pg_constraint 
                                WHERE conname = '{table}_unique_attendance'
                            ) THEN
                                ALTER TABLE {table} ADD CONSTRAINT {table}_unique_attendance UNIQUE (satsang_event_id, user_id);
                            END IF;
                        EXCEPTION WHEN undefined_table THEN
                            -- Table doesn't exist yet, skip
                            NULL;
                        END $$;
                    ''')
            
            logger.info("✅ Service tables constraints fixed")
            
        except Exception as e:
            logger.error(f"❌ Failed to fix service tables constraints: {e}")
    
    async def _fix_missing_columns(self, conn):
        """Fix missing columns that cause index creation failures"""
        logger.info("🔧 Fixing missing columns...")
        
        try:
            # Add service_type column to tables that need it
            tables_needing_service_type = [
                'service_usage_logs',
                'ai_pricing_recommendations'
            ]
            
            for table in tables_needing_service_type:
                await conn.execute(f'''
                    DO $$ 
                    BEGIN
                        IF NOT EXISTS (
                            SELECT 1 FROM information_schema.columns 
                            WHERE table_name = '{table}' AND column_name = 'service_type'
                        ) THEN
                            ALTER TABLE {table} ADD COLUMN service_type VARCHAR(100);
                        END IF;
                    EXCEPTION WHEN undefined_table THEN
                        -- Table doesn't exist yet, skip
                        NULL;
                    END $$;
                ''')
            
            # Add other commonly missing columns
            await conn.execute('''
                DO $$ 
                BEGIN
                    -- Add base_credits column to users if missing
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name = 'users' AND column_name = 'base_credits'
                    ) THEN
                        ALTER TABLE users ADD COLUMN base_credits INTEGER DEFAULT 0;
                    END IF;
                EXCEPTION WHEN undefined_table THEN
                    -- Table doesn't exist yet, skip
                    NULL;
                END $$;
            ''')
            
            logger.info("✅ Missing columns fixed")
            
        except Exception as e:
            logger.error(f"❌ Failed to fix missing columns: {e}")
    
    async def _fix_migration_dependencies(self, conn):
        """Fix migration dependencies and foreign key issues"""
        logger.info("🔧 Fixing migration dependencies...")
        
        try:
            # Ensure all referenced tables exist before creating foreign keys
            
            # Create users table if it doesn't exist (for foreign key references)
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    role VARCHAR(50) DEFAULT 'user',
                    credits INTEGER DEFAULT 0,
                    base_credits INTEGER DEFAULT 0,
                    phone VARCHAR(20),
                    birth_date DATE,
                    birth_time TIME,
                    birth_location VARCHAR(255),
                    spiritual_level VARCHAR(50) DEFAULT 'beginner',
                    preferred_language VARCHAR(10) DEFAULT 'en',
                    avatar_sessions_count INTEGER DEFAULT 0,
                    total_avatar_minutes INTEGER DEFAULT 0,
                    preferred_avatar_style VARCHAR(50) DEFAULT 'traditional',
                    voice_preference VARCHAR(50) DEFAULT 'compassionate',
                    video_quality_preference VARCHAR(20) DEFAULT 'high',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login_at TIMESTAMP
                );
            ''')
            
            # Add unique constraint on email for foreign key references
            await conn.execute('''
                DO $$ 
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM pg_constraint 
                        WHERE conname = 'users_email_unique'
                    ) THEN
                        ALTER TABLE users ADD CONSTRAINT users_email_unique UNIQUE (email);
                    END IF;
                END $$;
            ''')
            
            logger.info("✅ Migration dependencies fixed")
            
        except Exception as e:
            logger.error(f"❌ Failed to fix migration dependencies: {e}")

async def main():
    """Run the database constraint fixes"""
    fixer = DatabaseConstraintFixer()
    success = await fixer.fix_all_constraints()
    
    if success:
        print("✅ Database constraint fixes completed successfully!")
        return 0
    else:
        print("❌ Database constraint fixes failed!")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))

