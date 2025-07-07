"""
Dynamic Pricing Integration for JyotiFlow
Activates dynamic pricing system for comprehensive readings
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any

# Import all dynamic pricing components
try:
    from .dynamic_comprehensive_pricing import (
        DynamicComprehensivePricing,
        generate_pricing_recommendations,
        apply_admin_approved_pricing,
        get_pricing_dashboard_data,
        integrate_with_ai_pricing_recommendations
    )
    from .admin_pricing_dashboard import AdminPricingDashboard
    from .enhanced_spiritual_guidance_router import enhanced_router
    DYNAMIC_PRICING_READY = True
except ImportError as e:
    logging.error(f"Dynamic pricing import failed: {e}")
    DYNAMIC_PRICING_READY = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DynamicPricingManager:
    """Manages dynamic pricing system activation and monitoring"""
    
    def __init__(self):
        self.pricing_engine = None
        self.admin_dashboard = None
        self.active = False
        
    async def activate_dynamic_pricing(self) -> Dict[str, Any]:
        """Activate the dynamic pricing system"""
        try:
            if not DYNAMIC_PRICING_READY:
                return {
                    "success": False,
                    "message": "Dynamic pricing components not available",
                    "fallback_mode": True
                }
            
            # Initialize pricing engine
            self.pricing_engine = DynamicComprehensivePricing()
            
            # Initialize admin dashboard
            self.admin_dashboard = AdminPricingDashboard()
            
            # Calculate initial pricing
            initial_pricing = await self.pricing_engine.calculate_comprehensive_reading_price()
            
            # Update service price in database
            await self.pricing_engine.update_service_price(initial_pricing)
            
            # Mark as active
            self.active = True
            
            logger.info("🎯 Dynamic pricing system activated successfully!")
            logger.info(f"💰 Initial price set to: {initial_pricing['current_price']} credits")
            
            return {
                "success": True,
                "message": "Dynamic pricing system activated",
                "initial_price": initial_pricing['current_price'],
                "pricing_rationale": initial_pricing['pricing_rationale'],
                "system_status": "active",
                "activated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Dynamic pricing activation failed: {e}")
            return {
                "success": False,
                "message": f"Activation failed: {str(e)}",
                "fallback_mode": True
            }
    
    async def monitor_pricing_health(self) -> Dict[str, Any]:
        """Monitor pricing system health and performance"""
        try:
            if not self.active or not self.pricing_engine or not self.admin_dashboard:
                return {
                    "status": "inactive",
                    "message": "Dynamic pricing system not active"
                }
            
            # Get current pricing status
            current_pricing = await self.pricing_engine.get_current_price_info()
            
            # Get dashboard data
            dashboard_data = await get_pricing_dashboard_data()
            
            # Check for alerts
            alerts = await self.admin_dashboard.get_pricing_alerts()
            
            # Determine system health
            system_health = "healthy"
            if len(alerts) > 0:
                high_priority_alerts = [a for a in alerts if a.get("priority") == "high"]
                if high_priority_alerts:
                    system_health = "needs_attention"
            
            return {
                "status": "active",
                "system_health": system_health,
                "current_price": current_pricing.get("current_price", 12),
                "price_changes_needed": dashboard_data.get("price_change_needed", False),
                "alerts_count": len(alerts),
                "high_priority_alerts": len([a for a in alerts if a.get("priority") == "high"]),
                "last_check": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Pricing health monitoring failed: {e}")
            return {
                "status": "error",
                "system_health": "degraded",
                "message": str(e)
            }
    
    async def run_pricing_maintenance(self) -> Dict[str, Any]:
        """Run periodic pricing maintenance tasks"""
        try:
            if not self.active or not self.pricing_engine:
                return {
                    "success": False,
                    "message": "Dynamic pricing system not active"
                }
            
            # Generate pricing recommendations (NO AUTO-UPDATE)
            pricing_recommendation = await generate_pricing_recommendations()
            
            # Integrate with AI recommendations
            ai_integration_result = await integrate_with_ai_pricing_recommendations()
            
            logger.info("🔄 Pricing maintenance completed successfully")
            
            return {
                "success": True,
                "message": "Pricing maintenance completed - Admin approval required for price changes",
                "pricing_recommendation": pricing_recommendation,
                "ai_integration": ai_integration_result,
                "requires_admin_approval": True,
                "maintenance_completed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Pricing maintenance failed: {e}")
            return {
                "success": False,
                "message": f"Maintenance failed: {str(e)}"
            }

# Global pricing manager instance
pricing_manager = DynamicPricingManager()

async def initialize_dynamic_pricing():
    """Initialize dynamic pricing system on startup"""
    logger.info("🚀 Initializing dynamic pricing system...")
    
    activation_result = await pricing_manager.activate_dynamic_pricing()
    
    if activation_result["success"]:
        logger.info("✅ Dynamic pricing system ready!")
        logger.info(f"💰 Comprehensive reading price: {activation_result['initial_price']} credits")
        
        # Schedule periodic maintenance
        asyncio.create_task(periodic_pricing_maintenance())
        
    else:
        logger.warning("⚠️ Dynamic pricing system in fallback mode")
        logger.warning(f"Reason: {activation_result['message']}")
    
    return activation_result

async def periodic_pricing_maintenance():
    """Run periodic pricing maintenance every 6 hours"""
    while True:
        try:
            await asyncio.sleep(6 * 3600)  # 6 hours
            
            logger.info("🔄 Running periodic pricing maintenance...")
            
            # Run maintenance
            maintenance_result = await pricing_manager.run_pricing_maintenance()
            
            if maintenance_result["success"]:
                logger.info("✅ Pricing maintenance completed successfully")
            else:
                logger.warning(f"⚠️ Pricing maintenance issues: {maintenance_result['message']}")
                
        except Exception as e:
            logger.error(f"Periodic maintenance error: {e}")
            await asyncio.sleep(3600)  # Retry in 1 hour on error

async def get_pricing_status():
    """Get current pricing system status"""
    return await pricing_manager.monitor_pricing_health()

async def trigger_pricing_update():
    """Manually trigger pricing update"""
    return await pricing_manager.run_pricing_maintenance()

def get_pricing_router():
    """Get the enhanced router with pricing endpoints"""
    return enhanced_router if DYNAMIC_PRICING_READY else None

# Export key functions for main app integration
__all__ = [
    "initialize_dynamic_pricing",
    "get_pricing_status", 
    "trigger_pricing_update",
    "get_pricing_router",
    "pricing_manager"
]

if __name__ == "__main__":
    async def test_integration():
        """Test the integration system"""
        print("🧪 Testing Dynamic Pricing Integration...")
        
        # Test activation
        activation_result = await initialize_dynamic_pricing()
        print(f"✅ Activation: {activation_result['success']}")
        
        # Test status monitoring
        status = await get_pricing_status()
        print(f"📊 Status: {status['status']}")
        
        # Test maintenance
        maintenance_result = await trigger_pricing_update()
        print(f"🔄 Maintenance: {maintenance_result['success']}")
        
        print("\n🎉 Dynamic pricing integration is working!")
    
    asyncio.run(test_integration())