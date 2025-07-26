#!/usr/bin/env python3
"""
Restart Database Self-Healing System
The system is currently stopped and needs to be restarted
"""

import asyncio
import asyncpg
import os
import sys
import logging

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database_self_healing_system import DatabaseSelfHealingOrchestrator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")

async def restart_healing_system():
    """Restart the database self-healing system"""
    logger.info("🔄 Restarting Database Self-Healing System...")
    
    if not DATABASE_URL:
        logger.error("❌ DATABASE_URL not found")
        return False
    
    try:
        # Initialize the orchestrator
        orchestrator = DatabaseSelfHealingOrchestrator()
        
        # Start the monitoring system
        logger.info("⚡ Starting database healing orchestrator...")
        await orchestrator.start()
        
        # Verify it's running
        status = await orchestrator.get_health_status()
        logger.info(f"✅ Database healing system status: {status}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to restart healing system: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(restart_healing_system())