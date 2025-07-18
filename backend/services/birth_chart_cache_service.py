"""
Birth Chart Caching Service
Handles caching of birth chart data from Prokerala API to avoid repeated API calls
"""

import hashlib
import json
import asyncpg
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class BirthChartCacheService:
    """Service for managing birth chart data caching"""
    
    def __init__(self, db_url: str):
        self.db_url = db_url
        self.cache_duration_days = 365  # Cache for 1 year
        # In-memory cache for guest users
        self.guest_cache = {}
    
    def generate_birth_details_hash(self, birth_details: Dict[str, Any]) -> str:
        """Generate a unique hash for birth details to use as cache key"""
        # Create a normalized string from birth details
        normalized_data = {
            'date': birth_details.get('date', ''),
            'time': birth_details.get('time', ''),
            'location': birth_details.get('location', '').lower().strip(),
            'timezone': birth_details.get('timezone', 'Asia/Colombo')
        }
        
        # Sort keys for consistent hashing
        normalized_string = json.dumps(normalized_data, sort_keys=True)
        
        # Generate SHA256 hash
        return hashlib.sha256(normalized_string.encode()).hexdigest()
    
    async def get_cached_birth_chart(self, user_email: str, birth_details: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get cached birth chart data if available and valid"""
        try:
            birth_hash = self.generate_birth_details_hash(birth_details)
            
            # Handle guest users with in-memory cache
            if user_email.startswith("guest_"):
                cache_key = f"{user_email}_{birth_hash}"
                cached_data = self.guest_cache.get(cache_key)
                
                if cached_data and cached_data['expires_at'] > datetime.now():
                    logger.info(f"✅ Birth chart cache HIT for guest user {user_email}")
                    return cached_data
                else:
                    logger.info(f"❌ Birth chart cache MISS for guest user {user_email}")
                    return None
            
            # Handle registered users with database cache
            import db
            pool = db.get_db_pool()
            if not pool:
                logger.warning("Shared database pool not available for birth chart cache")
                return None
                
            async with pool.acquire() as conn:
                # Check for cached data with matching hash and valid expiry
                cached_data = await conn.fetchrow("""
                    SELECT birth_chart_data, birth_chart_cached_at, birth_chart_expires_at
                    FROM users 
                    WHERE email = $1 
                    AND birth_chart_hash = $2 
                    AND birth_chart_expires_at > NOW()
                    AND birth_chart_data IS NOT NULL
                """, user_email, birth_hash)
            
            if cached_data:
                logger.info(f"✅ Birth chart cache HIT for user {user_email}")
                return {
                    'data': cached_data['birth_chart_data'],
                    'cached_at': cached_data['birth_chart_cached_at'],
                    'expires_at': cached_data['birth_chart_expires_at'],
                    'cache_hit': True
                }
            else:
                logger.info(f"❌ Birth chart cache MISS for user {user_email}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting cached birth chart: {e}")
            return None
    
    async def cache_birth_chart(self, user_email: str, birth_details: Dict[str, Any], chart_data: Dict[str, Any]) -> bool:
        """Cache birth chart data for future use"""
        try:
            birth_hash = self.generate_birth_details_hash(birth_details)
            cached_at = datetime.now()
            expires_at = cached_at + timedelta(days=self.cache_duration_days)
            
            # Handle guest users with in-memory cache
            if user_email.startswith("guest_"):
                cache_key = f"{user_email}_{birth_hash}"
                self.guest_cache[cache_key] = {
                    'data': chart_data,
                    'cached_at': cached_at,
                    'expires_at': expires_at,
                    'cache_hit': True
                }
                logger.info(f"✅ Birth chart cached for guest user {user_email}, expires at {expires_at}")
                return True
            
            # Handle registered users with database cache
            import db
            pool = db.get_db_pool()
            if not pool:
                logger.warning("Database pool not available")
                return None
            
            async with pool.acquire() as conn:
                # Update user record with cached birth chart data
                await conn.execute("""
                    UPDATE users SET 
                        birth_chart_data = $1,
                        birth_chart_hash = $2,
                        birth_chart_cached_at = $3,
                        birth_chart_expires_at = $4,
                        has_free_birth_chart = true,
                        birth_date = $5,
                        birth_time = $6,
                        birth_location = $7
                    WHERE email = $8
                """, 
                json.dumps(chart_data), 
                birth_hash, 
                cached_at, 
                expires_at,
                birth_details.get('date'),
                birth_details.get('time'),
                birth_details.get('location'),
                user_email)
            
            logger.info(f"✅ Birth chart cached for user {user_email}, expires at {expires_at}")
            return True
            
        except Exception as e:
            logger.error(f"Error caching birth chart: {e}")
            return False
    
    async def invalidate_cache(self, user_email: str) -> bool:
        """Invalidate cached birth chart data"""
        try:
            # Handle guest users
            if user_email.startswith("guest_"):
                # Remove all cache entries for this guest user
                keys_to_remove = [key for key in self.guest_cache.keys() if key.startswith(f"{user_email}_")]
                for key in keys_to_remove:
                    del self.guest_cache[key]
                logger.info(f"✅ Birth chart cache invalidated for guest user {user_email}")
                return True
            
            # Handle registered users
            import db
            pool = db.get_db_pool()
            if not pool:
                logger.warning("Database pool not available")
                return None
            
            async with pool.acquire() as conn:
                await conn.execute("""
                    UPDATE users SET 
                        birth_chart_data = NULL,
                        birth_chart_hash = NULL,
                        birth_chart_cached_at = NULL,
                        birth_chart_expires_at = NULL
                    WHERE email = $1
                """, user_email)
            
            logger.info(f"✅ Birth chart cache invalidated for user {user_email}")
            return True
            
        except Exception as e:
            logger.error(f"Error invalidating birth chart cache: {e}")
            return False
    
    async def get_user_birth_chart_status(self, user_email: str) -> Dict[str, Any]:
        """Get user's birth chart cache status"""
        try:
            # Handle guest users
            if user_email.startswith("guest_"):
                # Count guest cache entries
                guest_entries = [key for key in self.guest_cache.keys() if key.startswith(f"{user_email}_")]
                has_cached_data = len(guest_entries) > 0
                
                return {
                    'has_birth_details': has_cached_data,
                    'has_cached_data': has_cached_data,
                    'cache_valid': has_cached_data,
                    'cached_at': datetime.now() if has_cached_data else None,
                    'expires_at': None,
                    'has_free_birth_chart': True,  # Guests always get free charts
                    'user_type': 'guest'
                }
            
            # Handle registered users
            import db
            pool = db.get_db_pool()
            if not pool:
                logger.warning("Database pool not available")
                return None
            
            async with pool.acquire() as conn:
                user_data = await conn.fetchrow("""
                    SELECT 
                        birth_date, birth_time, birth_location,
                        birth_chart_cached_at, birth_chart_expires_at,
                        has_free_birth_chart,
                        (birth_chart_data IS NOT NULL) as has_cached_data,
                        (birth_chart_expires_at > NOW()) as cache_valid
                    FROM users 
                    WHERE email = $1
                """, user_email)
            
            if user_data:
                return {
                    'has_birth_details': bool(user_data['birth_date'] and user_data['birth_time'] and user_data['birth_location']),
                    'has_cached_data': user_data['has_cached_data'],
                    'cache_valid': user_data['cache_valid'],
                    'cached_at': user_data['birth_chart_cached_at'],
                    'expires_at': user_data['birth_chart_expires_at'],
                    'has_free_birth_chart': user_data['has_free_birth_chart'],
                    'user_type': 'registered'
                }
            else:
                return {
                    'has_birth_details': False,
                    'has_cached_data': False,
                    'cache_valid': False,
                    'cached_at': None,
                    'expires_at': None,
                    'has_free_birth_chart': False,
                    'user_type': 'registered'
                }
                
        except Exception as e:
            logger.error(f"Error getting user birth chart status: {e}")
            return {
                'has_birth_details': False,
                'has_cached_data': False,
                'cache_valid': False,
                'cached_at': None,
                'expires_at': None,
                'has_free_birth_chart': False,
                'error': str(e)
            }
    
    async def cleanup_expired_cache(self) -> int:
        """Clean up expired birth chart cache entries"""
        try:
            # Clean up guest cache
            current_time = datetime.now()
            expired_guest_keys = [
                key for key, data in self.guest_cache.items() 
                if data['expires_at'] < current_time
            ]
            
            for key in expired_guest_keys:
                del self.guest_cache[key]
            
            guest_cleaned = len(expired_guest_keys)
            
            # Clean up database cache
            import db
            pool = db.get_db_pool()
            if not pool:
                logger.warning("Database pool not available")
                return None
            
            async with pool.acquire() as conn:
                result = await conn.execute("""
                    UPDATE users SET 
                        birth_chart_data = NULL,
                        birth_chart_hash = NULL,
                        birth_chart_cached_at = NULL,
                        birth_chart_expires_at = NULL
                    WHERE birth_chart_expires_at < NOW()
                    AND birth_chart_data IS NOT NULL
                """)
            
            # Extract number of rows updated using robust parsing
            db_cleaned = self._parse_affected_rows(result)
            total_cleaned = guest_cleaned + db_cleaned
            
            logger.info(f"✅ Cleaned up {total_cleaned} expired birth chart cache entries ({guest_cleaned} guest, {db_cleaned} database)")
            return total_cleaned
            
        except Exception as e:
            logger.error(f"Error cleaning up expired cache: {e}")
            return 0
    
    def _parse_affected_rows(self, command_tag: str) -> int:
        """
        Parse asyncpg command tag to extract the number of affected rows.
        
        Command tag formats:
        - UPDATE: "UPDATE n" where n = affected rows
        - DELETE: "DELETE n" where n = affected rows  
        - INSERT: "INSERT oid n" where n = affected rows
        - SELECT: "SELECT n" where n = selected rows
        
        Args:
            command_tag: Command tag string returned by asyncpg.execute()
            
        Returns:
            Number of affected rows, or 0 if parsing fails
        """
        try:
            parts = command_tag.strip().split()
            
            if not parts:
                logger.warning(f"Empty command tag received: '{command_tag}'")
                return 0
            
            command = parts[0].upper()
            
            if command in ('UPDATE', 'DELETE', 'SELECT'):
                # Format: "COMMAND n"
                if len(parts) >= 2:
                    return int(parts[1])
                else:
                    logger.warning(f"Unexpected {command} command tag format: '{command_tag}'")
                    return 0
                    
            elif command == 'INSERT':
                # Format: "INSERT oid n" where we want n
                if len(parts) >= 3:
                    return int(parts[2])
                else:
                    logger.warning(f"Unexpected INSERT command tag format: '{command_tag}'")
                    return 0
                    
            else:
                # Unknown command type
                logger.warning(f"Unknown command type in tag: '{command_tag}'")
                return 0
                
        except (ValueError, IndexError) as e:
            logger.error(f"Failed to parse command tag '{command_tag}': {e}")
            return 0
    
    async def get_cache_statistics(self) -> Dict[str, Any]:
        """Get birth chart cache statistics"""
        try:
            # Count guest cache entries
            current_time = datetime.now()
            guest_total = len(self.guest_cache)
            guest_valid = len([
                key for key, data in self.guest_cache.items() 
                if data['expires_at'] > current_time
            ])
            
            # Get database cache statistics
            import db
            pool = db.get_db_pool()
            if not pool:
                logger.warning("Database pool not available")
                return None
            
            async with pool.acquire() as conn:
                stats = await conn.fetchrow("""
                    SELECT 
                        COUNT(*) as total_users,
                        COUNT(birth_chart_data) as users_with_cached_data,
                        COUNT(CASE WHEN birth_chart_expires_at > NOW() THEN 1 END) as users_with_valid_cache,
                        COUNT(CASE WHEN has_free_birth_chart = true THEN 1 END) as users_with_free_chart,
                        AVG(EXTRACT(EPOCH FROM (NOW() - birth_chart_cached_at))/86400) as avg_cache_age_days
                    FROM users
                """)
            
            return {
                'total_users': stats['total_users'],
                'users_with_cached_data': stats['users_with_cached_data'],
                'users_with_valid_cache': stats['users_with_valid_cache'],
                'users_with_free_chart': stats['users_with_free_chart'],
                'cache_hit_ratio': stats['users_with_valid_cache'] / max(stats['total_users'], 1) * 100,
                'avg_cache_age_days': float(stats['avg_cache_age_days'] or 0),
                'guest_cache_total': guest_total,
                'guest_cache_valid': guest_valid
            }
            
        except Exception as e:
            logger.error(f"Error getting cache statistics: {e}")
            return {
                'error': str(e)
            }