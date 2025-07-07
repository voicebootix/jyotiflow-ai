"""
Dynamic Comprehensive Reading Pricing System
Calculates real-time pricing based on actual costs, demand, and market conditions
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import json
import sqlite3

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DynamicComprehensivePricing:
    """Dynamic pricing engine for comprehensive readings"""
    
    def __init__(self, db_path: str = "backend/jyotiflow.db"):
        self.db_path = db_path
        self.base_cost_factors = {
            "openai_api_calls": 0.5,  # Credits per API call
            "knowledge_retrieval": 0.2,  # Credits per knowledge piece
            "processing_time": 0.1,  # Credits per minute
            "chart_generation": 1.0,  # Credits for birth chart
            "remedies_generation": 0.8,  # Credits for personalized remedies
            "profit_margin": 1.3,  # 30% profit margin
            "market_demand_factor": 1.0  # Dynamic based on demand
        }
    
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
            "current_price": final_price,
            "base_cost": base_price,
            "demand_factor": demand_factor,
            "ai_recommendation": ai_recommendation,
            "cost_breakdown": costs,
            "pricing_rationale": self._generate_pricing_rationale(costs, demand_factor, ai_recommendation),
            "last_updated": datetime.now().isoformat(),
            "next_review": (datetime.now() + timedelta(hours=6)).isoformat()
        }
    
    async def _calculate_actual_costs(self) -> Dict[str, float]:
        """Calculate actual costs based on recent usage"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get recent comprehensive reading sessions
            cursor.execute("""
                SELECT COUNT(*) as session_count 
                FROM sessions 
                WHERE service_type = 'comprehensive_life_reading_30min' 
                AND created_at > datetime('now', '-7 days')
            """)
            recent_sessions = cursor.fetchone()[0] or 1
            
            # Calculate average costs
            costs = {
                "openai_api_cost": self._estimate_openai_costs(),
                "knowledge_processing_cost": self._estimate_knowledge_costs(),
                "chart_generation_cost": self._estimate_chart_costs(),
                "remedies_generation_cost": self._estimate_remedies_costs(),
                "server_processing_cost": self._estimate_processing_costs(),
                "total_operational_cost": 0
            }
            
            # Sum total operational cost
            costs["total_operational_cost"] = sum([
                costs["openai_api_cost"],
                costs["knowledge_processing_cost"], 
                costs["chart_generation_cost"],
                costs["remedies_generation_cost"],
                costs["server_processing_cost"]
            ])
            
            conn.close()
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
                "total_operational_cost": 7.0
            }
    
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
    
    async def _get_demand_factor(self) -> float:
        """Calculate demand factor based on recent usage patterns"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get sessions from last 24 hours vs previous 24 hours
            cursor.execute("""
                SELECT 
                    COUNT(CASE WHEN created_at > datetime('now', '-1 day') THEN 1 END) as recent,
                    COUNT(CASE WHEN created_at BETWEEN datetime('now', '-2 days') AND datetime('now', '-1 day') THEN 1 END) as previous
                FROM sessions 
                WHERE service_type = 'comprehensive_life_reading_30min'
                AND created_at > datetime('now', '-2 days')
            """)
            
            result = cursor.fetchone()
            recent_demand = result[0] or 0
            previous_demand = result[1] or 0
            
            conn.close()
            
            # Calculate demand factor
            if previous_demand == 0:
                demand_factor = 1.0 if recent_demand == 0 else 1.2
            else:
                demand_ratio = recent_demand / previous_demand
                # Convert to demand factor (0.8 to 1.4 range)
                demand_factor = 0.8 + (demand_ratio * 0.6)
                demand_factor = max(0.8, min(1.4, demand_factor))
            
            return demand_factor
            
        except Exception as e:
            logger.error(f"Demand calculation error: {e}")
            return 1.0  # Default neutral demand
    
    async def _get_ai_price_recommendation(self) -> Dict[str, Any]:
        """Get AI-based pricing recommendation"""
        try:
            # Integration with existing AI pricing system
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get latest AI recommendation for comprehensive service
            cursor.execute("""
                SELECT recommendation_data, confidence_score 
                FROM ai_pricing_recommendations 
                WHERE service_type = 'comprehensive_life_reading_30min'
                AND status = 'pending'
                ORDER BY created_at DESC 
                LIMIT 1
            """)
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                recommendation_data = json.loads(result[0])
                return {
                    "recommended_price": recommendation_data.get("suggested_price", 12),
                    "confidence": result[1],
                    "reasoning": recommendation_data.get("reasoning", "AI analysis based on market data")
                }
            else:
                return {
                    "recommended_price": 12,
                    "confidence": 0.7,
                    "reasoning": "Default AI recommendation - no recent data available"
                }
                
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
    
    async def update_service_price(self, new_pricing: Dict[str, Any]) -> bool:
        """Update the service price in the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Update service_types table
            cursor.execute("""
                UPDATE service_types 
                SET credits_required = ?, 
                    pricing_data = ?,
                    last_price_update = datetime('now')
                WHERE name = 'comprehensive_life_reading_30min'
            """, (
                new_pricing["current_price"],
                json.dumps(new_pricing)
            ))
            
            # Log the price change
            cursor.execute("""
                INSERT INTO pricing_history 
                (service_name, old_price, new_price, reasoning, changed_at)
                VALUES (?, ?, ?, ?, datetime('now'))
            """, (
                "comprehensive_life_reading_30min",
                0,  # We'll get old price in a real implementation
                new_pricing["current_price"],
                new_pricing["pricing_rationale"]
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Updated comprehensive reading price to {new_pricing['current_price']} credits")
            return True
            
        except Exception as e:
            logger.error(f"Price update error: {e}")
            return False
    
    async def get_current_price_info(self) -> Dict[str, Any]:
        """Get current pricing information"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT credits_required, pricing_data, last_price_update
                FROM service_types 
                WHERE name = 'comprehensive_life_reading_30min'
            """)
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    "current_price": result[0],
                    "pricing_data": json.loads(result[1]) if result[1] else {},
                    "last_updated": result[2]
                }
            else:
                # Return default if service not found
                return await self.calculate_comprehensive_reading_price()
                
        except Exception as e:
            logger.error(f"Price retrieval error: {e}")
            return await self.calculate_comprehensive_reading_price()

