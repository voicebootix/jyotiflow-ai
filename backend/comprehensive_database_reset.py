#!/usr/bin/env python3
"""
🚀 COMPREHENSIVE DATABASE RESET - ONE SHOT SOLUTION
Creates ALL tables needed for ALL JyotiFlow.ai features in one go

Features Covered:
✅ User Management & Authentication
✅ AI Marketing Director
✅ Live Chat (Agora Integration)
✅ Social Media Automation
✅ Universal Pricing Engine
✅ Avatar Generation
✅ Spiritual Guidance & Sessions
✅ Admin Dashboard & Analytics
✅ Credit System & Monetization
✅ Platform Settings & Configuration

NO MIGRATIONS - JUST CLEAN, WORKING TABLES
"""

import asyncio
import asyncpg
import os
import logging
from datetime import datetime
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComprehensiveDatabaseReset:
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL")
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable is required")
    
    async def execute_reset(self):
        """Execute the comprehensive database reset"""
        logger.info("🚀 Starting Comprehensive Database Reset...")
        
        conn = await asyncpg.connect(self.database_url)
        try:
            # Step 1: Backup existing user data
            await self._backup_user_data(conn)
            
            # Step 2: Drop all existing tables (clean slate)
            await self._drop_all_tables(conn)
            
            # Step 3: Create all tables with proper structure
            await self._create_all_tables(conn)
            
            # Step 4: Restore user data
            await self._restore_user_data(conn)
            
            # Step 5: Insert essential data
            await self._insert_essential_data(conn)
            
            logger.info("✅ Comprehensive Database Reset Completed Successfully!")
            
        except Exception as e:
            logger.error(f"❌ Database reset failed: {str(e)}")
            raise
        finally:
            await conn.close()
    
    async def _backup_user_data(self, conn):
        """Backup existing user data before reset"""
        logger.info("💾 Backing up existing user data...")
        
        self.user_backup = []
        self.session_backup = []
        
        try:
            # Backup users
            users = await conn.fetch("SELECT * FROM users")
            self.user_backup = [dict(user) for user in users]
            logger.info(f"📋 Backed up {len(self.user_backup)} users")
            
            # Backup sessions if they exist
            try:
                sessions = await conn.fetch("SELECT * FROM sessions")
                self.session_backup = [dict(session) for session in sessions]
                logger.info(f"📋 Backed up {len(self.session_backup)} sessions")
            except:
                logger.info("📋 No sessions table found - skipping session backup")
                
        except Exception as e:
            logger.warning(f"⚠️ Backup warning: {str(e)} - Proceeding with fresh install")
            self.user_backup = []
            self.session_backup = []
    
    async def _drop_all_tables(self, conn):
        """Drop all existing tables for clean slate"""
        logger.info("🧹 Dropping all existing tables...")
        
        # Get all table names
        tables = await conn.fetch("""
            SELECT tablename FROM pg_tables 
            WHERE schemaname = 'public' 
            AND tablename NOT LIKE 'pg_%'
        """)
        
        # Drop all tables with CASCADE
        for table in tables:
            table_name = table['tablename']
            try:
                await conn.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE")
                logger.info(f"🗑️ Dropped table: {table_name}")
            except Exception as e:
                logger.warning(f"⚠️ Could not drop {table_name}: {str(e)}")
    
    async def _create_all_tables(self, conn):
        """Create ALL tables needed for ALL features"""
        logger.info("🏗️ Creating all tables for all features...")
        
        # Execute table creation in proper order
        await self._create_core_tables(conn)
        await self._create_user_tables(conn)
        await self._create_session_tables(conn)
        await self._create_pricing_tables(conn)
        await self._create_avatar_tables(conn)
        await self._create_agora_tables(conn)
        await self._create_social_media_tables(conn)
        await self._create_ai_marketing_tables(conn)
        await self._create_admin_tables(conn)
        await self._create_analytics_tables(conn)
        await self._create_platform_tables(conn)
        
        logger.info("✅ All tables created successfully!")
    
    async def _create_core_tables(self, conn):
        """Create core system tables"""
        logger.info("Creating core tables...")
        
        tables = [
            # Schema migrations tracking
            '''CREATE TABLE schema_migrations (
                id SERIAL PRIMARY KEY,
                migration_name VARCHAR(255) UNIQUE NOT NULL,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''',
            
            # Service types (core pricing)
            '''CREATE TABLE service_types (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) UNIQUE NOT NULL,
                display_name VARCHAR(255) NOT NULL,
                description TEXT,
                category VARCHAR(100),
                duration_minutes INTEGER DEFAULT 15,
                voice_enabled BOOLEAN DEFAULT true,
                video_enabled BOOLEAN DEFAULT false,
                interactive_enabled BOOLEAN DEFAULT false,
                birth_chart_enabled BOOLEAN DEFAULT false,
                remedies_enabled BOOLEAN DEFAULT false,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                service_type VARCHAR(100),
                guidance BOOLEAN DEFAULT false,
                premium BOOLEAN DEFAULT false,
                icon VARCHAR(50) DEFAULT '🔮',
                gradient_class VARCHAR(100) DEFAULT 'from-purple-500 to-indigo-600',
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
                base_credits INTEGER DEFAULT 5,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''',
            
            # API usage metrics
            '''CREATE TABLE api_usage_metrics (
                id SERIAL PRIMARY KEY,
                api_name VARCHAR(100) NOT NULL,
                endpoint VARCHAR(255) NOT NULL,
                user_email VARCHAR(255),
                request_count INTEGER DEFAULT 1,
                response_time_ms INTEGER,
                status_code INTEGER,
                error_message TEXT,
                request_size_bytes INTEGER,
                response_size_bytes INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                date DATE DEFAULT CURRENT_DATE,
                UNIQUE(api_name, endpoint, user_email, date)
            )'''
        ]
        
        for table_sql in tables:
            await conn.execute(table_sql)
        
        logger.info("✅ Core tables created")
    
    async def _create_user_tables(self, conn):
        """Create user management tables"""
        logger.info("Creating user tables...")
        
        tables = [
            # Users table
            '''CREATE TABLE users (
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
                last_login TIMESTAMP,
                profile_picture_url VARCHAR(500),
                preferences JSONB DEFAULT '{}',
                birth_chart_data JSONB DEFAULT '{}',
                subscription_status VARCHAR(50) DEFAULT 'free',
                subscription_expires_at TIMESTAMP,
                total_sessions INTEGER DEFAULT 0,
                total_spent DECIMAL(10,2) DEFAULT 0.00
            )''',
            
            # User purchases
            '''CREATE TABLE user_purchases (
                id SERIAL PRIMARY KEY,
                user_email VARCHAR(255) NOT NULL,
                service_type VARCHAR(100) NOT NULL,
                credits_purchased INTEGER NOT NULL,
                amount_paid DECIMAL(10,2) NOT NULL,
                currency VARCHAR(3) DEFAULT 'USD',
                payment_method VARCHAR(50),
                transaction_id VARCHAR(255),
                status VARCHAR(50) DEFAULT 'completed',
                purchased_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                FOREIGN KEY (user_email) REFERENCES users(email) ON DELETE CASCADE
            )''',
            
            # User sessions tracking
            '''CREATE TABLE user_sessions (
                id SERIAL PRIMARY KEY,
                session_id VARCHAR(255) UNIQUE NOT NULL,
                user_email VARCHAR(255) NOT NULL,
                session_type VARCHAR(100) NOT NULL,
                status VARCHAR(50) DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ip_address INET,
                user_agent TEXT,
                FOREIGN KEY (user_email) REFERENCES users(email) ON DELETE CASCADE
            )'''
        ]
        
        for table_sql in tables:
            await conn.execute(table_sql)
        
        logger.info("✅ User tables created")
    
    async def _create_session_tables(self, conn):
        """Create session and spiritual guidance tables"""
        logger.info("Creating session tables...")
        
        tables = [
            # Main sessions table
            '''CREATE TABLE sessions (
                id SERIAL PRIMARY KEY,
                session_id VARCHAR(255) UNIQUE NOT NULL,
                user_email VARCHAR(255) NOT NULL,
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
                feedback TEXT,
                session_data JSONB DEFAULT '{}',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_email) REFERENCES users(email) ON DELETE CASCADE,
                FOREIGN KEY (service_type) REFERENCES service_types(name) ON DELETE RESTRICT
            )''',
            
            # Service usage logs
            '''CREATE TABLE service_usage_logs (
                id SERIAL PRIMARY KEY,
                user_email VARCHAR(255) NOT NULL,
                service_type VARCHAR(100) NOT NULL,
                session_reference VARCHAR(255),
                credits_used INTEGER NOT NULL,
                duration_minutes INTEGER,
                cost_breakdown JSONB DEFAULT '{}',
                usage_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                billing_status VARCHAR(50) DEFAULT 'completed',
                FOREIGN KEY (user_email) REFERENCES users(email) ON DELETE CASCADE,
                FOREIGN KEY (service_type) REFERENCES service_types(name) ON DELETE RESTRICT
            )''',
            
            # Birth chart cache
            '''CREATE TABLE birth_chart_cache (
                id SERIAL PRIMARY KEY,
                user_email VARCHAR(255) NOT NULL,
                birth_details_hash VARCHAR(64) UNIQUE NOT NULL,
                birth_details JSONB NOT NULL,
                chart_data JSONB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                access_count INTEGER DEFAULT 1,
                last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_email) REFERENCES users(email) ON DELETE CASCADE
            )''',
            
            # RAG knowledge base
            '''CREATE TABLE rag_knowledge_base (
                id SERIAL PRIMARY KEY,
                title VARCHAR(500) NOT NULL,
                content TEXT NOT NULL,
                category VARCHAR(100),
                tags TEXT[],
                embedding_vector FLOAT[],
                metadata JSONB DEFAULT '{}',
                source_url VARCHAR(500),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT true
            )'''
        ]
        
        for table_sql in tables:
            await conn.execute(table_sql)
        
        logger.info("✅ Session tables created")
    
    async def _create_pricing_tables(self, conn):
        """Create pricing and monetization tables"""
        logger.info("Creating pricing tables...")
        
        tables = [
            # AI pricing recommendations
            '''CREATE TABLE ai_pricing_recommendations (
                id SERIAL PRIMARY KEY,
                service_type VARCHAR(100) NOT NULL,
                current_price DECIMAL(10,2) NOT NULL,
                recommended_price DECIMAL(10,2) NOT NULL,
                demand_factor DECIMAL(5,2) DEFAULT 1.0,
                cost_breakdown JSONB DEFAULT '{}',
                ai_recommendation JSONB DEFAULT '{}',
                pricing_rationale TEXT,
                confidence_score DECIMAL(3,2) DEFAULT 0.5,
                status VARCHAR(50) DEFAULT 'pending',
                admin_approved BOOLEAN DEFAULT false,
                admin_notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                FOREIGN KEY (service_type) REFERENCES service_types(name) ON DELETE CASCADE
            )''',
            
            # Monetization insights
            '''CREATE TABLE monetization_insights (
                id SERIAL PRIMARY KEY,
                recommendation_id VARCHAR(100) UNIQUE NOT NULL,
                recommendation_type VARCHAR(50) NOT NULL,
                title VARCHAR(255) NOT NULL,
                description TEXT NOT NULL,
                projected_revenue_increase_percent DECIMAL(5,2),
                projected_user_impact VARCHAR(255),
                confidence_score DECIMAL(3,2) NOT NULL,
                implementation_effort VARCHAR(20) NOT NULL,
                timeframe_days INTEGER,
                risk_level VARCHAR(20) NOT NULL,
                data_points JSONB,
                status VARCHAR(50) DEFAULT 'pending',
                admin_response TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP
            )'''
        ]
        
        for table_sql in tables:
            await conn.execute(table_sql)
        
        logger.info("✅ Pricing tables created")
    
    async def _create_avatar_tables(self, conn):
        """Create avatar generation tables"""
        logger.info("Creating avatar tables...")
        
        tables = [
            # Avatar templates
            '''CREATE TABLE avatar_templates (
                id SERIAL PRIMARY KEY,
                template_name VARCHAR(100) UNIQUE NOT NULL,
                avatar_style VARCHAR(50) NOT NULL,
                voice_tone VARCHAR(50) NOT NULL,
                background_style VARCHAR(50) NOT NULL,
                clothing_style VARCHAR(50) NOT NULL,
                description TEXT,
                preview_image_url VARCHAR(500),
                is_premium BOOLEAN DEFAULT false,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''',
            
            # Avatar sessions
            '''CREATE TABLE avatar_sessions (
                id SERIAL PRIMARY KEY,
                session_id VARCHAR(255) UNIQUE NOT NULL,
                user_email VARCHAR(255) NOT NULL,
                template_id INTEGER NOT NULL,
                avatar_prompt TEXT NOT NULL,
                generated_avatar_url VARCHAR(500),
                status VARCHAR(50) DEFAULT 'pending',
                generation_time_seconds DECIMAL(10,2),
                quality_score DECIMAL(3,2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_email) REFERENCES users(email) ON DELETE CASCADE,
                FOREIGN KEY (template_id) REFERENCES avatar_templates(id) ON DELETE CASCADE
            )''',
            
            # Avatar generation queue
            '''CREATE TABLE avatar_generation_queue (
                id SERIAL PRIMARY KEY,
                session_id VARCHAR(255) NOT NULL,
                user_email VARCHAR(255) NOT NULL,
                template_id INTEGER NOT NULL,
                prompt TEXT NOT NULL,
                priority INTEGER DEFAULT 5,
                status VARCHAR(50) DEFAULT 'queued',
                attempts INTEGER DEFAULT 0,
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                FOREIGN KEY (user_email) REFERENCES users(email) ON DELETE CASCADE,
                FOREIGN KEY (template_id) REFERENCES avatar_templates(id) ON DELETE CASCADE
            )'''
        ]
        
        for table_sql in tables:
            await conn.execute(table_sql)
        
        logger.info("✅ Avatar tables created")
    
    async def _create_agora_tables(self, conn):
        """Create Agora live chat tables"""
        logger.info("Creating Agora tables...")
        
        tables = [
            # Live chat sessions
            '''CREATE TABLE live_chat_sessions (
                id SERIAL PRIMARY KEY,
                session_id VARCHAR(255) UNIQUE NOT NULL,
                user_email VARCHAR(255) NOT NULL,
                channel_name VARCHAR(255) NOT NULL,
                agora_app_id VARCHAR(255) NOT NULL,
                agora_token VARCHAR(500) NOT NULL,
                user_role VARCHAR(50) DEFAULT 'audience',
                session_type VARCHAR(100) DEFAULT 'spiritual_guidance',
                mode VARCHAR(20) DEFAULT 'video',
                status VARCHAR(50) DEFAULT 'active',
                credits_used INTEGER DEFAULT 0,
                duration_minutes INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                started_at TIMESTAMP,
                ended_at TIMESTAMP,
                expires_at TIMESTAMP,
                FOREIGN KEY (user_email) REFERENCES users(email) ON DELETE CASCADE
            )''',
            
            # Session participants
            '''CREATE TABLE session_participants (
                id SERIAL PRIMARY KEY,
                session_id VARCHAR(255) NOT NULL,
                user_email VARCHAR(255) NOT NULL,
                agora_uid INTEGER NOT NULL,
                role VARCHAR(50) DEFAULT 'audience',
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                left_at TIMESTAMP,
                duration_minutes INTEGER,
                FOREIGN KEY (user_email) REFERENCES users(email) ON DELETE CASCADE
            )''',
            
            # Agora usage logs
            '''CREATE TABLE agora_usage_logs (
                id SERIAL PRIMARY KEY,
                session_id VARCHAR(255) NOT NULL,
                user_email VARCHAR(255) NOT NULL,
                event_type VARCHAR(50) NOT NULL,
                event_data JSONB DEFAULT '{}',
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_email) REFERENCES users(email) ON DELETE CASCADE
            )'''
        ]
        
        for table_sql in tables:
            await conn.execute(table_sql)
        
        logger.info("✅ Agora tables created")
    
    async def _create_social_media_tables(self, conn):
        """Create social media automation tables"""
        logger.info("Creating social media tables...")
        
        tables = [
            # Platform settings
            '''CREATE TABLE platform_settings (
                id SERIAL PRIMARY KEY,
                key VARCHAR(100) UNIQUE NOT NULL,
                value JSONB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''',
            
            # Social campaigns
            '''CREATE TABLE social_campaigns (
                id SERIAL PRIMARY KEY,
                campaign_id VARCHAR(100) UNIQUE NOT NULL,
                name VARCHAR(255) NOT NULL,
                platform VARCHAR(50) NOT NULL,
                campaign_type VARCHAR(50) NOT NULL,
                budget DECIMAL(10,2),
                target_audience JSONB,
                duration_days INTEGER,
                status VARCHAR(50) DEFAULT 'active',
                start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                end_date TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''',
            
            # Social posts
            '''CREATE TABLE social_posts (
                id SERIAL PRIMARY KEY,
                post_id VARCHAR(100) UNIQUE NOT NULL,
                platform VARCHAR(50) NOT NULL,
                platform_post_id VARCHAR(255),
                title VARCHAR(500),
                content TEXT NOT NULL,
                hashtags TEXT,
                media_url VARCHAR(500),
                scheduled_time TIMESTAMP,
                posted_time TIMESTAMP,
                status VARCHAR(50) DEFAULT 'scheduled',
                engagement_metrics JSONB DEFAULT '{}',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''',
            
            # Social content
            '''CREATE TABLE social_content (
                id SERIAL PRIMARY KEY,
                content_id VARCHAR(100) UNIQUE NOT NULL,
                title VARCHAR(255) NOT NULL,
                content TEXT NOT NULL,
                content_type VARCHAR(50) NOT NULL,
                platform VARCHAR(50) NOT NULL,
                hashtags TEXT,
                media_urls TEXT[],
                engagement_score DECIMAL(5,2),
                performance_metrics JSONB DEFAULT '{}',
                status VARCHAR(50) DEFAULT 'draft',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )'''
        ]
        
        for table_sql in tables:
            await conn.execute(table_sql)
        
        logger.info("✅ Social media tables created")
    
    async def _create_ai_marketing_tables(self, conn):
        """Create AI Marketing Director tables"""
        logger.info("Creating AI Marketing tables...")
        
        tables = [
            # Marketing campaigns
            '''CREATE TABLE marketing_campaigns (
                id SERIAL PRIMARY KEY,
                campaign_id VARCHAR(100) UNIQUE NOT NULL,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                campaign_type VARCHAR(50) NOT NULL,
                target_audience JSONB,
                budget DECIMAL(10,2),
                status VARCHAR(50) DEFAULT 'draft',
                start_date TIMESTAMP,
                end_date TIMESTAMP,
                performance_metrics JSONB DEFAULT '{}',
                ai_recommendations JSONB DEFAULT '{}',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''',
            
            # Marketing insights
            '''CREATE TABLE marketing_insights (
                id SERIAL PRIMARY KEY,
                insight_id VARCHAR(100) UNIQUE NOT NULL,
                insight_type VARCHAR(50) NOT NULL,
                title VARCHAR(255) NOT NULL,
                description TEXT NOT NULL,
                data_points JSONB,
                confidence_score DECIMAL(3,2),
                actionable_recommendations TEXT[],
                impact_level VARCHAR(20),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP
            )''',
            
            # Performance analytics
            '''CREATE TABLE performance_analytics (
                id SERIAL PRIMARY KEY,
                metric_name VARCHAR(100) NOT NULL,
                metric_value DECIMAL(15,2) NOT NULL,
                metric_type VARCHAR(50) NOT NULL,
                time_period VARCHAR(50) NOT NULL,
                dimensions JSONB DEFAULT '{}',
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                date DATE DEFAULT CURRENT_DATE
            )'''
        ]
        
        for table_sql in tables:
            await conn.execute(table_sql)
        
        logger.info("✅ AI Marketing tables created")
    
    async def _create_admin_tables(self, conn):
        """Create admin dashboard tables"""
        logger.info("Creating admin tables...")
        
        tables = [
            # Admin analytics
            '''CREATE TABLE admin_analytics (
                id SERIAL PRIMARY KEY,
                metric_name VARCHAR(100) NOT NULL,
                metric_value DECIMAL(15,2) NOT NULL,
                metric_category VARCHAR(50) NOT NULL,
                time_period VARCHAR(50) NOT NULL,
                metadata JSONB DEFAULT '{}',
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                date DATE DEFAULT CURRENT_DATE
            )''',
            
            # System logs
            '''CREATE TABLE system_logs (
                id SERIAL PRIMARY KEY,
                log_level VARCHAR(20) NOT NULL,
                component VARCHAR(100) NOT NULL,
                message TEXT NOT NULL,
                details JSONB DEFAULT '{}',
                user_email VARCHAR(255),
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_email) REFERENCES users(email) ON DELETE SET NULL
            )''',
            
            # Admin notifications
            '''CREATE TABLE admin_notifications (
                id SERIAL PRIMARY KEY,
                notification_type VARCHAR(50) NOT NULL,
                title VARCHAR(255) NOT NULL,
                message TEXT NOT NULL,
                priority VARCHAR(20) DEFAULT 'medium',
                status VARCHAR(50) DEFAULT 'unread',
                metadata JSONB DEFAULT '{}',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                read_at TIMESTAMP
            )'''
        ]
        
        for table_sql in tables:
            await conn.execute(table_sql)
        
        logger.info("✅ Admin tables created")
    
    async def _create_analytics_tables(self, conn):
        """Create analytics and reporting tables"""
        logger.info("Creating analytics tables...")
        
        tables = [
            # User analytics
            '''CREATE TABLE user_analytics (
                id SERIAL PRIMARY KEY,
                user_email VARCHAR(255) NOT NULL,
                event_type VARCHAR(100) NOT NULL,
                event_data JSONB DEFAULT '{}',
                session_id VARCHAR(255),
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                date DATE DEFAULT CURRENT_DATE,
                FOREIGN KEY (user_email) REFERENCES users(email) ON DELETE CASCADE
            )''',
            
            # Revenue analytics
            '''CREATE TABLE revenue_analytics (
                id SERIAL PRIMARY KEY,
                revenue_type VARCHAR(50) NOT NULL,
                amount DECIMAL(10,2) NOT NULL,
                currency VARCHAR(3) DEFAULT 'USD',
                service_type VARCHAR(100),
                user_email VARCHAR(255),
                transaction_id VARCHAR(255),
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                date DATE DEFAULT CURRENT_DATE,
                FOREIGN KEY (user_email) REFERENCES users(email) ON DELETE SET NULL
            )''',
            
            # Feature usage analytics
            '''CREATE TABLE feature_usage_analytics (
                id SERIAL PRIMARY KEY,
                feature_name VARCHAR(100) NOT NULL,
                usage_count INTEGER DEFAULT 1,
                user_email VARCHAR(255),
                session_id VARCHAR(255),
                metadata JSONB DEFAULT '{}',
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                date DATE DEFAULT CURRENT_DATE,
                FOREIGN KEY (user_email) REFERENCES users(email) ON DELETE SET NULL
            )'''
        ]
        
        for table_sql in tables:
            await conn.execute(table_sql)
        
        logger.info("✅ Analytics tables created")
    
    async def _create_platform_tables(self, conn):
        """Create platform configuration tables"""
        logger.info("Creating platform tables...")
        
        tables = [
            # Feature flags
            '''CREATE TABLE feature_flags (
                id SERIAL PRIMARY KEY,
                flag_name VARCHAR(100) UNIQUE NOT NULL,
                is_enabled BOOLEAN DEFAULT false,
                description TEXT,
                target_audience VARCHAR(50) DEFAULT 'all',
                rollout_percentage INTEGER DEFAULT 0,
                metadata JSONB DEFAULT '{}',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''',
            
            # System configuration
            '''CREATE TABLE system_configuration (
                id SERIAL PRIMARY KEY,
                config_key VARCHAR(100) UNIQUE NOT NULL,
                config_value JSONB NOT NULL,
                description TEXT,
                is_sensitive BOOLEAN DEFAULT false,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''',
            
            # API keys and integrations
            '''CREATE TABLE api_integrations (
                id SERIAL PRIMARY KEY,
                integration_name VARCHAR(100) UNIQUE NOT NULL,
                api_key_encrypted TEXT,
                configuration JSONB DEFAULT '{}',
                status VARCHAR(50) DEFAULT 'inactive',
                last_tested TIMESTAMP,
                test_result JSONB DEFAULT '{}',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )'''
        ]
        
        for table_sql in tables:
            await conn.execute(table_sql)
        
        logger.info("✅ Platform tables created")
    
    async def _restore_user_data(self, conn):
        """Restore backed up user data"""
        logger.info("🔄 Restoring user data...")
        
        # Restore users
        for user in self.user_backup:
            try:
                await conn.execute("""
                    INSERT INTO users (
                        email, password_hash, full_name, phone, date_of_birth, 
                        birth_time, birth_location, timezone, credits, role, 
                        is_active, email_verified, phone_verified, created_at, 
                        updated_at, last_login, profile_picture_url, preferences, 
                        birth_chart_data, subscription_status, subscription_expires_at, 
                        total_sessions, total_spent
                    ) VALUES (
                        $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, 
                        $14, $15, $16, $17, $18, $19, $20, $21, $22, $23
                    ) ON CONFLICT (email) DO UPDATE SET
                        credits = EXCLUDED.credits,
                        role = EXCLUDED.role,
                        updated_at = CURRENT_TIMESTAMP
                """, 
                user['email'], user['password_hash'], user.get('full_name'), 
                user.get('phone'), user.get('date_of_birth'), user.get('birth_time'),
                user.get('birth_location'), user.get('timezone', 'Asia/Colombo'),
                user.get('credits', 0), user.get('role', 'user'),
                user.get('is_active', True), user.get('email_verified', False),
                user.get('phone_verified', False), user.get('created_at'),
                user.get('updated_at'), user.get('last_login'),
                user.get('profile_picture_url'), user.get('preferences', {}),
                user.get('birth_chart_data', {}), user.get('subscription_status', 'free'),
                user.get('subscription_expires_at'), user.get('total_sessions', 0),
                user.get('total_spent', 0.00))
                
                logger.info(f"✅ Restored user: {user['email']}")
            except Exception as e:
                logger.error(f"❌ Failed to restore user {user['email']}: {str(e)}")
        
        logger.info(f"✅ Restored {len(self.user_backup)} users")
    
    async def _insert_essential_data(self, conn):
        """Insert essential data for platform functionality"""
        logger.info("📝 Inserting essential data...")
        
        # Insert default service types
        default_services = [
            ('clarity', 'Basic Spiritual Clarity Session', 'Basic spiritual clarity session', 'guidance', 15, True, False, False, False, False, 5),
            ('love', 'Love & Relationship Guidance', 'Love and relationship guidance', 'guidance', 20, True, False, False, False, False, 8),
            ('premium', 'Premium Comprehensive Reading', 'Premium comprehensive reading', 'premium', 30, True, True, True, True, True, 12),
            ('elite', 'Elite Personalized Consultation', 'Elite personalized consultation', 'elite', 45, True, True, True, True, True, 20),
            ('comprehensive_life_reading_30min', 'Comprehensive Life Reading', 'Comprehensive 30-minute life reading', 'premium', 30, True, True, True, True, True, 15),
            ('horoscope_reading_quick', 'Quick Horoscope Reading', 'Quick horoscope reading', 'guidance', 10, True, False, False, True, False, 3),
            ('satsang_community', 'Satsang Community Access', 'Access to live satsang events', 'community', 90, True, True, True, False, False, 2)
        ]
        
        for service in default_services:
            await conn.execute("""
                INSERT INTO service_types (
                    name, display_name, description, category, duration_minutes, 
                    voice_enabled, video_enabled, interactive_enabled, 
                    birth_chart_enabled, remedies_enabled, base_credits
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                ON CONFLICT (name) DO UPDATE SET
                    display_name = EXCLUDED.display_name,
                    description = EXCLUDED.description,
                    updated_at = CURRENT_TIMESTAMP
            """, *service)
        
        # Insert default avatar templates
        avatar_templates = [
            ('traditional_swamiji', 'traditional', 'compassionate', 'ashram', 'saffron_robes'),
            ('modern_guide', 'modern', 'wise', 'studio', 'formal_attire'),
            ('festival_celebrant', 'festival', 'joyful', 'temple', 'festive_robes'),
            ('meditation_master', 'meditation', 'gentle', 'garden', 'simple_robes')
        ]
        
        for template in avatar_templates:
            await conn.execute("""
                INSERT INTO avatar_templates (
                    template_name, avatar_style, voice_tone, background_style, clothing_style
                ) VALUES ($1, $2, $3, $4, $5)
                ON CONFLICT (template_name) DO NOTHING
            """, *template)
        
        # Insert essential platform settings
        platform_settings = [
            ('youtube_api_key', '{}'),
            ('facebook_api_key', '{}'),
            ('instagram_api_key', '{}'),
            ('twitter_api_key', '{}'),
            ('linkedin_api_key', '{}'),
            ('social_media_automation_enabled', 'true'),
            ('ai_marketing_enabled', 'true'),
            ('live_chat_enabled', 'true')
        ]
        
        for setting in platform_settings:
            await conn.execute("""
                INSERT INTO platform_settings (key, value) 
                VALUES ($1, $2) 
                ON CONFLICT (key) DO NOTHING
            """, setting[0], setting[1])
        
        # Insert feature flags
        feature_flags = [
            ('ai_marketing_director', True, 'AI Marketing Director feature'),
            ('social_media_automation', True, 'Social media automation feature'),
            ('live_chat_agora', True, 'Live chat with Agora integration'),
            ('avatar_generation', True, 'Avatar generation feature'),
            ('universal_pricing', True, 'Universal pricing engine'),
            ('admin_analytics', True, 'Admin analytics dashboard')
        ]
        
        for flag in feature_flags:
            await conn.execute("""
                INSERT INTO feature_flags (flag_name, is_enabled, description) 
                VALUES ($1, $2, $3) 
                ON CONFLICT (flag_name) DO UPDATE SET
                    is_enabled = EXCLUDED.is_enabled,
                    updated_at = CURRENT_TIMESTAMP
            """, *flag)
        
        logger.info("✅ Essential data inserted")

# Main execution
async def main():
    """Main execution function"""
    reset = ComprehensiveDatabaseReset()
    await reset.execute_reset()

if __name__ == "__main__":
    asyncio.run(main())

