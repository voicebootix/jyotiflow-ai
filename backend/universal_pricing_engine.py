"""
Universal Pricing Engine for JyotiFlow
Supports ALL services: comprehensive readings, horoscope, satsang, interactive sessions, future products
Real API integrations: ElevenLabs, D-ID, Agora
"""

import asyncio
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import json
import asyncpg
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ServiceConfiguration:
    """Configuration for a service type"""
    name: str
    display_name: str
    duration_minutes: int
    voice_enabled: bool
    video_enabled: bool
    interactive_enabled: bool
    birth_chart_enabled: bool
    remedies_enabled: bool
    knowledge_domains: List[str]
    persona_modes: List[str]
    base_credits: int
    service_category: str

@dataclass
class PricingResult:
    """Result of pricing calculation"""
    service_type: str
    recommended_price: float
    cost_breakdown: Dict[str, float]
    confidence_level: float
    pricing_rationale: str
    requires_admin_approval: bool
    api_costs: Dict[str, float]

class UniversalPricingEngine:
    """Universal pricing engine for all JyotiFlow services"""
    
    def __init__(self, database_url: str = None):
        self.database_url = database_url or os.getenv("DATABASE_URL")
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable must be provided")
        self.api_keys = self._load_api_keys()
        self.rate_limits = self._initialize_rate_limits()
        
    def _load_api_keys(self) -> Dict[str, str]:
        """Load API keys from environment"""
        return {
            "elevenlabs": os.getenv("ELEVENLABS_API_KEY", ""),
            "d_id": os.getenv("D_ID_API_KEY", ""),
            "agora_app_id": os.getenv("AGORA_APP_ID", ""),
            "agora_app_certificate": os.getenv("AGORA_APP_CERTIFICATE", ""),
            "openai": os.getenv("OPENAI_API_KEY", "")
        }
    
    def _initialize_rate_limits(self) -> Dict[str, Dict[str, float]]:
        """Initialize API rate limits and costs"""
        return {
            "elevenlabs": {
                "cost_per_minute": 0.18,  # $0.18 per minute
                "credits_per_dollar": 10,  # 10 credits = $1
                "cost_per_character": 0.0001,  # For text-to-speech
                "setup_cost": 0.1  # Setup/initialization cost
            },
            "d_id": {
                "cost_per_minute": 0.12,  # $0.12 per minute
                "credits_per_dollar": 10,  # 10 credits = $1
                "cost_per_second": 0.002,  # For video generation
                "setup_cost": 0.05  # Setup/initialization cost
            },
            "agora": {
                "cost_per_minute": 0.0099,  # $0.0099 per minute
                "credits_per_dollar": 10,  # 10 credits = $1
                "cost_per_participant": 0.001,  # Per participant per minute
                "setup_cost": 0.01  # Channel setup cost
            },
            "openai": {
                "cost_per_1k_tokens": 0.002,  # $0.002 per 1K tokens
                "credits_per_dollar": 10,  # 10 credits = $1
                "average_tokens_per_minute": 500,  # Estimated tokens per minute
                "setup_cost": 0.05  # API setup cost
            }
        }
    
    async def calculate_service_price(self, service_config: ServiceConfiguration) -> PricingResult:
        """Calculate price for any service type"""
        try:
            # Get actual API costs
            api_costs = await self._calculate_api_costs(service_config)
            
            # Calculate operational costs
            operational_costs = await self._calculate_operational_costs(service_config)
            
            # Get demand factor
            demand_factor = await self._get_demand_factor(service_config.name)
            
            # Get AI recommendation
            ai_recommendation = await self._get_ai_recommendation(service_config.name)
            
            # Calculate total cost
            total_cost = sum(api_costs.values()) + sum(operational_costs.values())
            
            # Apply profit margin (30%)
            base_price = total_cost * 1.3
            
            # Apply demand factor
            demand_adjusted_price = base_price * demand_factor
            
            # Apply AI recommendations
            final_price = self._apply_ai_recommendations(demand_adjusted_price, ai_recommendation)
            
            # Apply service-specific adjustments
            final_price = self._apply_service_adjustments(final_price, service_config)
            
            # Ensure minimum and maximum bounds
            final_price = max(final_price, service_config.base_credits)  # Minimum base credits
            final_price = min(final_price, service_config.base_credits * 3)  # Maximum 3x base credits
            
            # Round to nearest 0.5
            final_price = round(final_price * 2) / 2
            
            # Create cost breakdown
            cost_breakdown = {
                **api_costs,
                **operational_costs,
                "total_api_cost": sum(api_costs.values()),
                "total_operational_cost": sum(operational_costs.values()),
                "total_base_cost": total_cost,
                "profit_margin": total_cost * 0.3,
                "demand_adjustment": (demand_adjusted_price - base_price),
                "ai_adjustment": (final_price - demand_adjusted_price),
                "final_price": final_price
            }
            
            return PricingResult(
                service_type=service_config.name,
                recommended_price=final_price,
                cost_breakdown=cost_breakdown,
                confidence_level=self._calculate_confidence_level(service_config, api_costs, demand_factor),
                pricing_rationale=self._generate_pricing_rationale(service_config, cost_breakdown, demand_factor),
                requires_admin_approval=True,
                api_costs=api_costs
            )
            
        except Exception as e:
            logger.error(f"Pricing calculation error for {service_config.name}: {e}")
            return self._get_fallback_pricing(service_config)
    
    async def _calculate_api_costs(self, service_config: ServiceConfiguration) -> Dict[str, float]:
        """Calculate real API costs based on service configuration"""
        costs = {}
        
        # ElevenLabs Voice Generation
        if service_config.voice_enabled:
            costs["elevenlabs_voice"] = await self._calculate_elevenlabs_cost(service_config)
        
        # D-ID Video Generation
        if service_config.video_enabled:
            costs["d_id_video"] = await self._calculate_did_cost(service_config)
        
        # Agora Interactive Sessions
        if service_config.interactive_enabled:
            costs["agora_interactive"] = await self._calculate_agora_cost(service_config)
        
        # OpenAI API
        costs["openai_api"] = await self._calculate_openai_cost(service_config)
        
        return costs
    
    async def _calculate_elevenlabs_cost(self, service_config: ServiceConfiguration) -> float:
        """Calculate ElevenLabs cost based on service duration"""
        if not self.api_keys["elevenlabs"]:
            logger.warning("ElevenLabs API key not configured")
            return 2.5  # Fallback estimate
        
        rates = self.rate_limits["elevenlabs"]
        
        # Calculate cost per minute
        cost_per_minute = rates["cost_per_minute"]
        
        # Total cost = (duration * cost_per_minute) + setup_cost
        duration_cost = service_config.duration_minutes * cost_per_minute
        setup_cost = rates["setup_cost"]
        
        total_usd_cost = duration_cost + setup_cost
        
        # Convert to credits
        credits_cost = total_usd_cost * rates["credits_per_dollar"]
        
        logger.info(f"ElevenLabs cost for {service_config.name}: ${total_usd_cost:.3f} = {credits_cost:.2f} credits")
        return credits_cost
    
    async def _calculate_did_cost(self, service_config: ServiceConfiguration) -> float:
        """Calculate D-ID cost based on service duration"""
        if not self.api_keys["d_id"]:
            logger.warning("D-ID API key not configured")
            return 4.0  # Fallback estimate
        
        rates = self.rate_limits["d_id"]
        
        # Calculate cost per minute
        cost_per_minute = rates["cost_per_minute"]
        
        # Total cost = (duration * cost_per_minute) + setup_cost
        duration_cost = service_config.duration_minutes * cost_per_minute
        setup_cost = rates["setup_cost"]
        
        total_usd_cost = duration_cost + setup_cost
        
        # Convert to credits
        credits_cost = total_usd_cost * rates["credits_per_dollar"]
        
        logger.info(f"D-ID cost for {service_config.name}: ${total_usd_cost:.3f} = {credits_cost:.2f} credits")
        return credits_cost
    
    async def _calculate_agora_cost(self, service_config: ServiceConfiguration) -> float:
        """Calculate Agora cost for interactive sessions"""
        if not self.api_keys["agora_app_id"]:
            logger.warning("Agora API credentials not configured")
            return 1.0  # Fallback estimate
        
        rates = self.rate_limits["agora"]
        
        # Calculate cost per minute (assume 1 participant average)
        cost_per_minute = rates["cost_per_minute"]
        participant_cost = rates["cost_per_participant"]
        
        # Total cost = (duration * cost_per_minute) + (duration * participant_cost) + setup_cost
        duration_cost = service_config.duration_minutes * cost_per_minute
        interaction_cost = service_config.duration_minutes * participant_cost
        setup_cost = rates["setup_cost"]
        
        total_usd_cost = duration_cost + interaction_cost + setup_cost
        
        # Convert to credits
        credits_cost = total_usd_cost * rates["credits_per_dollar"]
        
        logger.info(f"Agora cost for {service_config.name}: ${total_usd_cost:.3f} = {credits_cost:.2f} credits")
        return credits_cost
    
    async def _calculate_openai_cost(self, service_config: ServiceConfiguration) -> float:
        """Calculate OpenAI API cost based on service complexity"""
        if not self.api_keys["openai"]:
            logger.warning("OpenAI API key not configured")
            return 2.5  # Fallback estimate
        
        rates = self.rate_limits["openai"]
        
        # Calculate tokens based on service complexity
        base_tokens = rates["average_tokens_per_minute"] * service_config.duration_minutes
        
        # Add complexity multipliers
        complexity_multiplier = 1.0
        complexity_multiplier += len(service_config.knowledge_domains) * 0.2
        complexity_multiplier += len(service_config.persona_modes) * 0.1
        if service_config.birth_chart_enabled:
            complexity_multiplier += 0.5
        if service_config.remedies_enabled:
            complexity_multiplier += 0.3
        
        total_tokens = base_tokens * complexity_multiplier
        
        # Calculate cost
        cost_per_1k_tokens = rates["cost_per_1k_tokens"]
        tokens_cost = (total_tokens / 1000) * cost_per_1k_tokens
        setup_cost = rates["setup_cost"]
        
        total_usd_cost = tokens_cost + setup_cost
        
        # Convert to credits
        credits_cost = total_usd_cost * rates["credits_per_dollar"]
        
        logger.info(f"OpenAI cost for {service_config.name}: ${total_usd_cost:.3f} = {credits_cost:.2f} credits")
        return credits_cost
    
    async def _calculate_operational_costs(self, service_config: ServiceConfiguration) -> Dict[str, float]:
        """Calculate operational costs"""
        return {
            "knowledge_processing": len(service_config.knowledge_domains) * 0.3,
            "chart_generation": 1.5 if service_config.birth_chart_enabled else 0,
            "remedies_generation": 1.2 if service_config.remedies_enabled else 0,
            "server_processing": service_config.duration_minutes * 0.05,
            "database_operations": 0.2,
            "monitoring_logging": 0.1
        }
    
    def _apply_service_adjustments(self, price: float, service_config: ServiceConfiguration) -> float:
        """Apply service-specific pricing adjustments"""
        # Satsang community features
        if service_config.service_category == "satsang":
            if service_config.interactive_enabled:
                price *= 1.2  # Premium for interactive satsang
            if "donations" in service_config.name.lower():
                price *= 0.8  # Reduced pricing for donation-based satsang
        
        # Comprehensive readings
        elif service_config.service_category == "comprehensive":
            if service_config.birth_chart_enabled and service_config.remedies_enabled:
                price *= 1.1  # Premium for full comprehensive reading
        
        # Horoscope readings
        elif service_config.service_category == "horoscope":
            if service_config.duration_minutes < 10:
                price *= 0.9  # Reduced pricing for quick horoscope
        
        return price
    
    async def _get_demand_factor(self, service_name: str) -> float:
        """Get demand factor for the service"""
        try:
            import db
            pool = db.get_db_pool()
            if not pool:
                raise Exception("Shared database pool not available")
                
            async with pool.acquire() as conn:
                result = await conn.fetchrow("""
                    SELECT 
                        COUNT(CASE WHEN created_at > NOW() - INTERVAL '1 day' THEN 1 END) as recent,
                        COUNT(CASE WHEN created_at BETWEEN NOW() - INTERVAL '2 days' AND NOW() - INTERVAL '1 day' THEN 1 END) as previous
                    FROM sessions 
                    WHERE service_type = $1
                    AND created_at > NOW() - INTERVAL '2 days'
                """, service_name)
                
                recent_demand = result['recent'] if result and result['recent'] else 0
                previous_demand = result['previous'] if result and result['previous'] else 0
                
                if previous_demand == 0:
                    return 1.0 if recent_demand == 0 else 1.2
                else:
                    demand_ratio = recent_demand / previous_demand
                    demand_factor = 0.8 + (demand_ratio * 0.6)
                    return max(0.7, min(1.5, demand_factor))
                
        except Exception as e:
            logger.error(f"Demand calculation error: {e}")
            return 1.0
    
    async def _get_ai_recommendation(self, service_name: str) -> Dict[str, Any]:
        """Get AI-based pricing recommendation"""
        try:
            import db
            pool = db.get_db_pool()
            if not pool:
                raise Exception("Shared database pool not available")
            async with pool.acquire() as conn:
                result = await conn.fetchrow("""
                    SELECT recommendation_data, confidence_score 
                    FROM ai_pricing_recommendations 
                    WHERE service_type = $1
                    AND status = 'pending'
                    ORDER BY created_at DESC 
                    LIMIT 1
                """, service_name)
                
                if result:
                    recommendation_data = json.loads(result['recommendation_data'])
                    return {
                        "recommended_price": recommendation_data.get("suggested_price", 0),
                        "confidence": result['confidence_score'],
                        "reasoning": recommendation_data.get("reasoning", "AI analysis")
                    }
            
        except Exception as e:
            logger.error(f"AI recommendation error: {e}")
        
        return {
            "recommended_price": 0,
            "confidence": 0.5,
            "reasoning": "No AI recommendation available"
        }
    
    def _apply_ai_recommendations(self, base_price: float, ai_rec: Dict[str, Any]) -> float:
        """Apply AI recommendations to base price"""
        ai_price = ai_rec.get("recommended_price", 0)
        confidence = ai_rec.get("confidence", 0.5)
        
        if ai_price > 0:
            # Weighted average between base price and AI recommendation
            return (base_price * (1 - confidence)) + (ai_price * confidence)
        
        return base_price
    
    def _calculate_confidence_level(self, service_config: ServiceConfiguration, 
                                  api_costs: Dict[str, float], 
                                  demand_factor: float) -> float:
        """Calculate confidence level of pricing"""
        confidence_factors = []
        
        # API integration confidence
        api_confidence = 0.9 if all(self.api_keys.values()) else 0.6
        confidence_factors.append(api_confidence)
        
        # Cost calculation confidence
        cost_confidence = 0.8 if sum(api_costs.values()) > 0 else 0.4
        confidence_factors.append(cost_confidence)
        
        # Demand factor confidence
        if 0.9 <= demand_factor <= 1.1:
            confidence_factors.append(0.8)
        else:
            confidence_factors.append(0.6)
        
        # Service configuration confidence
        config_confidence = 0.7 + (len(service_config.knowledge_domains) * 0.05)
        confidence_factors.append(min(config_confidence, 0.95))
        
        return sum(confidence_factors) / len(confidence_factors)
    
    def _generate_pricing_rationale(self, service_config: ServiceConfiguration, 
                                  cost_breakdown: Dict[str, float], 
                                  demand_factor: float) -> str:
        """Generate pricing rationale"""
        rationale_parts = []
        
        # Base cost
        total_cost = cost_breakdown["total_base_cost"]
        rationale_parts.append(f"Base cost: {total_cost:.1f} credits")
        
        # API costs
        api_cost = cost_breakdown["total_api_cost"]
        if api_cost > 0:
            rationale_parts.append(f"API costs: {api_cost:.1f} credits")
        
        # Service features
        features = []
        if service_config.voice_enabled:
            features.append("voice")
        if service_config.video_enabled:
            features.append("video")
        if service_config.interactive_enabled:
            features.append("interactive")
        if features:
            rationale_parts.append(f"Features: {', '.join(features)}")
        
        # Demand factor
        if demand_factor > 1.1:
            rationale_parts.append("High demand detected")
        elif demand_factor < 0.9:
            rationale_parts.append("Lower demand - promotional pricing")
        
        return " | ".join(rationale_parts)
    
    def _get_fallback_pricing(self, service_config: ServiceConfiguration) -> PricingResult:
        """Get fallback pricing when calculation fails"""
        fallback_price = service_config.base_credits * 1.2
        
        return PricingResult(
            service_type=service_config.name,
            recommended_price=fallback_price,
            cost_breakdown={"fallback_estimate": fallback_price},
            confidence_level=0.3,
            pricing_rationale="Fallback pricing due to system error",
            requires_admin_approval=True,
            api_costs={}
        )
    
    async def get_service_config_from_db(self, service_name: str) -> Optional[ServiceConfiguration]:
        """Get service configuration from database"""
        try:
            import db
            pool = db.get_db_pool()
            if not pool:
                raise Exception("Shared database pool not available")
            async with pool.acquire() as conn:
                result = await conn.fetchrow("""
                    SELECT name, display_name, duration_minutes, credits_required, service_category,
                           voice_enabled, video_enabled, comprehensive_reading_enabled as interactive_enabled,
                           birth_chart_enabled, remedies_enabled, knowledge_domains, persona_modes,
                           dynamic_pricing_enabled
                    FROM service_types 
                    WHERE name = $1 OR display_name = $1
                """, service_name)
                
                if result:
                    return ServiceConfiguration(
                        name=result['name'],
                        display_name=result['display_name'],
                        duration_minutes=result['duration_minutes'],
                        voice_enabled=bool(result['voice_enabled']),
                        video_enabled=bool(result['video_enabled']),
                        interactive_enabled=bool(result['interactive_enabled']),
                        birth_chart_enabled=bool(result['birth_chart_enabled']),
                        remedies_enabled=bool(result['remedies_enabled']),
                        knowledge_domains=json.loads(result['knowledge_domains']) if result['knowledge_domains'] else [],
                        persona_modes=json.loads(result['persona_modes']) if result['persona_modes'] else [],
                        base_credits=result['credits_required'],
                        service_category=result['service_category']
                    )
                
        except Exception as e:
            logger.error(f"Database error: {e}")
        
        return None

