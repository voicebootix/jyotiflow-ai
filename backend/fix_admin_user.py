#!/usr/bin/env python3
"""
Fix Admin User Role and Credits
This script ensures the admin user has the correct role and credits
"""
import asyncio
import asyncpg
import os
import bcrypt
import uuid

async def fix_admin_user():
    DATABASE_URL = os.getenv('DATABASE_URL')
    if not DATABASE_URL:
        print("❌ DATABASE_URL not found in environment")
        return False
    
    print("🔧 Fixing admin user role and credits...")
    
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        print("✅ Connected to database")
        
        # Admin email to fix
        admin_email = "admin@jyotiflow.ai"
        
        # Check if admin user exists
        admin_user = await conn.fetchrow("SELECT * FROM users WHERE email = $1", admin_email)
        
        if admin_user:
            print(f"✅ Found admin user: {admin_email}")
            print(f"   Current role: {admin_user['role']}")
            print(f"   Current credits: {admin_user['credits']}")
            
            # Update admin user with correct role and credits
            await conn.execute("""
                UPDATE users 
                SET role = 'admin', credits = 1000 
                WHERE email = $1
            """, admin_email)
            
            print("✅ Updated admin user with role='admin' and credits=1000")
            
        else:
            print(f"❌ Admin user {admin_email} not found. Creating...")
            
            # Create admin user
            password_hash = bcrypt.hashpw("admin123".encode(), bcrypt.gensalt()).decode()
            user_id = uuid.uuid4()
            
            await conn.execute("""
                INSERT INTO users (id, email, password_hash, name, full_name, role, credits, created_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, NOW())
            """, user_id, admin_email, password_hash, "Admin User", "Admin User", "admin", 1000)
            
            print(f"✅ Created admin user: {admin_email} with password: admin123")
        
        # Verify the fix
        updated_admin = await conn.fetchrow("SELECT * FROM users WHERE email = $1", admin_email)
        print(f"\n🎯 Verification:")
        print(f"   Email: {updated_admin['email']}")
        print(f"   Role: {updated_admin['role']}")
        print(f"   Credits: {updated_admin['credits']}")
        print(f"   Name: {updated_admin['full_name']}")
        
        await conn.close()
        print("\n✅ Admin user fix completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing admin user: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(fix_admin_user())

