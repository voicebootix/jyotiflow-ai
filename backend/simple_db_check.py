#!/usr/bin/env python3
"""
🔍 Simple Database Connection Test
Tests if database is reachable using basic Python
"""

import socket
import urllib.parse
import sys
import os

def test_database_connection():
    """Test basic database connectivity"""
    
    print("🔍 JyotiFlow Database Connection Test")
    print("=" * 50)
    
    # Parse the database URL
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("❌ ERROR: DATABASE_URL environment variable is required but not set")
        print("Please set the DATABASE_URL environment variable with your database connection string")
        sys.exit(1)
    
    try:
        parsed = urllib.parse.urlparse(db_url)
        host = parsed.hostname
        port = parsed.port or 5432
        username = parsed.username
        database = parsed.path.lstrip('/')
        
        print(f"📋 Database Details:")
        print(f"   Host: {host}")
        print(f"   Port: {port}")
        print(f"   Database: {database}")
        print(f"   Username: {username}")
        print()
        
        # Test network connectivity
        print("🌐 Testing network connectivity...")
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            result = sock.connect_ex((host, port))
            sock.close()
            
            if result == 0:
                print("✅ Network connection successful - database server is reachable")
                print()
                print("🔧 Next Steps:")
                print("1. Install psql to connect:")
                print("   sudo apt-get install postgresql-client")
                print()
                print("2. Connect to database:")
                print(f"   psql '{db_url}'")
                print()
                print("3. Run these commands to check database state:")
                print("   \\dt                                    -- List tables")
                print("   SELECT COUNT(*) FROM users;           -- Count users")
                print("   SELECT * FROM users WHERE email = 'admin@jyotiflow.ai';  -- Check admin")
                print()
                return True
            else:
                print(f"❌ Network connection failed - cannot reach {host}:{port}")
                print("   Possible reasons:")
                print("   - Database server is down")
                print("   - Network/firewall issues") 
                print("   - Wrong host/port")
                return False
                
        except Exception as e:
            print(f"❌ Network test failed: {e}")
            return False
            
    except Exception as e:
        print(f"❌ URL parsing failed: {e}")
        return False

def show_database_check_options():
    """Show various options for checking the database"""
    
    print("\n" + "=" * 50)
    print("💡 DATABASE CHECK OPTIONS")
    print("=" * 50)
    
    print("\n🚀 QUICKEST METHODS:")
    print()
    print("1. Using Docker (if available):")
    print("   docker run -it --rm postgres:13 psql \\")
    print("   'postgresql://username:password@host/database'")
    print()
    print("2. Install psql and connect:")
    print("   sudo apt-get install postgresql-client")
    print("   psql 'postgresql://username:password@host/database'")
    print()
    print("3. Use pgAdmin (GUI):")
    print("   - Download from https://www.pgadmin.org/")
    print("   - Host: dpg-d12ohqemcj7s73fjbqtg-a")
    print("   - Port: 5432")
    print("   - Database: jyotiflow_db")
    print("   - Username: jyotiflow_db_user")
    print("   - Password: [REDACTED]")
    
    print("\n🔍 WHAT TO CHECK:")
    print()
    print("1. Does admin user exist?")
    print("   SELECT * FROM users WHERE email = 'admin@jyotiflow.ai';")
    print()
    print("2. How many tables exist?")
    print("   SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';")
    print()
    print("3. Are there any users at all?")
    print("   SELECT COUNT(*) FROM users;")
    print()
    print("4. What's the user ID data type?")
    print("   SELECT data_type FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'id';")
    
    print("\n🎯 EXPECTED RESULTS:")
    print()
    print("✅ If database is working:")
    print("   - 20+ tables exist")
    print("   - Admin user: admin@jyotiflow.ai with 1000 credits")
    print("   - ID type: integer (SERIAL)")
    print("   - 4 credit packages exist")
    print()
    print("❌ If database is empty:")
    print("   - 0 tables")
    print("   - No users")
    print("   - Initialization failed")

def main():
    """Main function"""
    print("🚀 Testing database connectivity...")
    print()
    
    success = test_database_connection()
    show_database_check_options()
    
    if success:
        print("\n✅ Database server is reachable!")
        print("Use one of the methods above to check the actual database contents.")
    else:
        print("\n❌ Cannot reach database server.")
        print("Check your network connection and database server status.")

if __name__ == "__main__":
    main()