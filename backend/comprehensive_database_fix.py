"""
Comprehensive Database Fix Script for JyotiFlow.ai
Addresses missing tables, column inconsistencies, and schema issues
identified in deployment log analysis.
"""

import asyncio
import asyncpg
import os
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseFixer:
    def __init__(self):
        self.db_url = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost:5432/jyotiflow')
        self.connection = None
    
    async def connect(self):
        """Establish database connection"""
        try:
            self.connection = await asyncpg.connect(self.db_url)
            logger.info("✅ Connected to database successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to connect to database: {e}")
            return False
    
    async def close(self):
        """Close database connection"""
        if self.connection:
            await self.connection.close()
            logger.info("✅ Database connection closed")
    
    async def table_exists(self, table_name):
        """Check if a table exists"""
        query = """
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = $1
        );
        """
        result = await self.connection.fetchval(query, table_name)
        return result
    
    async def column_exists(self, table_name, column_name):
        """Check if a column exists in a table"""
        query = """
        SELECT EXISTS (
            SELECT FROM information_schema.columns 
            WHERE table_schema = 'public' 
            AND table_name = $1 
            AND column_name = $2
        );
        """
        result = await self.connection.fetchval(query, table_name, column_name)
        return result
    
    async def create_credit_packages_table(self):
        """Create the missing credit_packages table"""
        logger.info("🔧 Creating credit_packages table...")
        
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS credit_packages (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            credits_amount INTEGER NOT NULL,
            price_usd DECIMAL(10, 2) NOT NULL,
            price_inr DECIMAL(10, 2),
            discount_percentage INTEGER DEFAULT 0,
            is_active BOOLEAN DEFAULT true,
            is_featured BOOLEAN DEFAULT false,
            validity_days INTEGER DEFAULT 365,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """
        
        await self.connection.execute(create_table_sql)
        
        # Insert default credit packages
        insert_packages_sql = """
        INSERT INTO credit_packages (name, description, credits_amount, price_usd, price_inr, discount_percentage, is_featured)
        VALUES 
            ('Starter Pack', 'Perfect for trying out our services', 100, 9.99, 799, 0, false),
            ('Popular Pack', 'Most popular choice for regular users', 500, 39.99, 3199, 20, true),
            ('Premium Pack', 'Best value for power users', 1000, 69.99, 5599, 30, false),
            ('Ultimate Pack', 'Maximum credits for unlimited access', 2500, 149.99, 11999, 40, false)
        ON CONFLICT DO NOTHING;
        """
        
        await self.connection.execute(insert_packages_sql)
        logger.info("✅ Credit packages table created and populated")
    
    async def create_donations_table(self):
        """Create the missing donations table"""
        logger.info("🔧 Creating donations table...")
        
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS donations (
            id SERIAL PRIMARY KEY,
            donor_name VARCHAR(255),
            donor_email VARCHAR(255),
            amount_usd DECIMAL(10, 2) NOT NULL,
            amount_inr DECIMAL(10, 2),
            currency VARCHAR(3) DEFAULT 'USD',
            payment_method VARCHAR(50),
            payment_status VARCHAR(50) DEFAULT 'pending',
            payment_id VARCHAR(255),
            transaction_id VARCHAR(255),
            message TEXT,
            is_anonymous BOOLEAN DEFAULT false,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """
        
        await self.connection.execute(create_table_sql)
        logger.info("✅ Donations table created")
    
    async def create_service_configuration_cache_table(self):
        """Create the missing service_configuration_cache table"""
        logger.info("🔧 Creating service_configuration_cache table...")
        
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS service_configuration_cache (
            id SERIAL PRIMARY KEY,
            service_name VARCHAR(255) NOT NULL,
            config_key VARCHAR(255) NOT NULL,
            config_value JSONB,
            expires_at TIMESTAMP WITH TIME ZONE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            UNIQUE(service_name, config_key)
        );
        """
        
        await self.connection.execute(create_table_sql)
        
        # Insert default service configurations
        insert_configs_sql = """
        INSERT INTO service_configuration_cache (service_name, config_key, config_value)
        VALUES 
            ('spiritual_guidance', 'max_session_duration', '{"value": 3600, "unit": "seconds"}'),
            ('spiritual_guidance', 'default_credits_cost', '{"value": 10, "currency": "credits"}'),
            ('live_chat', 'max_participants', '{"value": 2, "type": "one_on_one"}'),
            ('live_chat', 'audio_credits_per_minute', '{"value": 5, "currency": "credits"}'),
            ('live_chat', 'video_credits_per_minute', '{"value": 10, "currency": "credits"}'),
            ('ai_marketing', 'max_requests_per_hour', '{"value": 100, "type": "rate_limit"}')
        ON CONFLICT (service_name, config_key) DO NOTHING;
        """
        
        await self.connection.execute(insert_configs_sql)
        logger.info("✅ Service configuration cache table created and populated")
    
    async def fix_service_types_table(self):
        """Add missing credits_required column to service_types table"""
        logger.info("🔧 Fixing service_types table...")
        
        # Check if table exists
        if not await self.table_exists('service_types'):
            logger.info("📝 Creating service_types table...")
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS service_types (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                category VARCHAR(100),
                credits_required INTEGER DEFAULT 0,
                is_active BOOLEAN DEFAULT true,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            """
            await self.connection.execute(create_table_sql)
            
            # Insert default service types
            insert_services_sql = """
            INSERT INTO service_types (name, description, category, credits_required)
            VALUES 
                ('Spiritual Guidance', 'Personalized spiritual guidance and readings', 'spiritual', 10),
                ('Birth Chart Analysis', 'Detailed astrological birth chart analysis', 'astrology', 25),
                ('Live Chat Text', 'Text-based live chat with spiritual advisor', 'communication', 5),
                ('Live Chat Audio', 'Audio chat with spiritual advisor', 'communication', 15),
                ('Live Chat Video', 'Video chat with spiritual advisor', 'communication', 25),
                ('AI Marketing Director', 'AI-powered marketing intelligence', 'business', 20)
            ON CONFLICT DO NOTHING;
            """
            await self.connection.execute(insert_services_sql)
        else:
            # Add credits_required column if it doesn't exist
            if not await self.column_exists('service_types', 'credits_required'):
                logger.info("📝 Adding credits_required column to service_types...")
                alter_table_sql = """
                ALTER TABLE service_types 
                ADD COLUMN IF NOT EXISTS credits_required INTEGER DEFAULT 0;
                """
                await self.connection.execute(alter_table_sql)
                
                # Update existing records with appropriate credit values
                update_credits_sql = """
                UPDATE service_types 
                SET credits_required = CASE 
                    WHEN name ILIKE '%spiritual%' THEN 10
                    WHEN name ILIKE '%chart%' THEN 25
                    WHEN name ILIKE '%video%' THEN 25
                    WHEN name ILIKE '%audio%' THEN 15
                    WHEN name ILIKE '%chat%' THEN 5
                    WHEN name ILIKE '%marketing%' THEN 20
                    ELSE 5
                END
                WHERE credits_required = 0;
                """
                await self.connection.execute(update_credits_sql)
        
        logger.info("✅ Service types table fixed")
    
    async def fix_user_analytics_columns(self):
        """Fix column name inconsistencies in user analytics"""
        logger.info("🔧 Fixing user analytics column names...")
        
        # Check if users table exists and has the correct column
        if await self.table_exists('users'):
            has_last_login = await self.column_exists('users', 'last_login')
            has_last_login_at = await self.column_exists('users', 'last_login_at')
            
            if has_last_login and not has_last_login_at:
                # Add last_login_at as an alias or rename the column
                logger.info("📝 Adding last_login_at column...")
                alter_sql = """
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS last_login_at TIMESTAMP WITH TIME ZONE;
                """
                await self.connection.execute(alter_sql)
                
                # Copy data from last_login to last_login_at
                update_sql = """
                UPDATE users 
                SET last_login_at = last_login 
                WHERE last_login_at IS NULL AND last_login IS NOT NULL;
                """
                await self.connection.execute(update_sql)
            
            elif has_last_login_at and not has_last_login:
                # Add last_login column
                logger.info("📝 Adding last_login column...")
                alter_sql = """
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS last_login TIMESTAMP WITH TIME ZONE;
                """
                await self.connection.execute(alter_sql)
                
                # Copy data from last_login_at to last_login
                update_sql = """
                UPDATE users 
                SET last_login = last_login_at 
                WHERE last_login IS NULL AND last_login_at IS NOT NULL;
                """
                await self.connection.execute(update_sql)
        
        logger.info("✅ User analytics columns fixed")
    
    async def create_knowledge_base_tables(self):
        """Create knowledge base tables for spiritual guidance"""
        logger.info("🔧 Creating knowledge base tables...")
        
        # Spiritual wisdom table
        create_wisdom_sql = """
        CREATE TABLE IF NOT EXISTS spiritual_wisdom (
            id SERIAL PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            content TEXT NOT NULL,
            category VARCHAR(100),
            tags TEXT[],
            source VARCHAR(255),
            language VARCHAR(10) DEFAULT 'en',
            is_active BOOLEAN DEFAULT true,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """
        await self.connection.execute(create_wisdom_sql)
        
        # Astrological data table
        create_astro_sql = """
        CREATE TABLE IF NOT EXISTS astrological_data (
            id SERIAL PRIMARY KEY,
            planet VARCHAR(50),
            sign VARCHAR(50),
            house INTEGER,
            degree DECIMAL(5, 2),
            interpretation TEXT,
            category VARCHAR(100),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """
        await self.connection.execute(create_astro_sql)
        
        # Insert sample spiritual wisdom
        insert_wisdom_sql = """
        INSERT INTO spiritual_wisdom (title, content, category, tags, source)
        VALUES 
            ('Inner Peace', 'True peace comes from within. When we align our thoughts with our higher purpose, we find serenity even in chaos.', 'meditation', ARRAY['peace', 'meditation', 'mindfulness'], 'Ancient Wisdom'),
            ('Karma and Action', 'Every action has consequences. Act with compassion and wisdom, for what you give to the world returns to you.', 'karma', ARRAY['karma', 'action', 'dharma'], 'Vedic Teachings'),
            ('Divine Connection', 'The divine resides within each soul. Through prayer and meditation, we strengthen our connection to the universal consciousness.', 'spirituality', ARRAY['divine', 'prayer', 'consciousness'], 'Spiritual Masters')
        ON CONFLICT DO NOTHING;
        """
        await self.connection.execute(insert_wisdom_sql)
        
        logger.info("✅ Knowledge base tables created and seeded")
    
    async def run_comprehensive_fix(self):
        """Run all database fixes in sequence"""
        logger.info("🚀 Starting comprehensive database fix...")
        
        if not await self.connect():
            return False
        
        try:
            # Fix missing tables
            await self.create_credit_packages_table()
            await self.create_donations_table()
            await self.create_service_configuration_cache_table()
            
            # Fix existing table issues
            await self.fix_service_types_table()
            await self.fix_user_analytics_columns()
            
            # Create knowledge base
            await self.create_knowledge_base_tables()
            
            logger.info("🎉 Comprehensive database fix completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Database fix failed: {e}")
            return False
        
        finally:
            await self.close()

async def main():
    """Main execution function"""
    fixer = DatabaseFixer()
    success = await fixer.run_comprehensive_fix()
    
    if success:
        print("✅ Database fixes applied successfully!")
        print("🔄 Please restart the application to apply changes.")
    else:
        print("❌ Database fixes failed. Check logs for details.")

if __name__ == "__main__":
    asyncio.run(main())

