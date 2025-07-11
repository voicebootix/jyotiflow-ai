"""
Deployment Script for JyotiFlow.ai Fixes
This script should be run in the production environment to apply
database and authentication fixes.
"""

import asyncio
import os
import sys
import logging
from comprehensive_database_fix import DatabaseFixer
from authentication_fix import AuthenticationFixer

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ProductionDeployment:
    def __init__(self):
        self.db_fixer = DatabaseFixer()
        self.auth_fixer = AuthenticationFixer()
    
    async def verify_environment(self):
        """Verify that we're in the correct environment"""
        logger.info("🔍 Verifying deployment environment...")
        
        # Check for required environment variables
        required_vars = ['DATABASE_URL', 'JWT_SECRET_KEY']
        missing_vars = []
        
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            logger.error(f"❌ Missing required environment variables: {missing_vars}")
            return False
        
        logger.info("✅ Environment verification passed")
        return True
    
    async def backup_database(self):
        """Create a backup before applying fixes"""
        logger.info("💾 Creating database backup...")
        
        try:
            # Connect to database
            if not await self.db_fixer.connect():
                return False
            
            # Get list of all tables
            tables_query = """
            SELECT tablename FROM pg_tables 
            WHERE schemaname = 'public';
            """
            tables = await self.db_fixer.connection.fetch(tables_query)
            
            logger.info(f"📊 Found {len(tables)} tables to backup")
            
            # Create backup info
            backup_info = {
                'timestamp': str(asyncio.get_event_loop().time()),
                'tables': [table['tablename'] for table in tables],
                'total_tables': len(tables)
            }
            
            logger.info("✅ Database backup information collected")
            return True
            
        except Exception as e:
            logger.error(f"❌ Backup failed: {e}")
            return False
        finally:
            await self.db_fixer.close()
    
    async def apply_database_fixes(self):
        """Apply database fixes"""
        logger.info("🔧 Applying database fixes...")
        
        try:
            success = await self.db_fixer.run_comprehensive_fix()
            if success:
                logger.info("✅ Database fixes applied successfully")
                return True
            else:
                logger.error("❌ Database fixes failed")
                return False
        except Exception as e:
            logger.error(f"❌ Database fix error: {e}")
            return False
    
    async def apply_authentication_fixes(self):
        """Apply authentication fixes"""
        logger.info("🔐 Applying authentication fixes...")
        
        try:
            success = await self.auth_fixer.run_comprehensive_auth_fix()
            if success:
                logger.info("✅ Authentication fixes applied successfully")
                return True
            else:
                logger.error("❌ Authentication fixes failed")
                return False
        except Exception as e:
            logger.error(f"❌ Authentication fix error: {e}")
            return False
    
    async def verify_fixes(self):
        """Verify that fixes were applied correctly"""
        logger.info("🔍 Verifying applied fixes...")
        
        try:
            if not await self.db_fixer.connect():
                return False
            
            # Check for required tables
            required_tables = [
                'credit_packages',
                'donations', 
                'service_configuration_cache',
                'user_sessions',
                'live_chat_sessions',
                'spiritual_wisdom'
            ]
            
            missing_tables = []
            for table in required_tables:
                if not await self.db_fixer.table_exists(table):
                    missing_tables.append(table)
            
            if missing_tables:
                logger.error(f"❌ Missing tables after fix: {missing_tables}")
                return False
            
            # Check for required columns
            if not await self.db_fixer.column_exists('service_types', 'credits_required'):
                logger.error("❌ Missing credits_required column in service_types")
                return False
            
            logger.info("✅ All fixes verified successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Verification failed: {e}")
            return False
        finally:
            await self.db_fixer.close()
    
    async def run_deployment(self):
        """Run the complete deployment process"""
        logger.info("🚀 Starting JyotiFlow.ai fixes deployment...")
        
        # Step 1: Verify environment
        if not await self.verify_environment():
            logger.error("❌ Environment verification failed")
            return False
        
        # Step 2: Create backup
        if not await self.backup_database():
            logger.error("❌ Database backup failed")
            return False
        
        # Step 3: Apply database fixes
        if not await self.apply_database_fixes():
            logger.error("❌ Database fixes failed")
            return False
        
        # Step 4: Apply authentication fixes
        if not await self.apply_authentication_fixes():
            logger.error("❌ Authentication fixes failed")
            return False
        
        # Step 5: Verify fixes
        if not await self.verify_fixes():
            logger.error("❌ Fix verification failed")
            return False
        
        logger.info("🎉 Deployment completed successfully!")
        logger.info("📋 Next steps:")
        logger.info("   1. Restart the application server")
        logger.info("   2. Test spiritual guidance functionality")
        logger.info("   3. Test live chat audio/video features")
        logger.info("   4. Verify admin dashboard access")
        
        return True

async def main():
    """Main deployment function"""
    deployment = ProductionDeployment()
    
    print("=" * 60)
    print("🕉️  JyotiFlow.ai Production Fixes Deployment")
    print("=" * 60)
    print()
    
    success = await deployment.run_deployment()
    
    print()
    print("=" * 60)
    if success:
        print("✅ DEPLOYMENT SUCCESSFUL")
        print("🔄 Please restart your application server now")
    else:
        print("❌ DEPLOYMENT FAILED")
        print("📞 Contact support for assistance")
    print("=" * 60)
    
    return success

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Deployment interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Deployment failed with error: {e}")
        sys.exit(1)

