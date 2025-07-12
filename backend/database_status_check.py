"""
Database Status Check
Run this to verify your database is properly configured
"""
import asyncio
import asyncpg
import os

async def check_database_status():
    """Check database tables and configuration"""
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    if not DATABASE_URL:
        print("❌ DATABASE_URL not set!")
        return False
    
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        
        # Count tables
        table_count = await conn.fetchval("""
            SELECT COUNT(*) FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        print(f"✅ Total tables: {table_count}")
        
        # Check critical tables
        critical_tables = [
            'users',
            'service_types', 
            'service_configuration_cache',
            'credit_transactions',
            'notification_templates',
            'sessions'
        ]
        
        for table in critical_tables:
            exists = await conn.fetchval(f"""
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.tables 
                    WHERE table_name = '{table}'
                )
            """)
            status = "✅" if exists else "❌"
            print(f"{status} {table}")
        
        # Check for data in service_configuration_cache
        config_count = await conn.fetchval(
            "SELECT COUNT(*) FROM service_configuration_cache"
        )
        print(f"\n📊 Service configurations: {config_count}")
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database check failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(check_database_status())