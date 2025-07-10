#!/usr/bin/env python3
"""
🔍 JyotiFlow Authentication & Dashboard Diagnosis Script
Diagnoses authentication, admin access, and credit display issues without external dependencies
"""

import sqlite3
import uuid
import json
from datetime import datetime
import os
import hashlib

class JyotiFlowAuthenticationDiagnosis:
    def __init__(self):
        self.db_path = 'backend/jyotiflow.db'
        self.admin_email = 'admin@jyotiflow.ai'
        self.test_user_email = 'user@jyotiflow.ai'
        
    def connect_db(self):
        """Connect to the SQLite database"""
        if not os.path.exists(self.db_path):
            print(f"❌ Database not found at {self.db_path}")
            return None
        return sqlite3.connect(self.db_path)
    
    def simple_password_hash(self, password):
        """Create a simple password hash for testing (not secure for production)"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def diagnose_database_state(self):
        """Diagnose current database state"""
        print("🔍 Diagnosing JyotiFlow Database State...")
        print("=" * 60)
        
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
            
            print(f"📋 Users table columns: {', '.join(column_names)}")
            
            required_columns = ['email', 'role', 'credits', 'password_hash']
            missing_columns = [col for col in required_columns if col not in column_names]
            
            if missing_columns:
                print(f"❌ Missing columns in users table: {missing_columns}")
            else:
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
            
            # Check credit distribution
            cursor.execute("SELECT MIN(credits), MAX(credits), AVG(credits) FROM users WHERE credits IS NOT NULL")
            credit_stats = cursor.fetchone()
            print(f"💰 Credit statistics - Min: {credit_stats[0]}, Max: {credit_stats[1]}, Avg: {credit_stats[2]:.2f}")
            
            # Check users with zero or null credits
            cursor.execute("SELECT COUNT(*) FROM users WHERE credits IS NULL OR credits = 0")
            zero_credit_count = cursor.fetchone()[0]
            print(f"⚠️ Users with zero or null credits: {zero_credit_count}")
            
            # Check recent users
            cursor.execute("SELECT email, role, credits, created_at FROM users ORDER BY created_at DESC LIMIT 5")
            recent_users = cursor.fetchall()
            
            print("\n📋 Recent 5 users:")
            for user in recent_users:
                print(f"   - {user[0]} (role: {user[1]}, credits: {user[2]}, created: {user[3]})")
            
            # Check all users with role information
            cursor.execute("SELECT role, COUNT(*) FROM users GROUP BY role")
            role_distribution = cursor.fetchall()
            
            print("\n👥 User role distribution:")
            for role, count in role_distribution:
                print(f"   - {role}: {count} users")
            
            return True
            
        except Exception as e:
            print(f"❌ Error during diagnosis: {e}")
            return False
        finally:
            conn.close()
    
    def check_birth_chart_tables(self):
        """Check birth chart related tables"""
        print("\n🔍 Checking Birth Chart Tables...")
        
        conn = self.connect_db()
        if not conn:
            return False
        
        cursor = conn.cursor()
        
        birth_chart_tables = [
            'birth_chart_cache', 'sessions', 'spiritual_sessions'
        ]
        
        try:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            existing_tables = [row[0] for row in cursor.fetchall()]
            
            for table in birth_chart_tables:
                if table in existing_tables:
                    print(f"✅ Table '{table}' exists")
                    
                    # Check if table has data
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    print(f"   - Contains {count} records")
                else:
                    print(f"❌ Table '{table}' missing")
            
            # Check sessions table for birth chart data
            if 'sessions' in existing_tables:
                cursor.execute("SELECT COUNT(*) FROM sessions WHERE birth_details IS NOT NULL")
                birth_chart_sessions = cursor.fetchone()[0]
                print(f"📊 Sessions with birth chart data: {birth_chart_sessions}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error checking birth chart tables: {e}")
            return False
        finally:
            conn.close()
    
    def verify_service_types(self):
        """Verify service types table"""
        print("\n🔍 Checking Service Types...")
        
        conn = self.connect_db()
        if not conn:
            return False
        
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='service_types'")
            if not cursor.fetchone():
                print("❌ Service types table missing")
                return False
            
            cursor.execute("SELECT name, base_credits, enabled FROM service_types")
            service_types = cursor.fetchall()
            
            if not service_types:
                print("❌ No service types found")
            else:
                print(f"✅ Found {len(service_types)} service types:")
                for service in service_types:
                    status = "enabled" if len(service) < 3 or service[2] else "disabled"
                    credits = service[1] if len(service) > 1 else "unknown"
                    print(f"   - {service[0]} ({credits} credits, {status})")
            
            return True
            
        except Exception as e:
            print(f"❌ Error checking service types: {e}")
            return False
        finally:
            conn.close()
    
    def create_minimal_admin_user(self):
        """Create a minimal admin user for testing"""
        print("\n🔧 Creating Minimal Admin User...")
        
        conn = self.connect_db()
        if not conn:
            return False
        
        cursor = conn.cursor()
        
        try:
            # Check if admin user already exists
            cursor.execute("SELECT email, role, credits FROM users WHERE email = ?", (self.admin_email,))
            existing_admin = cursor.fetchone()
            
            if existing_admin:
                print(f"✅ Admin user already exists: {existing_admin}")
                
                # Update role and credits if needed
                if existing_admin[1] != 'admin':
                    cursor.execute("UPDATE users SET role = 'admin' WHERE email = ?", (self.admin_email,))
                    print("✅ Updated role to admin")
                
                if existing_admin[2] < 1000:
                    cursor.execute("UPDATE users SET credits = 1000 WHERE email = ?", (self.admin_email,))
                    print("✅ Updated credits to 1000")
                
                conn.commit()
                return True
            else:
                # Create new admin user with simple hash
                print("Creating new admin user...")
                
                user_id = str(uuid.uuid4())
                password_hash = self.simple_password_hash('admin123')
                
                cursor.execute("""
                    INSERT INTO users (id, email, password_hash, name, full_name, role, credits, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (user_id, self.admin_email, password_hash, 'Admin', 'Admin User', 'admin', 1000, datetime.now().isoformat()))
                
                conn.commit()
                print(f"✅ Created admin user: {self.admin_email}")
                return True
            
        except Exception as e:
            print(f"❌ Error creating admin user: {e}")
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
            # Count users that need fixing
            cursor.execute("SELECT COUNT(*) FROM users WHERE credits IS NULL OR credits = 0")
            users_to_fix = cursor.fetchone()[0]
            
            if users_to_fix == 0:
                print("✅ All users have proper credits")
                return True
            
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
            return False
        finally:
            conn.close()
    
    def run_complete_diagnosis(self):
        """Run complete diagnosis and basic fixes"""
        print("🚀 Starting JyotiFlow Authentication & Dashboard Diagnosis...")
        print("=" * 60)
        
        success = True
        
        # Step 1: Basic database diagnosis
        if not self.diagnose_database_state():
            print("❌ Basic diagnosis failed.")
            success = False
        
        # Step 2: Check birth chart tables
        if not self.check_birth_chart_tables():
            print("❌ Birth chart table check failed.")
            success = False
        
        # Step 3: Check service types
        if not self.verify_service_types():
            print("❌ Service types check failed.")
            success = False
        
        # Step 4: Create/fix admin user
        if not self.create_minimal_admin_user():
            print("❌ Admin user creation failed.")
            success = False
        
        # Step 5: Fix user credits
        if not self.fix_user_credits():
            print("❌ Credit fixing failed.")
            success = False
        
        # Final summary
        print("\n" + "=" * 60)
        print("📋 DIAGNOSIS SUMMARY")
        print("=" * 60)
        
        if success:
            print("✅ All checks and fixes completed successfully!")
            print("\n🎯 Test Credentials:")
            print(f"   Admin: {self.admin_email} / admin123")
            print("\n🔗 Key URLs to test:")
            print("   - Login: /login")
            print("   - Admin Dashboard: /admin")
            print("   - Birth Chart: /birth-chart")
            print("   - Profile: /profile")
            
            print("\n📝 Next Steps:")
            print("   1. Test login with admin credentials")
            print("   2. Verify admin dashboard shows proper tabs")
            print("   3. Check user profile shows correct credit balance")
            print("   4. Test birth chart generation functionality")
        else:
            print("❌ Some issues were found. Review the output above.")
        
        return success

def main():
    """Main function to run the diagnosis"""
    diagnosis = JyotiFlowAuthenticationDiagnosis()
    diagnosis.run_complete_diagnosis()

if __name__ == "__main__":
    main()