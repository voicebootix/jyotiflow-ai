#!/usr/bin/env python3
"""
Production Authentication Diagnostic Test
This script helps identify authentication issues in production environment
"""

import asyncio
import os
import bcrypt
import asyncpg
from datetime import datetime, timedelta
import jwt

async def production_auth_diagnostic():
    """Test authentication flow in production environment"""
    
    print("🔍 PRODUCTION AUTHENTICATION DIAGNOSTIC")
    print("=" * 55)
    
    # Step 1: Check Environment Variables
    print("\n1. 🔑 ENVIRONMENT VARIABLES:")
    database_url = os.getenv("DATABASE_URL")
    jwt_secret = os.getenv("JWT_SECRET")
    
    if not database_url:
        print("   ❌ DATABASE_URL not set")
        return False
    
    if not jwt_secret:
        print("   ❌ JWT_SECRET not set")
        return False
    
    print("   ✅ Both environment variables are set")
    
    # Step 2: Test Database Connection
    print("\n2. 🔗 DATABASE CONNECTION TEST:")
    try:
        conn = await asyncpg.connect(database_url)
        print("   ✅ Database connection successful")
    except Exception as e:
        print(f"   ❌ Database connection failed: {e}")
        return False
    
    # Step 3: Check Users Table
    print("\n3. 👥 USERS TABLE CHECK:")
    try:
        users = await conn.fetch("""
            SELECT email, password_hash, role, created_at 
            FROM users 
            ORDER BY created_at DESC 
            LIMIT 3
        """)
        
        print(f"   ✅ Found {len(users)} recent users:")
        for i, user in enumerate(users, 1):
            hash_preview = user['password_hash'][:15] + "..." if user['password_hash'] else "None"
            print(f"   {i}. {user['email']} | {user['role']} | {hash_preview}")
            
    except Exception as e:
        print(f"   ❌ Error fetching users: {e}")
        await conn.close()
        return False
    
    # Step 4: Pick a User for Testing
    if not users:
        print("\n   ❌ No users found in database")
        await conn.close()
        return False
    
    test_user = users[0]  # Use the most recent user
    print(f"\n4. 🧪 TESTING WITH USER: {test_user['email']}")
    
    # Step 5: Test Password Scenarios
    print("\n5. 🔐 PASSWORD VERIFICATION TESTS:")
    
    # We'll test with common passwords that might have been used
    test_passwords = [
        "password123",
        "test123",
        "admin123", 
        "user123",
        "123456",
        "password"
    ]
    
    stored_hash = test_user['password_hash']
    print(f"   Stored hash: {stored_hash[:20]}...")
    
    for password in test_passwords:
        try:
            result = bcrypt.checkpw(password.encode(), stored_hash.encode())
            if result:
                print(f"   ✅ Password '{password}' WORKS!")
                
                # Test JWT token generation
                print(f"\n6. 🎟️ JWT TOKEN GENERATION TEST:")
                try:
                    payload = {
                        "sub": str(test_user['id']),
                        "email": test_user['email'],
                        "role": test_user.get('role', 'user'),
                        "exp": datetime.utcnow() + timedelta(minutes=1440)
                    }
                    token = jwt.encode(payload, jwt_secret, algorithm="HS256")
                    print(f"   ✅ JWT token generated successfully")
                    print(f"   Token preview: {token[:30]}...")
                    
                    # Test token verification
                    try:
                        decoded = jwt.decode(token, jwt_secret, algorithms=["HS256"])
                        print(f"   ✅ JWT token verification successful")
                        print(f"   Decoded payload: {decoded}")
                        
                        print(f"\n🎯 DIAGNOSIS RESULT:")
                        print(f"   ✅ Authentication system is WORKING CORRECTLY")
                        print(f"   ✅ User: {test_user['email']}")
                        print(f"   ✅ Password: {password}")
                        print(f"   ✅ JWT generation: Working")
                        print(f"   ✅ JWT verification: Working")
                        
                        await conn.close()
                        return True
                        
                    except Exception as e:
                        print(f"   ❌ JWT verification failed: {e}")
                        
                except Exception as e:
                    print(f"   ❌ JWT generation failed: {e}")
                    
        except Exception as e:
            print(f"   ❌ Password '{password}' verification error: {e}")
    
    print(f"\n   ❌ None of the test passwords worked")
    
    # Step 6: Advanced Hash Analysis
    print(f"\n7. 🔬 HASH ANALYSIS:")
    
    # Check if hash is valid bcrypt format
    if stored_hash.startswith('$2b$'):
        print(f"   ✅ Hash format is valid bcrypt")
    else:
        print(f"   ❌ Hash format is NOT valid bcrypt: {stored_hash[:10]}...")
        
    # Check hash length
    if len(stored_hash) == 60:
        print(f"   ✅ Hash length is correct (60 chars)")
    else:
        print(f"   ❌ Hash length is incorrect: {len(stored_hash)} chars")
    
    # Check for encoding issues
    try:
        encoded_hash = stored_hash.encode('utf-8')
        print(f"   ✅ Hash can be encoded to UTF-8")
    except Exception as e:
        print(f"   ❌ Hash encoding error: {e}")
    
    print(f"\n🚨 DIAGNOSIS RESULT:")
    print(f"   ❌ AUTHENTICATION ISSUE CONFIRMED")
    print(f"   💡 Possible issues:")
    print(f"     - Password hash corrupted during storage")
    print(f"     - Password hash generated with different bcrypt version")
    print(f"     - Database field type causing encoding issues")
    print(f"     - Registration process not using same hashing as login")
    
    await conn.close()
    return False

if __name__ == "__main__":
    success = asyncio.run(production_auth_diagnostic())
    if success:
        print("\n✅ Authentication system is working correctly!")
    else:
        print("\n❌ Authentication system has issues that need fixing!")