#!/usr/bin/env python3
"""
🔍 JyotiFlow PostgreSQL Authentication Checker
Provides instructions for checking your actual Supabase PostgreSQL database
"""

import os

def get_database_info():
    """Get database connection information"""
    database_url = os.getenv("DATABASE_URL")
    
    print("🔍 JyotiFlow PostgreSQL Authentication Check")
    print("=" * 60)
    print(f"\n📊 Database URL: {database_url[:50]}...")
    
    return database_url

def print_sql_queries():
    """Print SQL queries to run on your PostgreSQL database"""
    
    print("\n🔍 SQL Queries to Run on Your Supabase PostgreSQL Database:")
    print("=" * 60)
    
    queries = [
        {
            "title": "1. Check if users table exists",
            "sql": """
SELECT EXISTS (
    SELECT 1 FROM information_schema.tables 
    WHERE table_name = 'users' AND table_schema = 'public'
);"""
        },
        {
            "title": "2. Check users table structure",
            "sql": """
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns 
WHERE table_name = 'users' AND table_schema = 'public'
ORDER BY ordinal_position;"""
        },
        {
            "title": "3. Check total users count",
            "sql": """
SELECT COUNT(*) as total_users FROM users;"""
        },
        {
            "title": "4. Check admin users",
            "sql": """
SELECT email, role, credits, created_at
FROM users 
WHERE role = 'admin' OR email ILIKE '%admin%'
ORDER BY created_at DESC;"""
        },
        {
            "title": "5. Check recent users",
            "sql": """
SELECT email, role, credits, created_at
FROM users 
ORDER BY created_at DESC
LIMIT 5;"""
        },
        {
            "title": "6. Check credit statistics",
            "sql": """
SELECT 
    MIN(credits) as min_credits,
    MAX(credits) as max_credits,
    AVG(credits) as avg_credits,
    COUNT(CASE WHEN credits = 0 THEN 1 END) as zero_credit_users,
    COUNT(CASE WHEN credits IS NULL THEN 1 END) as null_credit_users
FROM users;"""
        },
        {
            "title": "7. Check birth chart cache columns",
            "sql": """
SELECT column_name 
FROM information_schema.columns 
WHERE table_name = 'users' 
AND column_name IN ('birth_chart_data', 'birth_chart_hash', 'birth_chart_cached_at', 'birth_chart_expires_at')
ORDER BY column_name;"""
        },
        {
            "title": "8. Check service types table",
            "sql": """
SELECT name, description, base_credits, duration_minutes, enabled
FROM service_types
ORDER BY base_credits ASC;"""
        },
        {
            "title": "9. Check birth chart cache usage",
            "sql": """
SELECT 
    COUNT(*) as total_users,
    COUNT(birth_chart_data) as users_with_cached_data,
    COUNT(CASE WHEN birth_chart_expires_at > NOW() THEN 1 END) as users_with_valid_cache
FROM users;"""
        }
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n{query['title']}:")
        print("-" * 40)
        print(query['sql'])

def print_create_admin_user():
    """Print SQL to create admin user"""
    
    print("\n🔧 Create Admin User (if missing):")
    print("=" * 60)
    
    print("""
-- First, check if admin user exists:
SELECT email, role, credits FROM users WHERE email = 'admin@jyotiflow.ai';

-- If admin user doesn't exist, create one:
INSERT INTO users (
    id, email, password_hash, name, full_name, role, credits, created_at
) VALUES (
    gen_random_uuid(),
    'admin@jyotiflow.ai',
    '$2b$12$LQv3c1yqBwkVsvDqjrP1m.s7C1/pVnmshODVdYMfZFvHd1tM8yj0u', -- This is 'admin123' hashed
    'Admin',
    'Admin User',
    'admin',
    1000,
    NOW()
);

-- Or update existing user to admin:
UPDATE users 
SET role = 'admin', credits = 1000 
WHERE email = 'admin@jyotiflow.ai';
""")

def print_migration_commands():
    """Print commands to run migrations"""
    
    print("\n🚀 Migration Commands to Run:")
    print("=" * 60)
    
    print("""
# 1. Run birth chart cache migration (adds caching columns to users table):
python3 backend/run_birth_chart_cache_migration.py

# 2. Run database initialization (creates missing tables):
python3 backend/init_database.py

# 3. Initialize credit packages:
python3 backend/init_credit_packages.py

# 4. Check if migration system exists:
python3 backend/run_migrations.py
""")

def print_testing_steps():
    """Print testing steps"""
    
    print("\n🧪 Testing Steps:")
    print("=" * 60)
    
    print("""
1. **Test Database Connection**:
   - Connect to your Supabase PostgreSQL database
   - Run the SQL queries above to check your data

2. **Test Admin Login**:
   - Go to /login
   - Try: admin@jyotiflow.ai / admin123
   - Should redirect to /admin dashboard

3. **Test Birth Chart**:
   - Go to /birth-chart
   - Enter birth details
   - Should use your existing BirthChart.jsx component
   - Should cache data via enhanced_birth_chart_cache_service.py

4. **Test Credit Display**:
   - Login and go to /profile
   - Should show credit balance from PostgreSQL users table

5. **Check Authentication State**:
   - Check browser localStorage for 'jyotiflow_token'
   - Verify JWT token contains role and email fields
""")

def print_existing_system_info():
    """Print information about existing sophisticated system"""
    
    print("\n✅ Your Existing Sophisticated System:")
    print("=" * 60)
    
    print("""
BIRTH CHART SYSTEM (Already Built):
├── 📊 South Indian Chart Visualization (BirthChart.jsx)
├── 🗄️ PostgreSQL JSONB Caching (enhanced_birth_chart_cache_service.py)
├── 🔌 Prokerala API Integration (with PDF reports)
├── 🤖 AI-powered Swamiji Readings (OpenAI + RAG)
└── ⚡ Cache Migration System (run_birth_chart_cache_migration.py)

AUTHENTICATION SYSTEM (Already Built):
├── 🔐 JWT Authentication (auth.py)
├── 👤 User Management (user.py)
├── 👑 Admin Dashboard (AdminDashboard.jsx)
├── 🛡️ Role-based Access Control
└── 💰 Credit Management System

DATABASE (PostgreSQL/Supabase):
├── 👥 users (with JSONB birth_chart_data caching)
├── 📊 sessions (spiritual guidance)
├── 🛠️ service_types (configurable services)
├── 💳 credit_packages (credit management)
└── 📱 social_content (existing tables)

The system is sophisticated and complete - just needs verification!
""")

def main():
    """Main function"""
    
    get_database_info()
    print_existing_system_info()
    print_sql_queries()
    print_create_admin_user()
    print_migration_commands()
    print_testing_steps()
    
    print("\n" + "=" * 60)
    print("🎯 SUMMARY")
    print("=" * 60)
    print("""
Your system is already sophisticated with:
✅ PostgreSQL/Supabase database
✅ Advanced birth chart caching
✅ Beautiful South Indian chart components
✅ Complete authentication system

The issues are likely:
❓ Missing admin user in database
❓ Authentication token state issues
❓ Database migration not applied

Next steps:
1. Run the SQL queries above on your Supabase database
2. Create admin user if missing
3. Run the migration commands
4. Test your existing sophisticated system
""")

if __name__ == "__main__":
    main()