import httpx
import time
import os
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import asyncpg

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("prokerala_smart_service")

class ProkeralaSmartService:
    """
    Smart Prokerala service with cost-aware pricing
    Uses maximum cost + margin approach with cache optimization
    """
    
    def __init__(self, db_pool: asyncpg.Pool):
        self.db_pool = db_pool
        self.client_id = os.getenv("PROKERALA_CLIENT_ID")
        self.client_secret = os.getenv("PROKERALA_CLIENT_SECRET")
        self.base_url = "https://api.prokerala.com/v2"
        self.token = None
        self.token_expiry = 0
        
    async def _get_token(self) -> str:
        """Get or refresh OAuth token"""
        if self.token and time.time() < self.token_expiry:
            return self.token
            
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.prokerala.com/token",
                data={
                    "grant_type": "client_credentials",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data["access_token"]
                self.token_expiry = time.time() + data.get("expires_in", 3600) - 60
                return self.token
            else:
                raise Exception(f"Token fetch failed: {response.text}")
    
    async def calculate_service_cost(self, service_id: int, user_id: Optional[str] = None) -> Dict:
        """
        Calculate smart cost for a service based on cache availability
        This implements Option B: Auto-pricing based on cache
        """
        async with self.db_pool.acquire() as conn:
            # Get service configuration
            service = await conn.fetchrow("""
                SELECT name, prokerala_endpoints, estimated_api_calls, cache_effectiveness
                FROM service_types WHERE id = $1
            """, service_id)
            
            if not service:
                raise ValueError(f"Service {service_id} not found")
            
            # Get current cost configuration
            cost_config = await conn.fetchrow("""
                SELECT max_cost_per_call, margin_percentage, cache_discount_enabled
                FROM prokerala_cost_config
                ORDER BY last_updated DESC LIMIT 1
            """)
            
            max_cost = float(cost_config['max_cost_per_call'])
            margin = float(cost_config['margin_percentage'])
            cache_enabled = cost_config['cache_discount_enabled']
            
            # Calculate base cost
            num_endpoints = len(service['prokerala_endpoints']) if service['prokerala_endpoints'] else 1
            base_api_cost = max_cost * num_endpoints
            
            # Check cache availability for this user
            cache_discount = 0
            if cache_enabled and user_id:
                cache_rate = await self._get_user_cache_rate(user_id, service_id)
                cache_discount = cache_rate / 100.0
                
                # Track cache analytics
                await self._update_cache_analytics(service_id, cache_rate)
            
            # Calculate costs
            effective_api_cost = base_api_cost * (1 - cache_discount)
            
            # Add other service costs from configuration
            from config.prokerala_costs import get_other_costs
            other_costs = get_other_costs()
            
            # Add voice/video costs if enabled
            from config.prokerala_costs import get_voice_video_costs
            voice_video_costs = get_voice_video_costs()
            
            service_features = await conn.fetchrow("""
                SELECT avatar_video_enabled, live_chat_enabled, 
                       COALESCE(voice_enabled, false) as voice_enabled,
                       COALESCE(video_enabled, false) as video_enabled
                FROM service_types WHERE id = $1
            """, service_id)
            
            if service_features and service_features['voice_enabled']:
                other_costs['elevenlabs_voice'] = voice_video_costs.get('voice_processing', 0.05)
            if service_features and service_features['video_enabled']:
                other_costs['d_id_avatar'] = voice_video_costs.get('video_processing', 0.08)
            if service_features and service_features['live_chat_enabled']:
                other_costs['agora_live'] = voice_video_costs.get('live_chat_processing', 0.15)
            
            total_other_costs = sum(other_costs.values())
            total_cost = effective_api_cost + total_other_costs
            
            # Apply margin
            total_with_margin = total_cost * (1 + margin / 100)
            
            # Convert to credits (1 credit = $0.10)
            suggested_credits = int(round(total_with_margin / 0.10))
            
            # Get value suggestions
            suggestions = await self._get_value_suggestions(service['name'], num_endpoints)
            
            return {
                "service_id": service_id,
                "service_name": service['name'],
                "cost_breakdown": {
                    "prokerala_base_cost": base_api_cost,
                    "cache_discount_rate": cache_discount * 100,
                    "prokerala_effective_cost": effective_api_cost,
                    "other_costs": other_costs,
                    "total_cost": total_cost,
                    "margin_percentage": margin,
                    "total_with_margin": total_with_margin
                },
                "pricing": {
                    "current_credits": await self._get_current_credits(service_id),
                    "suggested_credits": suggested_credits,
                    "savings_from_cache": (base_api_cost - effective_api_cost) / 0.10,
                    "user_message": self._get_user_message(cache_discount)
                },
                "suggestions": suggestions
            }
    
    async def _get_user_cache_rate(self, user_id: str, service_id: int) -> float:
        """
        Calculate cache availability for specific user and service
        Based on their recent usage patterns
        """
        async with self.db_pool.acquire() as conn:
            # Get user email from user_id and service name from service_id
            user_data = await conn.fetchrow("""
                SELECT email FROM users WHERE id = $1
            """, user_id)
            
            if not user_data:
                return 0.0  # User not found
            
            service_data = await conn.fetchrow("""
                SELECT name FROM service_types WHERE id = $1
            """, service_id)
            
            if not service_data:
                return 0.0  # Service not found
            
            # Check if user has recent sessions for this service
            recent_session = await conn.fetchrow("""
                SELECT created_at, prokerala_cache_used
                FROM sessions 
                WHERE user_email = $1 AND service_type = $2 
                AND created_at > NOW() - INTERVAL '30 days'
                ORDER BY created_at DESC LIMIT 1
            """, user_data['email'], service_data['name'])
            
            if not recent_session:
                return 0.0  # No cache available
            
            # Calculate cache effectiveness based on time since last session
            days_since = (datetime.now() - recent_session['created_at']).days
            
            if days_since <= 1:
                return 95.0  # Daily horoscope still fresh
            elif days_since <= 7:
                return 80.0  # Most data still valid
            elif days_since <= 30:
                return 50.0  # Some data still cached
            else:
                return 20.0  # Minimal cache benefit
    
    async def _update_cache_analytics(self, service_id: int, cache_rate: float):
        """Track cache effectiveness for analytics"""
        async with self.db_pool.acquire() as conn:
            is_cache_hit = cache_rate > 50
            
            await conn.execute("""
                INSERT INTO cache_analytics (service_type_id, date, total_requests, cache_hits)
                VALUES ($1, CURRENT_DATE, 1, $2)
                ON CONFLICT (service_type_id, date) 
                DO UPDATE SET 
                    total_requests = cache_analytics.total_requests + 1,
                    cache_hits = cache_analytics.cache_hits + $2
            """, service_id, 1 if is_cache_hit else 0)
    
    async def _get_current_credits(self, service_id: int) -> int:
        """Get current credit requirement for service"""
        async with self.db_pool.acquire() as conn:
            result = await conn.fetchval("""
                SELECT credits_required FROM service_types WHERE id = $1
            """, service_id)
            return result or 0
    
    def _get_user_message(self, cache_discount: float) -> str:
        """Generate user-friendly message about pricing"""
        if cache_discount >= 0.8:
            return "✨ Special price today! Your recent reading gives you 80% off!"
        elif cache_discount >= 0.5:
            return "🎯 Great timing! 50% cached data reduces your cost!"
        elif cache_discount >= 0.2:
            return "💫 Some cached insights available - enjoy reduced pricing!"
        else:
            return "🌟 Fresh, comprehensive reading with all new insights!"
    
    async def _get_value_suggestions(self, service_name: str, num_endpoints: int) -> List[Dict]:
        """Get value-based suggestions for the service"""
        async with self.db_pool.acquire() as conn:
            # Get relevant endpoint suggestions
            suggestions = await conn.fetch("""
                SELECT * FROM endpoint_suggestions 
                WHERE $1 ILIKE '%' || typical_use_case || '%'
                OR typical_use_case ILIKE '%' || $1 || '%'
                ORDER BY value_score DESC
                LIMIT 3
            """, service_name or '')
            
            results = []
            for sugg in suggestions:
                current_endpoints = num_endpoints
                suggested_endpoints = len(sugg['endpoints'])
                
                if suggested_endpoints > current_endpoints:
                    added_value = (suggested_endpoints - current_endpoints) * 20  # % value increase
                    added_cost = (suggested_endpoints - current_endpoints) * 0.5  # credits
                    
                    results.append({
                        "suggestion": f"Add {sugg['description']} for {added_value}% more insights",
                        "cost_impact": f"+{added_cost} credits",
                        "value_score": sugg['value_score'],
                        "endpoints_to_add": [e for e in sugg['endpoints'] if e not in (service_name or [])]
                    })
            
            return results

    async def make_api_call(self, endpoint: str, params: Dict) -> Dict:
        """
        Make API call with proper GET method and query parameters
        CRITICAL: Uses GET method with query params (not POST with JSON)
        """
        try:
            token = await self._get_token()
            
            async with httpx.AsyncClient() as client:
                response = await client.get(  # GET method!
                    f"{self.base_url}{endpoint}",
                    params=params,  # Query parameters!
                    headers={"Authorization": f"Bearer {token}"}
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"API call failed: {response.status_code} - {response.text}")
                    raise Exception(f"API error: {response.status_code}")
                    
        except Exception as e:
            logger.error(f"Error making API call: {e}")
            raise

# Global instance
prokerala_smart_service = None

def get_prokerala_smart_service(db_pool: asyncpg.Pool) -> ProkeralaSmartService:
    global prokerala_smart_service
    if not prokerala_smart_service:
        prokerala_smart_service = ProkeralaSmartService(db_pool)
    return prokerala_smart_service