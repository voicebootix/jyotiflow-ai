#!/usr/bin/env python3
"""
Deployment Debug Script for JyotiFlow.ai
This script helps diagnose common deployment issues on Render
"""
import os
import asyncio
import asyncpg
import sys
from datetime import datetime

async def debug_database_connection():
    """Debug database connectivity issues"""
    print("🔍 JyotiFlow.ai Deployment Debugging Tool")
    print("=" * 50)
    print(f"⏰ Time: {datetime.now()}")
    print(f"🐍 Python version: {sys.version}")
    print()
    
    # Check environment variables
    print("📋 Environment Variables Check:")
    print("-" * 30)
    
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        # Mask sensitive parts of the URL for logging
        masked_url = database_url
        if '@' in masked_url:
            parts = masked_url.split('@')
            if ':' in parts[0]:
                user_pass = parts[0].split('://')[-1]
                if ':' in user_pass:
                    user, password = user_pass.split(':', 1)
                    masked_password = password[:2] + '*' * (len(password) - 4) + password[-2:] if len(password) > 4 else '***'
                    masked_url = masked_url.replace(password, masked_password)
        
        print(f"✅ DATABASE_URL is set: {masked_url}")
        
        # Parse database URL components
        try:
            if database_url.startswith('postgresql://'):
                url_part = database_url[13:]  # Remove postgresql://
                if '@' in url_part:
                    creds, host_db = url_part.split('@', 1)
                    if ':' in creds:
                        username, password = creds.split(':', 1)
                        print(f"👤 Username: {username}")
                        print(f"🔑 Password: {'*' * len(password)} (length: {len(password)})")
                    
                    if '/' in host_db:
                        host_port, database = host_db.split('/', 1)
                        if ':' in host_port:
                            host, port = host_port.split(':', 1)
                            print(f"🏠 Host: {host}")
                            print(f"🚪 Port: {port}")
                        else:
                            print(f"🏠 Host: {host_port}")
                            print(f"🚪 Port: 5432 (default)")
                        print(f"🗄️ Database: {database}")
        except Exception as e:
            print(f"⚠️ Error parsing DATABASE_URL: {e}")
            
    else:
        print("❌ DATABASE_URL is not set!")
        print("💡 Set it in your Render dashboard:")
        print("   Dashboard > Service > Environment > Add Environment Variable")
        return False
    
    print()
    
    # Check other important environment variables
    other_vars = ['JWT_SECRET', 'OPENAI_API_KEY', 'APP_ENV', 'PORT']
    for var in other_vars:
        value = os.getenv(var)
        if value:
            if 'SECRET' in var or 'KEY' in var:
                print(f"✅ {var}: {'*' * len(value)} (length: {len(value)})")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"⚠️ {var}: Not set")
    
    print()
    print("🔗 Database Connection Test:")
    print("-" * 30)
    
    # Test database connection
    try:
        print("🔄 Attempting to connect to database...")
        
        # Test with shorter timeout first
        conn = await asyncio.wait_for(
            asyncpg.connect(database_url),
            timeout=10.0
        )
        
        print("✅ Database connection successful!")
        
        # Test basic query
        try:
            result = await conn.fetchval("SELECT version()")
            print(f"🗄️ PostgreSQL version: {result}")
            
            # Test if we can create a simple table (for permissions check)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS deployment_test (
                    id SERIAL PRIMARY KEY,
                    test_time TIMESTAMP DEFAULT NOW()
                )
            """)
            print("✅ Database write permissions confirmed")
            
            # Clean up test table
            await conn.execute("DROP TABLE IF EXISTS deployment_test")
            print("✅ Database cleanup successful")
            
        except Exception as e:
            print(f"⚠️ Database query test failed: {e}")
            
        await conn.close()
        print("✅ Database connection closed properly")
        
        return True
        
    except asyncio.TimeoutError:
        print("❌ Database connection timeout (10 seconds)")
        print("💡 Possible issues:")
        print("   • Database server is down or overloaded")
        print("   • Network connectivity issues")
        print("   • Incorrect host/port in DATABASE_URL")
        return False
        
    except asyncpg.InvalidAuthorizationSpecificationError:
        print("❌ Database authentication failed")
        print("💡 Possible issues:")
        print("   • Incorrect username/password in DATABASE_URL")
        print("   • User doesn't have access to the database")
        return False
        
    except asyncpg.InvalidCatalogNameError:
        print("❌ Database does not exist")
        print("💡 Possible issues:")
        print("   • Database name is incorrect in DATABASE_URL")
        print("   • Database hasn't been created yet")
        return False
        
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        print(f"🔍 Error type: {type(e).__name__}")
        return False

async def main():
    """Main debugging function"""
    success = await debug_database_connection()
    
    print()
    print("📋 Deployment Readiness Summary:")
    print("-" * 30)
    
    if success:
        print("✅ Database connectivity: PASS")
        print("✅ Deployment should work!")
        print()
        print("🚀 Next steps:")
        print("   1. Deploy your application")
        print("   2. Monitor logs for any additional issues")
        print("   3. Test your API endpoints")
    else:
        print("❌ Database connectivity: FAIL")
        print("❌ Deployment will likely fail")
        print()
        print("🔧 Troubleshooting steps:")
        print("   1. Check DATABASE_URL in Render dashboard")
        print("   2. Ensure PostgreSQL service is running")
        print("   3. Verify database credentials")
        print("   4. Check network connectivity")
        print("   5. Contact Render support if issues persist")

if __name__ == "__main__":
    asyncio.run(main())