async def calculate_satsang_pricing(satsang_type: str = "community", 
                                  duration_minutes: int = 60,
                                  has_donations: bool = True,
                                  interactive_level: str = "basic") -> PricingResult:
    """Calculate pricing for Satsang services"""
    
    # Create service configuration for Satsang
    satsang_config = ServiceConfiguration(
        name=f"satsang_{satsang_type}",
        display_name=f"Satsang {satsang_type.title()}",
        duration_minutes=duration_minutes,
        voice_enabled=True,
        video_enabled=True,
        interactive_enabled=True,
        birth_chart_enabled=False,
        remedies_enabled=False,
        knowledge_domains=["satsang", "community", "spiritual_guidance"],
        persona_modes=["compassionate", "wise", "community_leader"],
        base_credits=5,
        service_category="satsang"
    )
    
    # Calculate pricing
    engine = UniversalPricingEngine()
    result = await engine.calculate_service_price(satsang_config)
    
    # Apply satsang-specific adjustments
    if has_donations:
        result.recommended_price *= 0.8  # Reduced for donation-based
    
    if interactive_level == "premium":
        result.recommended_price *= 1.3  # Premium for enhanced interaction
    
    return result

async def calculate_universal_pricing(service_name: str) -> PricingResult:
    """Calculate pricing for any service"""
    try:
        engine = UniversalPricingEngine()
        
        # Get service configuration from database
        service_config = await engine.get_service_config_from_db(service_name)
        
        if not service_config:
            # Create fallback configuration
            service_config = ServiceConfiguration(
                name=service_name,
                display_name=service_name.title(),
                duration_minutes=5,
                voice_enabled=False,
                video_enabled=False,
                interactive_enabled=False,
                birth_chart_enabled=False,
                remedies_enabled=False,
                knowledge_domains=["general"],
                persona_modes=["standard"],
                base_credits=5,
                service_category="general"
            )
        
        return await engine.calculate_service_price(service_config)
        
    except Exception as e:
        logger.error(f"Universal pricing calculation error: {e}")
        return PricingResult(
            service_type=service_name,
            recommended_price=5.0,
            cost_breakdown={"error": "Calculation failed"},
            confidence_level=0.1,
            pricing_rationale="Error fallback pricing",
            requires_admin_approval=True,
            api_costs={}
        )

