"""
Database Schema Fix Module
Handles schema inconsistencies during application startup
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)

async def fix_database_schema(db_pool) -> bool:
    """Fix database schema issues during startup"""
    try:
        logger.info("🔧 Applying database schema fixes...")
        
        async with db_pool.acquire() as conn:
            # Fix 1: Add missing columns to service_types table
            await _fix_service_types_columns(conn)
            
            # Fix 2: Add missing columns to credit_packages table
            await _fix_credit_packages_columns(conn)
            
            # Fix 3: Add missing columns to users table
            await _fix_users_columns(conn)
            
            # Fix 4: Update existing records with proper values
            await _update_existing_records(conn)
        
        logger.info("✅ Database schema fixes applied successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Database schema fix failed: {e}")
        return False

async def _fix_service_types_columns(conn):
    """Add missing columns to service_types table"""
    try:
        # Add missing columns with COALESCE to handle existing data
        await conn.execute("""
            ALTER TABLE service_types 
            ADD COLUMN IF NOT EXISTS display_name VARCHAR(200)
        """)
        
        await conn.execute("""
            ALTER TABLE service_types 
            ADD COLUMN IF NOT EXISTS description TEXT
        """)
        
        await conn.execute("""
            ALTER TABLE service_types 
            ADD COLUMN IF NOT EXISTS credits_required INTEGER DEFAULT 1
        """)
        
        await conn.execute("""
            ALTER TABLE service_types 
            ADD COLUMN IF NOT EXISTS price_usd DECIMAL(10,2) DEFAULT 0.0
        """)
        
        await conn.execute("""
            ALTER TABLE service_types 
            ADD COLUMN IF NOT EXISTS service_category VARCHAR(50) DEFAULT 'guidance'
        """)
        
        await conn.execute("""
            ALTER TABLE service_types 
            ADD COLUMN IF NOT EXISTS enabled BOOLEAN DEFAULT true
        """)
        
        await conn.execute("""
            ALTER TABLE service_types 
            ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true
        """)
        
        await conn.execute("""
            ALTER TABLE service_types 
            ADD COLUMN IF NOT EXISTS avatar_video_enabled BOOLEAN DEFAULT false
        """)
        
        await conn.execute("""
            ALTER TABLE service_types 
            ADD COLUMN IF NOT EXISTS live_chat_enabled BOOLEAN DEFAULT false
        """)
        
        await conn.execute("""
            ALTER TABLE service_types 
            ADD COLUMN IF NOT EXISTS icon VARCHAR(50) DEFAULT '🔮'
        """)
        
        await conn.execute("""
            ALTER TABLE service_types 
            ADD COLUMN IF NOT EXISTS color_gradient VARCHAR(100) DEFAULT 'from-purple-500 to-indigo-600'
        """)
        
        await conn.execute("""
            ALTER TABLE service_types 
            ADD COLUMN IF NOT EXISTS voice_enabled BOOLEAN DEFAULT false
        """)
        
        await conn.execute("""
            ALTER TABLE service_types 
            ADD COLUMN IF NOT EXISTS video_enabled BOOLEAN DEFAULT false
        """)
        
        await conn.execute("""
            ALTER TABLE service_types 
            ADD COLUMN IF NOT EXISTS interactive_enabled BOOLEAN DEFAULT false
        """)
        
        await conn.execute("""
            ALTER TABLE service_types 
            ADD COLUMN IF NOT EXISTS comprehensive_reading_enabled BOOLEAN DEFAULT false
        """)
        
        await conn.execute("""
            ALTER TABLE service_types 
            ADD COLUMN IF NOT EXISTS birth_chart_enabled BOOLEAN DEFAULT false
        """)
        
        await conn.execute("""
            ALTER TABLE service_types 
            ADD COLUMN IF NOT EXISTS remedies_enabled BOOLEAN DEFAULT false
        """)
        
        await conn.execute("""
            ALTER TABLE service_types 
            ADD COLUMN IF NOT EXISTS dynamic_pricing_enabled BOOLEAN DEFAULT false
        """)
        
        await conn.execute("""
            ALTER TABLE service_types 
            ADD COLUMN IF NOT EXISTS knowledge_domains TEXT[] DEFAULT '{}'
        """)
        
        await conn.execute("""
            ALTER TABLE service_types 
            ADD COLUMN IF NOT EXISTS persona_modes TEXT[] DEFAULT '{}'
        """)
        
        logger.info("✅ Service types columns fixed")
        
    except Exception as e:
        logger.warning(f"⚠️ Could not fix service_types columns: {e}")

async def _fix_credit_packages_columns(conn):
    """Add missing columns to credit_packages table"""
    try:
        await conn.execute("""
            ALTER TABLE credit_packages 
            ADD COLUMN IF NOT EXISTS description TEXT
        """)
        
        await conn.execute("""
            ALTER TABLE credit_packages 
            ADD COLUMN IF NOT EXISTS enabled BOOLEAN DEFAULT true
        """)
        
        await conn.execute("""
            ALTER TABLE credit_packages 
            ADD COLUMN IF NOT EXISTS bonus_credits INTEGER DEFAULT 0
        """)
        
        await conn.execute("""
            ALTER TABLE credit_packages 
            ADD COLUMN IF NOT EXISTS stripe_product_id VARCHAR(255)
        """)
        
        await conn.execute("""
            ALTER TABLE credit_packages 
            ADD COLUMN IF NOT EXISTS stripe_price_id VARCHAR(255)
        """)
        
        logger.info("✅ Credit packages columns fixed")
        
    except Exception as e:
        logger.warning(f"⚠️ Could not fix credit_packages columns: {e}")

async def _fix_users_columns(conn):
    """Add missing columns to users table"""
    try:
        await conn.execute("""
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS referral_code VARCHAR(50)
        """)
        
        await conn.execute("""
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS marketing_source VARCHAR(100)
        """)
        
        await conn.execute("""
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS timezone VARCHAR(50) DEFAULT 'Asia/Kolkata'
        """)
        
        await conn.execute("""
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS language VARCHAR(10) DEFAULT 'en'
        """)
        
        await conn.execute("""
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS total_sessions INTEGER DEFAULT 0
        """)
        
        await conn.execute("""
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS avatar_sessions_count INTEGER DEFAULT 0
        """)
        
        await conn.execute("""
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS total_avatar_minutes INTEGER DEFAULT 0
        """)
        
        await conn.execute("""
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS spiritual_level VARCHAR(50) DEFAULT 'beginner'
        """)
        
        await conn.execute("""
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS preferred_avatar_style VARCHAR(50) DEFAULT 'traditional'
        """)
        
        await conn.execute("""
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS voice_preference VARCHAR(50) DEFAULT 'compassionate'
        """)
        
        await conn.execute("""
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS video_quality_preference VARCHAR(20) DEFAULT 'high'
        """)
        
        logger.info("✅ Users columns fixed")
        
    except Exception as e:
        logger.warning(f"⚠️ Could not fix users columns: {e}")

async def _update_existing_records(conn):
    """Update existing records with proper values"""
    try:
        # Update service_types records
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
        
        # Update credit_packages records
        await conn.execute("""
            UPDATE credit_packages 
            SET 
                enabled = COALESCE(enabled, true),
                bonus_credits = COALESCE(bonus_credits, 0)
            WHERE enabled IS NULL OR bonus_credits IS NULL
        """)
        
        logger.info("✅ Existing records updated")
        
    except Exception as e:
        logger.warning(f"⚠️ Could not update existing records: {e}") 