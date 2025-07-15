"""
Dynamic Comprehensive Reading Pricing System
Calculates real-time pricing based on actual costs, demand, and market conditions
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import json
import asyncpg
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DynamicComprehensivePricing:
    """Dynamic pricing engine for comprehensive readings"""
    
    def __init__(self, database_url: str = None):
        self.database_url = database_url or os.getenv("DATABASE_URL", "postgresql://jyotiflow_db_user:em0MmaZmvPzASryvzLHpR5g5rRZTQqpw@dpg-d12ohqemcj7s73fjbqtg-a/jyotiflow_db")
        self.connection_pool = None
        # Initialize connection pool asynchronously
        asyncio.create_task(self.initialize_pool())
        self.base_cost_factors = {
            "openai_api_calls": 0.5,  # Credits per API call
            "knowledge_retrieval": 0.2,  # Credits per knowledge piece
            "processing_time": 0.1,  # Credits per minute
            "chart_generation": 1.0,  # Credits for birth chart
            "remedies_generation": 0.8,  # Credits for personalized remedies
            "elevenlabs_voice_generation": 2.5,  # Credits for voice narration
            "did_video_generation": 4.0,  # Credits for AI avatar video
            "profit_margin": 1.3,  # 30% profit margin
            "market_demand_factor": 1.0  # Dynamic based on demand
        }
    
    async def initialize_pool(self):
        """Initialize connection pool"""
        if not self.connection_pool:
            self.connection_pool = await asyncpg.create_pool(
                self.database_url,
                min_size=2,
                max_size=10
            )
    
    async def get_connection(self):
        """Get connection from pool"""
        if not self.connection_pool:
            await self.initialize_pool()
        return await self.connection_pool.acquire()
    
    async def release_connection(self, conn):
        """Release connection back to pool"""
        if self.connection_pool:
            await self.connection_pool.release(conn)
    
    async def close_pool(self):
        """Close connection pool"""
        if self.connection_pool:
            await self.connection_pool.close()
            self.connection_pool = None
    
    async def calculate_comprehensive_reading_price(self, 
                                                   service_config: Optional[Dict[str, Any]] = None,
                                                   current_demand: Optional[float] = None) -> Dict[str, Any]:
        """Calculate dynamic price for comprehensive reading"""
        
        # Get current cost factors
        costs = await self._calculate_actual_costs()
        
        # Get market demand factor
        demand_factor = await self._get_demand_factor() if current_demand is None else current_demand
        
        # Get AI pricing recommendation
        ai_recommendation = await self._get_ai_price_recommendation()
        
        # Calculate base price
        base_price = self._calculate_base_price(costs)
        
        # Apply demand factor
        demand_adjusted_price = base_price * demand_factor
        
        # Apply AI recommendations
        final_price = self._apply_ai_recommendations(demand_adjusted_price, ai_recommendation)
        
        # Ensure minimum viability
        final_price = max(final_price, 8)  # Minimum 8 credits
        final_price = min(final_price, 25)  # Maximum 25 credits
        
        # Round to nearest 0.5
        final_price = round(final_price * 2) / 2
        
        return {
            "recommended_price": final_price,
            "base_cost": base_price,
            "demand_factor": demand_factor,
            "ai_recommendation": ai_recommendation,
            "cost_breakdown": costs,
            "pricing_rationale": self._generate_pricing_rationale(costs, demand_factor, ai_recommendation),
            "requires_admin_approval": True,
            "confidence_level": self._calculate_confidence_level(costs, demand_factor, ai_recommendation),
            "last_calculated": datetime.now().isoformat(),
            "next_review": (datetime.now() + timedelta(hours=6)).isoformat()
        }
    
    async def _calculate_actual_costs(self) -> Dict[str, float]:
        """Calculate actual costs based on recent usage"""
        conn = None
        try:
            conn = await self.get_connection()
            
            # Get recent comprehensive reading sessions
            recent_sessions = await conn.fetchval("""
                SELECT COUNT(*) as session_count 
                FROM sessions 
                WHERE service_type = 'comprehensive_life_reading_30min' 
                AND created_at > NOW() - INTERVAL '7 days'
            """) or 1
            
            # Calculate average costs
            costs = {
                "openai_api_cost": self._estimate_openai_costs(),
                "knowledge_processing_cost": self._estimate_knowledge_costs(),
                "chart_generation_cost": self._estimate_chart_costs(),
                "remedies_generation_cost": self._estimate_remedies_costs(),
                "server_processing_cost": self._estimate_processing_costs(),
                "elevenlabs_voice_cost": self._estimate_elevenlabs_costs(),
                "did_video_generation_cost": self._estimate_did_costs(),
                "total_operational_cost": 0
            }
            
            # Sum total operational cost
            costs["total_operational_cost"] = sum([
                costs["openai_api_cost"],
                costs["knowledge_processing_cost"], 
                costs["chart_generation_cost"],
                costs["remedies_generation_cost"],
                costs["server_processing_cost"],
                costs["elevenlabs_voice_cost"],
                costs["did_video_generation_cost"]
            ])
            
            return costs
            
        except Exception as e:
            logger.error(f"Cost calculation error: {e}")
            # Return default costs if calculation fails
            return {
                "openai_api_cost": 2.5,
                "knowledge_processing_cost": 1.0,
                "chart_generation_cost": 1.5,
                "remedies_generation_cost": 1.2,
                "server_processing_cost": 0.8,
                "elevenlabs_voice_cost": 2.5,
                "did_video_generation_cost": 4.0,
                "total_operational_cost": 14.5
            }
        finally:
            if conn:
                await self.release_connection(conn)
    
    def _estimate_openai_costs(self) -> float:
        """Estimate OpenAI API costs for comprehensive reading"""
        # Comprehensive reading typically involves:
        # - 3-4 knowledge retrieval calls
        # - 1 main guidance generation call
        # - 1 chart analysis call  
        # - 1 remedies generation call
        # Average cost per call in credits: 0.4
        return 6 * 0.4  # 2.4 credits
    
    def _estimate_knowledge_costs(self) -> float:
        """Estimate knowledge processing costs"""
        # 6 knowledge domains * average 3 pieces per domain * 0.1 credits per piece
        return 6 * 3 * 0.1  # 1.8 credits
    
    def _estimate_chart_costs(self) -> float:
        """Estimate birth chart generation costs"""
        # Complex astrological calculations + rendering
        return 1.5  # 1.5 credits
    
    def _estimate_remedies_costs(self) -> float:
        """Estimate personalized remedies generation costs"""
        # Custom mantra/gemstone/charity recommendations
        return 1.2  # 1.2 credits
    
    def _estimate_processing_costs(self) -> float:
        """Estimate server processing costs"""
        # 30 minutes of processing time, database queries, etc.
        return 0.8  # 0.8 credits
    
    def _estimate_elevenlabs_costs(self) -> float:
        """Estimate ElevenLabs voice generation costs"""
        # Comprehensive reading typically involves:
        # - Voice narration of full reading (~10-15 minutes of audio)
        # - High-quality voice cloning
        # - Multiple voice segments for different sections
        # Average cost: ~2.5 credits for full narration
        return 2.5  # 2.5 credits
    
    def _estimate_did_costs(self) -> float:
        """Estimate D-ID video generation costs"""
        # Comprehensive reading typically involves:
        # - AI avatar video of the reading
        # - High-quality video generation
        # - Multiple video segments for different sections
        # - Video processing and rendering
        # Average cost: ~4.0 credits for full video
        return 4.0  # 4.0 credits
    
    async def _get_demand_factor(self) -> float:
        """Calculate demand factor based on recent usage patterns"""
        conn = None
        try:
            conn = await self.get_connection()
            
            # Get sessions from last 24 hours vs previous 24 hours
            result = await conn.fetchrow("""
                SELECT 
                    COUNT(CASE WHEN created_at > NOW() - INTERVAL '1 day' THEN 1 END) as recent,
                    COUNT(CASE WHEN created_at BETWEEN NOW() - INTERVAL '2 days' AND NOW() - INTERVAL '1 day' THEN 1 END) as previous
                FROM sessions 
                WHERE service_type = 'comprehensive_life_reading_30min'
                AND created_at > NOW() - INTERVAL '2 days'
            """)
            
            recent_demand = result['recent'] or 0
            previous_demand = result['previous'] or 0
            
            # Calculate demand factor
            if previous_demand == 0:
                demand_factor = 1.0  # No change if no previous data
            else:
                demand_ratio = recent_demand / previous_demand
                # Normalize demand factor between 0.8 and 1.5
                demand_factor = max(0.8, min(1.5, demand_ratio))
            
            return demand_factor
            
        except Exception as e:
            logger.error(f"Demand factor calculation error: {e}")
            return 1.0  # Default to no change
        finally:
            if conn:
                await self.release_connection(conn)
    
    async def _get_ai_price_recommendation(self) -> Dict[str, Any]:
        """Get AI-based pricing recommendation"""
        try:
            # Integration with existing AI pricing system
            conn = await asyncpg.connect(self.database_url)
            try:
                # Get latest AI recommendation for comprehensive service
                result = await conn.fetchrow("""
                    SELECT recommendation_data, confidence_score 
                    FROM ai_pricing_recommendations 
                    WHERE service_type = 'comprehensive_life_reading_30min'
                    AND status = 'pending'
                    ORDER BY created_at DESC 
                    LIMIT 1
                """)
                
                if result:
                    recommendation_data = json.loads(result['recommendation_data'])
                    return {
                        "recommended_price": recommendation_data.get("suggested_price", 12),
                        "confidence": result['confidence_score'],
                        "reasoning": recommendation_data.get("reasoning", "AI analysis based on market data")
                    }
                else:
                    return {
                        "recommended_price": 12,
                        "confidence": 0.7,
                        "reasoning": "Default AI recommendation - no recent data available"
                    }
                    
            finally:
                await conn.close()
                
        except Exception as e:
            logger.error(f"AI recommendation error: {e}")
            return {
                "recommended_price": 12,
                "confidence": 0.5,
                "reasoning": "Fallback recommendation due to system error"
            }
    
    def _calculate_base_price(self, costs: Dict[str, float]) -> float:
        """Calculate base price from costs"""
        total_cost = costs["total_operational_cost"]
        base_price = total_cost * self.base_cost_factors["profit_margin"]
        return base_price
    
    def _apply_ai_recommendations(self, base_price: float, ai_rec: Dict[str, Any]) -> float:
        """Apply AI recommendations to base price"""
        ai_price = ai_rec["recommended_price"]
        confidence = ai_rec["confidence"]
        
        # Weighted average between base price and AI recommendation
        # Higher confidence = more weight to AI recommendation
        final_price = (base_price * (1 - confidence)) + (ai_price * confidence)
        
        return final_price
    
    def _generate_pricing_rationale(self, costs: Dict[str, float], 
                                   demand_factor: float, 
                                   ai_rec: Dict[str, Any]) -> str:
        """Generate human-readable pricing rationale"""
        total_cost = costs["total_operational_cost"]
        
        rationale_parts = [
            f"Base operational cost: {total_cost:.1f} credits",
            f"Current demand factor: {demand_factor:.2f}x",
            f"AI recommendation: {ai_rec['recommended_price']} credits ({ai_rec['confidence']:.1%} confidence)"
        ]
        
        if demand_factor > 1.1:
            rationale_parts.append("High demand detected - premium pricing applied")
        elif demand_factor < 0.9:
            rationale_parts.append("Lower demand - promotional pricing applied")
        
        return " | ".join(rationale_parts)
    
    def _calculate_confidence_level(self, costs: Dict[str, float], 
                                   demand_factor: float, 
                                   ai_rec: Dict[str, Any]) -> float:
        """Calculate confidence level of the pricing recommendation"""
        confidence_factors = []
        
        # Cost calculation confidence
        total_cost = costs["total_operational_cost"]
        if total_cost > 0:
            confidence_factors.append(0.9)  # High confidence in cost calculation
        else:
            confidence_factors.append(0.3)  # Low confidence if costs are zero
        
        # Demand factor confidence
        if 0.9 <= demand_factor <= 1.1:
            confidence_factors.append(0.8)  # High confidence in stable demand
        elif 0.7 <= demand_factor <= 1.3:
            confidence_factors.append(0.7)  # Medium confidence in moderate demand change
        else:
            confidence_factors.append(0.5)  # Lower confidence in extreme demand change
        
        # AI recommendation confidence
        ai_confidence = ai_rec.get("confidence", 0.5)
        confidence_factors.append(ai_confidence)
        
        # Overall confidence is the average of all factors
        overall_confidence = sum(confidence_factors) / len(confidence_factors)
        
        return round(overall_confidence, 2)
    
    async def update_service_price(self, new_pricing: Dict[str, Any]) -> bool:
        """Update the service price in the database"""
        try:
            conn = await asyncpg.connect(self.database_url)
            try:
                # Update service_types table
                await conn.execute("""
                    UPDATE service_types 
                    SET credits_required = $1, 
                        pricing_data = $2,
                        last_price_update = NOW()
                    WHERE name = 'comprehensive_life_reading_30min'
                """, 
                    new_pricing["current_price"],
                    json.dumps(new_pricing)
                )
                
                # Log the price change
                await conn.execute("""
                    INSERT INTO pricing_history 
                    (service_name, old_price, new_price, reasoning, changed_at)
                    VALUES ($1, $2, $3, $4, NOW())
                """, 
                    "comprehensive_life_reading_30min",
                    0,  # We'll get old price in a real implementation
                    new_pricing["current_price"],
                    new_pricing["pricing_rationale"]
                )
                
                logger.info(f"Updated comprehensive reading price to {new_pricing['current_price']} credits")
                return True
                
            finally:
                await conn.close()
                
        except Exception as e:
            logger.error(f"Price update error: {e}")
            return False
    
    async def get_current_price_info(self) -> Dict[str, Any]:
        """Get current pricing information"""
        try:
            conn = await asyncpg.connect(self.database_url)
            try:
                result = await conn.fetchrow("""
                    SELECT credits_required, pricing_data, last_price_update
                    FROM service_types 
                    WHERE name = 'comprehensive_life_reading_30min'
                """)
                
                if result:
                    return {
                        "current_price": result['credits_required'],
                        "pricing_data": json.loads(result['pricing_data']) if result['pricing_data'] else {},
                        "last_updated": result['last_price_update'].isoformat() if result['last_price_update'] else None
                    }
                else:
                    # Return default if service not found
                    return await self.calculate_comprehensive_reading_price()
                    
            finally:
                await conn.close()
                
        except Exception as e:
            logger.error(f"Price retrieval error: {e}")
            return await self.calculate_comprehensive_reading_price()

# Pricing recommendation functions (NO AUTO-UPDATE)
async def generate_pricing_recommendations():
    """Generate pricing recommendations for admin review (NO AUTO-UPDATE)"""
    pricing_engine = DynamicComprehensivePricing()
    
    # Calculate recommended pricing
    pricing_recommendation = await pricing_engine.calculate_comprehensive_reading_price()
    
    # Get current pricing
    current_pricing = await pricing_engine.get_current_price_info()
    
    # Analyze the recommendation
    current_price = current_pricing.get("current_price", 12)
    recommended_price = pricing_recommendation["recommended_price"]
    
    price_change_percentage = abs(recommended_price - current_price) / current_price
    
    # Create recommendation report
    recommendation_report = {
        "current_price": current_price,
        "recommended_price": recommended_price,
        "price_change_percentage": price_change_percentage,
        "price_change_credits": recommended_price - current_price,
        "recommendation_urgency": "high" if price_change_percentage > 0.2 else "medium" if price_change_percentage > 0.1 else "low",
        "cost_breakdown": pricing_recommendation["cost_breakdown"],
        "demand_analysis": {
            "demand_factor": pricing_recommendation["demand_factor"],
            "demand_trend": "high" if pricing_recommendation["demand_factor"] > 1.1 else "low" if pricing_recommendation["demand_factor"] < 0.9 else "stable"
        },
        "ai_recommendation": pricing_recommendation["ai_recommendation"],
        "confidence_level": pricing_recommendation["confidence_level"],
        "pricing_rationale": pricing_recommendation["pricing_rationale"],
        "requires_admin_approval": True,
        "generated_at": datetime.now().isoformat()
    }
    
    logger.info(f"Generated pricing recommendation: {current_price} -> {recommended_price} credits (Admin approval required)")
    return recommendation_report

async def apply_admin_approved_pricing(approved_price: float, admin_notes: str = "") -> Dict[str, Any]:
    """Apply admin-approved pricing change"""
    pricing_engine = DynamicComprehensivePricing()
    
    try:
        # Get current pricing for comparison
        current_pricing = await pricing_engine.get_current_price_info()
        current_price = current_pricing.get("current_price", 12)
        
        # Create pricing update data
        approved_pricing = {
            "current_price": approved_price,
            "pricing_rationale": f"Admin approved: {admin_notes}",
            "last_updated": datetime.now().isoformat(),
            "approval_timestamp": datetime.now().isoformat(),
            "approved_by": "admin"
        }
        
        # Update the price
        success = await pricing_engine.update_service_price(approved_pricing)
        
        if success:
            logger.info(f"Admin approved price change: {current_price} -> {approved_price} credits")
            return {
                "success": True,
                "message": "Price updated successfully",
                "old_price": current_price,
                "new_price": approved_price,
                "updated_at": datetime.now().isoformat()
            }
        else:
            logger.error("Failed to apply admin approved pricing")
            return {
                "success": False,
                "message": "Failed to update price in database"
            }
            
    except Exception as e:
        logger.error(f"Admin pricing application error: {e}")
        return {
            "success": False,
            "message": f"Error applying pricing: {str(e)}"
        }

async def get_pricing_dashboard_data() -> Dict[str, Any]:
    """Get comprehensive pricing data for admin dashboard"""
    pricing_engine = DynamicComprehensivePricing()
    
    current_pricing = await pricing_engine.get_current_price_info()
    pricing_recommendation = await generate_pricing_recommendations()
    
    return {
        "current_pricing": current_pricing,
        "pricing_recommendation": pricing_recommendation,
        "price_change_needed": pricing_recommendation["recommendation_urgency"] in ["high", "medium"],
        "market_conditions": {
            "demand_factor": pricing_recommendation["demand_analysis"]["demand_factor"],
            "demand_trend": pricing_recommendation["demand_analysis"]["demand_trend"],
            "cost_trends": pricing_recommendation["cost_breakdown"],
            "ai_confidence": pricing_recommendation["ai_recommendation"]["confidence"]
        }
    }

# Integration with existing pricing system
async def integrate_with_ai_pricing_recommendations():
    """Generate pricing recommendations for admin review"""
    try:
        # Generate pricing recommendations (NO AUTO-UPDATE)
        recommendations = await generate_pricing_recommendations()
        
        logger.info("Generated pricing recommendations for admin review")
        return recommendations
        
    except Exception as e:
        logger.error(f"Integration error: {e}")
        return {
            "error": "Failed to generate pricing recommendations",
            "message": str(e)
        }

if __name__ == "__main__":
    async def test_dynamic_pricing():
        """Test the dynamic pricing system"""
        print("🧪 Testing Dynamic Comprehensive Pricing...")
        
        pricing_engine = DynamicComprehensivePricing()
        
        # Test price calculation
        print("\n📊 Testing Price Calculation:")
        pricing_result = await pricing_engine.calculate_comprehensive_reading_price()
        print(f"   Recommended Price: {pricing_result['recommended_price']} credits")
        print(f"   Confidence Level: {pricing_result['confidence_level']:.1%}")
        print(f"   Demand Factor: {pricing_result['demand_factor']:.2f}x")
        
        # Test current price info
        print("\n💰 Testing Current Price Info:")
        current_info = await pricing_engine.get_current_price_info()
        print(f"   Current Price: {current_info.get('current_price', 'N/A')} credits")
        print(f"   Last Updated: {current_info.get('last_updated', 'N/A')}")
        
        # Test pricing recommendations
        print("\n🤖 Testing Pricing Recommendations:")
        recommendations = await generate_pricing_recommendations()
        print(f"   Current: {recommendations['current_price']} credits")
        print(f"   Recommended: {recommendations['recommended_price']} credits")
        print(f"   Change: {recommendations['price_change_credits']:+.1f} credits")
        print(f"   Urgency: {recommendations['recommendation_urgency']}")
        
        print("\n✅ Dynamic Pricing Test Complete!")
    
    asyncio.run(test_dynamic_pricing())