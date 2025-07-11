"""
Surgical fix for admin authentication in JyotiFlow AI platform
This script addresses the exact authentication issue preventing AI Marketing Director access
"""

import asyncio
import asyncpg
import bcrypt
import jwt
import os
from datetime import datetime, timezone, timedelta

# JWT configuration matching the backend
JWT_SECRET = os.getenv("JWT_SECRET", "jyotiflow_secret")
JWT_ALGORITHM = "HS256"

async def surgical_admin_auth_fix():
    """
    Surgical fix for admin authentication issues
    """
    try:
        # Connect to database using the same method as backend
        DATABASE_URL = os.getenv("DATABASE_URL")
        if not DATABASE_URL:
            print("❌ DATABASE_URL not found in environment")
            return False
        
        conn = await asyncpg.connect(DATABASE_URL)
        print("✅ Connected to database")
        
        # 1. Check if admin user exists and get current state
        admin_user = await conn.fetchrow(
            "SELECT id, email, full_name, role, credits, password_hash FROM users WHERE email = $1", 
            "admin@jyotiflow.ai"
        )
        
        if not admin_user:
            print("❌ Admin user not found - creating admin user")
            # Create admin user with proper role and robust datetime handling
            password_hash = bcrypt.hashpw("admin123".encode(), bcrypt.gensalt()).decode()
            
            # Try different datetime approaches for compatibility
            try:
                # First try with timezone-aware datetime
                current_time = datetime.now(timezone.utc)
                admin_id = await conn.fetchval("""
                    INSERT INTO users (email, password_hash, full_name, role, credits, created_at)
                    VALUES ($1, $2, $3, $4, $5, $6)
                    RETURNING id
                """, "admin@jyotiflow.ai", password_hash, "Admin User", "admin", 1000, current_time)
            except Exception as e:
                print(f"⚠️ Timezone-aware datetime failed: {e}")
                # Fallback to naive datetime
                current_time = datetime.now()
                admin_id = await conn.fetchval("""
                    INSERT INTO users (email, password_hash, full_name, role, credits, created_at)
                    VALUES ($1, $2, $3, $4, $5, $6)
                    RETURNING id
                """, "admin@jyotiflow.ai", password_hash, "Admin User", "admin", 1000, current_time)
            
            print(f"✅ Created admin user with ID: {admin_id}")
            
            # Fetch the newly created user
            admin_user = await conn.fetchrow(
                "SELECT id, email, full_name, role, credits, password_hash FROM users WHERE id = $1", 
                admin_id
            )
        else:
            print(f"✅ Admin user found: {admin_user['email']}")
            
            # 2. Ensure admin user has correct role
            if admin_user['role'] != 'admin':
                await conn.execute(
                    "UPDATE users SET role = $1, credits = $2 WHERE id = $3",
                    "admin", 1000, admin_user['id']
                )
                print("✅ Updated admin user role to 'admin'")
                
                # Fetch updated user
                admin_user = await conn.fetchrow(
                    "SELECT id, email, full_name, role, credits, password_hash FROM users WHERE id = $1", 
                    admin_user['id']
                )
            else:
                print("✅ Admin user already has correct role")
        
        # 3. Generate a valid JWT token for testing
        def create_jwt_token(user_id, email, role):
            payload = {
                "sub": str(user_id),
                "email": email,
                "role": role,
                "exp": datetime.now(timezone.utc) + timedelta(days=30)
            }
            return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        
        test_token = create_jwt_token(admin_user['id'], admin_user['email'], admin_user['role'])
        print(f"✅ Generated test JWT token: {test_token[:50]}...")
        
        # 4. Verify token can be decoded
        try:
            payload = jwt.decode(test_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            print(f"✅ Token verification successful:")
            print(f"   User ID: {payload['sub']}")
            print(f"   Email: {payload['email']}")
            print(f"   Role: {payload['role']}")
            print(f"   Expires: {datetime.fromtimestamp(payload['exp'])}")
        except Exception as e:
            print(f"❌ Token verification failed: {e}")
            return False
        
        # 5. Save token to a file for testing
        with open('/tmp/admin_test_token.txt', 'w') as f:
            f.write(test_token)
        print("✅ Test token saved to /tmp/admin_test_token.txt")
        
        await conn.close()
        print("✅ Surgical admin authentication fix completed successfully")
        
        # 6. Print summary
        print("\n📊 ADMIN USER STATUS:")
        print(f"   ID: {admin_user['id']}")
        print(f"   Email: {admin_user['email']}")
        print(f"   Name: {admin_user['full_name']}")
        print(f"   Role: {admin_user['role']}")
        print(f"   Credits: {admin_user['credits']}")
        print(f"   JWT Token: Valid and ready for use")
        
        return True
        
    except Exception as e:
        print(f"❌ Surgical admin authentication fix failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(surgical_admin_auth_fix())

