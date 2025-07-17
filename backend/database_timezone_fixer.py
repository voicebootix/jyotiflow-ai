"""
Database Timezone Fixer - Comprehensive Fix for All Timezone Issues
Addresses all datetime.now(timezone.utc) usage in database queries
Enhanced for JyotiFlow.ai Spiritual Services Platform
"""

from datetime import datetime, timezone
from typing import Any, Union
import logging

logger = logging.getLogger(__name__)

def normalize_datetime_for_db(dt: Union[datetime, Any]) -> datetime:
    """
    Normalize datetime for database storage to prevent timezone issues.
    
    IMPORTANT: This function normalizes STORAGE timestamps only.
    Birth chart calculations maintain separate timezone handling for accuracy.
    
    Converts timezone-aware datetime to timezone-naive for PostgreSQL TIMESTAMP columns.
    This prevents the "can't subtract offset-naive and offset-aware datetimes" error.
    
    Args:
        dt: datetime object (timezone-aware or naive) or other value
        
    Returns:
        timezone-naive datetime object or original value
    """
    if isinstance(dt, datetime):
        if dt.tzinfo is not None:
            # Convert timezone-aware to UTC and remove timezone info
            utc_dt = dt.utctimetuple()
            return datetime(*utc_dt[:6])
        else:
            # Already timezone-naive
            return dt
    else:
        # Not a datetime, return as-is
        return dt

def safe_utc_now() -> datetime:
    """
    Get current UTC time as timezone-naive datetime for database storage.
    
    SPIRITUAL SERVICE NOTE: This is for system timestamps (sessions, logs, etc.)
    NOT for birth chart calculations which require precise timezone handling.
    
    Returns:
        timezone-naive datetime in UTC
    """
    return datetime.now(timezone.utc).replace(tzinfo=None)

def safe_utc_now_with_tz() -> datetime:
    """
    Get current UTC time as timezone-aware datetime for application use.
    
    Returns:
        timezone-aware datetime in UTC
    """
    return datetime.now(timezone.utc)

def prepare_datetime_params(*args) -> tuple:
    """
    Prepare multiple datetime parameters for database execution.
    
    CRITICAL FOR SPIRITUAL SERVICES: Ensures session timestamps, follow-up scheduling,
    and system events are stored consistently without timezone conflicts.
    
    Args:
        *args: Variable number of arguments that may include datetime objects
        
    Returns:
        Tuple of normalized arguments safe for database usage
    """
    return tuple(normalize_datetime_for_db(arg) for arg in args)

def log_timezone_safety_check(context: str):
    """
    Log timezone safety information for debugging spiritual service issues.
    
    Args:
        context: Description of where this is being used
    """
    logger.info(f"🕐 Timezone safety check: {context} - Using timezone-naive storage")
    logger.debug(f"Birth chart calculations remain timezone-aware for accuracy")