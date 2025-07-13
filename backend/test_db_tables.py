import asyncio
import os
import asyncpg

async def test_database():
    try:
        # Get database URL from environment
        database_url = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/jyotiflow")
        
        print("🔍 Testing database connection...")
        print(f"Database URL: {database_url}")
        
        # Connect to database
        conn = await asyncpg.connect(database_url)
        
        # Get all tables
        result = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name
        """)
        
        print(f"\n📋 Available tables ({len(result)}):")
        for row in result:
            print(f"  - {row['table_name']}")
        
        # Check specific admin tables
        admin_tables = [
            'ai_recommendations',
            'monetization_experiments', 
            'ai_insights_cache',
            'payments',
            'users',
            'service_types',
            'credit_packages',
            'donations'
        ]
        
        print(f"\n🔍 Checking admin tables:")
        # Whitelist of expected table names to prevent SQL injection
        expected_tables = [
            'ai_recommendations', 'monetization_experiments', 'ai_insights_cache',
            'payments', 'users', 'service_types', 'credit_packages', 'donations'
        ]
        
        for table in admin_tables:
            if table in expected_tables:
                exists = await conn.fetchval("SELECT 1 FROM information_schema.tables WHERE table_name = $1", table)
                status = "✅ EXISTS" if exists else "❌ MISSING"
                print(f"  {table}: {status}")
            else:
                print(f"  {table}: ⚠️ NOT IN WHITELIST")
        
        # Test basic queries
        print(f"\n🧪 Testing basic queries:")
        
        # Test users table
        try:
            user_count = await conn.fetchval("SELECT COUNT(*) FROM users")
            print(f"  Users count: {user_count}")
        except Exception as e:
            print(f"  ❌ Users query failed: {e}")
        
        # Test payments table
        try:
            payment_count = await conn.fetchval("SELECT COUNT(*) FROM payments")
            print(f"  Payments count: {payment_count}")
        except Exception as e:
            print(f"  ❌ Payments query failed: {e}")
        
        # Test service_types table
        try:
            service_count = await conn.fetchval("SELECT COUNT(*) FROM service_types")
            print(f"  Service types count: {service_count}")
        except Exception as e:
            print(f"  ❌ Service types query failed: {e}")
        
        await conn.close()
        print(f"\n✅ Database test completed successfully!")
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_database())