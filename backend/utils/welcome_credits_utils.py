"""
Shared utility for dynamic welcome credits management
Eliminates code duplication and fixes database column mismatch issues
"""

import logging
from typing import Optional
from db import db_manager

logger = logging.getLogger(__name__)

async def get_dynamic_welcome_credits() -> int:
    """
    Get dynamic welcome credits from database configuration
    Returns default of 20 credits if not configured
    """
    try:
        conn = await db_manager.get_connection()
        try:
            # FIXED: Use correct column names 'key' and 'value' instead of 'config_key' and 'config_value'
            result = await conn.fetchrow("""
                SELECT value FROM pricing_config 
                WHERE key = 'welcome_credits' 
                AND is_active = true
            """)
            
            if result and result['value']:
                try:
                    credits = int(result['value'])
                    logger.info(f"Retrieved dynamic welcome credits: {credits}")
                    return credits
                except (ValueError, TypeError):
                    logger.warning(f"Invalid welcome credits value in database: {result['value']}")
            
            # Default to 20 credits (consistent with other functionalities)
            logger.info("Using default welcome credits: 20")
            return 20
            
        finally:
            await db_manager.release_connection(conn)
            
    except Exception as e:
        logger.error(f"Error retrieving dynamic welcome credits: {e}")
        # Return consistent default of 20 credits
        return 20

async def set_dynamic_welcome_credits(credits: int) -> bool:
    """
    Set dynamic welcome credits in database configuration
    """
    try:
        conn = await db_manager.get_connection()
        try:
            # FIXED: Use correct column names and proper upsert logic
            await conn.execute("""
                INSERT INTO pricing_config (key, value, is_active, created_at, updated_at)
                VALUES ('welcome_credits', $1, true, NOW(), NOW())
                ON CONFLICT (key) 
                DO UPDATE SET 
                    value = EXCLUDED.value,
                    updated_at = NOW()
            """, str(credits))
            
            logger.info(f"Successfully set dynamic welcome credits to: {credits}")
            return True
            
        finally:
            await db_manager.release_connection(conn)
            
    except Exception as e:
        logger.error(f"Error setting dynamic welcome credits: {e}")
        return False

async def validate_welcome_credits(credits: int) -> bool:
    """
    Validate welcome credits value
    """
    return isinstance(credits, int) and 0 <= credits <= 1000