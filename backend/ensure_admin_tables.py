#!/usr/bin/env python3
"""
Ensure Admin Dashboard Tables Exist
This script creates any missing tables required by the admin dashboard
"""

import asyncio
import os
import asyncpg
import json

async def ensure_admin_tables():
    """Ensure all admin dashboard tables exist"""
    
    # Get database URL
    database_url = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/jyotiflow")
    
    print("🔍 Ensuring admin dashboard tables exist...")
    
    try:
        conn = await asyncpg.connect(database_url)
        
        # List of required admin tables
        admin_tables = [
            # Core tables
            ("users", """
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    full_name VARCHAR(255),
                    password_hash VARCHAR(255) NOT NULL,
                    role VARCHAR(50) DEFAULT 'user',
                    credits INTEGER DEFAULT 0,
                    is_active BOOLEAN DEFAULT true,
                    email_verified BOOLEAN DEFAULT false,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login_at TIMESTAMP
                )
            """),
            
            # Service types
            ("service_types", """
                CREATE TABLE IF NOT EXISTS service_types (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) UNIQUE NOT NULL,
                    display_name VARCHAR(255),
                    description TEXT,
                    credits_required INTEGER DEFAULT 1,
                    duration_minutes INTEGER DEFAULT 15,
                    price_usd DECIMAL(10,2) DEFAULT 0,
                    service_category VARCHAR(100),
                    enabled BOOLEAN DEFAULT true,
                    avatar_video_enabled BOOLEAN DEFAULT false,
                    live_chat_enabled BOOLEAN DEFAULT false,
                    icon VARCHAR(50) DEFAULT '🔮',
                    color_gradient VARCHAR(100) DEFAULT 'from-purple-500 to-indigo-600',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """),
            
            # Credit packages
            ("credit_packages", """
                CREATE TABLE IF NOT EXISTS credit_packages (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    credits_amount INTEGER NOT NULL,
                    price_usd DECIMAL(10,2) NOT NULL,
                    bonus_credits INTEGER DEFAULT 0,
                    enabled BOOLEAN DEFAULT true,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """),
            
            # Payments
            ("payments", """
                CREATE TABLE IF NOT EXISTS payments (
                    id SERIAL PRIMARY KEY,
                    user_email VARCHAR(255) NOT NULL,
                    amount DECIMAL(10,2) NOT NULL,
                    currency VARCHAR(3) DEFAULT 'USD',
                    status VARCHAR(50) DEFAULT 'pending',
                    payment_method VARCHAR(50),
                    transaction_id VARCHAR(255),
                    product_id VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_email) REFERENCES users(email) ON DELETE CASCADE
                )
            """),
            
            # Donations
            ("donations", """
                CREATE TABLE IF NOT EXISTS donations (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    tamil_name VARCHAR(255),
                    description TEXT,
                    price_usd DECIMAL(10,2) NOT NULL,
                    icon VARCHAR(50) DEFAULT '🪔',
                    category VARCHAR(100),
                    enabled BOOLEAN DEFAULT true,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """),
            
            # AI recommendations
            ("ai_recommendations", """
                CREATE TABLE IF NOT EXISTS ai_recommendations (
                    id SERIAL PRIMARY KEY,
                    recommendation_type VARCHAR(50) NOT NULL,
                    title VARCHAR(255) NOT NULL,
                    description TEXT NOT NULL,
                    expected_revenue_impact DECIMAL(10,2),
                    implementation_difficulty VARCHAR(20),
                    timeline_weeks INTEGER,
                    priority_score DECIMAL(3,2),
                    priority_level VARCHAR(20),
                    status VARCHAR(50) DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """),
            
            # Monetization experiments
            ("monetization_experiments", """
                CREATE TABLE IF NOT EXISTS monetization_experiments (
                    id SERIAL PRIMARY KEY,
                    experiment_name VARCHAR(255) NOT NULL,
                    experiment_type VARCHAR(50) NOT NULL,
                    control_conversion_rate DECIMAL(5,2),
                    test_conversion_rate DECIMAL(5,2),
                    control_revenue DECIMAL(10,2),
                    test_revenue DECIMAL(10,2),
                    status VARCHAR(50) DEFAULT 'running',
                    winner VARCHAR(20),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """),
            
            # AI insights cache
            ("ai_insights_cache", """
                CREATE TABLE IF NOT EXISTS ai_insights_cache (
                    id SERIAL PRIMARY KEY,
                    insight_type VARCHAR(50) NOT NULL,
                    data JSONB NOT NULL,
                    expires_at TIMESTAMP NOT NULL,
                    is_active BOOLEAN DEFAULT true,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """),
            
            # Subscription plans
            ("subscription_plans", """
                CREATE TABLE IF NOT EXISTS subscription_plans (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    monthly_price DECIMAL(10,2) NOT NULL,
                    credits_per_month INTEGER NOT NULL,
                    features JSONB DEFAULT '{}',
                    is_active BOOLEAN DEFAULT true,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """),
            
            # User subscriptions
            ("user_subscriptions", """
                CREATE TABLE IF NOT EXISTS user_subscriptions (
                    id SERIAL PRIMARY KEY,
                    user_email VARCHAR(255) NOT NULL,
                    plan_id INTEGER NOT NULL,
                    is_active BOOLEAN DEFAULT true,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_email) REFERENCES users(email) ON DELETE CASCADE,
                    FOREIGN KEY (plan_id) REFERENCES subscription_plans(id) ON DELETE CASCADE
                )
            """)
        ]
        
        # Create tables
        for table_name, create_sql in admin_tables:
            try:
                await conn.execute(create_sql)
                print(f"✅ Table '{table_name}' ensured")
            except Exception as e:
                print(f"⚠️ Error creating table '{table_name}': {e}")
        
        # Insert sample data if tables are empty
        await insert_sample_data(conn)
        
        await conn.close()
        print("✅ Admin dashboard tables check completed!")
        
    except Exception as e:
        print(f"❌ Error ensuring admin tables: {e}")

