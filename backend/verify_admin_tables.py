#!/usr/bin/env python3
"""
Verify Admin Dashboard Tables
This script checks if all required tables exist and have the expected structure
"""

import asyncio
import os
import asyncpg

async def verify_admin_tables():
    """Verify all admin dashboard tables exist and have data"""
    
    # Get database URL
    database_url = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/jyotiflow")
    
    print("🔍 Verifying admin dashboard tables...")
    
    try:
        conn = await asyncpg.connect(database_url)
        
        # List of required admin tables with their expected columns
        admin_tables = [
            ("users", ["id", "email", "full_name", "role", "credits", "is_active"]),
            ("service_types", ["id", "name", "display_name", "price_usd", "enabled", "base_credits"]),
            ("credit_packages", ["id", "name", "credits_amount", "price_usd", "enabled"]),
            ("payments", ["id", "user_email", "amount", "status", "created_at"]),
            ("donations", ["id", "name", "price_usd", "enabled"]),
            ("donation_transactions", ["id", "user_email", "amount", "status"]),
            ("ai_recommendations", ["id", "recommendation_type", "title", "description", "status"]),
            ("monetization_experiments", ["id", "experiment_name", "experiment_type", "status"]),
            ("ai_insights_cache", ["id", "insight_type", "data", "is_active"]),
            ("subscription_plans", ["id", "plan_id", "name", "price_usd", "is_active"]),
            ("admin_analytics", ["id", "metric_name", "metric_value", "timestamp"]),
            ("admin_notifications", ["id", "notification_type", "title", "message", "status"]),
            ("social_campaigns", ["id", "campaign_id", "name", "platform", "status"]),
            ("social_posts", ["id", "post_id", "platform", "content", "status"]),
            ("social_content", ["id", "content_id", "title", "content", "status"]),
            ("platform_settings", ["id", "key", "value"]),
            ("pricing_config", ["id", "key", "value", "is_active"]),
            ("revenue_analytics", ["id", "revenue_type", "amount", "timestamp"]),
            ("performance_analytics", ["id", "metric_name", "metric_value", "timestamp"]),
            ("sessions", ["id", "session_id", "user_email", "service_type", "status"]),
            ("followup_interactions", ["id", "session_id", "user_email", "question", "answer"])
        ]
        
        print(f"\n📋 Checking {len(admin_tables)} admin tables:")
        
        all_tables_exist = True
        tables_with_data = []
        tables_without_data = []
        
        for table_name, expected_columns in admin_tables:
            try:
                # Check if table exists
                table_exists = await conn.fetchval(f"""
                    SELECT 1 FROM information_schema.tables 
                    WHERE table_name = '{table_name}' AND table_schema = 'public'
                """)
                
                if table_exists:
                    # Check table structure
                    columns = await conn.fetch(f"""
                        SELECT column_name FROM information_schema.columns 
                        WHERE table_name = '{table_name}' AND table_schema = 'public'
                        ORDER BY ordinal_position
                    """)
                    column_names = [col['column_name'] for col in columns]
                    
                    # Check if expected columns exist
                    missing_columns = [col for col in expected_columns if col not in column_names]
                    
                    if missing_columns:
                        print(f"  ⚠️  {table_name}: Missing columns {missing_columns}")
                    else:
                        print(f"  ✅ {table_name}: Structure OK")
                    
                    # Check if table has data
                    row_count = await conn.fetchval(f"SELECT COUNT(*) FROM {table_name}")
                    if row_count > 0:
                        tables_with_data.append((table_name, row_count))
                        print(f"     📊 Has {row_count} rows")
                    else:
                        tables_without_data.append(table_name)
                        print(f"     📭 No data")
                        
                else:
                    print(f"  ❌ {table_name}: Table missing")
                    all_tables_exist = False
                    
            except Exception as e:
                print(f"  ❌ {table_name}: Error checking table - {e}")
                all_tables_exist = False
        
        # Summary
        print(f"\n📊 SUMMARY:")
        print(f"  ✅ Tables with data: {len(tables_with_data)}")
        print(f"  📭 Tables without data: {len(tables_without_data)}")
        
        if tables_with_data:
            print(f"\n📈 Tables with data:")
            for table_name, row_count in tables_with_data:
                print(f"  - {table_name}: {row_count} rows")
        
        if tables_without_data:
            print(f"\n📭 Tables without data:")
            for table_name in tables_without_data:
                print(f"  - {table_name}")
        
        # Test admin user
        print(f"\n👤 Checking admin user:")
        admin_user = await conn.fetchrow("SELECT email, role, credits FROM users WHERE email = 'admin@jyotiflow.ai'")
        if admin_user:
            print(f"  ✅ Admin user exists: {admin_user['email']} (role: {admin_user['role']}, credits: {admin_user['credits']})")
        else:
            print(f"  ❌ Admin user not found")
        
        # Test sample queries
        print(f"\n🧪 Testing sample queries:")
        
        # Test users count
        try:
            user_count = await conn.fetchval("SELECT COUNT(*) FROM users")
            print(f"  👥 Total users: {user_count}")
        except Exception as e:
            print(f"  ❌ Users query failed: {e}")
        
        # Test service types
        try:
            service_count = await conn.fetchval("SELECT COUNT(*) FROM service_types WHERE enabled = true")
            print(f"  🔮 Active services: {service_count}")
        except Exception as e:
            print(f"  ❌ Service types query failed: {e}")
        
        # Test credit packages
        try:
            package_count = await conn.fetchval("SELECT COUNT(*) FROM credit_packages WHERE enabled = true")
            print(f"  💰 Active credit packages: {package_count}")
        except Exception as e:
            print(f"  ❌ Credit packages query failed: {e}")
        
        # Test payments
        try:
            payment_count = await conn.fetchval("SELECT COUNT(*) FROM payments WHERE status = 'completed'")
            print(f"  💳 Completed payments: {payment_count}")
        except Exception as e:
            print(f"  ❌ Payments query failed: {e}")
        
        await conn.close()
        
        if all_tables_exist:
            print(f"\n✅ All admin dashboard tables exist!")
        else:
            print(f"\n⚠️  Some admin dashboard tables are missing!")
        
        return all_tables_exist
        
    except Exception as e:
        print(f"❌ Error verifying admin tables: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(verify_admin_tables())