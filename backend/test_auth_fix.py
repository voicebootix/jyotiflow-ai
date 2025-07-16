#!/usr/bin/env python3
"""
Test script to verify authentication fix works correctly
"""
import asyncio
import asyncpg
import bcrypt
import os

DATABASE_URL = os.getenv("DATABASE_URL")

async def test_password_verification():
    """Test that password verification works correctly"""
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        print("✅ Connected to database")
        
        # Test admin user
        admin_user = await conn.fetchrow(
            "SELECT email, password_hash, role, credits FROM users WHERE email = $1",
            "admin@jyotiflow.ai"
        )
        
        if admin_user:
            print(f"✅ Admin user found: {admin_user['email']}")
            print(f"   Role: {admin_user['role']}")
            print(f"   Credits: {admin_user['credits']}")
            
            # Test password verification
            password = "Jyoti@2024!"
            if bcrypt.checkpw(password.encode(), admin_user['password_hash'].encode()):
                print(f"✅ Admin password verification PASSED for: {password}")
            else:
                print(f"❌ Admin password verification FAILED for: {password}")
                
        else:
            print("❌ Admin user not found")
        
        print()
        
        # Test test user
        test_user = await conn.fetchrow(
            "SELECT email, password_hash, role, credits FROM users WHERE email = $1",
            "user@jyotiflow.ai"
        )
        
        if test_user:
            print(f"✅ Test user found: {test_user['email']}")
            print(f"   Role: {test_user['role']}")
            print(f"   Credits: {test_user['credits']}")
            
            # Test password verification
            password = "user123"
            if bcrypt.checkpw(password.encode(), test_user['password_hash'].encode()):
                print(f"✅ Test user password verification PASSED for: {password}")
            else:
                print(f"❌ Test user password verification FAILED for: {password}")
                
        else:
            print("❌ Test user not found")
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_password_verification())