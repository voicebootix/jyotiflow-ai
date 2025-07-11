"""
🚀 JyotiFlow.ai Enterprise Database Architecture Upgrade
Comprehensive Priority 1 database schema fixes and enhancements

This script upgrades the database to enterprise-grade architecture supporting:
- Spiritual guidance with birth chart caching and RAG knowledge base
- Live chat with proper session management and credit system
- Enhanced authentication and user management
- Social media automation and analytics
- Comprehensive audit trails and monitoring

NO SIMPLIFICATION - Full enterprise features preserved and enhanced
"""

import os
import json
import logging
import asyncpg
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JyotiFlowEnterpriseUpgrade:
    """Handles enterprise-grade database architecture upgrade"""
    
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL", "postgresql://jyotiflow_db_user:em0MmaZmvPzASryvzLHpR5g5rRZTQqpw@dpg-d12ohqemcj7s73fjbqtg-a/jyotiflow_db")
        
    async def upgrade_database(self):
        """Execute comprehensive enterprise database upgrade"""
        logger.info("🚀 Starting JyotiFlow Enterprise Database Upgrade...")
        
        try:
            conn = await asyncpg.connect(self.database_url)
            
            # Phase 1: Core table structure upgrades
            await self._upgrade_core_tables(conn)
            
            # Phase 2: Add missing enterprise tables
            await self._create_missing_enterprise_tables(conn)
            
            # Phase 3: Fix query syntax compatibility issues
            await self._fix_query_syntax_issues(conn)
            
            # Phase 4: Add enterprise-grade indexes and constraints
            await self._add_enterprise_indexes(conn)
            
            # Phase 5: Insert enterprise configuration data
            await self._insert_enterprise_configuration(conn)
            
            # Phase 6: Validate and verify upgrade
            await self._validate_upgrade(conn)
            
            await conn.close()
            logger.info("✅ Enterprise Database Upgrade completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Enterprise Database Upgrade failed: {e}")
            return False
    
    async def _upgrade_core_tables(self, conn):
        """Upgrade core tables with enterprise features"""
        logger.info("📊 Upgrading core tables to enterprise standards...")
        
        # Upgrade users table with birth chart caching and enhanced features
        await conn.execute("""
            -- Add birth chart caching columns
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS birth_chart_data JSONB,
            ADD COLUMN IF NOT EXISTS birth_chart_hash VARCHAR(64),
            ADD COLUMN IF NOT EXISTS birth_chart_cached_at TIMESTAMP,
            ADD COLUMN IF NOT EXISTS birth_chart_expires_at TIMESTAMP,
            ADD COLUMN IF NOT EXISTS has_free_birth_chart BOOLEAN DEFAULT false,
            
            -- Add enterprise user management columns
            ADD COLUMN IF NOT EXISTS subscription_tier VARCHAR(50) DEFAULT 'free',
            ADD COLUMN IF NOT EXISTS subscription_expires_at TIMESTAMP,
            ADD COLUMN IF NOT EXISTS total_sessions_count INTEGER DEFAULT 0,
            ADD COLUMN IF NOT EXISTS total_credits_purchased INTEGER DEFAULT 0,
            ADD COLUMN IF NOT EXISTS total_credits_used INTEGER DEFAULT 0,
            ADD COLUMN IF NOT EXISTS user_tier VARCHAR(50) DEFAULT 'basic',
            ADD COLUMN IF NOT EXISTS referral_code VARCHAR(20),
            ADD COLUMN IF NOT EXISTS referred_by_user_id INTEGER,
            ADD COLUMN IF NOT EXISTS email_verified BOOLEAN DEFAULT false,
            ADD COLUMN IF NOT EXISTS phone_verified BOOLEAN DEFAULT false,
            ADD COLUMN IF NOT EXISTS two_factor_enabled BOOLEAN DEFAULT false,
            ADD COLUMN IF NOT EXISTS last_activity_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ADD COLUMN IF NOT EXISTS account_status VARCHAR(20) DEFAULT 'active',
            
            -- Add spiritual profile enhancements
            ADD COLUMN IF NOT EXISTS spiritual_interests TEXT[],
            ADD COLUMN IF NOT EXISTS preferred_consultation_style VARCHAR(50) DEFAULT 'comprehensive',
            ADD COLUMN IF NOT EXISTS timezone VARCHAR(50) DEFAULT 'Asia/Kolkata',
            ADD COLUMN IF NOT EXISTS notification_preferences JSONB DEFAULT '{}',
            ADD COLUMN IF NOT EXISTS privacy_settings JSONB DEFAULT '{}';
        """)
        
        # Upgrade service_types table with enterprise pricing and configuration
        await conn.execute("""
            ALTER TABLE service_types
            ADD COLUMN IF NOT EXISTS credits_required INTEGER,
            ADD COLUMN IF NOT EXISTS price_usd DECIMAL(10,2),
            ADD COLUMN IF NOT EXISTS price_inr DECIMAL(10,2),
            ADD COLUMN IF NOT EXISTS enabled BOOLEAN DEFAULT true,
            ADD COLUMN IF NOT EXISTS requires_birth_chart BOOLEAN DEFAULT false,
            ADD COLUMN IF NOT EXISTS max_duration_minutes INTEGER,
            ADD COLUMN IF NOT EXISTS min_credits_required INTEGER,
            ADD COLUMN IF NOT EXISTS service_category VARCHAR(50) DEFAULT 'spiritual_guidance',
            ADD COLUMN IF NOT EXISTS expertise_level VARCHAR(50) DEFAULT 'standard',
            ADD COLUMN IF NOT EXISTS cultural_focus VARCHAR(100) DEFAULT 'universal',
            ADD COLUMN IF NOT EXISTS language_support TEXT[] DEFAULT ARRAY['en', 'ta'],
            ADD COLUMN IF NOT EXISTS ai_model_config JSONB DEFAULT '{}',
            ADD COLUMN IF NOT EXISTS quality_tier VARCHAR(20) DEFAULT 'standard';
        """)
        
        # Upgrade sessions table with comprehensive tracking
        await conn.execute("""
            ALTER TABLE sessions
            ADD COLUMN IF NOT EXISTS session_type VARCHAR(50) DEFAULT 'spiritual_guidance',
            ADD COLUMN IF NOT EXISTS ai_model_used VARCHAR(50),
            ADD COLUMN IF NOT EXISTS processing_time_seconds DECIMAL(10,2),
            ADD COLUMN IF NOT EXISTS birth_chart_used BOOLEAN DEFAULT false,
            ADD COLUMN IF NOT EXISTS knowledge_domains_used TEXT[],
            ADD COLUMN IF NOT EXISTS response_quality_score DECIMAL(3,2),
            ADD COLUMN IF NOT EXISTS user_satisfaction_score DECIMAL(3,2),
            ADD COLUMN IF NOT EXISTS follow_up_recommended BOOLEAN DEFAULT false,
            ADD COLUMN IF NOT EXISTS remedies_provided TEXT[],
            ADD COLUMN IF NOT EXISTS spiritual_insights TEXT,
            ADD COLUMN IF NOT EXISTS astrological_analysis TEXT,
            ADD COLUMN IF NOT EXISTS session_metadata JSONB DEFAULT '{}',
            ADD COLUMN IF NOT EXISTS error_logs TEXT,
            ADD COLUMN IF NOT EXISTS api_costs JSONB DEFAULT '{}';
        """)
        
        logger.info("✅ Core tables upgraded to enterprise standards")
    
    async def _create_missing_enterprise_tables(self, conn):
        """Create missing enterprise tables for full functionality"""
        logger.info("🏗️ Creating missing enterprise tables...")
        
        # Birth Chart Cache Service table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS birth_chart_cache (
                id SERIAL PRIMARY KEY,
                cache_key VARCHAR(64) UNIQUE NOT NULL,
                user_id INTEGER,
                birth_date DATE NOT NULL,
                birth_time TIME NOT NULL,
                birth_location VARCHAR(255) NOT NULL,
                latitude DECIMAL(10,8),
                longitude DECIMAL(11,8),
                timezone_offset VARCHAR(10),
                prokerala_response JSONB NOT NULL,
                chart_analysis JSONB,
                cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                access_count INTEGER DEFAULT 1,
                last_accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
            );
        """)
        
        # Enhanced RAG Knowledge Base for spiritual guidance
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS spiritual_knowledge_base (
                id TEXT PRIMARY KEY,
                knowledge_domain VARCHAR(100) NOT NULL,
                content_type VARCHAR(50) NOT NULL,
                title VARCHAR(500) NOT NULL,
                content TEXT NOT NULL,
                metadata JSONB DEFAULT '{}',
                embedding_vector TEXT,
                tags TEXT[] DEFAULT '{}',
                source_reference VARCHAR(500),
                authority_level INTEGER DEFAULT 1 CHECK (authority_level >= 1 AND authority_level <= 10),
                cultural_context VARCHAR(100) DEFAULT 'universal',
                language VARCHAR(10) DEFAULT 'en',
                spiritual_tradition VARCHAR(100),
                applicable_life_areas TEXT[],
                astrological_relevance JSONB DEFAULT '{}',
                remedial_measures TEXT[],
                difficulty_level VARCHAR(20) DEFAULT 'beginner',
                verification_status VARCHAR(20) DEFAULT 'verified',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by VARCHAR(255),
                last_reviewed_at TIMESTAMP
            );
        """)
        
        # Credit Packages for monetization
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS credit_packages (
                id SERIAL PRIMARY KEY,
                package_name VARCHAR(100) UNIQUE NOT NULL,
                credits INTEGER NOT NULL,
                price_usd DECIMAL(10,2) NOT NULL,
                price_inr DECIMAL(10,2) NOT NULL,
                discount_percentage DECIMAL(5,2) DEFAULT 0,
                bonus_credits INTEGER DEFAULT 0,
                package_type VARCHAR(50) DEFAULT 'standard',
                validity_days INTEGER DEFAULT 365,
                is_popular BOOLEAN DEFAULT false,
                is_active BOOLEAN DEFAULT true,
                stripe_price_id VARCHAR(255),
                razorpay_plan_id VARCHAR(255),
                description TEXT,
                features TEXT[],
                target_audience VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Donations tracking for spiritual contributions
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS donations (
                id SERIAL PRIMARY KEY,
                donation_id VARCHAR(100) UNIQUE NOT NULL,
                user_id INTEGER,
                user_email VARCHAR(255),
                amount_usd DECIMAL(10,2),
                amount_inr DECIMAL(10,2),
                currency VARCHAR(3) NOT NULL,
                donation_type VARCHAR(50) DEFAULT 'general',
                purpose VARCHAR(255),
                message TEXT,
                is_anonymous BOOLEAN DEFAULT false,
                payment_method VARCHAR(50),
                payment_gateway VARCHAR(50),
                transaction_id VARCHAR(255),
                payment_status VARCHAR(50) DEFAULT 'pending',
                receipt_sent BOOLEAN DEFAULT false,
                tax_receipt_required BOOLEAN DEFAULT false,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                processed_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
            );
        """)
        
        # Enhanced Agora Usage Logs with proper schema
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS agora_usage_logs (
                id SERIAL PRIMARY KEY,
                session_id VARCHAR(100) NOT NULL,
                user_id INTEGER NOT NULL,
                user_email VARCHAR(255),
                duration_minutes INTEGER NOT NULL,
                cost_credits INTEGER NOT NULL,
                session_type VARCHAR(50) DEFAULT 'video',
                agora_channel_name VARCHAR(255),
                participant_count INTEGER DEFAULT 1,
                quality_metrics JSONB DEFAULT '{}',
                connection_quality VARCHAR(20),
                bandwidth_usage_mb DECIMAL(10,2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ended_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
        """)
        
        # User Authentication Tokens for enterprise security
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS user_auth_tokens (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                token_hash VARCHAR(255) NOT NULL,
                token_type VARCHAR(50) NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                is_revoked BOOLEAN DEFAULT false,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_used_at TIMESTAMP,
                ip_address VARCHAR(45),
                user_agent TEXT,
                device_info JSONB DEFAULT '{}',
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
        """)
        
        logger.info("✅ Missing enterprise tables created")
    
    async def _fix_query_syntax_issues(self, conn):
        """Fix PostgreSQL query syntax compatibility issues"""
        logger.info("🔧 Fixing query syntax compatibility issues...")
        
        # Note: The actual query fixes will be applied in the router files
        # This function documents the issues that need to be fixed
        
        syntax_fixes_needed = [
            {
                "file": "routers/livechat.py",
                "line": 225,
                "issue": "SQLite syntax (?) instead of PostgreSQL ($1, $2)",
                "fix": "UPDATE users SET credits = credits - $1 WHERE id = $2"
            },
            {
                "file": "routers/livechat.py", 
                "line": 238,
                "issue": "Table schema mismatch - user_id vs user_email",
                "fix": "Use user_id INTEGER column instead of user_email"
            },
            {
                "file": "routers/livechat.py",
                "line": 284,
                "issue": "SQLite syntax (?) instead of PostgreSQL ($1, $2)",
                "fix": "UPDATE users SET credits = credits - $1 WHERE id = $2"
            }
        ]
        
        logger.info(f"📝 Documented {len(syntax_fixes_needed)} syntax fixes needed in router files")
        logger.info("✅ Query syntax issues documented for router updates")
    
    async def _add_enterprise_indexes(self, conn):
        """Add enterprise-grade database indexes for performance"""
        logger.info("⚡ Adding enterprise-grade database indexes...")
        
        indexes = [
            # User table indexes
            "CREATE INDEX IF NOT EXISTS idx_users_email_active ON users(email) WHERE account_status = 'active';",
            "CREATE INDEX IF NOT EXISTS idx_users_birth_chart_hash ON users(birth_chart_hash);",
            "CREATE INDEX IF NOT EXISTS idx_users_birth_chart_expires ON users(birth_chart_expires_at);",
            "CREATE INDEX IF NOT EXISTS idx_users_subscription_tier ON users(subscription_tier);",
            "CREATE INDEX IF NOT EXISTS idx_users_last_activity ON users(last_activity_at);",
            "CREATE INDEX IF NOT EXISTS idx_users_referral_code ON users(referral_code);",
            
            # Session table indexes
            "CREATE INDEX IF NOT EXISTS idx_sessions_user_email_date ON sessions(user_email, created_at);",
            "CREATE INDEX IF NOT EXISTS idx_sessions_service_type ON sessions(service_type);",
            "CREATE INDEX IF NOT EXISTS idx_sessions_status ON sessions(status);",
            "CREATE INDEX IF NOT EXISTS idx_sessions_created_at ON sessions(created_at);",
            
            # Birth chart cache indexes
            "CREATE INDEX IF NOT EXISTS idx_birth_chart_cache_key ON birth_chart_cache(cache_key);",
            "CREATE INDEX IF NOT EXISTS idx_birth_chart_cache_user ON birth_chart_cache(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_birth_chart_cache_expires ON birth_chart_cache(expires_at);",
            
            # Knowledge base indexes
            "CREATE INDEX IF NOT EXISTS idx_spiritual_knowledge_domain ON spiritual_knowledge_base(knowledge_domain);",
            "CREATE INDEX IF NOT EXISTS idx_spiritual_knowledge_type ON spiritual_knowledge_base(content_type);",
            "CREATE INDEX IF NOT EXISTS idx_spiritual_knowledge_tags ON spiritual_knowledge_base USING GIN(tags);",
            "CREATE INDEX IF NOT EXISTS idx_spiritual_knowledge_cultural ON spiritual_knowledge_base(cultural_context);",
            
            # Service types indexes
            "CREATE INDEX IF NOT EXISTS idx_service_types_enabled ON service_types(enabled) WHERE enabled = true;",
            "CREATE INDEX IF NOT EXISTS idx_service_types_category ON service_types(service_category);",
            
            # Agora usage logs indexes
            "CREATE INDEX IF NOT EXISTS idx_agora_logs_user_date ON agora_usage_logs(user_id, created_at);",
            "CREATE INDEX IF NOT EXISTS idx_agora_logs_session ON agora_usage_logs(session_id);",
            
            # Auth tokens indexes
            "CREATE INDEX IF NOT EXISTS idx_auth_tokens_user ON user_auth_tokens(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_auth_tokens_hash ON user_auth_tokens(token_hash);",
            "CREATE INDEX IF NOT EXISTS idx_auth_tokens_expires ON user_auth_tokens(expires_at);"
        ]
        
        for index_sql in indexes:
            try:
                await conn.execute(index_sql)
            except Exception as e:
                logger.warning(f"Index creation warning: {e}")
        
        logger.info("✅ Enterprise indexes added")
    
    async def _insert_enterprise_configuration(self, conn):
        """Insert enterprise configuration data"""
        logger.info("⚙️ Inserting enterprise configuration data...")
        
        # Insert enhanced service types with enterprise features
        enterprise_services = [
            {
                'name': 'spiritual_clarity_basic',
                'description': 'Basic spiritual clarity and guidance session',
                'base_credits': 5,
                'credits_required': 5,
                'duration_minutes': 15,
                'price_usd': 4.99,
                'price_inr': 399.00,
                'service_category': 'spiritual_guidance',
                'expertise_level': 'standard',
                'requires_birth_chart': False,
                'cultural_focus': 'universal'
            },
            {
                'name': 'love_relationship_mastery',
                'description': 'Comprehensive love and relationship guidance with astrological insights',
                'base_credits': 12,
                'credits_required': 12,
                'duration_minutes': 25,
                'price_usd': 11.99,
                'price_inr': 999.00,
                'service_category': 'relationship_guidance',
                'expertise_level': 'advanced',
                'requires_birth_chart': True,
                'cultural_focus': 'vedic_astrology'
            },
            {
                'name': 'comprehensive_life_reading_30min',
                'description': 'Complete life analysis with birth chart and spiritual guidance',
                'base_credits': 25,
                'credits_required': 25,
                'duration_minutes': 30,
                'price_usd': 24.99,
                'price_inr': 1999.00,
                'service_category': 'comprehensive_reading',
                'expertise_level': 'master',
                'requires_birth_chart': True,
                'cultural_focus': 'vedic_astrology'
            },
            {
                'name': 'live_video_consultation',
                'description': 'Live video consultation with Swamiji',
                'base_credits': 15,
                'credits_required': 15,
                'duration_minutes': 15,
                'price_usd': 14.99,
                'price_inr': 1199.00,
                'service_category': 'live_consultation',
                'expertise_level': 'master',
                'requires_birth_chart': False,
                'cultural_focus': 'universal'
            },
            {
                'name': 'live_audio_consultation',
                'description': 'Live audio consultation with Swamiji',
                'base_credits': 10,
                'credits_required': 10,
                'duration_minutes': 15,
                'price_usd': 9.99,
                'price_inr': 799.00,
                'service_category': 'live_consultation',
                'expertise_level': 'master',
                'requires_birth_chart': False,
                'cultural_focus': 'universal'
            }
        ]
        
        for service in enterprise_services:
            # Check if service already exists
            existing = await conn.fetchrow(
                "SELECT id FROM service_types WHERE name = $1", service['name']
            )
            if not existing:
                await conn.execute("""
                    INSERT INTO service_types 
                    (name, description, base_credits, credits_required, duration_minutes, 
                     price_usd, price_inr, service_category, expertise_level, 
                     requires_birth_chart, cultural_focus, enabled, video_enabled)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, true, true)
                """, (
                    service['name'], service['description'], service['base_credits'],
                    service['credits_required'], service['duration_minutes'],
                    service['price_usd'], service['price_inr'], service['service_category'],
                    service['expertise_level'], service['requires_birth_chart'],
                    service['cultural_focus']
                ))
            else:
                # Update existing service with enterprise features
                await conn.execute("""
                    UPDATE service_types SET
                        credits_required = $2,
                        price_usd = $3,
                        price_inr = $4,
                        service_category = $5,
                        expertise_level = $6,
                        requires_birth_chart = $7,
                        cultural_focus = $8,
                        enabled = true
                    WHERE name = $1
                """, (
                    service['name'], service['credits_required'], service['price_usd'],
                    service['price_inr'], service['service_category'], service['expertise_level'],
                    service['requires_birth_chart'], service['cultural_focus']
                ))
        
        # Insert enterprise credit packages
        credit_packages = [
            {
                'package_name': 'starter_pack',
                'credits': 25,
                'price_usd': 19.99,
                'price_inr': 1599.00,
                'bonus_credits': 5,
                'package_type': 'starter',
                'description': 'Perfect for trying our spiritual guidance services'
            },
            {
                'package_name': 'spiritual_seeker',
                'credits': 60,
                'price_usd': 44.99,
                'price_inr': 3599.00,
                'bonus_credits': 15,
                'package_type': 'popular',
                'is_popular': True,
                'description': 'Most popular package for regular spiritual guidance'
            },
            {
                'package_name': 'enlightenment_path',
                'credits': 150,
                'price_usd': 99.99,
                'price_inr': 7999.00,
                'bonus_credits': 50,
                'package_type': 'premium',
                'description': 'Comprehensive package for deep spiritual exploration'
            },
            {
                'package_name': 'master_guidance',
                'credits': 300,
                'price_usd': 179.99,
                'price_inr': 14399.00,
                'bonus_credits': 100,
                'package_type': 'elite',
                'description': 'Elite package for unlimited spiritual guidance access'
            }
        ]
        
        for package in credit_packages:
            # Check if package already exists
            existing = await conn.fetchrow(
                "SELECT id FROM credit_packages WHERE package_name = $1", package['package_name']
            )
            if not existing:
                await conn.execute("""
                    INSERT INTO credit_packages 
                    (package_name, credits, price_usd, price_inr, bonus_credits, 
                     package_type, is_popular, description, is_active)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, true)
                """, (
                    package['package_name'], package['credits'], package['price_usd'],
                    package['price_inr'], package['bonus_credits'], package['package_type'],
                    package.get('is_popular', False), package['description']
                ))
        
        logger.info("✅ Enterprise configuration data inserted")
    
    async def _validate_upgrade(self, conn):
        """Validate the enterprise database upgrade"""
        logger.info("🔍 Validating enterprise database upgrade...")
        
        # Check that all required tables exist
        required_tables = [
            'users', 'service_types', 'sessions', 'birth_chart_cache',
            'spiritual_knowledge_base', 'credit_packages', 'donations',
            'agora_usage_logs', 'user_auth_tokens'
        ]
        
        for table in required_tables:
            result = await conn.fetchrow("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = $1
                );
            """, table)
            
            if not result['exists']:
                raise Exception(f"Required table {table} was not created")
        
        # Check that key columns exist in users table
        user_columns = await conn.fetch("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'users'
        """)
        
        user_column_names = [col['column_name'] for col in user_columns]
        required_user_columns = [
            'birth_chart_data', 'birth_chart_hash', 'subscription_tier',
            'total_sessions_count', 'email_verified', 'account_status'
        ]
        
        for column in required_user_columns:
            if column not in user_column_names:
                raise Exception(f"Required column {column} not found in users table")
        
        # Validate service types have enterprise columns
        service_columns = await conn.fetch("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'service_types'
        """)
        
        service_column_names = [col['column_name'] for col in service_columns]
        required_service_columns = [
            'credits_required', 'price_usd', 'price_inr', 'enabled',
            'service_category', 'expertise_level'
        ]
        
        for column in required_service_columns:
            if column not in service_column_names:
                raise Exception(f"Required column {column} not found in service_types table")
        
        logger.info("✅ Enterprise database upgrade validation completed")

# Global instance
enterprise_upgrader = JyotiFlowEnterpriseUpgrade()

async def upgrade_to_enterprise_database():
    """Main function to upgrade to enterprise database"""
    return await enterprise_upgrader.upgrade_database()

if __name__ == "__main__":
    import asyncio
    asyncio.run(upgrade_to_enterprise_database())

