import asyncio
import asyncpg
import json
import os
from datetime import datetime

async def create_platform_settings_table():
    """Create the missing platform_settings table in PostgreSQL"""
    print("🔧 Creating platform_settings table in PostgreSQL...")
    
    # Use your Supabase connection string
    database_url = os.getenv("DATABASE_URL", 
        "postgresql://jyotiflow_db_user:em0MmaZmvPzASryvzLHpR5g5rRZTQqpw@dpg-d12ohqemcj7s73fjbqtg-a/jyotiflow_db")
    
    try:
        conn = await asyncpg.connect(database_url)
        
        # Create platform_settings table
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS platform_settings (
                id SERIAL PRIMARY KEY,
                key VARCHAR(100) UNIQUE NOT NULL,
                value JSONB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create initial placeholder entries
        initial_settings = [
            ('facebook_credentials', '{}'),
            ('instagram_credentials', '{}'),
            ('youtube_credentials', '{}'),
            ('twitter_credentials', '{}'),
            ('tiktok_credentials', '{}'),
            ('ai_model_config', '{}')
        ]
        
        for key, value in initial_settings:
            await conn.execute('''
                INSERT INTO platform_settings (key, value)
                VALUES ($1, $2)
                ON CONFLICT (key) DO NOTHING
            ''', key, json.loads(value))
            print(f"✅ Created setting: {key}")
        
        # Verify table creation
        count = await conn.fetchval("SELECT COUNT(*) FROM platform_settings")
        keys = await conn.fetch("SELECT key FROM platform_settings ORDER BY key")
        
        await conn.close()
        
        print(f"✅ Platform settings table created successfully!")
        print(f"📊 Total settings: {count}")
        print(f"🔑 Available keys: {', '.join([row['key'] for row in keys])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating table: {e}")
        return False

async def verify_table_creation():
    """Verify that the table was created successfully"""
    print("\n🔍 Verifying table creation...")
    
    database_url = os.getenv("DATABASE_URL", 
        "postgresql://jyotiflow_db_user:em0MmaZmvPzASryvzLHpR5g5rRZTQqpw@dpg-d12ohqemcj7s73fjbqtg-a/jyotiflow_db")
    
    try:
        conn = await asyncpg.connect(database_url)
        
        # Check if table exists
        table_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'platform_settings'
            )
        """)
        
        if table_exists:
            print("✅ Table exists in PostgreSQL database")
            
            # Check table structure
            columns = await conn.fetch("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'platform_settings'
                ORDER BY ordinal_position
            """)
            print(f"📋 Table columns: {[col['column_name'] for col in columns]}")
            
            # Check initial data
            rows = await conn.fetch("SELECT key, value FROM platform_settings ORDER BY key")
            
            print("📝 Initial settings:")
            for row in rows:
                value_status = 'configured' if row['value'] != {} else 'empty'
                print(f"   - {row['key']}: {value_status}")
        else:
            print("❌ Table creation failed!")
            
        await conn.close()
        return table_exists
        
    except Exception as e:
        print(f"❌ Error verifying table: {e}")
        return False

async def test_database_connection():
    """Test the database connection"""
    print("🔌 Testing database connection...")
    
    database_url = os.getenv("DATABASE_URL", 
        "postgresql://jyotiflow_db_user:em0MmaZmvPzASryvzLHpR5g5rRZTQqpw@dpg-d12ohqemcj7s73fjbqtg-a/jyotiflow_db")
    
    try:
        conn = await asyncpg.connect(database_url)
        
        # Test basic query
        version = await conn.fetchval("SELECT version()")
        print(f"✅ Connected to PostgreSQL: {version.split(',')[0]}")
        
        # List existing tables
        tables = await conn.fetch("""
            SELECT tablename FROM pg_tables 
            WHERE schemaname = 'public' 
            ORDER BY tablename
        """)
        
        print(f"📋 Existing tables: {[table['tablename'] for table in tables]}")
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

if __name__ == "__main__":
    async def main():
        print("🚀 JyotiFlow Platform Settings PostgreSQL Fix")
        print("=" * 50)
        
        try:
            # Test connection first
            connected = await test_database_connection()
            
            if not connected:
                print("❌ Cannot proceed without database connection")
                return
            
            # Create the table
            success = await create_platform_settings_table()
            
            if success:
                # Verify creation
                await verify_table_creation()
                
                print("\n🎯 NEXT STEPS:")
                print("1. Configure your Facebook credentials")
                print("2. Test the Facebook service")
                print("3. Test social media posting")
                print("\n📚 For detailed instructions, see:")
                print("   SOCIAL_MEDIA_AUTOMATION_ROOT_CAUSE_ANALYSIS.md")
                
                print("\n🔧 Quick credential configuration:")
                print("   python3 configure_facebook_credentials_postgresql.py")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            print("Please check your database connection and try again")
    
    asyncio.run(main())