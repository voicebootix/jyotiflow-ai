#!/usr/bin/env python3
"""
Database Initialization Fix for JyotiFlow Platform
Ensures the existing database initialization system works properly
"""

import asyncio
import os
import logging
from init_database import JyotiFlowDatabaseInitializer

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def fix_database_initialization():
    """Ensure database initialization works properly"""
    try:
        logger.info("🔧 Fixing database initialization...")
        
        # Get database URL
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            logger.error("❌ DATABASE_URL environment variable not set")
            return False
        
        # Initialize database using existing system
        initializer = JyotiFlowDatabaseInitializer()
        success = await initializer.initialize_database()
        
        if success:
            logger.info("✅ Database initialization fixed successfully")
            return True
        else:
            logger.error("❌ Database initialization fix failed")
            return False
            
    except Exception as e:
        logger.error(f"💥 Database initialization fix error: {str(e)}")
        return False

if __name__ == "__main__":
    # Run database initialization fix
    success = asyncio.run(fix_database_initialization())
    
    if success:
        logger.info("🎯 Database initialization fix completed successfully")
    else:
        logger.error("💥 Database initialization fix failed")

