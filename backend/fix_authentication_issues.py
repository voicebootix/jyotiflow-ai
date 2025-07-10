#!/usr/bin/env python3
"""
🔧 JyotiFlow Authentication & Dashboard Issues Fix Script
Diagnoses and fixes authentication, admin access, and credit display issues
"""

import sqlite3
import bcrypt
import uuid
import json
from datetime import datetime
import os

class JyotiFlowAuthenticationFixer:
    def __init__(self):
        self.db_path = 'backend/jyotiflow.db'
        self.admin_email = 'admin@jyotiflow.ai'
        self.admin_password = 'admin123'
        self.test_user_email = 'user@jyotiflow.ai'
        self.test_user_password = 'user123'
        
    def connect_db(self):
        """Connect to the SQLite database"""
        if not os.path.exists(self.db_path):
            print(f"❌ Database not found at {self.db_path}")
            return None
        return sqlite3.connect(self.db_path)
    
    def diagnose_issues(self):
        """Diagnose authentication and dashboard issues"""
        print("🔍 Diagnosing JyotiFlow Authentication & Dashboard Issues...")
        
        conn = self.connect_db()
        if not conn:
            return False
        
        cursor = conn.cursor()
        
        try:
            # Check if users table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
            users_table = cursor.fetchone()
            
            if not users_table:
                print("❌ Users table does not exist!")
                return False
            
            print("✅ Users table exists")
            
            # Check table structure
            cursor.execute("PRAGMA table_info(users)")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]
            
            required_columns = ['email', 'role', 'credits', 'password_hash']
            missing_columns = [col for col in required_columns if col not in column_names]
            
            if missing_columns:
                print(f"❌ Missing columns in users table: {missing_columns}")
                return False
            
            print("✅ Users table has all required columns")
            
            # Check total users
            cursor.execute("SELECT COUNT(*) FROM users")
            total_users = cursor.fetchone()[0]
            print(f"📊 Total users in database: {total_users}")
            
            # Check admin users
            cursor.execute("SELECT email, role, credits FROM users WHERE role = 'admin'")
            admin_users = cursor.fetchall()
            
            if not admin_users:
                print("❌ No admin users found!")
            else:
                print(f"✅ Found {len(admin_users)} admin users:")
                for admin in admin_users:
                    print(f"   - {admin[0]} (role: {admin[1]}, credits: {admin[2]})")
            
            # Check for the specific admin user
            cursor.execute("SELECT email, role, credits FROM users WHERE email = ?", (self.admin_email,))
            admin_user = cursor.fetchone()
            
            if not admin_user:
                print(f"❌ Admin user {self.admin_email} not found!")
            else:
                print(f"✅ Admin user found: {admin_user}")
            
            # Check credit values
            cursor.execute("SELECT email, credits FROM users WHERE credits IS NULL OR credits = 0")
            zero_credit_users = cursor.fetchall()
            
            if zero_credit_users:
                print(f"⚠️ Found {len(zero_credit_users)} users with zero or null credits:")
                for user in zero_credit_users[:5]:  # Show first 5
                    print(f"   - {user[0]}: {user[1]} credits")
            
            # Check recent users
            cursor.execute("SELECT email, role, credits, created_at FROM users ORDER BY rowid DESC LIMIT 5")
            recent_users = cursor.fetchall()
            
            print("\n📋 Recent 5 users:")
            for user in recent_users:
                print(f"   - {user[0]} (role: {user[1]}, credits: {user[2]})")
            
            return True
            
        except Exception as e:
            print(f"❌ Error during diagnosis: {e}")
            return False
        finally:
            conn.close()
    
    def fix_admin_user(self):
        """Create or fix admin user"""
        print("\n🔧 Fixing Admin User...")
        
        conn = self.connect_db()
        if not conn:
            return False
        
        cursor = conn.cursor()
        
        try:
            # Check if admin user exists
            cursor.execute("SELECT id, email, role, credits FROM users WHERE email = ?", (self.admin_email,))
            admin_user = cursor.fetchone()
            
            if admin_user:
                # Update existing admin user
                print(f"✅ Admin user exists: {admin_user}")
                
                # Ensure role is admin
                if admin_user[2] != 'admin':
                    cursor.execute("UPDATE users SET role = 'admin' WHERE email = ?", (self.admin_email,))
                    print("✅ Updated admin user role to 'admin'")
                
                # Ensure admin has sufficient credits
                if admin_user[3] < 1000:
                    cursor.execute("UPDATE users SET credits = 1000 WHERE email = ?", (self.admin_email,))
                    print("✅ Updated admin user credits to 1000")
                
                # Update password
                password_hash = bcrypt.hashpw(self.admin_password.encode(), bcrypt.gensalt()).decode()
                cursor.execute("UPDATE users SET password_hash = ? WHERE email = ?", (password_hash, self.admin_email))
                print("✅ Updated admin user password")
                
            else:
                # Create new admin user
                print("❌ Admin user not found. Creating new admin user...")
                
                password_hash = bcrypt.hashpw(self.admin_password.encode(), bcrypt.gensalt()).decode()
                user_id = str(uuid.uuid4())
                
                cursor.execute("""
                    INSERT INTO users (id, email, password_hash, name, full_name, role, credits, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (user_id, self.admin_email, password_hash, 'Admin', 'Admin User', 'admin', 1000, datetime.now()))
                
                print(f"✅ Created new admin user: {self.admin_email}")
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"❌ Error fixing admin user: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def fix_test_user(self):
        """Create or fix test user"""
        print("\n🔧 Fixing Test User...")
        
        conn = self.connect_db()
        if not conn:
            return False
        
        cursor = conn.cursor()
        
        try:
            # Check if test user exists
            cursor.execute("SELECT id, email, role, credits FROM users WHERE email = ?", (self.test_user_email,))
            test_user = cursor.fetchone()
            
            if test_user:
                # Update existing test user
                print(f"✅ Test user exists: {test_user}")
                
                # Ensure test user has sufficient credits
                if test_user[3] < 100:
                    cursor.execute("UPDATE users SET credits = 100 WHERE email = ?", (self.test_user_email,))
                    print("✅ Updated test user credits to 100")
                
                # Update password
                password_hash = bcrypt.hashpw(self.test_user_password.encode(), bcrypt.gensalt()).decode()
                cursor.execute("UPDATE users SET password_hash = ? WHERE email = ?", (password_hash, self.test_user_email))
                print("✅ Updated test user password")
                
            else:
                # Create new test user
                print("❌ Test user not found. Creating new test user...")
                
                password_hash = bcrypt.hashpw(self.test_user_password.encode(), bcrypt.gensalt()).decode()
                user_id = str(uuid.uuid4())
                
                cursor.execute("""
                    INSERT INTO users (id, email, password_hash, name, full_name, role, credits, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (user_id, self.test_user_email, password_hash, 'Test User', 'Test User', 'user', 100, datetime.now()))
                
                print(f"✅ Created new test user: {self.test_user_email}")
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"❌ Error fixing test user: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def fix_user_credits(self):
        """Fix users with zero or null credits"""
        print("\n🔧 Fixing User Credits...")
        
        conn = self.connect_db()
        if not conn:
            return False
        
        cursor = conn.cursor()
        
        try:
            # Update users with null credits
            cursor.execute("UPDATE users SET credits = 5 WHERE credits IS NULL")
            null_credits_updated = cursor.rowcount
            
            # Update users with zero credits (except admin)
            cursor.execute("UPDATE users SET credits = 5 WHERE credits = 0 AND role != 'admin'")
            zero_credits_updated = cursor.rowcount
            
            conn.commit()
            
            print(f"✅ Updated {null_credits_updated} users with null credits")
            print(f"✅ Updated {zero_credits_updated} users with zero credits")
            
            return True
            
        except Exception as e:
            print(f"❌ Error fixing user credits: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def verify_tables(self):
        """Verify all required tables exist"""
        print("\n🔍 Verifying Database Tables...")
        
        conn = self.connect_db()
        if not conn:
            return False
        
        cursor = conn.cursor()
        
        required_tables = [
            'users', 'service_types', 'sessions', 'user_purchases', 
            'satsang_events', 'social_content', 'credit_packages'
        ]
        
        try:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            existing_tables = [row[0] for row in cursor.fetchall()]
            
            for table in required_tables:
                if table in existing_tables:
                    print(f"✅ Table '{table}' exists")
                else:
                    print(f"❌ Table '{table}' missing")
            
            return True
            
        except Exception as e:
            print(f"❌ Error verifying tables: {e}")
            return False
        finally:
            conn.close()
    
    def run_complete_fix(self):
        """Run complete authentication and dashboard fix"""
        print("🚀 Starting JyotiFlow Authentication & Dashboard Fix...")
        print("=" * 60)
        
        # Step 1: Diagnose issues
        if not self.diagnose_issues():
            print("❌ Diagnosis failed. Cannot proceed with fixes.")
            return False
        
        # Step 2: Verify tables
        if not self.verify_tables():
            print("❌ Table verification failed.")
            return False
        
        # Step 3: Fix admin user
        if not self.fix_admin_user():
            print("❌ Failed to fix admin user.")
            return False
        
        # Step 4: Fix test user
        if not self.fix_test_user():
            print("❌ Failed to fix test user.")
            return False
        
        # Step 5: Fix user credits
        if not self.fix_user_credits():
            print("❌ Failed to fix user credits.")
            return False
        
        # Step 6: Final verification
        print("\n🔍 Final Verification...")
        self.diagnose_issues()
        
        print("\n" + "=" * 60)
        print("✅ JyotiFlow Authentication & Dashboard Fix Complete!")
        print("\n📋 Login Credentials:")
        print(f"   Admin: {self.admin_email} / {self.admin_password}")
        print(f"   Test User: {self.test_user_email} / {self.test_user_password}")
        print("\n🎯 Next Steps:")
        print("   1. Test login with admin credentials")
        print("   2. Verify admin dashboard access")
        print("   3. Check credit balance display")
        print("   4. Test birth chart functionality")
        
        return True

def main():
    """Main function to run the fix script"""
    fixer = JyotiFlowAuthenticationFixer()
    success = fixer.run_complete_fix()
    
    if success:
        print("\n🎉 All fixes completed successfully!")
    else:
        print("\n❌ Some fixes failed. Please review the output above.")

if __name__ == "__main__":
    main()