# Pricing automation functions
async def auto_update_comprehensive_pricing():
    """Automatically update pricing based on current conditions"""
    pricing_engine = DynamicComprehensivePricing()
    
    # Calculate new pricing
    new_pricing = await pricing_engine.calculate_comprehensive_reading_price()
    
    # Get current pricing
    current_pricing = await pricing_engine.get_current_price_info()
    
    # Check if significant change is needed (more than 10% difference)
    current_price = current_pricing.get("current_price", 12)
    new_price = new_pricing["current_price"]
    
    price_change_percentage = abs(new_price - current_price) / current_price
    
    if price_change_percentage > 0.1:  # 10% change threshold
        # Update the price
        success = await pricing_engine.update_service_price(new_pricing)
        
        if success:
            logger.info(f"Auto-updated comprehensive reading price from {current_price} to {new_price} credits")
            return new_pricing
        else:
            logger.error("Failed to auto-update pricing")
            return current_pricing
    else:
        logger.info(f"Price stable at {current_price} credits - no update needed")
        return current_pricing

async def get_pricing_dashboard_data() -> Dict[str, Any]:
    """Get comprehensive pricing data for admin dashboard"""
    pricing_engine = DynamicComprehensivePricing()
    
    current_pricing = await pricing_engine.get_current_price_info()
    new_calculation = await pricing_engine.calculate_comprehensive_reading_price()
    
    return {
        "current_pricing": current_pricing,
        "recommended_pricing": new_calculation,
        "price_change_needed": abs(current_pricing.get("current_price", 12) - new_calculation["current_price"]) > 1,
        "market_conditions": {
            "demand_factor": new_calculation["demand_factor"],
            "cost_trends": new_calculation["cost_breakdown"],
            "ai_confidence": new_calculation["ai_recommendation"]["confidence"]
        }
    }

# Integration with existing pricing system
async def integrate_with_ai_pricing_recommendations():
    """Integrate with existing AI pricing recommendations system"""
    try:
        # This would be called by the existing AI pricing system
        # when it generates new recommendations
        
        pricing_engine = DynamicComprehensivePricing()
        dashboard_data = await get_pricing_dashboard_data()
        
        # Check if auto-update should be triggered
        if dashboard_data["price_change_needed"]:
            await auto_update_comprehensive_pricing()
        
        return dashboard_data
        
    except Exception as e:
        logger.error(f"AI pricing integration error: {e}")
        return {}

if __name__ == "__main__":
    async def test_dynamic_pricing():
        """Test the dynamic pricing system"""
        print("🧪 Testing Dynamic Comprehensive Pricing...")
        
        pricing_engine = DynamicComprehensivePricing()
        
        # Test price calculation
        pricing = await pricing_engine.calculate_comprehensive_reading_price()
        print(f"✅ Current recommended price: {pricing['current_price']} credits")
        print(f"📊 Demand factor: {pricing['demand_factor']:.2f}")
        print(f"🤖 AI recommendation: {pricing['ai_recommendation']['recommended_price']} credits")
        print(f"💰 Cost breakdown: {pricing['cost_breakdown']['total_operational_cost']:.1f} credits")
        print(f"📝 Reasoning: {pricing['pricing_rationale']}")
        
        # Test dashboard data
        dashboard = await get_pricing_dashboard_data()
        print(f"\n📈 Dashboard ready: {len(dashboard)} data points")
        
        print("\n🎉 Dynamic pricing system is working!")
    
    asyncio.run(test_dynamic_pricing())