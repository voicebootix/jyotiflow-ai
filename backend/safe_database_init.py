#!/usr/bin/env python3
"""
🚀 SAFE DATABASE INITIALIZATION - Production-Ready Approach
Creates tables ONLY if they don't exist. Never drops or destroys data.
"""

import asyncio
import asyncpg
import os
import logging
import bcrypt
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SafeDatabaseInitializer:
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL")
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable is required")
    
    async def initialize(self):
        """Initialize database safely without destroying existing data"""
        logger.info("🚀 Starting Safe Database Initialization...")
        
        conn = await asyncpg.connect(self.database_url)
        try:
            # Create schema_migrations table first
            await self._ensure_migrations_table(conn)
            
            # Check what tables already exist
            existing_tables = await self._get_existing_tables(conn)
            logger.info(f"📊 Found {len(existing_tables)} existing tables")
            
            # Create missing tables only
            await self._create_missing_tables(conn, existing_tables)
            
            # Apply column fixes
            await self._fix_column_issues(conn)
            
            # Ensure essential data
            await self._ensure_essential_data(conn)
            
            logger.info("✅ Safe Database Initialization Completed!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Safe initialization failed: {str(e)}")
            return False
        finally:
            await conn.close()
    
    async def _ensure_migrations_table(self, conn):
        """Ensure migrations tracking table exists"""
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                id SERIAL PRIMARY KEY,
                migration_name VARCHAR(255) UNIQUE NOT NULL,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                checksum VARCHAR(64)
            )
        """)
        logger.info("✅ Migrations table ready")
    
    async def _get_existing_tables(self, conn):
        """Get list of existing tables"""
        result = await conn.fetch("""
            SELECT tablename FROM pg_tables 
            WHERE schemaname = 'public' 
            AND tablename NOT LIKE 'pg_%'
        """)
        return {row['tablename'] for row in result}
    
    async def _create_missing_tables(self, conn, existing_tables):
        """Create only missing tables"""
        
        # Core tables
        if 'service_types' not in existing_tables:
            await conn.execute("""
                CREATE TABLE service_types (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) UNIQUE NOT NULL,
                    display_name VARCHAR(255) NOT NULL,
                    description TEXT,
                    category VARCHAR(100),
                    duration_minutes INTEGER DEFAULT 15,
                    credits_required INTEGER DEFAULT 5,
                    price_usd DECIMAL(10,2) DEFAULT 0,
                    base_credits INTEGER DEFAULT 5,
                    enabled BOOLEAN DEFAULT true,
                    service_category VARCHAR(100),
                    icon VARCHAR(50) DEFAULT '🔮',
                    color_gradient VARCHAR(100) DEFAULT 'from-purple-500 to-indigo-600',
                    gradient_class VARCHAR(100) DEFAULT 'from-purple-500 to-indigo-600',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    -- Enhanced fields
                    voice_enabled BOOLEAN DEFAULT true,
                    video_enabled BOOLEAN DEFAULT false,
                    interactive_enabled BOOLEAN DEFAULT false,
                    birth_chart_enabled BOOLEAN DEFAULT false,
                    remedies_enabled BOOLEAN DEFAULT false,
                    guidance BOOLEAN DEFAULT false,
                    premium BOOLEAN DEFAULT false,
                    active BOOLEAN DEFAULT true,
                    featured BOOLEAN DEFAULT false,
                    requires_birth_details BOOLEAN DEFAULT true,
                    ai_enhanced BOOLEAN DEFAULT false,
                    personalized BOOLEAN DEFAULT false,
                    includes_remedies BOOLEAN DEFAULT false,
                    includes_predictions BOOLEAN DEFAULT false,
                    includes_compatibility BOOLEAN DEFAULT false,
                    knowledge_domains JSONB DEFAULT '[]',
                    persona_modes JSONB DEFAULT '[]',
                    avatar_video_enabled BOOLEAN DEFAULT false,
                    live_chat_enabled BOOLEAN DEFAULT false,
                    dynamic_pricing_enabled BOOLEAN DEFAULT false,
                    comprehensive_reading_enabled BOOLEAN DEFAULT false
                )
            """)
            logger.info("✅ Created service_types table")
        
        # Users table
        if 'users' not in existing_tables:
            await conn.execute("""
                CREATE TABLE users (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    full_name VARCHAR(255),
                    phone VARCHAR(20),
                    date_of_birth DATE,
                    birth_time TIME,
                    birth_location VARCHAR(255),
                    timezone VARCHAR(50) DEFAULT 'Asia/Colombo',
                    credits INTEGER DEFAULT 0,
                    role VARCHAR(50) DEFAULT 'user',
                    is_active BOOLEAN DEFAULT true,
                    email_verified BOOLEAN DEFAULT false,
                    phone_verified BOOLEAN DEFAULT false,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login_at TIMESTAMP,
                    profile_picture_url VARCHAR(500),
                    preferences JSONB DEFAULT '{}',
                    birth_chart_data JSONB DEFAULT '{}',
                    subscription_status VARCHAR(50) DEFAULT 'free',
                    subscription_expires_at TIMESTAMP,
                    total_sessions INTEGER DEFAULT 0,
                    total_spent DECIMAL(10,2) DEFAULT 0.00
                )
            """)
            logger.info("✅ Created users table")
        
        # Credit packages table (MISSING IN COMPREHENSIVE RESET!)
        if 'credit_packages' not in existing_tables:
            await conn.execute("""
                CREATE TABLE credit_packages (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    credits_amount INTEGER NOT NULL,
                    price_usd DECIMAL(10,2) NOT NULL,
                    bonus_credits INTEGER DEFAULT 0,
                    description TEXT,
                    enabled BOOLEAN DEFAULT TRUE,
                    stripe_product_id VARCHAR(255),
                    stripe_price_id VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            logger.info("✅ Created credit_packages table")
        
        # Sessions table
        if 'sessions' not in existing_tables:
            await conn.execute("""
                CREATE TABLE sessions (
                    id SERIAL PRIMARY KEY,
                    session_id VARCHAR(255) UNIQUE NOT NULL,
                    user_email VARCHAR(255) NOT NULL,
                    user_id INTEGER,
                    service_type VARCHAR(100) NOT NULL,
                    status VARCHAR(50) DEFAULT 'active',
                    credits_used INTEGER DEFAULT 0,
                    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    end_time TIMESTAMP,
                    duration_minutes INTEGER,
                    birth_details JSONB DEFAULT '{}',
                    questions_asked TEXT[],
                    ai_responses TEXT[],
                    satisfaction_rating INTEGER CHECK (satisfaction_rating >= 1 AND satisfaction_rating <= 5),
                    user_rating INTEGER,
                    feedback TEXT,
                    session_data JSONB DEFAULT '{}',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_email) REFERENCES users(email) ON DELETE CASCADE
                )
            """)
            logger.info("✅ Created sessions table")
        
        # Pricing config table
        if 'pricing_config' not in existing_tables:
            await conn.execute("""
                CREATE TABLE pricing_config (
                    id SERIAL PRIMARY KEY,
                    key VARCHAR(100) UNIQUE NOT NULL,
                    value VARCHAR(500) NOT NULL,
                    type VARCHAR(50) NOT NULL,
                    description TEXT,
                    is_active BOOLEAN DEFAULT true,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            logger.info("✅ Created pricing_config table")
        
        # Donations table
        if 'donations' not in existing_tables:
            await conn.execute("""
                CREATE TABLE donations (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    tamil_name VARCHAR(255),
                    description TEXT,
                    price_usd DECIMAL(10,2) NOT NULL,
                    icon VARCHAR(50) DEFAULT '🪔',
                    category VARCHAR(100),
                    enabled BOOLEAN DEFAULT true,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            logger.info("✅ Created donations table")
        
        # Payments table
        if 'payments' not in existing_tables:
            await conn.execute("""
                CREATE TABLE payments (
                    id SERIAL PRIMARY KEY,
                    user_email VARCHAR(255) NOT NULL,
                    amount DECIMAL(10,2) NOT NULL,
                    currency VARCHAR(3) DEFAULT 'USD',
                    status VARCHAR(50) DEFAULT 'pending',
                    payment_method VARCHAR(50),
                    transaction_id VARCHAR(255),
                    product_id VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_email) REFERENCES users(email) ON DELETE CASCADE
                )
            """)
            logger.info("✅ Created payments table")
        
        # AI recommendations table
        if 'ai_recommendations' not in existing_tables:
            await conn.execute("""
                CREATE TABLE ai_recommendations (
                    id SERIAL PRIMARY KEY,
                    recommendation_type VARCHAR(50) NOT NULL,
                    title VARCHAR(255) NOT NULL,
                    description TEXT NOT NULL,
                    expected_revenue_impact DECIMAL(10,2),
                    implementation_difficulty VARCHAR(20),
                    timeline_weeks INTEGER,
                    priority_score DECIMAL(3,2),
                    priority_level VARCHAR(20),
                    status VARCHAR(50) DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            logger.info("✅ Created ai_recommendations table")
        
        # AI pricing recommendations table
        if 'ai_pricing_recommendations' not in existing_tables:
            await conn.execute("""
                CREATE TABLE ai_pricing_recommendations (
                    id SERIAL PRIMARY KEY,
                    recommendation_type VARCHAR(50) NOT NULL,
                    service_name VARCHAR(100),
                    current_value DECIMAL(10,2),
                    suggested_value DECIMAL(10,2),
                    expected_impact DECIMAL(10,2),
                    confidence_level DECIMAL(3,2),
                    reasoning TEXT,
                    implementation_difficulty VARCHAR(20),
                    status VARCHAR(50) DEFAULT 'pending',
                    priority_level VARCHAR(20),
                    metadata JSONB DEFAULT '{}',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    implemented_at TIMESTAMP
                )
            """)
            logger.info("✅ Created ai_pricing_recommendations table")
        
        # Monetization experiments table
        if 'monetization_experiments' not in existing_tables:
            await conn.execute("""
                CREATE TABLE monetization_experiments (
                    id SERIAL PRIMARY KEY,
                    experiment_name VARCHAR(255) NOT NULL,
                    experiment_type VARCHAR(50) NOT NULL,
                    control_conversion_rate DECIMAL(5,2),
                    test_conversion_rate DECIMAL(5,2),
                    control_revenue DECIMAL(10,2),
                    test_revenue DECIMAL(10,2),
                    status VARCHAR(50) DEFAULT 'running',
                    winner VARCHAR(20),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            logger.info("✅ Created monetization_experiments table")
        
        # AI insights cache table
        if 'ai_insights_cache' not in existing_tables:
            await conn.execute("""
                CREATE TABLE ai_insights_cache (
                    id SERIAL PRIMARY KEY,
                    insight_type VARCHAR(50) NOT NULL,
                    data JSONB NOT NULL,
                    expires_at TIMESTAMP NOT NULL,
                    is_active BOOLEAN DEFAULT true,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            logger.info("✅ Created ai_insights_cache table")
        
        # User purchases table for credit transaction history
        if 'user_purchases' not in existing_tables:
            await conn.execute("""
                CREATE TABLE user_purchases (
                    id SERIAL PRIMARY KEY,
                    user_email VARCHAR(255) NOT NULL,
                    transaction_type VARCHAR(50) NOT NULL DEFAULT 'purchase',
                    amount DECIMAL(10,2) NOT NULL,
                    credits INTEGER NOT NULL,
                    balance_before INTEGER DEFAULT 0,
                    balance_after INTEGER DEFAULT 0,
                    package_type VARCHAR(100),
                    payment_method VARCHAR(50),
                    stripe_session_id VARCHAR(255),
                    stripe_payment_intent_id VARCHAR(255),
                    description TEXT NOT NULL,
                    status VARCHAR(50) DEFAULT 'completed',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_email) REFERENCES users(email) ON DELETE CASCADE
                )
            """)
            logger.info("✅ Created user_purchases table")
        
        # Note: Social media tables are created by migrations to avoid duplication
        # The migration system will handle:
        # - social_campaigns
        # - social_posts  
        # - social_content
        # - platform_settings
        # This avoids schema conflicts from multiple creation attempts
    
    async def _fix_column_issues(self, conn):
        """Fix column naming and missing columns"""
        logger.info("🔧 Fixing column issues...")
        
        # Fix last_login vs last_login_at
        try:
            col_exists = await conn.fetchval("""
                SELECT 1 FROM information_schema.columns 
                WHERE table_name='users' AND column_name='last_login'
            """)
            if col_exists:
                await conn.execute("ALTER TABLE users RENAME COLUMN last_login TO last_login_at")
                logger.info("✅ Renamed last_login to last_login_at")
        except Exception as e:
            logger.warning(f"⚠️ Could not rename last_login column: {e}")
            pass
        
        # Fix knowledge_domain column in rag_knowledge_base table
        try:
            logger.info("🔍 Checking rag_knowledge_base table schema...")
            
            # Check if table exists
            table_exists = await conn.fetchval("""
                SELECT 1 FROM information_schema.tables 
                WHERE table_name = 'rag_knowledge_base'
            """)
            
            if table_exists:
                # Check if knowledge_domain column exists
                column_exists = await conn.fetchval("""
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'rag_knowledge_base' 
                    AND column_name = 'knowledge_domain'
                """)
                
                if not column_exists:
                    logger.info("⚠️ knowledge_domain column missing in rag_knowledge_base. Adding it...")
                    await conn.execute("""
                        ALTER TABLE rag_knowledge_base 
                        ADD COLUMN knowledge_domain VARCHAR(100) NOT NULL DEFAULT 'general'
                    """)
                    logger.info("✅ knowledge_domain column added to rag_knowledge_base")
                    
                    # Update existing records if any
                    records_count = await conn.fetchval("SELECT COUNT(*) FROM rag_knowledge_base")
                    if records_count > 0:
                        await conn.execute("""
                            UPDATE rag_knowledge_base 
                            SET knowledge_domain = 'classical_astrology' 
                            WHERE knowledge_domain = 'general'
                        """)
                        logger.info(f"✅ Updated {records_count} existing records with default domain")
                else:
                    logger.info("✅ knowledge_domain column already exists in rag_knowledge_base")
            else:
                logger.info("⚠️ rag_knowledge_base table does not exist yet")
                
        except Exception as e:
            logger.warning(f"⚠️ Could not fix knowledge_domain column: {e}")
        
        # Fix content_type column in rag_knowledge_base table
        try:
            logger.info("🔍 Checking rag_knowledge_base table for content_type column...")
            
            # Check if table exists
            table_exists = await conn.fetchval("""
                SELECT 1 FROM information_schema.tables 
                WHERE table_name = 'rag_knowledge_base'
            """)
            
            if table_exists:
                # Check if content_type column exists
                column_exists = await conn.fetchval("""
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'rag_knowledge_base' 
                    AND column_name = 'content_type'
                """)
                
                if not column_exists:
                    logger.info("⚠️ content_type column missing in rag_knowledge_base. Adding it...")
                    await conn.execute("""
                        ALTER TABLE rag_knowledge_base 
                        ADD COLUMN content_type VARCHAR(50) NOT NULL DEFAULT 'knowledge'
                    """)
                    logger.info("✅ content_type column added to rag_knowledge_base")
                    
                    # Update existing records to have appropriate content_type values
                    records_count = await conn.fetchval("SELECT COUNT(*) FROM rag_knowledge_base")
                    if records_count > 0:
                        await conn.execute("""
                            UPDATE rag_knowledge_base 
                            SET content_type = CASE 
                                WHEN title ILIKE '%meditation%' OR content ILIKE '%meditation%' THEN 'meditation'
                                WHEN title ILIKE '%ritual%' OR content ILIKE '%ritual%' THEN 'ritual'
                                WHEN title ILIKE '%astrology%' OR content ILIKE '%astrology%' THEN 'astrology'
                                WHEN title ILIKE '%psychology%' OR content ILIKE '%psychology%' THEN 'psychology'
                                WHEN title ILIKE '%spiritual%' OR content ILIKE '%spiritual%' THEN 'spiritual'
                                ELSE 'knowledge'
                            END
                            WHERE content_type = 'knowledge'
                        """)
                        logger.info(f"✅ Updated content_type for {records_count} existing records")
                else:
                    logger.info("✅ content_type column already exists in rag_knowledge_base")
            else:
                logger.info("⚠️ rag_knowledge_base table does not exist yet")
                
        except Exception as e:
            logger.warning(f"⚠️ Could not fix content_type column: {e}")
                
        # Fix cultural_context column in rag_knowledge_base table
        try:
            logger.info("🔍 Checking rag_knowledge_base table for cultural_context column...")
            
            # Check if table exists
            table_exists = await conn.fetchval("""
                SELECT 1 FROM information_schema.tables 
                WHERE table_name = 'rag_knowledge_base'
            """)
            
            if table_exists:
                # Check if cultural_context column exists
                column_exists = await conn.fetchval("""
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'rag_knowledge_base' 
                    AND column_name = 'cultural_context'
                """)
                
                if not column_exists:
                    logger.info("⚠️ cultural_context column missing in rag_knowledge_base. Adding it...")
                    await conn.execute("""
                        ALTER TABLE rag_knowledge_base 
                        ADD COLUMN cultural_context VARCHAR(100) NOT NULL DEFAULT 'universal'
                    """)
                    logger.info("✅ cultural_context column added to rag_knowledge_base")
                    
                    # Update existing records with default cultural context
                    records_count = await conn.fetchval("SELECT COUNT(*) FROM rag_knowledge_base")
                    if records_count > 0:
                        await conn.execute("""
                            UPDATE rag_knowledge_base 
                            SET cultural_context = 'universal' 
                            WHERE cultural_context IS NULL
                        """)
                        logger.info(f"✅ Updated cultural_context for {records_count} existing records")
                else:
                    logger.info("✅ cultural_context column already exists in rag_knowledge_base")
            else:
                logger.info("⚠️ rag_knowledge_base table does not exist yet")
                
        except Exception as e:
            logger.warning(f"⚠️ Could not fix cultural_context column: {e}")
        
        # Add missing columns to service_types
        columns_to_add = [
            ("enabled", "BOOLEAN DEFAULT true"),
            ("price_usd", "DECIMAL(10,2) DEFAULT 0"),
            ("service_category", "VARCHAR(100)"),
            ("avatar_video_enabled", "BOOLEAN DEFAULT false"),
            ("live_chat_enabled", "BOOLEAN DEFAULT false"),
            # NEW: Add missing columns that are causing current errors
            ("comprehensive_reading_enabled", "BOOLEAN DEFAULT false"),
            ("credits_required", "INTEGER DEFAULT 10"),
            ("base_credits", "INTEGER DEFAULT 5"),
            ("duration_minutes", "INTEGER DEFAULT 15"),
            ("video_enabled", "BOOLEAN DEFAULT true"),
            ("dynamic_pricing_enabled", "BOOLEAN DEFAULT false"),
            ("personalized", "BOOLEAN DEFAULT false"),
            ("includes_remedies", "BOOLEAN DEFAULT false"),
            ("includes_predictions", "BOOLEAN DEFAULT false"),
            ("includes_compatibility", "BOOLEAN DEFAULT false"),
            ("knowledge_domains", "JSONB DEFAULT '[]'"),
            ("persona_modes", "JSONB DEFAULT '[]'")
        ]
        
        for col_name, col_def in columns_to_add:
            try:
                col_exists = await conn.fetchval(f"""
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='service_types' AND column_name='{col_name}'
                """)
                if not col_exists:
                    await conn.execute(f"ALTER TABLE service_types ADD COLUMN {col_name} {col_def}")
                    logger.info(f"✅ Added {col_name} to service_types")
            except Exception as e:
                logger.warning(f"⚠️ Could not add column {col_name} to service_types: {e}")
                pass

        # Create cache_analytics table if it doesn't exist
        try:
            table_exists = await conn.fetchval("""
                SELECT 1 FROM information_schema.tables 
                WHERE table_name='cache_analytics'
            """)
            if not table_exists:
                await conn.execute("""
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
        except Exception as e:
            logger.warning(f"⚠️ Could not create cache_analytics table: {e}")

        # Create followup_templates table if it doesn't exist
        try:
            table_exists = await conn.fetchval("""
                SELECT 1 FROM information_schema.tables 
                WHERE table_name='followup_templates'
            """)
            if not table_exists:
                await conn.execute("""
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
        except Exception as e:
            logger.warning(f"⚠️ Could not create followup_templates table: {e}")
            
        # Add missing columns to sessions table
        session_columns_to_add = [
            ("follow_up_sent", "BOOLEAN DEFAULT FALSE"),
            ("follow_up_count", "INTEGER DEFAULT 0"),
            ("follow_up_email_sent", "BOOLEAN DEFAULT FALSE"),
            ("follow_up_sms_sent", "BOOLEAN DEFAULT FALSE"),
            ("follow_up_whatsapp_sent", "BOOLEAN DEFAULT FALSE")
        ]
        
        for col_name, col_def in session_columns_to_add:
            try:
                col_exists = await conn.fetchval(f"""
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='sessions' AND column_name='{col_name}'
                """)
                if not col_exists:
                    await conn.execute(f"ALTER TABLE sessions ADD COLUMN {col_name} {col_def}")
                    logger.info(f"✅ Added {col_name} to sessions table")
            except Exception as e:
                logger.warning(f"⚠️ Could not add column {col_name} to sessions table: {e}")
                pass
    
    async def _ensure_essential_data(self, conn):
        """Ensure essential data exists"""
        logger.info("📦 Ensuring essential data...")
        
        # Ensure admin user exists
        admin_exists = await conn.fetchval(
            "SELECT 1 FROM users WHERE email = 'admin@jyotiflow.ai'"
        )
        
        if not admin_exists:
            # Create admin user with proper password hash using same bcrypt method as auth router
            admin_password_hash = bcrypt.hashpw("Jyoti@2024!".encode(), bcrypt.gensalt()).decode()
            
            await conn.execute("""
                INSERT INTO users (email, password_hash, full_name, role, credits, is_active, email_verified)
                VALUES ('admin@jyotiflow.ai', $1, 'Admin User', 'admin', 1000, true, true)
            """, admin_password_hash)
            logger.info("✅ Created admin user")
        else:
            # Admin exists, but ensure password is hashed with bcrypt (fix passlib mismatch)
            admin_password_hash = bcrypt.hashpw("Jyoti@2024!".encode(), bcrypt.gensalt()).decode()
            await conn.execute("""
                UPDATE users SET password_hash = $1, credits = 1000, role = 'admin'
                WHERE email = 'admin@jyotiflow.ai'
            """, admin_password_hash)
            logger.info("✅ Updated admin user password hash to bcrypt format")
        
        # Ensure test user exists for testing
        test_user_exists = await conn.fetchval(
            "SELECT 1 FROM users WHERE email = 'user@jyotiflow.ai'"
        )
        
        if not test_user_exists:
            # Create test user with proper password hash using same bcrypt method as auth router
            test_password_hash = bcrypt.hashpw("user123".encode(), bcrypt.gensalt()).decode()
            
            await conn.execute("""
                INSERT INTO users (email, password_hash, full_name, role, credits, is_active, email_verified)
                VALUES ('user@jyotiflow.ai', $1, 'Test User', 'user', 100, true, true)
            """, test_password_hash)
            logger.info("✅ Created test user")
        else:
            # Test user exists, but ensure password is hashed with bcrypt for consistency
            test_password_hash = bcrypt.hashpw("user123".encode(), bcrypt.gensalt()).decode()
            await conn.execute("""
                UPDATE users SET password_hash = $1, credits = 100, role = 'user'
                WHERE email = 'user@jyotiflow.ai'
            """, test_password_hash)
            logger.info("✅ Updated test user password hash to bcrypt format")
        
        # Ensure default credit packages
        packages_exist = await conn.fetchval("SELECT COUNT(*) FROM credit_packages")
        if packages_exist == 0:
            default_packages = [
                ('Starter Pack', 10, 9.99, 2),
                ('Spiritual Seeker', 25, 19.99, 5),
                ('Divine Wisdom', 50, 34.99, 15),
                ('Enlightened Master', 100, 59.99, 30)
            ]
            
            for name, credits, price, bonus in default_packages:
                await conn.execute("""
                    INSERT INTO credit_packages (name, credits_amount, price_usd, bonus_credits, enabled)
                    VALUES ($1, $2, $3, $4, true)
                """, name, credits, price, bonus)
            logger.info("✅ Created default credit packages")

async def safe_initialize_database():
    """Main entry point for safe database initialization"""
    initializer = SafeDatabaseInitializer()
    return await initializer.initialize()

if __name__ == "__main__":
    asyncio.run(safe_initialize_database())