"""
🔧 Platform Credentials Initialization for Social Media Automation
Adds Facebook and other social media platform credentials to the database
"""

import os
import json
import logging
import asyncpg
from datetime import datetime, timezone

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PlatformCredentialsInitializer:
    """Handles platform credentials initialization"""
    
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL", "postgresql://jyotiflow_db_user:em0MmaZmvPzASryvzLHpR5g5rRZTQqpw@dpg-d12ohqemcj7s73fjbqtg-a/jyotiflow_db")
        
    async def initialize_facebook_credentials(self, facebook_config=None):
        """Initialize Facebook credentials in the database"""
        logger.info("🔧 Initializing Facebook credentials...")
        
        if facebook_config is None:
            # Use environment variables if no config provided
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
        
        try:
            conn = await asyncpg.connect(self.database_url)
            
            # Update Facebook credentials
            await conn.execute("""
                UPDATE platform_settings 
                SET value = $1, updated_at = CURRENT_TIMESTAMP 
                WHERE key = 'facebook_credentials'
            """, json.dumps(facebook_config))
            
            await conn.close()
            
            if facebook_config["status"] == "configured":
                logger.info("✅ Facebook credentials configured from environment variables")
                logger.info(f"   App ID: {facebook_config['app_id']}")
                logger.info(f"   Page ID: {facebook_config['page_id']}")
            else:
                logger.info("⚠️ Facebook credentials placeholders created - configure in admin dashboard")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Facebook credentials: {e}")
            return False
    
    async def initialize_all_platform_credentials(self):
        """Initialize all platform credentials"""
        logger.info("🚀 Initializing all platform credentials...")
        
        try:
            conn = await asyncpg.connect(self.database_url)
            
            # Platform credential templates
            platform_configs = {
                "instagram_credentials": {
                    "app_id": os.getenv("INSTAGRAM_APP_ID", ""),
                    "access_token": os.getenv("INSTAGRAM_ACCESS_TOKEN", ""),
                    "configured_at": datetime.now(timezone.utc).isoformat(),
                    "status": "configured" if os.getenv("INSTAGRAM_ACCESS_TOKEN") else "pending"
                },
                "youtube_credentials": {
                    "api_key": os.getenv("YOUTUBE_API_KEY", ""),
                    "channel_id": os.getenv("YOUTUBE_CHANNEL_ID", ""),
                    "oauth_credentials": os.getenv("YOUTUBE_OAUTH_CREDENTIALS", ""),
                    "configured_at": datetime.now(timezone.utc).isoformat(),
                    "status": "configured" if os.getenv("YOUTUBE_API_KEY") else "pending"
                },
                "twitter_credentials": {
                    "api_key": os.getenv("TWITTER_API_KEY", ""),
                    "api_secret": os.getenv("TWITTER_API_SECRET", ""),
                    "access_token": os.getenv("TWITTER_ACCESS_TOKEN", ""),
                    "access_token_secret": os.getenv("TWITTER_ACCESS_TOKEN_SECRET", ""),
                    "bearer_token": os.getenv("TWITTER_BEARER_TOKEN", ""),
                    "configured_at": datetime.now(timezone.utc).isoformat(),
                    "status": "configured" if os.getenv("TWITTER_API_KEY") else "pending"
                },
                "tiktok_credentials": {
                    "client_key": os.getenv("TIKTOK_CLIENT_KEY", ""),
                    "client_secret": os.getenv("TIKTOK_CLIENT_SECRET", ""),
                    "access_token": os.getenv("TIKTOK_ACCESS_TOKEN", ""),
                    "configured_at": datetime.now(timezone.utc).isoformat(),
                    "status": "configured" if os.getenv("TIKTOK_CLIENT_KEY") else "pending"
                },
                "ai_model_config": {
                    "openai_api_key": os.getenv("OPENAI_API_KEY", ""),
                    "model": "gpt-4",
                    "max_tokens": 1000,
                    "temperature": 0.7,
                    "configured_at": datetime.now(timezone.utc).isoformat(),
                    "status": "configured" if os.getenv("OPENAI_API_KEY") else "pending"
                }
            }
            
            # Update all platform settings
            for platform_key, config in platform_configs.items():
                await conn.execute("""
                    UPDATE platform_settings 
                    SET value = $1, updated_at = CURRENT_TIMESTAMP 
                    WHERE key = $2
                """, (json.dumps(config), platform_key))
                
                status_emoji = "✅" if config["status"] == "configured" else "⚠️"
                logger.info(f"{status_emoji} {platform_key}: {config['status']}")
            
            await conn.close()
            
            # Also initialize Facebook credentials
            await self.initialize_facebook_credentials()
            
            logger.info("🎊 All platform credentials initialized!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize platform credentials: {e}")
            return False
    
    async def verify_credentials(self):
        """Verify that all credentials are properly configured"""
        logger.info("🔍 Verifying platform credentials...")
        
        try:
            conn = await asyncpg.connect(self.database_url)
            
            # Get all platform settings
            rows = await conn.fetch("SELECT key, value FROM platform_settings ORDER BY key")
            
            configured_count = 0
            total_count = 0
            
            for row in rows:
                if row['key'].endswith('_credentials') or row['key'] == 'ai_model_config':
                    total_count += 1
                    config = row['value']
                    status = config.get('status', 'unknown')
                    
                    if status == 'configured':
                        configured_count += 1
                        logger.info(f"✅ {row['key']}: Ready for use")
                    else:
                        logger.info(f"⚠️ {row['key']}: Needs configuration")
            
            await conn.close()
            
            logger.info(f"📊 Platform Status: {configured_count}/{total_count} configured")
            
            if configured_count > 0:
                logger.info("🚀 You can start using social media automation!")
            else:
                logger.info("📝 Configure your platform credentials to start automation")
            
            return configured_count, total_count
            
        except Exception as e:
            logger.error(f"❌ Failed to verify credentials: {e}")
            return 0, 0

# Global instance
platform_initializer = PlatformCredentialsInitializer()

async def initialize_platform_credentials():
    """Main function to initialize platform credentials"""
    return await platform_initializer.initialize_all_platform_credentials()

async def verify_platform_credentials():
    """Main function to verify platform credentials"""
    return await platform_initializer.verify_credentials()

if __name__ == "__main__":
    import asyncio
    
    async def main():
        print("🔧 JyotiFlow Platform Credentials Initializer")
        print("=" * 50)
        
        # Initialize credentials
        success = await initialize_platform_credentials()
        
        if success:
            # Verify configuration
            await verify_platform_credentials()
            
            print("\n🎯 Next Steps:")
            print("1. Set your environment variables for any pending platforms")
            print("2. Or configure credentials via the admin dashboard")
            print("3. Run your social media automation!")
        else:
            print("❌ Initialization failed - check your database connection")
    
    asyncio.run(main())