async def get_smart_pricing_recommendations() -> Dict[str, Any]:
    """Get smart pricing recommendations based on system performance"""
    try:
        import db
        pool = db.get_db_pool()
        if not pool:
            print("❌ ERROR: Shared database pool not available")
            return {}
        
        async with pool.acquire() as conn:
            # Get pricing performance data
            performance_data = await conn.fetchrow("""
                SELECT 
                    COUNT(*) as total_sessions,
                    AVG(credits_used) as avg_credits_used,
                    COUNT(CASE WHEN created_at > NOW() - INTERVAL '1 day' THEN 1 END) as recent_sessions,
                    AVG(CASE WHEN created_at > NOW() - INTERVAL '7 days' THEN credits_used END) as weekly_avg_credits
                FROM sessions
                WHERE created_at > NOW() - INTERVAL '30 days'
            """)
            
            # Get service popularity
            service_popularity = await conn.fetch("""
                SELECT 
                    service_type,
                    COUNT(*) as usage_count,
                    AVG(credits_used) as avg_credits
                FROM sessions
                WHERE created_at > NOW() - INTERVAL '7 days'
                GROUP BY service_type
                ORDER BY usage_count DESC
                LIMIT 5
            """)
            
            # Generate recommendations
            recommendations = {
                "overall_performance": {
                    "total_sessions": performance_data['total_sessions'],
                    "avg_credits_used": float(performance_data['avg_credits_used'] or 0),
                    "recent_activity": performance_data['recent_sessions'],
                    "weekly_trend": float(performance_data['weekly_avg_credits'] or 0)
                },
                "popular_services": [
                    {
                        "service_type": row['service_type'],
                        "usage_count": row['usage_count'],
                        "avg_credits": float(row['avg_credits'])
                    }
                    for row in service_popularity
                ],
                "pricing_recommendations": []
            }
            
            # Generate specific recommendations
            for service in service_popularity:
                if service['usage_count'] > 10:  # Popular service
                    recommendations["pricing_recommendations"].append({
                        "service": service['service_type'],
                        "recommendation": "Consider premium pricing",
                        "reason": f"High usage ({service['usage_count']} sessions)"
                    })
                elif service['usage_count'] < 3:  # Low usage
                    recommendations["pricing_recommendations"].append({
                        "service": service['service_type'],
                        "recommendation": "Consider promotional pricing",
                        "reason": f"Low usage ({service['usage_count']} sessions)"
                    })
            
            return recommendations
            
    except Exception as e:
        logger.error(f"Smart pricing recommendations error: {e}")
        return {
            "error": "Unable to generate recommendations",
            "fallback_recommendations": [
                {
                    "service": "general",
                    "recommendation": "Standard pricing",
                    "reason": "System fallback"
                }
            ]
        }

