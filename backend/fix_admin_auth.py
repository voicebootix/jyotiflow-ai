"""
Comprehensive fix for admin authentication issues
This script will:
1. Ensure admin user exists with correct role
2. Test JWT token generation
3. Verify admin authentication flow
"""

import asyncio
import asyncpg
import bcrypt
import jwt
import os
from datetime import datetime, timezone, timedelta

# JWT configuration
JWT_SECRET = os.getenv("JWT_SECRET", "jyotiflow_secret")
JWT_ALGORITHM = "HS256"

async def create_jwt_token(user_id, email, role="user"):
    """Create JWT token with proper role"""
    payload = {
        "sub": str(user_id),
        "email": email,
        "role": role,
        "exp": datetime.now(timezone.utc) + timedelta(days=30)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

async def fix_admin_authentication():
    """Fix admin authentication issues"""
    try:
        # Connect to database using environment variable
        DATABASE_URL = os.getenv("DATABASE_URL")
        if not DATABASE_URL:
            print("❌ DATABASE_URL not found in environment")
            return False
        
        conn = await asyncpg.connect(DATABASE_URL)
        print("✅ Connected to database")
        
        # Check if admin user exists
        admin_user = await conn.fetchrow(
            "SELECT * FROM users WHERE email = $1", 
            "admin@jyotiflow.ai"
        )
        
        if not admin_user:
            print("❌ Admin user not found")
            # Create admin user
            password_hash = bcrypt.hashpw("admin123".encode(), bcrypt.gensalt()).decode()
            admin_id = await conn.fetchval("""
                INSERT INTO users (email, password_hash, full_name, role, credits, created_at)
                VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING id
            """, "admin@jyotiflow.ai", password_hash, "Admin User", "admin", 1000, datetime.now(timezone.utc))
            print(f"✅ Created admin user with ID: {admin_id}")
        else:
            print(f"✅ Admin user found: {admin_user['email']}")
            
            # Update role to admin if not already
            if admin_user['role'] != 'admin':
                await conn.execute(
                    "UPDATE users SET role = $1, credits = $2 WHERE id = $3",
                    "admin", 1000, admin_user['id']
                )
                print("✅ Updated admin user role and credits")
            else:
                print("✅ Admin user already has correct role")
        
        # Get updated admin user
        admin_user = await conn.fetchrow(
            "SELECT * FROM users WHERE email = $1", 
            "admin@jyotiflow.ai"
        )
        
        # Test JWT token generation
        token = await create_jwt_token(admin_user['id'], admin_user['email'], admin_user['role'])
        print(f"✅ Generated JWT token: {token[:50]}...")
        
        # Verify token
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            print(f"✅ Token verification successful:")
            print(f"   User ID: {payload['sub']}")
            print(f"   Email: {payload['email']}")
            print(f"   Role: {payload['role']}")
        except Exception as e:
            print(f"❌ Token verification failed: {e}")
        
        await conn.close()
        print("✅ Admin authentication fix completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing admin authentication: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(fix_admin_authentication())

