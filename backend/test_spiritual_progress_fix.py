#!/usr/bin/env python3
"""
Test script to verify spiritual progress endpoint database connection fix
"""

import asyncio
import asyncpg
import os
from datetime import datetime

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/yourdb")

async def test_spiritual_progress_fix():
    """Test spiritual progress endpoint database connection"""
    
    print("🔍 Testing Spiritual Progress Endpoint Fix...")
    print("=" * 50)
    
    # Connect to database
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        print("✅ Database connection successful")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return
    
    # Test the query that was failing
    print("\n🧪 Testing Spiritual Progress Query:")
    print("-" * 40)
    
    try:
        # Test with a sample user email
        test_email = "test@example.com"
        
        # This is the query from the spiritual progress endpoint
        sessions = await conn.fetch("""
            SELECT s.*, st.name as service_name, st.credits_required
            FROM sessions s
            LEFT JOIN service_types st ON s.service_type_id = st.id
            WHERE s.user_email = $1
            ORDER BY s.created_at DESC
        """, test_email)
        
        print(f"✅ Query executed successfully")
        print(f"   Found {len(sessions)} sessions for {test_email}")
        
        if sessions:
            print(f"   Sample session: {sessions[0]}")
        
    except Exception as e:
        print(f"❌ Query failed: {e}")
    
    # Test user_id conversion
    print("\n🧪 Testing User ID Conversion:")
    print("-" * 30)
    
    test_user_ids = ["1", "2", "3", "invalid"]
    
    for user_id_str in test_user_ids:
        try:
            user_id_int = int(user_id_str)
            print(f"✅ '{user_id_str}' -> {user_id_int}")
            
            # Test user lookup
            user = await conn.fetchrow("SELECT id, email FROM users WHERE id = $1", user_id_int)
            if user:
                print(f"   ✅ User found: {user['email']}")
            else:
                print(f"   ⚠️ User not found in database")
                
        except (ValueError, TypeError):
            print(f"❌ '{user_id_str}' -> Cannot convert to integer")
        except Exception as e:
            print(f"❌ Database error: {e}")
    
    # Test database schema
    print("\n🗄️ Testing Database Schema:")
    print("-" * 30)
    
    tables_to_check = ["users", "sessions", "service_types"]
    
    for table in tables_to_check:
        try:
            count = await conn.fetchval(f"SELECT COUNT(*) FROM {table}")
            print(f"✅ {table}: {count} records")
        except Exception as e:
            print(f"❌ {table}: {str(e)}")
    
    await conn.close()
    print("\n✅ Spiritual progress endpoint testing completed!")

if __name__ == "__main__":
    asyncio.run(test_spiritual_progress_fix()) 