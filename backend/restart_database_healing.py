#!/usr/bin/env python3
"""
Database Self-Healing System Restart Script
Restarts the DatabaseSelfHealingOrchestrator that was found to be in 'stopped' state
"""

import asyncio
import asyncpg
import os
import sys
import logging

# Add current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

async def restart_database_healing():
    """Restart the DatabaseSelfHealingOrchestrator"""
    try:
        logger.info("🔄 Attempting to restart Database Self-Healing System...")
        
        # Import the orchestrator
        from database_self_healing_system import DatabaseSelfHealingOrchestrator
        
        # Create a new orchestrator instance
        orchestrator = DatabaseSelfHealingOrchestrator()
        
        # Check current status
        current_status = await orchestrator.get_system_status()
        logger.info(f"📊 Current system status: {current_status}")
        
        # Start the orchestrator
        logger.info("🚀 Starting DatabaseSelfHealingOrchestrator...")
        await orchestrator.start()
        
        # Verify it's running
        new_status = await orchestrator.get_system_status()
        logger.info(f"✅ New system status: {new_status}")
        
        if new_status.get("status") == "running":
            logger.info("🎉 Database Self-Healing System successfully restarted!")
            return True
        else:
            logger.error("❌ Failed to restart Database Self-Healing System")
            return False
            
    except ImportError as e:
        logger.error(f"❌ Failed to import DatabaseSelfHealingOrchestrator: {e}")
        logger.error("💡 This might indicate the module is not available in the current environment")
        return False
    except Exception as e:
        logger.error(f"❌ Error restarting Database Self-Healing System: {e}")
        return False

async def verify_database_connection():
    """Verify we can connect to the database"""
    try:
        logger.info("🔍 Verifying database connection...")
        if not DATABASE_URL:
            logger.error("❌ DATABASE_URL environment variable not set")
            return False
            
        conn = await asyncpg.connect(DATABASE_URL)
        await conn.close()
        logger.info("✅ Database connection verified")
        return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False

async def main():
    """Main execution function"""
    logger.info("🎯 Starting Database Self-Healing System Restart...")
    
    # Step 1: Verify database connection
    if not await verify_database_connection():
        logger.error("❌ Cannot proceed without database connection")
        return False
    
    # Step 2: Restart the healing system
    success = await restart_database_healing()
    
    if success:
        logger.info("🎉 Database Self-Healing System restart completed successfully!")
    else:
        logger.error("❌ Database Self-Healing System restart failed")
    
    return success

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        if result:
            logger.info("✅ Script completed successfully")
            sys.exit(0)
        else:
            logger.error("❌ Script completed with errors")
            sys.exit(1)
    except KeyboardInterrupt:
        logger.info("🛑 Script interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"💥 Unexpected error: {e}")
        sys.exit(1)