#!/usr/bin/env python3
"""
Test script to verify user_id conversion fixes
"""

import asyncio
import asyncpg
import os
from datetime import datetime

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/yourdb")

async def test_user_id_conversion():
    """Test user_id conversion from string to integer"""
    
    print("🔍 Testing User ID Conversion Fixes...")
    print("=" * 50)
    
    # Connect to database
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        print("✅ Database connection successful")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return
    
    # Test user_id conversion
    test_user_ids = ["1", "2", "3", "invalid", "abc"]
    
    print("\n🧪 Testing User ID Conversion:")
    print("-" * 30)
    
    for user_id_str in test_user_ids:
        try:
            user_id_int = int(user_id_str)
            print(f"✅ '{user_id_str}' -> {user_id_int}")
            
            # Test database query
            user = await conn.fetchrow("SELECT id, email FROM users WHERE id = $1", user_id_int)
            if user:
                print(f"   ✅ User found: {user['email']}")
            else:
                print(f"   ⚠️ User not found in database")
                
        except (ValueError, TypeError):
            print(f"❌ '{user_id_str}' -> Cannot convert to integer")
        except Exception as e:
            print(f"❌ Database error: {e}")
    
    # Test existing users in database
    print("\n👥 Testing Existing Users:")
    print("-" * 30)
    
    try:
        users = await conn.fetch("SELECT id, email FROM users LIMIT 5")
        for user in users:
            print(f"✅ User ID: {user['id']} (type: {type(user['id'])}) - Email: {user['email']}")
    except Exception as e:
        print(f"❌ Error fetching users: {e}")
    
    await conn.close()
    print("\n✅ User ID conversion testing completed!")

if __name__ == "__main__":
    asyncio.run(test_user_id_conversion()) 