# Test function
async def test_universal_pricing():
    """Test the universal pricing system"""
    print("🧪 Testing Universal Pricing Engine...")
    
    # Test service configurations
    test_services = [
        ("clarity", "Standard clarity reading"),
        ("love", "Love and relationship guidance"),
        ("premium", "Premium comprehensive reading"),
        ("satsang_community", "Community satsang")
    ]
    
    for service_name, description in test_services:
        print(f"\n� Testing {service_name}: {description}")
        
        try:
            result = await calculate_universal_pricing(service_name)
            print(f"   💰 Recommended Price: {result.recommended_price:.2f} credits")
            print(f"   🎯 Confidence Level: {result.confidence_level:.1%}")
            print(f"   📝 Rationale: {result.pricing_rationale}")
            print(f"   ⚠️  Requires Admin Approval: {result.requires_admin_approval}")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Test smart recommendations
    print(f"\n🤖 Testing Smart Pricing Recommendations...")
    try:
        recommendations = await get_smart_pricing_recommendations()
        print(f"   📈 Total Sessions: {recommendations['overall_performance']['total_sessions']}")
        print(f"   📊 Popular Services: {len(recommendations['popular_services'])}")
        print(f"   💡 Recommendations: {len(recommendations['pricing_recommendations'])}")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_universal_pricing())