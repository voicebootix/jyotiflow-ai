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
import sqlite3
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
    
    def __init__(self, db_path: str = "backend/jyotiflow.db"):
        self.db_path = db_path
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
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    COUNT(CASE WHEN created_at > datetime('now', '-1 day') THEN 1 END) as recent,
                    COUNT(CASE WHEN created_at BETWEEN datetime('now', '-2 days') AND datetime('now', '-1 day') THEN 1 END) as previous
                FROM sessions 
                WHERE service_type = ?
                AND created_at > datetime('now', '-2 days')
            """, (service_name,))
            
            result = cursor.fetchone()
            recent_demand = result[0] if result and result[0] else 0
            previous_demand = result[1] if result and result[1] else 0
            
            conn.close()
            
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
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT recommendation_data, confidence_score 
                FROM ai_pricing_recommendations 
                WHERE service_type = ?
                AND status = 'pending'
                ORDER BY created_at DESC 
                LIMIT 1
            """, (service_name,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                recommendation_data = json.loads(result[0])
                return {
                    "recommended_price": recommendation_data.get("suggested_price", 0),
                    "confidence": result[1],
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
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT name, display_name, duration_minutes, credits_required, service_category,
                       voice_enabled, video_enabled, comprehensive_reading_enabled as interactive_enabled,
                       birth_chart_enabled, remedies_enabled, knowledge_domains, persona_modes,
                       dynamic_pricing_enabled
                FROM service_types 
                WHERE name = ? OR display_name = ?
            """, (service_name, service_name))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return ServiceConfiguration(
                    name=result[0],
                    display_name=result[1],
                    duration_minutes=result[2],
                    voice_enabled=bool(result[5]),
                    video_enabled=bool(result[6]),
                    interactive_enabled=bool(result[7]),
                    birth_chart_enabled=bool(result[8]),
                    remedies_enabled=bool(result[9]),
                    knowledge_domains=json.loads(result[10]) if result[10] else [],
                    persona_modes=json.loads(result[11]) if result[11] else [],
                    base_credits=result[3],
                    service_category=result[4]
                )
            
        except Exception as e:
            logger.error(f"Error getting service config: {e}")
        
        return None
    
    async def calculate_satsang_pricing(self, satsang_type: str = "community", 
                                      duration_minutes: int = 60,
                                      has_donations: bool = True,
                                      interactive_level: str = "basic") -> PricingResult:
        """Calculate pricing for Satsang services"""
        
        # Create satsang service configuration
        service_config = ServiceConfiguration(
            name=f"satsang_{satsang_type}",
            display_name=f"Satsang {satsang_type.title()}",
            duration_minutes=duration_minutes,
            voice_enabled=True,
            video_enabled=True,
            interactive_enabled=interactive_level in ["advanced", "premium"],
            birth_chart_enabled=False,
            remedies_enabled=satsang_type == "spiritual",
            knowledge_domains=["tamil_spiritual_literature", "spiritual_guidance"],
            persona_modes=["traditional_guru", "compassionate_healer"],
            base_credits=5 if has_donations else 10,
            service_category="satsang"
        )
        
        # Calculate base pricing
        pricing_result = await self.calculate_service_price(service_config)
        
        # Apply satsang-specific adjustments
        if has_donations:
            pricing_result.recommended_price *= 0.7  # Reduced for donation-based
            pricing_result.pricing_rationale += " | Donation-based satsang"
        
        if interactive_level == "premium":
            pricing_result.recommended_price *= 1.3  # Premium for advanced interaction
            pricing_result.pricing_rationale += " | Premium interactive features"
        
        return pricing_result

# Universal pricing functions
async def calculate_universal_pricing(service_name: str) -> PricingResult:
    """Calculate pricing for any service"""
    engine = UniversalPricingEngine()
    
    # Get service configuration
    service_config = await engine.get_service_config_from_db(service_name)
    
    if not service_config:
        logger.error(f"Service configuration not found for: {service_name}")
        # Create fallback configuration
        service_config = ServiceConfiguration(
            name=service_name,
            display_name=service_name.replace("_", " ").title(),
            duration_minutes=15,
            voice_enabled=False,
            video_enabled=False,
            interactive_enabled=False,
            birth_chart_enabled=False,
            remedies_enabled=False,
            knowledge_domains=[],
            persona_modes=[],
            base_credits=10,
            service_category="guidance"
        )
    
    return await engine.calculate_service_price(service_config)

async def get_smart_pricing_recommendations() -> Dict[str, Any]:
    """Get smart pricing recommendations for admin dashboard"""
    engine = UniversalPricingEngine()
    
    try:
        conn = sqlite3.connect(engine.db_path)
        cursor = conn.cursor()
        
        # Get all services with dynamic pricing enabled
        cursor.execute("""
            SELECT name, display_name, credits_required, dynamic_pricing_enabled
            FROM service_types 
            WHERE is_active = 1
        """)
        
        services = cursor.fetchall()
        conn.close()
        
        recommendations = []
        
        for service in services:
            service_name, display_name, current_price, dynamic_enabled = service
            
            if dynamic_enabled:
                # Calculate new pricing
                pricing_result = await calculate_universal_pricing(service_name)
                
                # Compare with current price
                price_difference = pricing_result.recommended_price - current_price
                urgency = "high" if abs(price_difference) > 2 else "medium" if abs(price_difference) > 1 else "low"
                
                recommendations.append({
                    "service_name": service_name,
                    "display_name": display_name,
                    "current_price": current_price,
                    "recommended_price": pricing_result.recommended_price,
                    "price_difference": price_difference,
                    "urgency": urgency,
                    "confidence": pricing_result.confidence_level,
                    "rationale": pricing_result.pricing_rationale,
                    "cost_breakdown": pricing_result.cost_breakdown
                })
        
        return {
            "recommendations": recommendations,
            "total_services": len(services),
            "dynamic_services": len([s for s in services if s[3]]),
            "high_priority": len([r for r in recommendations if r["urgency"] == "high"]),
            "api_status": {
                "elevenlabs": bool(engine.api_keys["elevenlabs"]),
                "d_id": bool(engine.api_keys["d_id"]),
                "agora": bool(engine.api_keys["agora_app_id"]),
                "openai": bool(engine.api_keys["openai"])
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting smart pricing recommendations: {e}")
        return {
            "recommendations": [],
            "error": str(e)
        }

if __name__ == "__main__":
    async def test_universal_pricing():
        """Test the universal pricing engine"""
        print("🧪 Testing Universal Pricing Engine...")
        
        # Test comprehensive reading
        print("\n📊 Testing Comprehensive Reading:")
        comprehensive_result = await calculate_universal_pricing("comprehensive_life_reading_30min")
        print(f"   Price: {comprehensive_result.recommended_price} credits")
        print(f"   API Costs: {comprehensive_result.api_costs}")
        print(f"   Confidence: {comprehensive_result.confidence_level:.2f}")
        
        # Test satsang pricing
        print("\n🙏 Testing Satsang Pricing:")
        engine = UniversalPricingEngine()
        satsang_result = await engine.calculate_satsang_pricing("community", 60, True, "basic")
        print(f"   Price: {satsang_result.recommended_price} credits")
        print(f"   API Costs: {satsang_result.api_costs}")
        print(f"   Rationale: {satsang_result.pricing_rationale}")
        
        # Test smart recommendations
        print("\n🤖 Testing Smart Recommendations:")
        recommendations = await get_smart_pricing_recommendations()
        print(f"   Total Services: {recommendations.get('total_services', 0)}")
        print(f"   Dynamic Services: {recommendations.get('dynamic_services', 0)}")
        print(f"   High Priority: {recommendations.get('high_priority', 0)}")
        print(f"   API Status: {recommendations.get('api_status', {})}")
        
        print("\n✅ Universal Pricing Engine Test Complete!")
    
    asyncio.run(test_universal_pricing())