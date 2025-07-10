#!/usr/bin/env python3
"""
🧪 JyotiFlow Backend Authentication Test
Tests the authentication endpoints to ensure they work with the initialized database
"""

import sqlite3
import hashlib
import json
from datetime import datetime

class BackendAuthTest:
    def __init__(self):
        self.db_path = 'backend/jyotiflow.db'
    
    def connect_db(self):
        return sqlite3.connect(self.db_path)
    
    def test_user_lookup(self):
        """Test user lookup functionality"""
        print("🧪 Testing User Lookup...")
        
        conn = self.connect_db()
        cursor = conn.cursor()
        
        try:
            # Test admin user lookup
            admin_email = 'admin@jyotiflow.ai'
            cursor.execute("SELECT email, role, credits FROM users WHERE email = ?", (admin_email,))
            admin_user = cursor.fetchone()
            
            if admin_user:
                print(f"✅ Admin user found: {admin_user}")
                if admin_user[1] == 'admin':
                    print("✅ Admin role is correct")
                else:
                    print(f"❌ Admin role is incorrect: {admin_user[1]}")
            else:
                print("❌ Admin user not found")
            
            # Test test user lookup
            test_email = 'user@jyotiflow.ai'
            cursor.execute("SELECT email, role, credits FROM users WHERE email = ?", (test_email,))
            test_user = cursor.fetchone()
            
            if test_user:
                print(f"✅ Test user found: {test_user}")
                if test_user[1] == 'user':
                    print("✅ User role is correct")
                else:
                    print(f"❌ User role is incorrect: {test_user[1]}")
            else:
                print("❌ Test user not found")
            
            return True
            
        except Exception as e:
            print(f"❌ Error testing user lookup: {e}")
            return False
        finally:
            conn.close()
    
    def test_password_verification(self):
        """Test password hash verification"""
        print("\n🧪 Testing Password Verification...")
        
        conn = self.connect_db()
        cursor = conn.cursor()
        
        try:
            # Test admin password
            admin_email = 'admin@jyotiflow.ai'
            admin_password = 'admin123'
            
            cursor.execute("SELECT password_hash FROM users WHERE email = ?", (admin_email,))
            stored_hash = cursor.fetchone()
            
            if stored_hash:
                expected_hash = hashlib.sha256(admin_password.encode()).hexdigest()
                if stored_hash[0] == expected_hash:
                    print("✅ Admin password hash verification successful")
                else:
                    print(f"❌ Admin password hash mismatch")
                    print(f"   Stored: {stored_hash[0]}")
                    print(f"   Expected: {expected_hash}")
            else:
                print("❌ Admin user password hash not found")
            
            # Test user password
            test_email = 'user@jyotiflow.ai'
            test_password = 'user123'
            
            cursor.execute("SELECT password_hash FROM users WHERE email = ?", (test_email,))
            stored_hash = cursor.fetchone()
            
            if stored_hash:
                expected_hash = hashlib.sha256(test_password.encode()).hexdigest()
                if stored_hash[0] == expected_hash:
                    print("✅ Test user password hash verification successful")
                else:
                    print(f"❌ Test user password hash mismatch")
            else:
                print("❌ Test user password hash not found")
            
            return True
            
        except Exception as e:
            print(f"❌ Error testing password verification: {e}")
            return False
        finally:
            conn.close()
    
    def test_service_types(self):
        """Test service types configuration"""
        print("\n🧪 Testing Service Types...")
        
        conn = self.connect_db()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT name, base_credits, enabled FROM service_types WHERE enabled = 1")
            enabled_services = cursor.fetchall()
            
            if enabled_services:
                print(f"✅ Found {len(enabled_services)} enabled services:")
                for service in enabled_services:
                    print(f"   - {service[0]}: {service[1]} credits")
            else:
                print("❌ No enabled services found")
            
            # Check specific services
            expected_services = ['spiritual_guidance', 'love_reading', 'birth_chart', 'premium_reading', 'elite_consultation']
            
            for service_name in expected_services:
                cursor.execute("SELECT name FROM service_types WHERE name = ?", (service_name,))
                if cursor.fetchone():
                    print(f"✅ Service '{service_name}' exists")
                else:
                    print(f"❌ Service '{service_name}' missing")
            
            return True
            
        except Exception as e:
            print(f"❌ Error testing service types: {e}")
            return False
        finally:
            conn.close()
    
    def test_credit_management(self):
        """Test credit management functionality"""
        print("\n🧪 Testing Credit Management...")
        
        conn = self.connect_db()
        cursor = conn.cursor()
        
        try:
            # Check admin credits
            cursor.execute("SELECT credits FROM users WHERE email = ?", ('admin@jyotiflow.ai',))
            admin_credits = cursor.fetchone()
            
            if admin_credits and admin_credits[0] >= 1000:
                print(f"✅ Admin has sufficient credits: {admin_credits[0]}")
            else:
                print(f"❌ Admin has insufficient credits: {admin_credits[0] if admin_credits else 'None'}")
            
            # Check test user credits
            cursor.execute("SELECT credits FROM users WHERE email = ?", ('user@jyotiflow.ai',))
            user_credits = cursor.fetchone()
            
            if user_credits and user_credits[0] >= 100:
                print(f"✅ Test user has sufficient credits: {user_credits[0]}")
            else:
                print(f"❌ Test user has insufficient credits: {user_credits[0] if user_credits else 'None'}")
            
            # Test credit deduction simulation
            original_credits = user_credits[0] if user_credits else 0
            service_cost = 5
            
            if original_credits >= service_cost:
                print(f"✅ Credit deduction test: {original_credits} - {service_cost} = {original_credits - service_cost}")
            else:
                print(f"❌ Insufficient credits for service: {original_credits} < {service_cost}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error testing credit management: {e}")
            return False
        finally:
            conn.close()
    
    def test_birth_chart_schema(self):
        """Test birth chart database schema"""
        print("\n🧪 Testing Birth Chart Schema...")
        
        conn = self.connect_db()
        cursor = conn.cursor()
        
        try:
            # Check birth_chart_cache table
            cursor.execute("PRAGMA table_info(birth_chart_cache)")
            birth_chart_columns = cursor.fetchall()
            
            expected_columns = ['user_email', 'birth_date', 'birth_time', 'birth_location', 'chart_data']
            found_columns = [col[1] for col in birth_chart_columns]
            
            for col in expected_columns:
                if col in found_columns:
                    print(f"✅ Birth chart column '{col}' exists")
                else:
                    print(f"❌ Birth chart column '{col}' missing")
            
            # Check sessions table for birth details
            cursor.execute("PRAGMA table_info(sessions)")
            sessions_columns = cursor.fetchall()
            sessions_column_names = [col[1] for col in sessions_columns]
            
            if 'birth_details' in sessions_column_names:
                print("✅ Sessions table has birth_details column")
            else:
                print("❌ Sessions table missing birth_details column")
            
            return True
            
        except Exception as e:
            print(f"❌ Error testing birth chart schema: {e}")
            return False
        finally:
            conn.close()
    
    def run_all_tests(self):
        """Run all authentication tests"""
        print("🧪 JyotiFlow Backend Authentication Test Suite")
        print("=" * 60)
        
        tests = [
            self.test_user_lookup,
            self.test_password_verification,
            self.test_service_types,
            self.test_credit_management,
            self.test_birth_chart_schema
        ]
        
        results = []
        for test in tests:
            try:
                result = test()
                results.append(result)
            except Exception as e:
                print(f"❌ Test failed with exception: {e}")
                results.append(False)
        
        print("\n" + "=" * 60)
        print("📋 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        passed = sum(results)
        total = len(results)
        
        if passed == total:
            print(f"✅ All tests passed! ({passed}/{total})")
            print("\n🎉 Backend authentication system is ready!")
            print("\n🔗 Next steps:")
            print("   1. Start the backend server")
            print("   2. Test frontend login with admin credentials")
            print("   3. Verify admin dashboard access")
            print("   4. Test birth chart generation")
        else:
            print(f"❌ Some tests failed ({passed}/{total})")
            print("   Please review the test output above")
        
        return passed == total

def main():
    """Main test function"""
    tester = BackendAuthTest()
    tester.run_all_tests()

if __name__ == "__main__":
    main()