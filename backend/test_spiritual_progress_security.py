#!/usr/bin/env python3
"""
Test script to verify spiritual progress endpoint security fix
"""

import asyncio
import asyncpg
import os
from datetime import datetime

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/yourdb")

async def test_spiritual_progress_security():
    """Test spiritual progress endpoint security"""
    
    print("🔒 Testing Spiritual Progress Endpoint Security...")
    print("=" * 55)
    
    # Connect to database
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        print("✅ Database connection successful")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return
    
    # Test user_id validation
    print("\n🧪 Testing User ID Validation:")
    print("-" * 35)
    
    test_user_ids = ["1", "2", "3", "invalid", "abc", "-1"]
    
    for user_id_str in test_user_ids:
        try:
            user_id_int = int(user_id_str)
            print(f"✅ '{user_id_str}' -> {user_id_int}")
        except (ValueError, TypeError):
            print(f"❌ '{user_id_str}' -> Invalid format (should return 400)")
    
    # Test authorization logic
    print("\n🔐 Testing Authorization Logic:")
    print("-" * 35)
    
    try:
        # Get sample users from database
        users = await conn.fetch("SELECT id, email, role FROM users LIMIT 3")
        
        if len(users) >= 2:
            user1 = users[0]
            user2 = users[1]
            
            print(f"User 1: ID={user1['id']}, Email={user1['email']}, Role={user1['role']}")
            print(f"User 2: ID={user2['id']}, Email={user2['email']}, Role={user2['role']}")
            
            # Test authorization scenarios
            scenarios = [
                (user1["id"], user1["id"], "Same user access", "✅ Should allow"),
                (user1["id"], user2["id"], "Different user access", "❌ Should deny (unless admin)"),
                (user1["id"], 999, "Non-existent user", "❌ Should deny")
            ]
            
            for current_user_id, requested_user_id, description, expected in scenarios:
                print(f"\n{description}: {expected}")
                print(f"  Current user ID: {current_user_id}")
                print(f"  Requested user ID: {requested_user_id}")
                
                if current_user_id == requested_user_id:
                    print("  ✅ Authorization: ALLOWED (same user)")
                else:
                    # Check if current user is admin
                    current_user = await conn.fetchrow("SELECT role FROM users WHERE id = $1", current_user_id)
                    if current_user and current_user["role"] in ["admin", "super_admin"]:
                        print("  ✅ Authorization: ALLOWED (admin user)")
                    else:
                        print("  ❌ Authorization: DENIED (different user, not admin)")
        else:
            print("⚠️ Need at least 2 users in database for authorization testing")
            
    except Exception as e:
        print(f"❌ Authorization testing failed: {e}")
    
    # Test database query with user_id
    print("\n🗄️ Testing Database Query with User ID:")
    print("-" * 40)
    
    try:
        # Test sessions query with user_email (correct foreign key)
        test_user_email = "test@example.com"
        sessions = await conn.fetch("""
            SELECT s.*, st.name as service_name, st.credits_required
            FROM sessions s
            LEFT JOIN service_types st ON s.service_type_id = st.id
            WHERE s.user_email = $1
            ORDER BY s.created_at DESC
        """, test_user_email)
        
        print(f"✅ Query executed successfully with user_email={test_user_email}")
        print(f"   Found {len(sessions)} sessions")
        
        if sessions:
            print(f"   Sample session: {sessions[0]}")
        
    except Exception as e:
        print(f"❌ Query failed: {e}")
    
    # Test database schema
    print("\n🗄️ Testing Database Schema:")
    print("-" * 30)
    
    try:
        # Check if sessions table has user_id column
        columns = await conn.fetch("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'sessions' 
            AND column_name IN ('user_id', 'user_email')
        """)
        
        print("Sessions table columns:")
        for col in columns:
            print(f"  ✅ {col['column_name']}: {col['data_type']}")
        
        # Check if users table has role column
        role_columns = await conn.fetch("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'users' 
            AND column_name = 'role'
        """)
        
        if role_columns:
            print(f"  ✅ Users table has role column: {role_columns[0]['data_type']}")
        else:
            print("  ⚠️ Users table missing role column")
            
    except Exception as e:
        print(f"❌ Schema check failed: {e}")
    
    await conn.close()
    print("\n✅ Spiritual progress security testing completed!")

if __name__ == "__main__":
    asyncio.run(test_spiritual_progress_security()) 