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
            
            conn = await asyncpg.connect(self.db_url)
            
            # Check for cached data with matching hash and valid expiry
            cached_data = await conn.fetchrow("""
                SELECT birth_chart_data, birth_chart_cached_at, birth_chart_expires_at
                FROM users 
                WHERE email = $1 
                AND birth_chart_hash = $2 
                AND birth_chart_expires_at > NOW()
                AND birth_chart_data IS NOT NULL
            """, user_email, birth_hash)
            
            await conn.close()
            
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
            
            conn = await asyncpg.connect(self.db_url)
            
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
            
            await conn.close()
            
            logger.info(f"✅ Birth chart cached for user {user_email}, expires at {expires_at}")
            return True
            
        except Exception as e:
            logger.error(f"Error caching birth chart: {e}")
            return False
    
    async def invalidate_cache(self, user_email: str) -> bool:
        """Invalidate cached birth chart data"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            await conn.execute("""
                UPDATE users SET 
                    birth_chart_data = NULL,
                    birth_chart_hash = NULL,
                    birth_chart_cached_at = NULL,
                    birth_chart_expires_at = NULL
                WHERE email = $1
            """, user_email)
            
            await conn.close()
            
            logger.info(f"✅ Birth chart cache invalidated for user {user_email}")
            return True
            
        except Exception as e:
            logger.error(f"Error invalidating birth chart cache: {e}")
            return False
    
    async def get_user_birth_chart_status(self, user_email: str) -> Dict[str, Any]:
        """Get user's birth chart cache status"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
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
            
            await conn.close()
            
            if user_data:
                return {
                    'has_birth_details': bool(user_data['birth_date'] and user_data['birth_time'] and user_data['birth_location']),
                    'has_cached_data': user_data['has_cached_data'],
                    'cache_valid': user_data['cache_valid'],
                    'cached_at': user_data['birth_chart_cached_at'],
                    'expires_at': user_data['birth_chart_expires_at'],
                    'has_free_birth_chart': user_data['has_free_birth_chart']
                }
            else:
                return {
                    'has_birth_details': False,
                    'has_cached_data': False,
                    'cache_valid': False,
                    'cached_at': None,
                    'expires_at': None,
                    'has_free_birth_chart': False
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
            conn = await asyncpg.connect(self.db_url)
            
            result = await conn.execute("""
                UPDATE users SET 
                    birth_chart_data = NULL,
                    birth_chart_hash = NULL,
                    birth_chart_cached_at = NULL,
                    birth_chart_expires_at = NULL
                WHERE birth_chart_expires_at < NOW()
                AND birth_chart_data IS NOT NULL
            """)
            
            await conn.close()
            
            # Extract number of rows updated
            rows_cleaned = int(result.split()[-1])
            logger.info(f"✅ Cleaned up {rows_cleaned} expired birth chart cache entries")
            return rows_cleaned
            
        except Exception as e:
            logger.error(f"Error cleaning up expired cache: {e}")
            return 0
    
    async def get_cache_statistics(self) -> Dict[str, Any]:
        """Get birth chart cache statistics"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            stats = await conn.fetchrow("""
                SELECT 
                    COUNT(*) as total_users,
                    COUNT(birth_chart_data) as users_with_cached_data,
                    COUNT(CASE WHEN birth_chart_expires_at > NOW() THEN 1 END) as users_with_valid_cache,
                    COUNT(CASE WHEN has_free_birth_chart = true THEN 1 END) as users_with_free_chart,
                    AVG(EXTRACT(EPOCH FROM (NOW() - birth_chart_cached_at))/86400) as avg_cache_age_days
                FROM users
            """)
            
            await conn.close()
            
            return {
                'total_users': stats['total_users'],
                'users_with_cached_data': stats['users_with_cached_data'],
                'users_with_valid_cache': stats['users_with_valid_cache'],
                'users_with_free_chart': stats['users_with_free_chart'],
                'cache_hit_ratio': stats['users_with_valid_cache'] / max(stats['total_users'], 1) * 100,
                'avg_cache_age_days': float(stats['avg_cache_age_days'] or 0)
            }
            
        except Exception as e:
            logger.error(f"Error getting cache statistics: {e}")
            return {
                'error': str(e)
            }