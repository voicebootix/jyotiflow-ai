import asyncio
import asyncpg
import json
import os
from datetime import datetime

async def configure_facebook_credentials():
    """Configure Facebook credentials interactively in PostgreSQL"""
    print("🔧 Facebook Credentials Configuration for PostgreSQL")
    print("=" * 50)
    
    print("\n📋 You'll need the following from your Facebook Developer App:")
    print("1. App ID (from App Dashboard -> Settings -> Basic)")
    print("2. App Secret (from App Dashboard -> Settings -> Basic)")
    print("3. Page ID (from your Facebook page -> About section)")
    print("4. Page Access Token (from Graph API Explorer)")
    
    print("\n🔗 Helpful links:")
    print("- Facebook Developers: https://developers.facebook.com/")
    print("- Graph API Explorer: https://developers.facebook.com/tools/explorer/")
    print("- Access Token Debugger: https://developers.facebook.com/tools/debug/accesstoken/")
    
    # Get credentials from user
    app_id = input("\n📱 Enter your Facebook App ID: ").strip()
    app_secret = input("🔐 Enter your Facebook App Secret: ").strip()
    page_id = input("📄 Enter your Facebook Page ID: ").strip()
    page_access_token = input("🎫 Enter your Page Access Token: ").strip()
    
    # Validate inputs
    if not all([app_id, app_secret, page_id, page_access_token]):
        print("❌ All fields are required!")
        return False
    
    # Create credentials object
    facebook_creds = {
        "app_id": app_id,
        "app_secret": app_secret,
        "page_id": page_id,
        "page_access_token": page_access_token,
        "configured_at": datetime.now().isoformat()
    }
    
    # Save to PostgreSQL database
    try:
        database_url = os.getenv("DATABASE_URL", 
            "postgresql://jyotiflow_db_user:em0MmaZmvPzASryvzLHpR5g5rRZTQqpw@dpg-d12ohqemcj7s73fjbqtg-a/jyotiflow_db")
        
        conn = await asyncpg.connect(database_url)
        
        await conn.execute('''
            UPDATE platform_settings 
            SET value = $1, updated_at = CURRENT_TIMESTAMP 
            WHERE key = 'facebook_credentials'
        ''', facebook_creds)
        
        await conn.close()
        
        print("\n✅ Facebook credentials saved successfully to PostgreSQL!")
        print(f"📊 App ID: {app_id}")
        print(f"📄 Page ID: {page_id}")
        print(f"🔐 Token configured (length: {len(page_access_token)} chars)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error saving credentials: {e}")
        return False

async def test_facebook_credentials():
    """Test if Facebook credentials are properly configured in PostgreSQL"""
    print("\n🧪 Testing Facebook credentials...")
    
    try:
        database_url = os.getenv("DATABASE_URL", 
            "postgresql://jyotiflow_db_user:em0MmaZmvPzASryvzLHpR5g5rRZTQqpw@dpg-d12ohqemcj7s73fjbqtg-a/jyotiflow_db")
        
        conn = await asyncpg.connect(database_url)
        
        row = await conn.fetchrow('SELECT value FROM platform_settings WHERE key = $1', 'facebook_credentials')
        
        if row and row['value'] != {}:
            creds = row['value']  # JSONB is already parsed
            required_fields = ['app_id', 'app_secret', 'page_id', 'page_access_token']
            missing = [field for field in required_fields if not creds.get(field)]
            
            if missing:
                print(f"❌ Missing fields: {', '.join(missing)}")
                await conn.close()
                return False
            else:
                print("✅ All required fields present")
                print(f"   App ID: {creds['app_id']}")
                print(f"   Page ID: {creds['page_id']}")
                print(f"   Token: {creds['page_access_token'][:20]}...")
                await conn.close()
                return True
        else:
            print("❌ No credentials configured")
            await conn.close()
            return False
            
    except Exception as e:
        print(f"❌ Error testing credentials: {e}")
        return False

async def quick_configure():
    """Quick configuration with placeholder values"""
    print("🚀 Quick configuration with test values...")
    print("⚠️  Replace these with your real credentials!")
    
    facebook_creds = {
        "app_id": "YOUR_FACEBOOK_APP_ID",
        "app_secret": "YOUR_FACEBOOK_APP_SECRET",
        "page_id": "YOUR_FACEBOOK_PAGE_ID", 
        "page_access_token": "YOUR_FACEBOOK_PAGE_ACCESS_TOKEN",
        "configured_at": datetime.now().isoformat(),
        "note": "These are placeholder values - replace with real credentials"
    }
    
    try:
        database_url = os.getenv("DATABASE_URL", 
            "postgresql://jyotiflow_db_user:em0MmaZmvPzASryvzLHpR5g5rRZTQqpw@dpg-d12ohqemcj7s73fjbqtg-a/jyotiflow_db")
        
        conn = await asyncpg.connect(database_url)
        
        await conn.execute('''
            UPDATE platform_settings 
            SET value = $1, updated_at = CURRENT_TIMESTAMP 
            WHERE key = 'facebook_credentials'
        ''', facebook_creds)
        
        await conn.close()
        
        print("✅ Placeholder credentials configured!")
        print("🔧 Edit the database or run this script again with real values")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

async def test_facebook_api():
    """Test actual Facebook API connection"""
    print("\n🌐 Testing Facebook API connection...")
    
    try:
        # Import the Facebook service
        import sys
        sys.path.append('.')
        from services.facebook_service import facebook_service
        
        # Test credentials validation
        result = await facebook_service.validate_credentials()
        
        if result.get('success'):
            print("✅ Facebook API credentials are valid!")
            print(f"   Page: {result.get('page_name', 'Unknown')}")
            print(f"   Page ID: {result.get('page_id', 'Unknown')}")
        else:
            print("❌ Facebook API validation failed:")
            print(f"   Error: {result.get('error', 'Unknown error')}")
            
        return result.get('success', False)
        
    except Exception as e:
        print(f"❌ Error testing Facebook API: {e}")
        return False

if __name__ == "__main__":
    async def main():
        print("🎯 JyotiFlow Facebook Integration Setup (PostgreSQL)")
        print("=" * 50)
        
        # Check current status
        await test_facebook_credentials()
        
        print("\nChoose an option:")
        print("1. Configure real Facebook credentials")
        print("2. Quick setup with placeholder values")
        print("3. Just test current credentials")
        print("4. Test Facebook API connection")
        print("5. Exit")
        
        choice = input("\nEnter choice (1-5): ").strip()
        
        if choice == "1":
            success = await configure_facebook_credentials()
            if success:
                await test_facebook_credentials()
                await test_facebook_api()
                print("\n🎯 Next steps:")
                print("1. Start your backend: uvicorn main:app --reload")
                print("2. Test social media posting")
                print("3. Check logs for success messages")
                
        elif choice == "2":
            await quick_configure()
            print("\n⚠️  Remember to replace placeholder values!")
            
        elif choice == "3":
            await test_facebook_credentials()
            
        elif choice == "4":
            await test_facebook_api()
            
        elif choice == "5":
            print("👋 Goodbye!")
            
        else:
            print("❌ Invalid choice")

        print("\n📚 For detailed setup instructions, see:")
        print("   SOCIAL_MEDIA_AUTOMATION_ROOT_CAUSE_ANALYSIS.md")
    
    asyncio.run(main())