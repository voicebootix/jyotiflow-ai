"""
🎯 JyotiFlow Database Initialization Script
Automatically creates all necessary tables in Supabase PostgreSQL
"""

import os
import json
import logging
import asyncpg
from datetime import datetime, timezone, timedelta
from typing import Dict, Any

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JyotiFlowDatabaseInitializer:
    """Handles complete database initialization for JyotiFlow"""
    
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL")
        
        # Validate DATABASE_URL is set
        if not self.database_url:
            raise ValueError(
                "DATABASE_URL environment variable is missing or empty. "
                "Please set the DATABASE_URL environment variable before running database initialization. "
                "Example: export DATABASE_URL='postgresql://user:password@localhost/dbname'"
            )
        
    async def initialize_database(self):
        """Initialize complete JyotiFlow database"""
        logger.info("🚀 Initializing JyotiFlow Database...")
        
        try:
            conn = await asyncpg.connect(self.database_url)
            
            # Create all tables
            await self._create_core_tables(conn)
            await self._create_user_tables(conn)
            await self._create_session_tables(conn)
            await self._create_pricing_tables(conn)
            await self._create_avatar_tables(conn)
            await self._create_agora_tables(conn)
            await self._create_enhanced_tables(conn)
            await self._create_admin_tables(conn)
            await self._create_platform_tables(conn)
            
            # Insert initial data
            await self._insert_initial_data(conn)
            
            await conn.close()
            logger.info("✅ Database initialization completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")
            return False
    
    async def _create_core_tables(self, conn):
        """Create core system tables"""
        logger.info("Creating core tables...")
        
        tables = [
            # Users table
            '''CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                name VARCHAR(255) NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                role VARCHAR(50) DEFAULT 'user',
                credits INTEGER DEFAULT 0,
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
            );''',
            
            # Service types table
            '''CREATE TABLE IF NOT EXISTS service_types (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) UNIQUE NOT NULL,
                description TEXT,
                base_credits INTEGER NOT NULL,
                duration_minutes INTEGER DEFAULT 15,
                video_enabled BOOLEAN DEFAULT true,
                knowledge_configuration JSONB DEFAULT '{}',
                specialized_prompts JSONB DEFAULT '{}',
                response_behavior JSONB DEFAULT '{}',
                swami_persona_mode VARCHAR(100) DEFAULT 'general',
                analysis_depth VARCHAR(50) DEFAULT 'standard',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );''',
            
            # Sessions table
            '''CREATE TABLE IF NOT EXISTS sessions (
                id SERIAL PRIMARY KEY,
                session_id VARCHAR(100) UNIQUE NOT NULL,
                user_email VARCHAR(255) NOT NULL,
                service_type VARCHAR(100) NOT NULL,
                question TEXT NOT NULL,
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
                credits_used INTEGER DEFAULT 0,
                original_price DECIMAL(10,2),
                user_rating INTEGER CHECK (user_rating >= 1 AND user_rating <= 5),
                user_feedback TEXT,
                session_quality_score DECIMAL(3,2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                FOREIGN KEY (user_email) REFERENCES users(email)
            );'''
        ]
        
        for table_sql in tables:
            await conn.execute(table_sql)
        
        logger.info("✅ Core tables created")
    
    async def _create_user_tables(self, conn):
        """Create user-related tables"""
        logger.info("Creating user tables...")
        
        tables = [
            # User purchases/transactions
            '''CREATE TABLE IF NOT EXISTS user_purchases (
                id SERIAL PRIMARY KEY,
                user_email VARCHAR(255) NOT NULL,
                transaction_type VARCHAR(50) DEFAULT 'purchase',
                amount DECIMAL(10,2) NOT NULL,
                credits INTEGER NOT NULL,
                balance_before INTEGER DEFAULT 0,
                balance_after INTEGER DEFAULT 0,
                package_type VARCHAR(100),
                payment_method VARCHAR(50),
                stripe_session_id VARCHAR(255),
                stripe_payment_intent_id VARCHAR(255),
                description TEXT,
                status VARCHAR(50) DEFAULT 'completed',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_email) REFERENCES users(email)
            );''',
            
            # User subscriptions
            '''CREATE TABLE IF NOT EXISTS user_subscriptions (
                id SERIAL PRIMARY KEY,
                user_email VARCHAR(255) NOT NULL,
                subscription_tier VARCHAR(50) NOT NULL,
                stripe_subscription_id VARCHAR(255),
                status VARCHAR(50) DEFAULT 'active',
                current_period_start TIMESTAMP,
                current_period_end TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_email) REFERENCES users(email)
            );'''
        ]
        
        for table_sql in tables:
            await conn.execute(table_sql)
        
        logger.info("✅ User tables created")
    
    async def _create_session_tables(self, conn):
        """Create session-related tables"""
        logger.info("Creating session tables...")
        
        tables = [
            # Avatar sessions
            '''CREATE TABLE IF NOT EXISTS avatar_sessions (
                id SERIAL PRIMARY KEY,
                session_id VARCHAR(100) UNIQUE NOT NULL,
                user_email VARCHAR(255) NOT NULL,
                avatar_prompt TEXT NOT NULL,
                voice_script TEXT NOT NULL,
                avatar_style VARCHAR(50) DEFAULT 'traditional',
                voice_tone VARCHAR(50) DEFAULT 'compassionate',
                generation_status VARCHAR(50) DEFAULT 'pending',
                generation_started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                generation_completed_at TIMESTAMP,
                video_url VARCHAR(500),
                audio_url VARCHAR(500),
                duration_seconds INTEGER,
                file_size_mb DECIMAL(10,2),
                video_quality VARCHAR(20) DEFAULT 'high',
                d_id_cost DECIMAL(10,2),
                elevenlabs_cost DECIMAL(10,2),
                total_cost DECIMAL(10,2),
                generation_time_seconds DECIMAL(10,2),
                quality_score DECIMAL(3,2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_email) REFERENCES users(email)
            );''',
            
            # Satsang events
            '''CREATE TABLE IF NOT EXISTS satsang_events (
                id SERIAL PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                scheduled_date TIMESTAMP NOT NULL,
                duration_minutes INTEGER DEFAULT 90,
                max_attendees INTEGER DEFAULT 1000,
                is_premium_only BOOLEAN DEFAULT false,
                stream_url VARCHAR(500),
                agora_channel_name VARCHAR(255),
                recording_url VARCHAR(500),
                status VARCHAR(50) DEFAULT 'scheduled',
                actual_start_time TIMESTAMP,
                actual_end_time TIMESTAMP,
                total_registrations INTEGER DEFAULT 0,
                peak_concurrent_attendees INTEGER DEFAULT 0,
                average_engagement_score DECIMAL(3,2),
                spiritual_theme VARCHAR(255),
                key_teachings TEXT[],
                created_by VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );''',
            
            # Satsang attendees
            '''CREATE TABLE IF NOT EXISTS satsang_attendees (
                id SERIAL PRIMARY KEY,
                satsang_id INTEGER NOT NULL,
                user_email VARCHAR(255) NOT NULL,
                registration_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                attended BOOLEAN DEFAULT false,
                join_time TIMESTAMP,
                leave_time TIMESTAMP,
                duration_minutes INTEGER,
                questions_asked INTEGER DEFAULT 0,
                chat_messages_sent INTEGER DEFAULT 0,
                engagement_score DECIMAL(3,2),
                rating INTEGER CHECK (rating >= 1 AND rating <= 5),
                feedback TEXT,
                FOREIGN KEY (satsang_id) REFERENCES satsang_events(id),
                FOREIGN KEY (user_email) REFERENCES users(email)
            );'''
        ]
        
        for table_sql in tables:
            await conn.execute(table_sql)
        
        logger.info("✅ Session tables created")
    
    async def _create_pricing_tables(self, conn):
        """Create pricing and monetization tables"""
        logger.info("Creating pricing tables...")
        
        tables = [
            # AI pricing recommendations
            '''CREATE TABLE IF NOT EXISTS ai_pricing_recommendations (
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
                expires_at TIMESTAMP
            );''',
            
            # Monetization insights
            '''CREATE TABLE IF NOT EXISTS monetization_insights (
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
            );'''
        ]
        
        for table_sql in tables:
            await conn.execute(table_sql)
        
        logger.info("✅ Pricing tables created")
    
    async def _create_avatar_tables(self, conn):
        """Create avatar generation tables"""
        logger.info("Creating avatar tables...")
        
        tables = [
            # Avatar generation queue
            '''CREATE TABLE IF NOT EXISTS avatar_generation_queue (
                id SERIAL PRIMARY KEY,
                session_id VARCHAR(100) UNIQUE NOT NULL,
                user_email VARCHAR(255) NOT NULL,
                status VARCHAR(50) DEFAULT 'queued',
                priority INTEGER DEFAULT 5,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                error_message TEXT,
                FOREIGN KEY (user_email) REFERENCES users(email)
            );''',
            
            # Avatar templates
            '''CREATE TABLE IF NOT EXISTS avatar_templates (
                id SERIAL PRIMARY KEY,
                template_name VARCHAR(100) UNIQUE NOT NULL,
                avatar_style VARCHAR(50) NOT NULL,
                voice_tone VARCHAR(50) NOT NULL,
                background_style VARCHAR(50),
                clothing_style VARCHAR(50),
                is_active BOOLEAN DEFAULT true,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );'''
        ]
        
        for table_sql in tables:
            await conn.execute(table_sql)
        
        logger.info("✅ Avatar tables created")
    
    async def _create_agora_tables(self, conn):
        """Create Agora live chat tables"""
        logger.info("Creating Agora tables...")
        
        tables = [
            # Live chat sessions
            '''CREATE TABLE IF NOT EXISTS live_chat_sessions (
                id SERIAL PRIMARY KEY,
                session_id VARCHAR(100) UNIQUE NOT NULL,
                user_email VARCHAR(255) NOT NULL,
                service_type VARCHAR(50) NOT NULL,
                session_duration_minutes INTEGER DEFAULT 15,
                status VARCHAR(50) DEFAULT 'active',
                agora_channel_name VARCHAR(255),
                agora_token TEXT,
                start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                end_time TIMESTAMP,
                total_cost DECIMAL(10,2),
                credits_used INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_email) REFERENCES users(email)
            );''',
            
            # Session participants
            '''CREATE TABLE IF NOT EXISTS session_participants (
                id SERIAL PRIMARY KEY,
                session_id VARCHAR(100) NOT NULL,
                user_email VARCHAR(255) NOT NULL,
                role VARCHAR(20) DEFAULT 'participant',
                join_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                leave_time TIMESTAMP,
                duration_minutes INTEGER,
                FOREIGN KEY (session_id) REFERENCES live_chat_sessions(session_id),
                FOREIGN KEY (user_email) REFERENCES users(email)
            );''',
            
            # Agora usage logs
            '''CREATE TABLE IF NOT EXISTS agora_usage_logs (
                id SERIAL PRIMARY KEY,
                session_id VARCHAR(100) NOT NULL,
                user_email VARCHAR(255) NOT NULL,
                event_type VARCHAR(50) NOT NULL,
                event_data JSONB,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES live_chat_sessions(session_id),
                FOREIGN KEY (user_email) REFERENCES users(email)
            );'''
        ]
        
        for table_sql in tables:
            await conn.execute(table_sql)
        
        logger.info("✅ Agora tables created")
    
    async def _create_enhanced_tables(self, conn):
        """Create enhanced system tables"""
        logger.info("Creating enhanced tables...")
        
        tables = [
            # RAG knowledge base
            '''CREATE TABLE IF NOT EXISTS rag_knowledge_base (
                id TEXT PRIMARY KEY,
                knowledge_domain VARCHAR(100) NOT NULL,
                content_type VARCHAR(50) NOT NULL,
                title VARCHAR(500) NOT NULL,
                content TEXT NOT NULL,
                metadata JSONB DEFAULT '{}',
                embedding_vector TEXT,
                tags TEXT DEFAULT '',
                source_reference VARCHAR(500),
                authority_level INTEGER DEFAULT 1,
                cultural_context VARCHAR(100) DEFAULT 'universal',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );''',
            
            # Service configuration cache
            '''CREATE TABLE IF NOT EXISTS service_configuration_cache (
                service_name VARCHAR(100) PRIMARY KEY,
                configuration JSONB NOT NULL,
                persona_config JSONB NOT NULL,
                knowledge_domains TEXT NOT NULL,
                cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP
            );''',
            
            # Social media content (updated for admin interface compatibility)
            '''CREATE TABLE IF NOT EXISTS social_content (
                id SERIAL PRIMARY KEY,
                content_id VARCHAR(100) UNIQUE NOT NULL,
                content_type VARCHAR(50) NOT NULL,
                platform VARCHAR(50) NOT NULL,
                title VARCHAR(255),
                content_text TEXT NOT NULL,
                media_url VARCHAR(500),
                hashtags VARCHAR(500),
                scheduled_at TIMESTAMP,
                published_at TIMESTAMP,
                status VARCHAR(50) DEFAULT 'draft',
                views INTEGER DEFAULT 0,
                likes INTEGER DEFAULT 0,
                shares INTEGER DEFAULT 0,
                comments INTEGER DEFAULT 0,
                engagement_rate DECIMAL(5,2) DEFAULT 0.0,
                source_session_id VARCHAR(100),
                source_user_email VARCHAR(255),
                ai_generated BOOLEAN DEFAULT true,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (source_user_email) REFERENCES users(email)
            );'''
        ]
        
        for table_sql in tables:
            await conn.execute(table_sql)
        
        logger.info("✅ Enhanced tables created")
    
    async def _create_admin_tables(self, conn):
        """Create admin and analytics tables"""
        logger.info("Creating admin tables...")
        
        tables = [
            # System analytics
            '''CREATE TABLE IF NOT EXISTS system_analytics (
                id SERIAL PRIMARY KEY,
                metric_name VARCHAR(100) NOT NULL,
                metric_value DECIMAL(15,2) NOT NULL,
                metric_unit VARCHAR(50),
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata JSONB DEFAULT '{}'
            );''',
            
            # Admin audit logs
            '''CREATE TABLE IF NOT EXISTS admin_audit_logs (
                id SERIAL PRIMARY KEY,
                admin_email VARCHAR(255) NOT NULL,
                action VARCHAR(100) NOT NULL,
                resource_type VARCHAR(50),
                resource_id VARCHAR(100),
                details JSONB,
                ip_address VARCHAR(45),
                user_agent TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );'''
        ]
        
        for table_sql in tables:
            await conn.execute(table_sql)
        
        logger.info("✅ Admin tables created")
    
    async def _create_platform_tables(self, conn):
        """Create platform settings and social media automation tables"""
        logger.info("Creating platform tables...")
        
        tables = [
            # Platform settings for API credentials and configuration
            '''CREATE TABLE IF NOT EXISTS platform_settings (
                id SERIAL PRIMARY KEY,
                key VARCHAR(100) UNIQUE NOT NULL,
                value JSONB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );''',
            
            # Social media campaigns
            '''CREATE TABLE IF NOT EXISTS social_campaigns (
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
            );''',
            
            # Social media posts tracking
            '''CREATE TABLE IF NOT EXISTS social_posts (
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
            );'''
        ]
        
        for table_sql in tables:
            await conn.execute(table_sql)
        
        logger.info("✅ Platform tables created")
    
    async def _insert_initial_data(self, conn):
        """Insert initial data into tables"""
        logger.info("Inserting initial data...")
        
        try:
            # Insert default service types
            default_services = [
                ('clarity', 'Basic spiritual clarity session', 5, 15, True),
                ('love', 'Love and relationship guidance', 8, 20, True),
                ('premium', 'Premium comprehensive reading', 12, 30, True),
                ('elite', 'Elite personalized consultation', 20, 45, True)
            ]
            
            for service in default_services:
                # Check if service already exists
                existing = await conn.fetchrow(
                    "SELECT id FROM service_types WHERE name = $1", service[0]
                )
                if not existing:
                    await conn.execute("""
                        INSERT INTO service_types (name, description, base_credits, duration_minutes, video_enabled)
                        VALUES ($1, $2, $3, $4, $5)
                    """, *service)
            
            # Insert default avatar templates
            avatar_templates = [
                ('traditional_swamiji', 'traditional', 'compassionate', 'ashram', 'saffron_robes'),
                ('modern_guide', 'modern', 'wise', 'studio', 'formal_attire'),
                ('festival_celebrant', 'festival', 'joyful', 'temple', 'festive_robes'),
                ('meditation_master', 'meditation', 'gentle', 'garden', 'simple_robes')
            ]
            
            for template in avatar_templates:
                # Check if template already exists
                existing = await conn.fetchrow(
                    "SELECT id FROM avatar_templates WHERE template_name = $1", template[0]
                )
                if not existing:
                    await conn.execute("""
                        INSERT INTO avatar_templates (template_name, avatar_style, voice_tone, background_style, clothing_style)
                        VALUES ($1, $2, $3, $4, $5)
                    """, *template)
            
            # Insert default service configurations
            service_configs = [
                {
                    "service_name": "love_relationship_mastery",
                    "configuration": {
                        "knowledge_domains": ["relationship_astrology", "remedial_measures", "tamil_spiritual_literature"],
                        "analysis_depth": "comprehensive",
                        "persona_mode": "relationship_counselor_authority"
                    },
                    "persona_config": {
                        "expertise_level": "master_relationship_guide",
                        "speaking_style": "warm_understanding_with_relationship_wisdom",
                        "cultural_focus": "love_marriage_family_dynamics"
                    },
                    "knowledge_domains": "relationship_astrology,remedial_measures,tamil_spiritual_literature"
                },
                {
                    "service_name": "comprehensive_life_reading_30min",
                    "configuration": {
                        "knowledge_domains": ["classical_astrology", "tamil_spiritual_literature", "health_astrology", "career_astrology", "relationship_astrology", "remedial_measures"],
                        "analysis_depth": "comprehensive_30_minute",
                        "persona_mode": "comprehensive_life_master"
                    },
                    "persona_config": {
                        "expertise_level": "complete_life_analysis_authority",
                        "speaking_style": "profound_wisdom_with_comprehensive_understanding",
                        "cultural_focus": "complete_life_transformation"
                    },
                    "knowledge_domains": "classical_astrology,tamil_spiritual_literature,health_astrology,career_astrology,relationship_astrology,remedial_measures"
                }
            ]
            
            for config in service_configs:
                # Check if service configuration already exists
                existing = await conn.fetchrow(
                    "SELECT service_name FROM service_configuration_cache WHERE service_name = $1", 
                    config["service_name"]
                )
                if not existing:
                    await conn.execute("""
                        INSERT INTO service_configuration_cache (service_name, configuration, persona_config, knowledge_domains)
                        VALUES ($1, $2, $3, $4)
                    """, (
                        config["service_name"],
                        json.dumps(config["configuration"]),
                        json.dumps(config["persona_config"]),
                        config["knowledge_domains"]
                    ))
            
            # Insert initial platform settings
            platform_settings = [
                ('facebook_credentials', {}),
                ('instagram_credentials', {}),
                ('youtube_credentials', {}),
                ('twitter_credentials', {}),
                ('tiktok_credentials', {}),
                ('ai_model_config', {}),
                ('social_automation_config', {
                    'auto_posting_enabled': True,
                    'auto_comment_response': True,
                    'daily_content_generation': True,
                    'posting_schedule': {
                        'facebook': ['09:00', '15:00', '20:00'],
                        'instagram': ['10:00', '16:00', '21:00'],
                        'youtube': ['12:00', '18:00'],
                        'twitter': ['08:00', '14:00', '19:00', '22:00'],
                        'tiktok': ['11:00', '17:00', '20:30']
                    }
                })
            ]
            
            for setting_key, setting_value in platform_settings:
                # Check if platform setting already exists
                existing = await conn.fetchrow(
                    "SELECT id FROM platform_settings WHERE key = $1", setting_key
                )
                if not existing:
                    await conn.execute("""
                        INSERT INTO platform_settings (key, value)
                        VALUES ($1, $2)
                    """, (setting_key, json.dumps(setting_value)))
            
            # Insert sample social media content for testing
            now = datetime.now()
            
            sample_social_content = [
                ('daily_wisdom_001', 'daily_wisdom', 'instagram', '✨ Daily Wisdom from Swamiji', 
                 '🕉️ Test post for social media automation - Experience the divine wisdom that transforms your daily life', 
                 None, '#wisdom #spirituality #jyotiflow #dailywisdom', 
                 now + timedelta(hours=1), None, 'draft'),
                
                ('satsang_promo_001', 'satsang_promo', 'facebook', '🙏 Join Our Sacred Satsang', 
                 'Come join us for a transformative satsang experience with Swami Jyotirananthan. Discover profound spiritual insights and connect with like-minded souls on the path of enlightenment.', 
                 None, '#satsang #spirituality #jyotiflow #enlightenment', 
                 now + timedelta(hours=6), None, 'scheduled'),
                
                ('spiritual_quote_001', 'spiritual_quote', 'twitter', '🌟 Spiritual Quote of the Day', 
                 'Truth is not something you find, but something you become. 🙏 #SpiritualWisdom', 
                 None, '#truth #spirituality #wisdom #transformation', 
                 None, now - timedelta(hours=2), 'published')
            ]
            
            for content in sample_social_content:
                # Check if social content already exists
                existing = await conn.fetchrow(
                    "SELECT id FROM social_content WHERE content_id = $1", content[0]
                )
                if not existing:
                    await conn.execute("""
                        INSERT INTO social_content 
                        (content_id, content_type, platform, title, content_text, media_url, hashtags, 
                         scheduled_at, published_at, status)
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                    """, content)
            
            logger.info("✅ Initial data inserted")
            logger.info("✅ Sample social media content created")
            
        except Exception as e:
            logger.error(f"Error inserting initial data: {e}")
            # Don't fail the entire initialization for this

# Global instance
db_initializer = JyotiFlowDatabaseInitializer()

async def initialize_jyotiflow_database():
    """Main function to initialize the database"""
    return await db_initializer.initialize_database()

if __name__ == "__main__":
    import asyncio
    asyncio.run(initialize_jyotiflow_database())