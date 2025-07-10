#!/usr/bin/env python3
"""
🚀 JyotiFlow SQLite Database Initialization
Creates required tables for authentication, user management, and core functionality
"""

import sqlite3
import uuid
import hashlib
from datetime import datetime
import os

class SQLiteDatabaseInitializer:
    def __init__(self):
        self.db_path = 'backend/jyotiflow.db'
        
    def connect_db(self):
        """Connect to SQLite database"""
        return sqlite3.connect(self.db_path)
    
    def create_users_table(self):
        """Create users table"""
        conn = self.connect_db()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    name TEXT,
                    full_name TEXT,
                    role TEXT DEFAULT 'user',
                    credits INTEGER DEFAULT 5,
                    phone TEXT,
                    birth_date TEXT,
                    birth_time TEXT,
                    birth_location TEXT,
                    spiritual_level TEXT DEFAULT 'beginner',
                    preferred_language TEXT DEFAULT 'en',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    last_login_at TEXT
                )
            ''')
            
            print("✅ Users table created")
            conn.commit()
            return True
            
        except Exception as e:
            print(f"❌ Error creating users table: {e}")
            return False
        finally:
            conn.close()
    
    def create_sessions_table(self):
        """Create sessions table"""
        conn = self.connect_db()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    session_id TEXT UNIQUE NOT NULL,
                    user_email TEXT NOT NULL,
                    service_type TEXT NOT NULL,
                    question TEXT NOT NULL,
                    birth_details TEXT,
                    status TEXT DEFAULT 'active',
                    result_summary TEXT,
                    full_result TEXT,
                    guidance TEXT,
                    avatar_video_url TEXT,
                    credits_used INTEGER DEFAULT 0,
                    user_rating INTEGER,
                    user_feedback TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    completed_at TEXT,
                    FOREIGN KEY (user_email) REFERENCES users(email)
                )
            ''')
            
            print("✅ Sessions table created")
            conn.commit()
            return True
            
        except Exception as e:
            print(f"❌ Error creating sessions table: {e}")
            return False
        finally:
            conn.close()
    
    def create_service_types_table(self):
        """Create service_types table"""
        conn = self.connect_db()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS service_types (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT,
                    base_credits INTEGER NOT NULL DEFAULT 5,
                    duration_minutes INTEGER DEFAULT 15,
                    enabled BOOLEAN DEFAULT 1,
                    video_enabled BOOLEAN DEFAULT 1,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            print("✅ Service types table created")
            conn.commit()
            return True
            
        except Exception as e:
            print(f"❌ Error creating service_types table: {e}")
            return False
        finally:
            conn.close()
    
    def create_birth_chart_cache_table(self):
        """Create birth_chart_cache table"""
        conn = self.connect_db()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS birth_chart_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_email TEXT NOT NULL,
                    birth_date TEXT NOT NULL,
                    birth_time TEXT NOT NULL,
                    birth_location TEXT NOT NULL,
                    chart_data TEXT,
                    cached_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    expires_at TEXT,
                    FOREIGN KEY (user_email) REFERENCES users(email)
                )
            ''')
            
            print("✅ Birth chart cache table created")
            conn.commit()
            return True
            
        except Exception as e:
            print(f"❌ Error creating birth_chart_cache table: {e}")
            return False
        finally:
            conn.close()
    
    def insert_default_service_types(self):
        """Insert default service types"""
        conn = self.connect_db()
        cursor = conn.cursor()
        
        try:
            default_services = [
                ('spiritual_guidance', 'Basic spiritual guidance session', 5, 15, 1),
                ('love_reading', 'Love and relationship guidance', 8, 20, 1),
                ('birth_chart', 'Birth chart analysis', 10, 25, 1),
                ('premium_reading', 'Premium comprehensive reading', 15, 30, 1),
                ('elite_consultation', 'Elite personalized consultation', 25, 45, 1)
            ]
            
            for service in default_services:
                cursor.execute('''
                    INSERT OR IGNORE INTO service_types (name, description, base_credits, duration_minutes, enabled)
                    VALUES (?, ?, ?, ?, ?)
                ''', service)
            
            print("✅ Default service types inserted")
            conn.commit()
            return True
            
        except Exception as e:
            print(f"❌ Error inserting default service types: {e}")
            return False
        finally:
            conn.close()
    
    def create_admin_user(self):
        """Create admin user"""
        conn = self.connect_db()
        cursor = conn.cursor()
        
        try:
            admin_email = 'admin@jyotiflow.ai'
            admin_password = 'admin123'
            
            # Check if admin already exists
            cursor.execute('SELECT email FROM users WHERE email = ?', (admin_email,))
            if cursor.fetchone():
                print("✅ Admin user already exists")
                return True
            
            # Create admin user
            user_id = str(uuid.uuid4())
            password_hash = hashlib.sha256(admin_password.encode()).hexdigest()
            
            cursor.execute('''
                INSERT INTO users (id, email, password_hash, name, full_name, role, credits, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, admin_email, password_hash, 'Admin', 'Admin User', 'admin', 1000, datetime.now().isoformat()))
            
            print(f"✅ Admin user created: {admin_email}")
            conn.commit()
            return True
            
        except Exception as e:
            print(f"❌ Error creating admin user: {e}")
            return False
        finally:
            conn.close()
    
    def create_test_user(self):
        """Create test user"""
        conn = self.connect_db()
        cursor = conn.cursor()
        
        try:
            test_email = 'user@jyotiflow.ai'
            test_password = 'user123'
            
            # Check if test user already exists
            cursor.execute('SELECT email FROM users WHERE email = ?', (test_email,))
            if cursor.fetchone():
                print("✅ Test user already exists")
                return True
            
            # Create test user
            user_id = str(uuid.uuid4())
            password_hash = hashlib.sha256(test_password.encode()).hexdigest()
            
            cursor.execute('''
                INSERT INTO users (id, email, password_hash, name, full_name, role, credits, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, test_email, password_hash, 'Test User', 'Test User', 'user', 100, datetime.now().isoformat()))
            
            print(f"✅ Test user created: {test_email}")
            conn.commit()
            return True
            
        except Exception as e:
            print(f"❌ Error creating test user: {e}")
            return False
        finally:
            conn.close()
    
    def run_initialization(self):
        """Run complete database initialization"""
        print("🚀 Initializing JyotiFlow SQLite Database...")
        print("=" * 60)
        
        success = True
        
        # Create core tables
        if not self.create_users_table():
            success = False
        
        if not self.create_sessions_table():
            success = False
        
        if not self.create_service_types_table():
            success = False
        
        if not self.create_birth_chart_cache_table():
            success = False
        
        # Insert default data
        if not self.insert_default_service_types():
            success = False
        
        if not self.create_admin_user():
            success = False
        
        if not self.create_test_user():
            success = False
        
        print("\n" + "=" * 60)
        if success:
            print("✅ Database initialization completed successfully!")
            print("\n🎯 Test Credentials:")
            print("   Admin: admin@jyotiflow.ai / admin123")
            print("   Test User: user@jyotiflow.ai / user123")
            print("\n📋 Tables Created:")
            print("   - users (authentication & profiles)")
            print("   - sessions (spiritual guidance sessions)")
            print("   - service_types (available services)")
            print("   - birth_chart_cache (birth chart data)")
            print("\n🔗 Ready to test:")
            print("   - Login system")
            print("   - Admin dashboard")
            print("   - Birth chart generation")
            print("   - Credit management")
        else:
            print("❌ Database initialization had some errors.")
        
        return success

def main():
    """Main function"""
    initializer = SQLiteDatabaseInitializer()
    initializer.run_initialization()

if __name__ == "__main__":
    main()