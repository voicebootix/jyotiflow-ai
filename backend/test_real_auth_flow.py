#!/usr/bin/env python3
"""
Test script to reproduce the real authentication issue
Tests the complete registration -> login flow
"""

import asyncio
import asyncpg
import bcrypt
import os
from datetime import datetime
import json

# Database connection settings
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost/jyotiflow")

async def test_real_auth_flow():
    """Test the complete registration -> login flow to reproduce the issue"""
    
    print("🧪 Testing Real Authentication Flow")
    print("=" * 60)
    
    # Test user credentials
    test_email = "test_user_auth@example.com"
    test_password = "testpassword123"
    test_full_name = "Test User"
    
    try:
        # Connect to database
        print("\n1. 📊 DATABASE CONNECTION:")
        try:
            conn = await asyncpg.connect(DATABASE_URL)
            print("   ✅ Connected to database")
        except Exception as e:
            print(f"   ❌ Database connection failed: {e}")
            print("   💡 Make sure PostgreSQL is running and DATABASE_URL is correct")
            return
        
        # Clean up any existing test user
        print("\n2. 🧹 CLEANUP:")
        await conn.execute("DELETE FROM users WHERE email = $1", test_email)
        print(f"   ✅ Cleaned up existing user: {test_email}")
        
        # Test Registration Process
        print("\n3. 📝 REGISTRATION PROCESS:")
        print(f"   Email: {test_email}")
        print(f"   Password: {test_password}")
        print(f"   Full Name: {test_full_name}")
        
        # Check if user already exists (should not exist after cleanup)
        exists = await conn.fetchval("SELECT 1 FROM users WHERE email=$1", test_email)
        print(f"   User exists before registration: {exists}")
        
        # Hash password exactly as done in registration
        password_hash = bcrypt.hashpw(test_password.encode(), bcrypt.gensalt()).decode()
        print(f"   Password hash: {password_hash}")
        print(f"   Password hash type: {type(password_hash)}")
        
        # Insert user exactly as done in registration
        free_credits = 5
        try:
            user_id = await conn.fetchval("""
                INSERT INTO users (email, password_hash, full_name, credits, role, is_active, created_at)
                VALUES ($1, $2, $3, $4, 'user', true, NOW())
                RETURNING id
            """, test_email, password_hash, test_full_name, free_credits)
            print(f"   ✅ User registered successfully with ID: {user_id}")
        except Exception as e:
            print(f"   ❌ Registration failed: {e}")
            await conn.close()
            return
        
        # Test Login Process
        print("\n4. 🔐 LOGIN PROCESS:")
        print(f"   Attempting login with email: {test_email}")
        print(f"   Attempting login with password: {test_password}")
        
        # Fetch user exactly as done in login
        user = await conn.fetchrow("SELECT * FROM users WHERE email=$1", test_email)
        if not user:
            print("   ❌ User not found during login")
            await conn.close()
            return
        
        print(f"   ✅ User found in database:")
        print(f"     ID: {user['id']}")
        print(f"     Email: {user['email']}")
        print(f"     Full Name: {user['full_name']}")
        print(f"     Role: {user['role']}")
        print(f"     Credits: {user['credits']}")
        print(f"     Password Hash: {user['password_hash']}")
        print(f"     Password Hash Type: {type(user['password_hash'])}")
        
        # Test password verification exactly as done in login
        print("\n5. 🔍 PASSWORD VERIFICATION:")
        print(f"   Stored hash: {user['password_hash']}")
        print(f"   Input password: {test_password}")
        
        # This is the exact line from auth.py that might be failing
        try:
            password_check = bcrypt.checkpw(test_password.encode(), user["password_hash"].encode())
            print(f"   ✅ Password verification result: {password_check}")
            
            if password_check:
                print("   ✅ Password verification PASSED")
            else:
                print("   ❌ Password verification FAILED")
                print("   🚨 THIS IS THE ISSUE: Password verification is failing!")
                
        except Exception as e:
            print(f"   ❌ Password verification error: {e}")
            print("   🚨 THIS IS THE ISSUE: Password verification is throwing an error!")
        
        # Test different scenarios that might cause issues
        print("\n6. 🧪 DEBUGGING SCENARIOS:")
        
        # Scenario A: Check if password hash is None or empty
        if not user["password_hash"]:
            print("   ❌ Password hash is None or empty")
        else:
            print(f"   ✅ Password hash exists: {len(user['password_hash'])} characters")
        
        # Scenario B: Check if password hash is valid bcrypt format
        if user["password_hash"].startswith("$2b$"):
            print("   ✅ Password hash appears to be valid bcrypt format")
        else:
            print("   ❌ Password hash is not valid bcrypt format")
        
        # Scenario C: Test with different encoding methods
        try:
            # Test without encoding the stored hash
            alt_check = bcrypt.checkpw(test_password.encode(), user["password_hash"])
            print(f"   Alternative verification (no .encode()): {alt_check}")
        except Exception as e:
            print(f"   Alternative verification failed: {e}")
        
        # Scenario D: Test with bytes password
        try:
            bytes_check = bcrypt.checkpw(test_password.encode('utf-8'), user["password_hash"].encode('utf-8'))
            print(f"   UTF-8 encoding verification: {bytes_check}")
        except Exception as e:
            print(f"   UTF-8 encoding verification failed: {e}")
        
        # Test the complete authentication flow
        print("\n7. 🎯 COMPLETE AUTH FLOW TEST:")
        
        # Registration simulation
        print("   Registration: ✅ User created successfully")
        
        # Login simulation  
        if user and password_check:
            print("   Login: ✅ Authentication successful")
            print("   🎉 AUTHENTICATION WORKS CORRECTLY!")
        else:
            print("   Login: ❌ Authentication failed")
            print("   🚨 AUTHENTICATION ISSUE CONFIRMED!")
            
            # Additional debugging
            print("\n8. 🔧 ADDITIONAL DEBUGGING:")
            
            # Check if there are any weird characters in the password
            print(f"   Password bytes: {test_password.encode()}")
            print(f"   Password hash bytes: {user['password_hash'].encode()}")
            
            # Try to create a new hash with the same password and see if it works
            new_hash = bcrypt.hashpw(test_password.encode(), bcrypt.gensalt()).decode()
            new_check = bcrypt.checkpw(test_password.encode(), new_hash.encode())
            print(f"   New hash verification: {new_check}")
            
            # Compare the hashes
            print(f"   Original hash: {user['password_hash']}")
            print(f"   New hash: {new_hash}")
            print(f"   Hashes are different: {user['password_hash'] != new_hash}")
        
        # Cleanup
        await conn.execute("DELETE FROM users WHERE email = $1", test_email)
        print(f"\n9. 🧹 CLEANUP: Removed test user {test_email}")
        
        await conn.close()
        print("\n   ✅ Database connection closed")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_real_auth_flow())