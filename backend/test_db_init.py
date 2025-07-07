#!/usr/bin/env python3
"""
🧪 JyotiFlow Database Initialization Test
Test script to verify database initialization works correctly
"""

import asyncio
import os
import sys

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import asyncpg
from init_database import JyotiFlowDatabaseInitializer

async def test_database_connection():
    """Test database connection"""
    print("🔍 Testing database connection...")
    
    try:
        db_initializer = JyotiFlowDatabaseInitializer()
        conn = await asyncpg.connect(db_initializer.database_url)
        
        # Test basic connection
        result = await conn.fetchval("SELECT 1")
        print(f"✅ Database connection successful: {result}")
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

async def test_table_creation():
    """Test table creation"""
    print("🔍 Testing table creation...")
    
    try:
        db_initializer = JyotiFlowDatabaseInitializer()
        conn = await asyncpg.connect(db_initializer.database_url)
        
        # Check if core tables exist
        tables_to_check = [
            'users',
            'service_types', 
            'sessions',
            'user_purchases',
            'user_subscriptions',
            'avatar_sessions',
            'satsang_events',
            'satsang_attendees',
            'ai_pricing_recommendations',
            'monetization_insights',
            'avatar_generation_queue',
            'avatar_templates',
            'live_chat_sessions',
            'session_participants',
            'agora_usage_logs',
            'rag_knowledge_base',
            'service_configuration_cache',
            'social_content',
            'system_analytics',
            'admin_audit_logs'
        ]
        
        existing_tables = []
        missing_tables = []
        
        for table in tables_to_check:
            try:
                result = await conn.fetchval(f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '{table}')")
                if result:
                    existing_tables.append(table)
                    print(f"✅ Table '{table}' exists")
                else:
                    missing_tables.append(table)
                    print(f"❌ Table '{table}' missing")
            except Exception as e:
                missing_tables.append(table)
                print(f"❌ Error checking table '{table}': {e}")
        
        await conn.close()
        
        print(f"\n📊 Table Status Summary:")
        print(f"✅ Existing tables: {len(existing_tables)}")
        print(f"❌ Missing tables: {len(missing_tables)}")
        
        if missing_tables:
            print(f"Missing tables: {missing_tables}")
            return False
        else:
            print("🎉 All tables exist!")
            return True
            
    except Exception as e:
        print(f"❌ Table creation test failed: {e}")
        return False

async def test_initial_data():
    """Test initial data insertion"""
    print("🔍 Testing initial data...")
    
    try:
        db_initializer = JyotiFlowDatabaseInitializer()
        conn = await asyncpg.connect(db_initializer.database_url)
        
        # Check service types
        service_count = await conn.fetchval("SELECT COUNT(*) FROM service_types")
        print(f"✅ Service types count: {service_count}")
        
        # Check avatar templates
        template_count = await conn.fetchval("SELECT COUNT(*) FROM avatar_templates")
        print(f"✅ Avatar templates count: {template_count}")
        
        # Check service configurations
        config_count = await conn.fetchval("SELECT COUNT(*) FROM service_configuration_cache")
        print(f"✅ Service configurations count: {config_count}")
        
        await conn.close()
        
        if service_count > 0 and template_count > 0 and config_count > 0:
            print("🎉 Initial data verified!")
            return True
        else:
            print("⚠️ Some initial data may be missing")
            return False
            
    except Exception as e:
        print(f"❌ Initial data test failed: {e}")
        return False

async def main():
    """Main test function"""
    print("🧪 JyotiFlow Database Initialization Test")
    print("=" * 50)
    
    # Test 1: Database connection
    connection_ok = await test_database_connection()
    if not connection_ok:
        print("❌ Database connection test failed. Exiting.")
        sys.exit(1)
    
    print()
    
    # Test 2: Table creation
    tables_ok = await test_table_creation()
    if not tables_ok:
        print("❌ Table creation test failed. Running initialization...")
        try:
            from init_database import initialize_jyotiflow_database
            success = await initialize_jyotiflow_database()
            if success:
                print("✅ Database initialization completed. Re-running table test...")
                tables_ok = await test_table_creation()
            else:
                print("❌ Database initialization failed.")
                sys.exit(1)
        except Exception as e:
            print(f"❌ Database initialization error: {e}")
            sys.exit(1)
    
    print()
    
    # Test 3: Initial data
    data_ok = await test_initial_data()
    
    print()
    print("=" * 50)
    print("📊 Test Results Summary:")
    print(f"✅ Database Connection: {'PASS' if connection_ok else 'FAIL'}")
    print(f"✅ Table Creation: {'PASS' if tables_ok else 'FAIL'}")
    print(f"✅ Initial Data: {'PASS' if data_ok else 'FAIL'}")
    
    if connection_ok and tables_ok and data_ok:
        print("🎉 All tests passed! JyotiFlow database is ready!")
    else:
        print("❌ Some tests failed. Please check the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 