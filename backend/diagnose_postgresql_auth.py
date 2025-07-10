#!/usr/bin/env python3
"""
🔍 JyotiFlow PostgreSQL Authentication Diagnosis
Diagnoses the real Supabase PostgreSQL database to understand authentication issues
"""

import asyncio
import asyncpg
import os
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PostgreSQLAuthDiagnosis:
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL", "postgresql://jyotiflow_db_user:em0MmaZmvPzASryvzLHpR5g5rRZTQqpw@dpg-d12ohqemcj7s73fjbqtg-a/jyotiflow_db")
    
    async def connect(self):
        """Connect to PostgreSQL database"""
        return await asyncpg.connect(self.database_url)
    
    async def check_database_connection(self):
        """Test database connection"""
        try:
            conn = await self.connect()
            result = await conn.fetchval("SELECT version()")
            await conn.close()
            print(f"✅ Database connected: {result[:50]}...")
            return True
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False
    
    async def check_tables_exist(self):
        """Check if required tables exist"""
        try:
            conn = await self.connect()
            
            # Check for essential tables
            essential_tables = ['users', 'sessions', 'service_types', 'credit_packages']
            
            tables_query = """
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
                ORDER BY table_name
            """
            
            existing_tables = await conn.fetch(tables_query)
            existing_table_names = [table['table_name'] for table in existing_tables]
            
            print(f"\n📋 Found {len(existing_table_names)} tables:")
            for table in existing_table_names:
                print(f"   - {table}")
            
            print(f"\n🔍 Essential table check:")
            for table in essential_tables:
                if table in existing_table_names:
                    print(f"   ✅ {table}")
                else:
                    print(f"   ❌ {table} - MISSING")
            
            await conn.close()
            return existing_table_names
        except Exception as e:
            print(f"❌ Error checking tables: {e}")
            return []
    
    async def check_users_table_structure(self):
        """Check users table structure"""
        try:
            conn = await self.connect()
            
            # Check if users table exists
            table_exists = await conn.fetchval("""
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.tables 
                    WHERE table_name = 'users' AND table_schema = 'public'
                )
            """)
            
            if not table_exists:
                print("❌ Users table does not exist!")
                await conn.close()
                return False
            
            # Get table structure
            columns = await conn.fetch("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'users' AND table_schema = 'public'
                ORDER BY ordinal_position
            """)
            
            print(f"\n📋 Users table structure ({len(columns)} columns):")
            for col in columns:
                nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
                default = f" DEFAULT {col['column_default']}" if col['column_default'] else ""
                print(f"   - {col['column_name']}: {col['data_type']} {nullable}{default}")
            
            # Check for authentication-related columns
            auth_columns = ['email', 'password_hash', 'role', 'credits']
            column_names = [col['column_name'] for col in columns]
            
            print(f"\n🔍 Authentication columns check:")
            for col in auth_columns:
                if col in column_names:
                    print(f"   ✅ {col}")
                else:
                    print(f"   ❌ {col} - MISSING")
            
            # Check for birth chart caching columns
            cache_columns = ['birth_chart_data', 'birth_chart_hash', 'birth_chart_cached_at']
            print(f"\n🔍 Birth chart caching columns check:")
            for col in cache_columns:
                if col in column_names:
                    print(f"   ✅ {col}")
                else:
                    print(f"   ❌ {col} - MISSING")
            
            await conn.close()
            return True
        except Exception as e:
            print(f"❌ Error checking users table: {e}")
            return False
    
    async def check_user_data(self):
        """Check actual user data"""
        try:
            conn = await self.connect()
            
            # Check total users
            total_users = await conn.fetchval("SELECT COUNT(*) FROM users")
            print(f"\n📊 Total users in database: {total_users}")
            
            if total_users == 0:
                print("❌ No users found in database!")
                await conn.close()
                return False
            
            # Check admin users
            admin_users = await conn.fetch("""
                SELECT email, role, credits, created_at
                FROM users 
                WHERE role = 'admin' OR email LIKE '%admin%'
                ORDER BY created_at DESC
            """)
            
            if admin_users:
                print(f"\n👑 Found {len(admin_users)} admin users:")
                for admin in admin_users:
                    print(f"   - {admin['email']} (role: {admin['role']}, credits: {admin['credits']})")
            else:
                print("\n❌ No admin users found!")
            
            # Check recent users
            recent_users = await conn.fetch("""
                SELECT email, role, credits, created_at
                FROM users 
                ORDER BY created_at DESC
                LIMIT 5
            """)
            
            print(f"\n📋 Recent 5 users:")
            for user in recent_users:
                created = user['created_at'].strftime('%Y-%m-%d %H:%M') if user['created_at'] else 'Unknown'
                print(f"   - {user['email']} (role: {user['role']}, credits: {user['credits']}, created: {created})")
            
            # Check credit distribution
            credit_stats = await conn.fetchrow("""
                SELECT 
                    MIN(credits) as min_credits,
                    MAX(credits) as max_credits,
                    AVG(credits) as avg_credits,
                    COUNT(CASE WHEN credits = 0 THEN 1 END) as zero_credit_users,
                    COUNT(CASE WHEN credits IS NULL THEN 1 END) as null_credit_users
                FROM users
            """)
            
            print(f"\n💰 Credit statistics:")
            print(f"   - Min: {credit_stats['min_credits']}")
            print(f"   - Max: {credit_stats['max_credits']}")
            print(f"   - Average: {credit_stats['avg_credits']:.2f}")
            print(f"   - Zero credits: {credit_stats['zero_credit_users']} users")
            print(f"   - Null credits: {credit_stats['null_credit_users']} users")
            
            await conn.close()
            return True
        except Exception as e:
            print(f"❌ Error checking user data: {e}")
            return False
    
    async def check_birth_chart_cache_status(self):
        """Check birth chart caching status"""
        try:
            conn = await self.connect()
            
            # Check if birth chart columns exist
            cache_columns = await conn.fetch("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'users' 
                AND column_name IN ('birth_chart_data', 'birth_chart_hash', 'birth_chart_cached_at', 'birth_chart_expires_at')
            """)
            
            if not cache_columns:
                print("\n❌ Birth chart caching columns not found - need to run migration")
                await conn.close()
                return False
            
            print(f"\n📊 Birth chart cache columns found: {len(cache_columns)}")
            
            # Check cache usage statistics
            cache_stats = await conn.fetchrow("""
                SELECT 
                    COUNT(*) as total_users,
                    COUNT(birth_chart_data) as users_with_cached_data,
                    COUNT(CASE WHEN birth_chart_expires_at > NOW() THEN 1 END) as users_with_valid_cache,
                    COUNT(CASE WHEN birth_chart_expires_at <= NOW() THEN 1 END) as users_with_expired_cache
                FROM users
            """)
            
            print(f"📈 Cache statistics:")
            print(f"   - Total users: {cache_stats['total_users']}")
            print(f"   - Users with cached data: {cache_stats['users_with_cached_data']}")
            print(f"   - Users with valid cache: {cache_stats['users_with_valid_cache']}")
            print(f"   - Users with expired cache: {cache_stats['users_with_expired_cache']}")
            
            await conn.close()
            return True
        except Exception as e:
            print(f"❌ Error checking birth chart cache: {e}")
            return False
    
    async def check_service_types(self):
        """Check service types configuration"""
        try:
            conn = await self.connect()
            
            # Check if service_types table exists
            table_exists = await conn.fetchval("""
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.tables 
                    WHERE table_name = 'service_types' AND table_schema = 'public'
                )
            """)
            
            if not table_exists:
                print("\n❌ Service types table does not exist!")
                await conn.close()
                return False
            
            # Get service types
            services = await conn.fetch("""
                SELECT name, description, base_credits, duration_minutes, enabled
                FROM service_types
                ORDER BY base_credits ASC
            """)
            
            if services:
                print(f"\n🛠️ Found {len(services)} service types:")
                for service in services:
                    status = "✅ enabled" if service['enabled'] else "❌ disabled"
                    print(f"   - {service['name']}: {service['base_credits']} credits, {service['duration_minutes']}min ({status})")
            else:
                print("\n❌ No service types found!")
            
            await conn.close()
            return len(services) > 0
        except Exception as e:
            print(f"❌ Error checking service types: {e}")
            return False
    
    async def run_complete_diagnosis(self):
        """Run complete PostgreSQL authentication diagnosis"""
        print("🔍 JyotiFlow PostgreSQL Authentication Diagnosis")
        print("=" * 80)
        
        results = []
        
        # Database connection test
        print("\n1. 🔌 Testing Database Connection...")
        db_connected = await self.check_database_connection()
        results.append(("Database Connection", db_connected))
        
        if not db_connected:
            print("❌ Cannot proceed without database connection")
            return False
        
        # Check tables
        print("\n2. 📋 Checking Database Tables...")
        tables = await self.check_tables_exist()
        results.append(("Tables Exist", len(tables) > 0))
        
        # Check users table structure
        print("\n3. 🏗️ Checking Users Table Structure...")
        users_ok = await self.check_users_table_structure()
        results.append(("Users Table Structure", users_ok))
        
        if users_ok:
            # Check user data
            print("\n4. 👥 Checking User Data...")
            user_data_ok = await self.check_user_data()
            results.append(("User Data", user_data_ok))
            
            # Check birth chart cache
            print("\n5. 📊 Checking Birth Chart Cache...")
            cache_ok = await self.check_birth_chart_cache_status()
            results.append(("Birth Chart Cache", cache_ok))
        
        # Check service types
        print("\n6. 🛠️ Checking Service Types...")
        services_ok = await self.check_service_types()
        results.append(("Service Types", services_ok))
        
        # Summary
        print("\n" + "=" * 80)
        print("📋 DIAGNOSIS SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"   {test_name}: {status}")
        
        print(f"\n🎯 Results: {passed}/{total} checks passed")
        
        if passed == total:
            print("\n✅ All checks passed! Authentication system should be working.")
            print("\n🔗 Test URLs:")
            print("   - Admin login: admin@jyotiflow.ai")
            print("   - Birth chart: /birth-chart")
            print("   - Profile: /profile")
        else:
            print(f"\n❌ {total - passed} issues found. Check the details above.")
        
        return passed == total

async def main():
    """Main function"""
    diagnosis = PostgreSQLAuthDiagnosis()
    await diagnosis.run_complete_diagnosis()

if __name__ == "__main__":
    asyncio.run(main())