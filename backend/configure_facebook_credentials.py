import sqlite3
import json
from datetime import datetime

def configure_facebook_credentials():
    """Configure Facebook credentials interactively"""
    print("🔧 Facebook Credentials Configuration")
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
    
    # Save to database
    try:
        conn = sqlite3.connect('jyotiflow.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE platform_settings 
            SET value = ?, updated_at = CURRENT_TIMESTAMP 
            WHERE key = 'facebook_credentials'
        ''', (json.dumps(facebook_creds),))
        
        conn.commit()
        conn.close()
        
        print("\n✅ Facebook credentials saved successfully!")
        print(f"📊 App ID: {app_id}")
        print(f"📄 Page ID: {page_id}")
        print(f"🔐 Token configured (length: {len(page_access_token)} chars)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error saving credentials: {e}")
        return False

def test_facebook_credentials():
    """Test if Facebook credentials are properly configured"""
    print("\n🧪 Testing Facebook credentials...")
    
    try:
        conn = sqlite3.connect('jyotiflow.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT value FROM platform_settings WHERE key = "facebook_credentials"')
        row = cursor.fetchone()
        
        if row and row[0] != '{}':
            creds = json.loads(row[0])
            required_fields = ['app_id', 'app_secret', 'page_id', 'page_access_token']
            missing = [field for field in required_fields if not creds.get(field)]
            
            if missing:
                print(f"❌ Missing fields: {', '.join(missing)}")
                return False
            else:
                print("✅ All required fields present")
                print(f"   App ID: {creds['app_id']}")
                print(f"   Page ID: {creds['page_id']}")
                print(f"   Token: {creds['page_access_token'][:20]}...")
                return True
        else:
            print("❌ No credentials configured")
            return False
            
    except Exception as e:
        print(f"❌ Error testing credentials: {e}")
        return False
    finally:
        conn.close()

def quick_configure():
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
        conn = sqlite3.connect('jyotiflow.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE platform_settings 
            SET value = ?, updated_at = CURRENT_TIMESTAMP 
            WHERE key = 'facebook_credentials'
        ''', (json.dumps(facebook_creds),))
        
        conn.commit()
        conn.close()
        
        print("✅ Placeholder credentials configured!")
        print("🔧 Edit the database or run this script again with real values")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🎯 JyotiFlow Facebook Integration Setup")
    print("=" * 50)
    
    # Check current status
    test_facebook_credentials()
    
    print("\nChoose an option:")
    print("1. Configure real Facebook credentials")
    print("2. Quick setup with placeholder values")
    print("3. Just test current credentials")
    print("4. Exit")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice == "1":
        success = configure_facebook_credentials()
        if success:
            test_facebook_credentials()
            print("\n🎯 Next steps:")
            print("1. Start your backend: uvicorn main:app --reload")
            print("2. Test social media posting")
            print("3. Check logs for success messages")
            
    elif choice == "2":
        quick_configure()
        print("\n⚠️  Remember to replace placeholder values!")
        
    elif choice == "3":
        test_facebook_credentials()
        
    elif choice == "4":
        print("👋 Goodbye!")
        
    else:
        print("❌ Invalid choice")

    print("\n📚 For detailed setup instructions, see:")
    print("   SOCIAL_MEDIA_AUTOMATION_ROOT_CAUSE_ANALYSIS.md")