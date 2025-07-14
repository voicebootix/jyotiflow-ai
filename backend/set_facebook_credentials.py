"""
🔧 Quick Facebook Credentials Setup
Run this after running the migration script to add your Facebook credentials
"""

import os
import json
import asyncio
import asyncpg
from datetime import datetime, timezone

async def set_facebook_credentials():
    """Set Facebook credentials in the database"""
    print("🔧 Setting up Facebook credentials...")
    
    # Get Facebook credentials from environment variables
    facebook_config = {
        "app_id": os.getenv("FACEBOOK_APP_ID", ""),
        "app_secret": os.getenv("FACEBOOK_APP_SECRET", ""),
        "page_id": os.getenv("FACEBOOK_PAGE_ID", ""),
        "page_access_token": os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN", ""),
        "configured_at": datetime.now(timezone.utc).isoformat(),
        "status": "configured" if all([
            os.getenv("FACEBOOK_APP_ID"),
            os.getenv("FACEBOOK_APP_SECRET"),
            os.getenv("FACEBOOK_PAGE_ID"),
            os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN")
        ]) else "pending"
    }
    
    # Connect to database
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL environment variable not set")
        return False
    
    try:
        conn = await asyncpg.connect(database_url)
        
        # Update Facebook credentials
        await conn.execute("""
            UPDATE platform_settings 
            SET value = $1, updated_at = CURRENT_TIMESTAMP 
            WHERE key = 'facebook_credentials'
        """, json.dumps(facebook_config))
        
        # Verify the update
        row = await conn.fetchrow("""
            SELECT value FROM platform_settings 
            WHERE key = 'facebook_credentials'
        """)
        
        await conn.close()
        
        if facebook_config["status"] == "configured":
            print("✅ Facebook credentials configured successfully!")
            print(f"   App ID: {facebook_config['app_id']}")
            print(f"   Page ID: {facebook_config['page_id']}")
            print("🚀 Your social media automation is ready to use!")
        else:
            print("⚠️ Facebook credentials created but not fully configured")
            print("   Please set these environment variables:")
            print("   - FACEBOOK_APP_ID")
            print("   - FACEBOOK_APP_SECRET")
            print("   - FACEBOOK_PAGE_ID")
            print("   - FACEBOOK_PAGE_ACCESS_TOKEN")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to set Facebook credentials: {e}")
        return False

async def verify_social_media_setup():
    """Verify that social media automation is ready"""
    print("\n🔍 Verifying social media automation setup...")
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL not set")
        return False
    
    try:
        conn = await asyncpg.connect(database_url)
        
        # Check if platform_settings table exists
        table_exists = await conn.fetchrow("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'platform_settings'
            )
        """)
        
        if not table_exists[0]:
            print("❌ platform_settings table not found")
            print("   Run the migration script first: SOCIAL_MEDIA_MIGRATION_SCRIPT.sql")
            return False
        
        # Check credentials
        rows = await conn.fetch("""
            SELECT key, value FROM platform_settings 
            WHERE key ILIKE '%_credentials' OR key = 'ai_model_config'
            ORDER BY key
        """)
        
        configured_count = 0
        for row in rows:
            config = row['value']
            status = config.get('status', 'pending')
            
            if status == 'configured':
                configured_count += 1
                print(f"✅ {row['key']}: Ready")
            else:
                print(f"⚠️ {row['key']}: Needs configuration")
        
        await conn.close()
        
        print(f"\n📊 Status: {configured_count}/{len(rows)} platforms configured")
        
        if configured_count > 0:
            print("🎊 Social media automation is ready to use!")
        else:
            print("📝 Configure your platform credentials to get started")
        
        return True
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

if __name__ == "__main__":
    async def main():
        print("🚀 JyotiFlow Facebook Credentials Setup")
        print("=" * 40)
        
        # Set Facebook credentials
        success = await set_facebook_credentials()
        
        if success:
            # Verify the setup
            await verify_social_media_setup()
        
        print("\n🎯 Next steps:")
        print("1. Make sure your environment variables are set")
        print("2. Test your social media automation endpoints")
        print("3. Start generating content!")
    
    asyncio.run(main())