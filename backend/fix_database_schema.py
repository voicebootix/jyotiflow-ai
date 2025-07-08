#!/usr/bin/env python3
"""
Database Schema Fix Script for JyotiFlow
Fixes schema inconsistencies and ensures all tables have the correct structure
"""

import os
import asyncpg
import logging
from datetime import datetime, timezone

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseSchemaFixer:
    """Handles database schema fixes and migrations"""
    
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL", "postgresql://jyotiflow_db_user:em0MmaZmvPzASryvzLHpR5g5rRZTQqpw@dpg-d12ohqemcj7s73fjbqtg-a/jyotiflow_db")
        
    async def fix_database_schema(self):
        """Fix database schema inconsistencies"""
        logger.info("🔧 Starting database schema fixes...")
        
        try:
            conn = await asyncpg.connect(self.database_url)
            
            # Step 1: Fix users table
            await self._fix_users_table(conn)
            
            # Step 2: Fix service_types table
            await self._fix_service_types_table(conn)
            
            # Step 3: Fix credit_packages table
            await self._fix_credit_packages_table(conn)
            
            # Step 4: Fix foreign key constraints
            await self._fix_foreign_key_constraints(conn)
            
            # Step 5: Add missing columns
            await self._add_missing_columns(conn)
            
            await conn.close()
            logger.info("✅ Database schema fixes completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Database schema fix failed: {e}")
            return False
    
    async def _fix_users_table(self, conn):
        """Fix users table structure"""
        logger.info("Fixing users table...")
        
        # Add missing columns if they don't exist
        columns_to_add = [
            ("referral_code", "VARCHAR(50)"),
            ("marketing_source", "VARCHAR(100)"),
            ("timezone", "VARCHAR(50) DEFAULT 'Asia/Kolkata'"),
            ("language", "VARCHAR(10) DEFAULT 'en'"),
            ("total_sessions", "INTEGER DEFAULT 0"),
            ("avatar_sessions_count", "INTEGER DEFAULT 0"),
            ("total_avatar_minutes", "INTEGER DEFAULT 0"),
            ("spiritual_level", "VARCHAR(50) DEFAULT 'beginner'"),
            ("preferred_avatar_style", "VARCHAR(50) DEFAULT 'traditional'"),
            ("voice_preference", "VARCHAR(50) DEFAULT 'compassionate'"),
            ("video_quality_preference", "VARCHAR(20) DEFAULT 'high'")
        ]
        
        for column_name, column_type in columns_to_add:
            try:
                await conn.execute(f"""
                    ALTER TABLE users 
                    ADD COLUMN IF NOT EXISTS {column_name} {column_type}
                """)
                logger.info(f"✅ Added column {column_name} to users table")
            except Exception as e:
                logger.warning(f"⚠️ Could not add column {column_name}: {e}")
    
    async def _fix_service_types_table(self, conn):
        """Fix service_types table structure"""
        logger.info("Fixing service_types table...")
        
        # Add missing columns if they don't exist
        columns_to_add = [
            ("display_name", "VARCHAR(200)"),
            ("description", "TEXT"),
            ("credits_required", "INTEGER DEFAULT 1"),
            ("price_usd", "DECIMAL(10,2) DEFAULT 0.0"),
            ("service_category", "VARCHAR(50) DEFAULT 'guidance'"),
            ("is_active", "BOOLEAN DEFAULT true"),
            ("enabled", "BOOLEAN DEFAULT true"),
            ("avatar_video_enabled", "BOOLEAN DEFAULT false"),
            ("live_chat_enabled", "BOOLEAN DEFAULT false"),
            ("icon", "VARCHAR(50) DEFAULT '🔮'"),
            ("color_gradient", "VARCHAR(100) DEFAULT 'from-purple-500 to-indigo-600'"),
            ("voice_enabled", "BOOLEAN DEFAULT false"),
            ("video_enabled", "BOOLEAN DEFAULT false"),
            ("interactive_enabled", "BOOLEAN DEFAULT false"),
            ("comprehensive_reading_enabled", "BOOLEAN DEFAULT false"),
            ("birth_chart_enabled", "BOOLEAN DEFAULT false"),
            ("remedies_enabled", "BOOLEAN DEFAULT false"),
            ("dynamic_pricing_enabled", "BOOLEAN DEFAULT false"),
            ("knowledge_domains", "TEXT[] DEFAULT '{}'"),
            ("persona_modes", "TEXT[] DEFAULT '{}'")
        ]
        
        for column_name, column_type in columns_to_add:
            try:
                await conn.execute(f"""
                    ALTER TABLE service_types 
                    ADD COLUMN IF NOT EXISTS {column_name} {column_type}
                """)
                logger.info(f"✅ Added column {column_name} to service_types table")
            except Exception as e:
                logger.warning(f"⚠️ Could not add column {column_name}: {e}")
        
        # Update existing records to have proper values
        try:
            await conn.execute("""
                UPDATE service_types 
                SET 
                    display_name = COALESCE(display_name, name),
                    credits_required = COALESCE(credits_required, base_credits, 1),
                    price_usd = COALESCE(price_usd, 0.0),
                    enabled = COALESCE(enabled, true),
                    is_active = COALESCE(is_active, true)
                WHERE display_name IS NULL OR credits_required IS NULL OR price_usd IS NULL
            """)
            logger.info("✅ Updated existing service_types records")
        except Exception as e:
            logger.warning(f"⚠️ Could not update service_types records: {e}")
    
    async def _fix_credit_packages_table(self, conn):
        """Fix credit_packages table structure"""
        logger.info("Fixing credit_packages table...")
        
        # Add missing columns if they don't exist
        columns_to_add = [
            ("description", "TEXT"),
            ("enabled", "BOOLEAN DEFAULT true"),
            ("stripe_product_id", "VARCHAR(255)"),
            ("stripe_price_id", "VARCHAR(255)"),
            ("bonus_credits", "INTEGER DEFAULT 0")
        ]
        
        for column_name, column_type in columns_to_add:
            try:
                await conn.execute(f"""
                    ALTER TABLE credit_packages 
                    ADD COLUMN IF NOT EXISTS {column_name} {column_type}
                """)
                logger.info(f"✅ Added column {column_name} to credit_packages table")
            except Exception as e:
                logger.warning(f"⚠️ Could not add column {column_name}: {e}")
    
    async def _fix_foreign_key_constraints(self, conn):
        """Fix foreign key constraints"""
        logger.info("Fixing foreign key constraints...")
        
        # Drop problematic foreign key constraints
        constraints_to_drop = [
            ("sessions", "user_email"),
            ("user_purchases", "user_email"),
            ("user_subscriptions", "user_email"),
            ("avatar_sessions", "user_email"),
            ("satsang_attendees", "user_email")
        ]
        
        for table, column in constraints_to_drop:
            try:
                # Get constraint name
                constraint_info = await conn.fetchrow("""
                    SELECT tc.constraint_name
                    FROM information_schema.table_constraints tc
                    JOIN information_schema.key_column_usage kcu 
                        ON tc.constraint_name = kcu.constraint_name
                    WHERE tc.table_name = $1 
                        AND kcu.column_name = $2 
                        AND tc.constraint_type = 'FOREIGN KEY'
                """, table, column)
                
                if constraint_info:
                    constraint_name = constraint_info['constraint_name']
                    await conn.execute(f"ALTER TABLE {table} DROP CONSTRAINT IF EXISTS {constraint_name}")
                    logger.info(f"✅ Dropped foreign key constraint on {table}.{column}")
            except Exception as e:
                logger.warning(f"⚠️ Could not drop foreign key constraint on {table}.{column}: {e}")
    
    async def _add_missing_columns(self, conn):
        """Add any other missing columns"""
        logger.info("Adding other missing columns...")
        
        # Add missing columns to various tables
        missing_columns = [
            ("sessions", "is_video", "BOOLEAN DEFAULT false"),
            ("sessions", "is_audio", "BOOLEAN DEFAULT false"),
            ("service_types", "is_video", "BOOLEAN DEFAULT false"),
            ("service_types", "is_audio", "BOOLEAN DEFAULT false")
        ]
        
        for table, column_name, column_type in missing_columns:
            try:
                await conn.execute(f"""
                    ALTER TABLE {table} 
                    ADD COLUMN IF NOT EXISTS {column_name} {column_type}
                """)
                logger.info(f"✅ Added column {column_name} to {table} table")
            except Exception as e:
                logger.warning(f"⚠️ Could not add column {column_name} to {table}: {e}")

async def main():
    """Main function to run database schema fixes"""
    print("🔧 JyotiFlow Database Schema Fix")
    print("=" * 50)
    
    try:
        fixer = DatabaseSchemaFixer()
        success = await fixer.fix_database_schema()
        
        if success:
            print("=" * 50)
            print("✅ Database schema fixes completed successfully!")
            print("🚀 JyotiFlow database is now ready!")
        else:
            print("=" * 50)
            print("❌ Database schema fixes failed!")
            print("Please check the error messages above.")
            
    except Exception as e:
        print(f"❌ Unexpected error during schema fix: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 