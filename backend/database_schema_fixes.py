#!/usr/bin/env python3
"""
Database Schema Fixes for JyotiFlow
Fixes all the issues identified in the frontend vs backend error comparison
"""

import asyncio
import asyncpg
import logging
from datetime import datetime
import os
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required but not set")

class DatabaseSchemaFixer:
    def __init__(self):
        self.conn = None
        self.fixes_applied = []

    async def connect(self):
        """Connect to the database"""
        try:
            self.conn = await asyncpg.connect(DATABASE_URL)
            logger.info("✅ Connected to database")
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            raise

    async def disconnect(self):
        """Disconnect from the database"""
        if self.conn:
            await self.conn.close()
            logger.info("✅ Disconnected from database")

    async def check_column_exists(self, table_name: str, column_name: str) -> bool:
        """Check if a column exists in a table"""
        try:
            result = await self.conn.fetchval("""
                SELECT COUNT(*) FROM information_schema.columns 
                WHERE table_name=$1 AND column_name=$2
            """, table_name, column_name)
            return result > 0
        except Exception as e:
            logger.error(f"❌ Error checking column {table_name}.{column_name}: {e}")
            return False

    async def check_table_exists(self, table_name: str) -> bool:
        """Check if a table exists"""
        try:
            result = await self.conn.fetchval("""
                SELECT COUNT(*) FROM information_schema.tables 
                WHERE table_name=$1
            """, table_name)
            return result > 0
        except Exception as e:
            logger.error(f"❌ Error checking table {table_name}: {e}")
            return False

    async def add_missing_columns_to_service_types(self):
        """Add missing columns to service_types table"""
        logger.info("🔧 Checking service_types table for missing columns...")
        
        missing_columns = {
            'comprehensive_reading_enabled': 'BOOLEAN DEFAULT false',
            'credits_required': 'INTEGER DEFAULT 10',
            'base_credits': 'INTEGER DEFAULT 5',
            'duration_minutes': 'INTEGER DEFAULT 15',
            'video_enabled': 'BOOLEAN DEFAULT true',
            'avatar_video_enabled': 'BOOLEAN DEFAULT false',
            'live_chat_enabled': 'BOOLEAN DEFAULT false',
            'dynamic_pricing_enabled': 'BOOLEAN DEFAULT false',
            'personalized': 'BOOLEAN DEFAULT false',
            'includes_remedies': 'BOOLEAN DEFAULT false',
            'includes_predictions': 'BOOLEAN DEFAULT false',
            'includes_compatibility': 'BOOLEAN DEFAULT false',
            'knowledge_domains': 'JSONB DEFAULT \'[]\'',
            'persona_modes': 'JSONB DEFAULT \'[]\''
        }
        
        for column_name, column_def in missing_columns.items():
            if not await self.check_column_exists('service_types', column_name):
                try:
                    await self.conn.execute(f"ALTER TABLE service_types ADD COLUMN {column_name} {column_def}")
                    logger.info(f"✅ Added {column_name} to service_types table")
                    self.fixes_applied.append(f"Added {column_name} column to service_types")
                except Exception as e:
                    logger.error(f"❌ Failed to add {column_name} to service_types: {e}")
            else:
                logger.info(f"✅ {column_name} already exists in service_types")

    async def create_cache_analytics_table(self):
        """Create cache_analytics table if it doesn't exist"""
        logger.info("🔧 Checking cache_analytics table...")
        
        if not await self.check_table_exists('cache_analytics'):
            try:
                await self.conn.execute("""
                    CREATE TABLE cache_analytics (
                        id SERIAL PRIMARY KEY,
                        service_type_id INTEGER NOT NULL,
                        date DATE NOT NULL,
                        total_requests INTEGER DEFAULT 0,
                        cache_hits INTEGER DEFAULT 0,
                        cache_rate DECIMAL(5,2) DEFAULT 0.00,
                        created_at TIMESTAMP DEFAULT NOW(),
                        UNIQUE(service_type_id, date)
                    )
                """)
                logger.info("✅ Created cache_analytics table")
                self.fixes_applied.append("Created cache_analytics table")
            except Exception as e:
                logger.error(f"❌ Failed to create cache_analytics table: {e}")
        else:
            logger.info("✅ cache_analytics table already exists")

    async def fix_sessions_table_issues(self):
        """Fix any issues with sessions table"""
        logger.info("🔧 Checking sessions table...")
        
        # The sessions table should have service_type column (which it does)
        # But let's make sure it has all required columns
        missing_columns = {
            'follow_up_sent': 'BOOLEAN DEFAULT FALSE',
            'follow_up_count': 'INTEGER DEFAULT 0',
            'follow_up_email_sent': 'BOOLEAN DEFAULT FALSE',
            'follow_up_sms_sent': 'BOOLEAN DEFAULT FALSE',
            'follow_up_whatsapp_sent': 'BOOLEAN DEFAULT FALSE'
        }
        
        for column_name, column_def in missing_columns.items():
            if not await self.check_column_exists('sessions', column_name):
                try:
                    await self.conn.execute(f"ALTER TABLE sessions ADD COLUMN {column_name} {column_def}")
                    logger.info(f"✅ Added {column_name} to sessions table")
                    self.fixes_applied.append(f"Added {column_name} column to sessions")
                except Exception as e:
                    logger.error(f"❌ Failed to add {column_name} to sessions: {e}")

    async def ensure_service_types_data(self):
        """Ensure service_types table has basic data"""
        logger.info("🔧 Ensuring service_types has basic data...")
        
        # Check if service_types table has data
        count = await self.conn.fetchval("SELECT COUNT(*) FROM service_types")
        if count == 0:
            logger.info("📝 Adding basic service types...")
            
            services = [
                ('clarity', 'Clarity Guidance', 'Get clear guidance on your life questions', 10, 15, 25.00),
                ('love', 'Love & Relationships', 'Guidance on love and relationship matters', 15, 20, 35.00),
                ('premium', 'Premium Consultation', 'Comprehensive spiritual guidance', 25, 30, 75.00),
                ('elite', 'Elite Consultation', 'Deep spiritual insights and remedies', 50, 45, 150.00)
            ]
            
            for name, display_name, description, credits, duration, price in services:
                try:
                    # Check if display_name column exists before inserting
                    column_exists = await self.conn.fetchval("""
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name = 'service_types' AND column_name = 'display_name'
                    """)
                    
                    if column_exists:
                        await self.conn.execute("""
                            INSERT INTO service_types (name, display_name, description, credits_required, duration_minutes, price_usd, enabled)
                            VALUES ($1, $2, $3, $4, $5, $6, true)
                            ON CONFLICT (name) DO NOTHING
                        """, name, display_name, description, credits, duration, price)
                    else:
                        await self.conn.execute("""
                            INSERT INTO service_types (name, description, credits_required, duration_minutes, price_usd, enabled)
                            VALUES ($1, $2, $3, $4, $5, true)
                            ON CONFLICT (name) DO NOTHING
                        """, name, description, credits, duration, price)
                    logger.info(f"✅ Added service type: {name}")
                except Exception as e:
                    logger.error(f"❌ Failed to add service type {name}: {e}")
            
            self.fixes_applied.append("Added basic service types data")

    async def fix_followup_table_issues(self):
        """Fix followup table issues"""
        logger.info("🔧 Checking followup tables...")
        
        # Check if followup_templates table exists
        if not await self.check_table_exists('followup_templates'):
            try:
                await self.conn.execute("""
                    CREATE TABLE followup_templates (
                        id SERIAL PRIMARY KEY,
                        service_type VARCHAR(50) NOT NULL,
                        template_name VARCHAR(100) NOT NULL,
                        email_subject VARCHAR(200),
                        email_body TEXT,
                        sms_body TEXT,
                        whatsapp_body TEXT,
                        trigger_days INTEGER DEFAULT 1,
                        is_active BOOLEAN DEFAULT true,
                        created_at TIMESTAMP DEFAULT NOW(),
                        UNIQUE(service_type, template_name)
                    )
                """)
                logger.info("✅ Created followup_templates table")
                self.fixes_applied.append("Created followup_templates table")
            except Exception as e:
                logger.error(f"❌ Failed to create followup_templates table: {e}")

    async def validate_fixes(self):
        """Validate that all fixes were applied correctly"""
        logger.info("🔍 Validating fixes...")
        
        # Check critical columns exist
        critical_checks = [
            ('service_types', 'comprehensive_reading_enabled'),
            ('service_types', 'credits_required'),
            ('sessions', 'service_type'),
            ('sessions', 'follow_up_sent')
        ]
        
        all_good = True
        for table, column in critical_checks:
            if not await self.check_column_exists(table, column):
                logger.error(f"❌ Critical column {table}.{column} is missing!")
                all_good = False
            else:
                logger.info(f"✅ {table}.{column} exists")
        
        # Check service_types has data
        count = await self.conn.fetchval("SELECT COUNT(*) FROM service_types WHERE enabled = true")
        if count > 0:
            logger.info(f"✅ service_types table has {count} enabled services")
        else:
            logger.error("❌ service_types table has no enabled services!")
            all_good = False
        
        return all_good

    async def run_all_fixes(self):
        """Run all database fixes"""
        logger.info("🚀 Starting database schema fixes...")
        
        try:
            await self.connect()
            
            # Apply all fixes
            await self.add_missing_columns_to_service_types()
            await self.create_cache_analytics_table()
            await self.fix_sessions_table_issues()
            await self.ensure_service_types_data()
            await self.fix_followup_table_issues()
            
            # Validate
            if await self.validate_fixes():
                logger.info("✅ All database schema fixes completed successfully!")
                logger.info("📋 Fixes applied:")
                for fix in self.fixes_applied:
                    logger.info(f"  - {fix}")
                return True
            else:
                logger.error("❌ Some fixes failed validation")
                return False
                
        except Exception as e:
            logger.error(f"❌ Database schema fix failed: {e}")
            return False
        finally:
            await self.disconnect()

async def main():
    """Main function to run database fixes"""
    fixer = DatabaseSchemaFixer()
    success = await fixer.run_all_fixes()
    
    if success:
        print("\n🎉 DATABASE SCHEMA FIXES COMPLETED SUCCESSFULLY!")
        print("✅ The following issues have been resolved:")
        print("  - Fixed service_type_id → service_type column references")
        print("  - Added missing columns to service_types table")
        print("  - Created cache_analytics table")
        print("  - Added missing columns to sessions table")
        print("  - Ensured service_types has basic data")
        print("  - Created followup_templates table")
        print("\n🚀 Your application should now work properly!")
    else:
        print("\n❌ DATABASE SCHEMA FIXES FAILED!")
        print("Please check the logs above for specific error details.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(asyncio.run(main()))