async def insert_sample_data(conn):
    """Insert sample data for admin dashboard"""
    
    # Check if admin user exists
    admin_exists = await conn.fetchval("SELECT 1 FROM users WHERE email = 'admin@jyotiflow.ai'")
    if not admin_exists:
        # Create admin user (password: Jyoti@2024!)
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        # Generate secure admin password from environment or use secure default
        admin_password = os.getenv("ADMIN_DEFAULT_PASSWORD", "Jyoti@2024!")
        admin_password_hash = pwd_context.hash(admin_password)
        
        await conn.execute("""
            INSERT INTO users (email, full_name, password_hash, role, credits, is_active, email_verified)
            VALUES ('admin@jyotiflow.ai', 'Admin User', $1, 'admin', 1000, true, true)
        """, admin_password_hash)
        print("✅ Created admin user")
    
    # Check if credit packages exist
    packages_exist = await conn.fetchval("SELECT COUNT(*) FROM credit_packages")
    if packages_exist == 0:
        default_packages = [
            ('Starter Pack', 10, 9.99, 2),
            ('Spiritual Seeker', 25, 19.99, 5),
            ('Divine Wisdom', 50, 34.99, 15),
            ('Enlightened Master', 100, 59.99, 30)
        ]
        
        for name, credits, price, bonus in default_packages:
            await conn.execute("""
                INSERT INTO credit_packages (name, credits_amount, price_usd, bonus_credits, enabled)
                VALUES ($1, $2, $3, $4, true)
            """, name, credits, price, bonus)
        print("✅ Created default credit packages")
    
    # Check if service types exist
    services_exist = await conn.fetchval("SELECT COUNT(*) FROM service_types")
    if services_exist == 0:
        default_services = [
            ('basic_reading', 'Basic Reading', 'Simple spiritual guidance', 5, 15, 9.99, 'guidance'),
            ('love_guidance', 'Love Guidance', 'Relationship and love advice', 8, 20, 14.99, 'guidance'),
            ('career_reading', 'Career Reading', 'Professional and career guidance', 10, 25, 19.99, 'guidance'),
            ('comprehensive', 'Comprehensive Reading', 'Complete life analysis', 15, 30, 29.99, 'guidance')
        ]
        
        for name, display_name, description, credits, duration, price, category in default_services:
            await conn.execute("""
                INSERT INTO service_types (name, display_name, description, credits_required, duration_minutes, price_usd, service_category, enabled)
                VALUES ($1, $2, $3, $4, $5, $6, $7, true)
            """, name, display_name, description, credits, duration, price, category)
        print("✅ Created default service types")

if __name__ == "__main__":
    asyncio.run(ensure_admin_tables())