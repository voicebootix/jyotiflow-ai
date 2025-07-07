"""
Admin Pricing Dashboard for Dynamic Comprehensive Reading Pricing
Allows admins to monitor and control dynamic pricing in real-time
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
import sqlite3

# Try to import dynamic pricing system
try:
    from .dynamic_comprehensive_pricing import (
        DynamicComprehensivePricing, 
        auto_update_comprehensive_pricing,
        get_pricing_dashboard_data
    )
    DYNAMIC_PRICING_AVAILABLE = True
except ImportError:
    DYNAMIC_PRICING_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PricingOverrideRequest(BaseModel):
    """Request to override pricing for specific conditions"""
    service_type: str = Field(..., description="Service type to override")
    override_price: float = Field(..., description="Override price in credits")
    duration_hours: int = Field(default=24, description="Duration of override in hours")
    reason: str = Field(..., description="Reason for override")

class PricingAnalyticsResponse(BaseModel):
    """Response with pricing analytics"""
    current_price: float
    price_history: List[Dict[str, Any]]
    demand_analytics: Dict[str, Any]
    revenue_impact: Dict[str, Any]
    optimization_suggestions: List[str]

class AdminPricingDashboard:
    """Admin dashboard for managing dynamic pricing"""
    
    def __init__(self, db_path: str = "backend/jyotiflow.db"):
        self.db_path = db_path
        
    async def get_pricing_overview(self) -> Dict[str, Any]:
        """Get comprehensive pricing overview for admin dashboard"""
        try:
            if not DYNAMIC_PRICING_AVAILABLE:
                return {
                    "status": "fixed_pricing",
                    "message": "Dynamic pricing system not available",
                    "current_price": 12,
                    "system_health": "limited_functionality"
                }
            
            pricing_engine = DynamicComprehensivePricing()
            
            # Get current pricing info
            current_pricing = await pricing_engine.get_current_price_info()
            new_calculation = await pricing_engine.calculate_comprehensive_reading_price()
            
            # Get pricing history
            pricing_history = await self._get_pricing_history()
            
            # Get demand analytics
            demand_analytics = await self._get_demand_analytics()
            
            # Get revenue impact
            revenue_impact = await self._calculate_revenue_impact()
            
            # Get optimization suggestions
            optimization_suggestions = await self._get_optimization_suggestions(
                current_pricing, new_calculation, demand_analytics
            )
            
            return {
                "status": "active",
                "current_pricing": current_pricing,
                "recommended_pricing": new_calculation,
                "pricing_history": pricing_history,
                "demand_analytics": demand_analytics,
                "revenue_impact": revenue_impact,
                "optimization_suggestions": optimization_suggestions,
                "system_health": "fully_operational",
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Pricing overview error: {e}")
            return {
                "status": "error",
                "message": f"Failed to get pricing overview: {str(e)}",
                "system_health": "degraded"
            }
    
    async def _get_pricing_history(self) -> List[Dict[str, Any]]:
        """Get pricing history for the last 30 days"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT service_name, old_price, new_price, reasoning, changed_at
                FROM pricing_history
                WHERE service_name = 'comprehensive_life_reading_30min'
                AND changed_at > datetime('now', '-30 days')
                ORDER BY changed_at DESC
                LIMIT 50
            """)
            
            history = []
            for row in cursor.fetchall():
                history.append({
                    "service_name": row[0],
                    "old_price": row[1],
                    "new_price": row[2],
                    "reasoning": row[3],
                    "changed_at": row[4],
                    "price_change": row[2] - row[1] if row[1] and row[2] else 0
                })
            
            conn.close()
            return history
            
        except Exception as e:
            logger.error(f"Pricing history error: {e}")
            return []
    
    async def _get_demand_analytics(self) -> Dict[str, Any]:
        """Get demand analytics for pricing decisions"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get session counts by day for last 30 days
            cursor.execute("""
                SELECT 
                    DATE(created_at) as session_date,
                    COUNT(*) as session_count,
                    AVG(credits_required) as avg_price_paid
                FROM sessions
                WHERE service_type = 'comprehensive_life_reading_30min'
                AND created_at > datetime('now', '-30 days')
                GROUP BY DATE(created_at)
                ORDER BY session_date DESC
            """)
            
            daily_demand = []
            for row in cursor.fetchall():
                daily_demand.append({
                    "date": row[0],
                    "sessions": row[1],
                    "avg_price": row[2] or 0
                })
            
            # Get hourly demand patterns
            cursor.execute("""
                SELECT 
                    CAST(strftime('%H', created_at) AS INTEGER) as hour,
                    COUNT(*) as session_count
                FROM sessions
                WHERE service_type = 'comprehensive_life_reading_30min'
                AND created_at > datetime('now', '-7 days')
                GROUP BY CAST(strftime('%H', created_at) AS INTEGER)
                ORDER BY hour
            """)
            
            hourly_demand = []
            for row in cursor.fetchall():
                hourly_demand.append({
                    "hour": row[0],
                    "sessions": row[1]
                })
            
            conn.close()
            
            # Calculate demand trends
            total_sessions = sum(day["sessions"] for day in daily_demand)
            avg_daily_sessions = total_sessions / max(len(daily_demand), 1)
            
            recent_7_days = daily_demand[:7]
            recent_avg = sum(day["sessions"] for day in recent_7_days) / max(len(recent_7_days), 1)
            
            trend = "increasing" if recent_avg > avg_daily_sessions else "decreasing"
            
            return {
                "daily_demand": daily_demand,
                "hourly_demand": hourly_demand,
                "total_sessions_30_days": total_sessions,
                "avg_daily_sessions": avg_daily_sessions,
                "recent_7_day_avg": recent_avg,
                "trend": trend,
                "peak_hours": sorted(hourly_demand, key=lambda x: x["sessions"], reverse=True)[:3]
            }
            
        except Exception as e:
            logger.error(f"Demand analytics error: {e}")
            return {
                "daily_demand": [],
                "hourly_demand": [],
                "total_sessions_30_days": 0,
                "avg_daily_sessions": 0,
                "recent_7_day_avg": 0,
                "trend": "unknown",
                "peak_hours": []
            }
    
    async def _calculate_revenue_impact(self) -> Dict[str, Any]:
        """Calculate revenue impact of pricing changes"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get revenue for last 30 days
            cursor.execute("""
                SELECT 
                    SUM(credits_required) as total_revenue,
                    COUNT(*) as total_sessions,
                    AVG(credits_required) as avg_price_per_session
                FROM sessions
                WHERE service_type = 'comprehensive_life_reading_30min'
                AND created_at > datetime('now', '-30 days')
            """)
            
            revenue_data = cursor.fetchone()
            
            # Get revenue by price point
            cursor.execute("""
                SELECT 
                    credits_required,
                    COUNT(*) as sessions,
                    SUM(credits_required) as revenue
                FROM sessions
                WHERE service_type = 'comprehensive_life_reading_30min'
                AND created_at > datetime('now', '-30 days')
                GROUP BY credits_required
                ORDER BY credits_required
            """)
            
            price_performance = []
            for row in cursor.fetchall():
                price_performance.append({
                    "price": row[0],
                    "sessions": row[1],
                    "revenue": row[2],
                    "revenue_per_session": row[0]
                })
            
            conn.close()
            
            # Calculate projections
            total_revenue = revenue_data[0] if revenue_data[0] else 0
            total_sessions = revenue_data[1] if revenue_data[1] else 0
            avg_price = revenue_data[2] if revenue_data[2] else 0
            
            # Simulate revenue impact of price changes
            price_scenarios = []
            for price_change in [-2, -1, 0, 1, 2]:
                new_price = avg_price + price_change
                # Estimate demand change (simple elasticity model)
                demand_change = -0.1 * price_change  # 10% demand change per credit
                estimated_sessions = total_sessions * (1 + demand_change)
                estimated_revenue = estimated_sessions * new_price
                
                price_scenarios.append({
                    "price": new_price,
                    "estimated_sessions": max(0, estimated_sessions),
                    "estimated_revenue": max(0, estimated_revenue),
                    "revenue_change": estimated_revenue - total_revenue
                })
            
            return {
                "current_revenue_30_days": total_revenue,
                "current_sessions_30_days": total_sessions,
                "current_avg_price": avg_price,
                "price_performance": price_performance,
                "price_scenarios": price_scenarios,
                "optimal_price_range": {
                    "min": avg_price - 1,
                    "max": avg_price + 1
                }
            }
            
        except Exception as e:
            logger.error(f"Revenue impact calculation error: {e}")
            return {
                "current_revenue_30_days": 0,
                "current_sessions_30_days": 0,
                "current_avg_price": 12,
                "price_performance": [],
                "price_scenarios": [],
                "optimal_price_range": {"min": 11, "max": 13}
            }
    
    async def _get_optimization_suggestions(self, 
                                          current_pricing: Dict[str, Any], 
                                          new_calculation: Dict[str, Any],
                                          demand_analytics: Dict[str, Any]) -> List[str]:
        """Generate optimization suggestions for pricing"""
        suggestions = []
        
        current_price = current_pricing.get("current_price", 12)
        recommended_price = new_calculation.get("current_price", 12)
        demand_trend = demand_analytics.get("trend", "unknown")
        
        # Price adjustment suggestions
        if recommended_price > current_price + 1:
            suggestions.append(f"Consider increasing price to {recommended_price:.1f} credits based on high demand")
        elif recommended_price < current_price - 1:
            suggestions.append(f"Consider decreasing price to {recommended_price:.1f} credits to stimulate demand")
        
        # Demand trend suggestions
        if demand_trend == "increasing":
            suggestions.append("Demand is increasing - consider premium pricing strategy")
        elif demand_trend == "decreasing":
            suggestions.append("Demand is decreasing - consider promotional pricing or service enhancements")
        
        # Time-based suggestions
        peak_hours = demand_analytics.get("peak_hours", [])
        if peak_hours:
            top_hour = peak_hours[0]["hour"]
            suggestions.append(f"Peak demand at {top_hour}:00 - consider time-based pricing")
        
        # Cost optimization
        cost_breakdown = new_calculation.get("cost_breakdown", {})
        total_cost = cost_breakdown.get("total_operational_cost", 8.5)
        if current_price < total_cost * 1.2:
            suggestions.append(f"Price may be too low - minimum viable price is {total_cost * 1.2:.1f} credits")
        
        # AI confidence suggestions
        ai_confidence = new_calculation.get("ai_recommendation", {}).get("confidence", 0.5)
        if ai_confidence < 0.6:
            suggestions.append("AI pricing confidence is low - consider manual review")
        
        return suggestions if suggestions else ["Current pricing appears optimal"]
    
    async def set_pricing_override(self, override_request: PricingOverrideRequest) -> Dict[str, Any]:
        """Set a pricing override for specific conditions"""
        try:
            if not DYNAMIC_PRICING_AVAILABLE:
                return {
                    "success": False,
                    "message": "Dynamic pricing system not available"
                }
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Store pricing override
            cursor.execute("""
                INSERT INTO pricing_overrides 
                (service_type, override_price, duration_hours, reason, created_at, expires_at, status)
                VALUES (?, ?, ?, ?, datetime('now'), datetime('now', '+' || ? || ' hours'), 'active')
            """, (
                override_request.service_type,
                override_request.override_price,
                override_request.duration_hours,
                override_request.reason,
                override_request.duration_hours
            ))
            
            # Update service price immediately
            cursor.execute("""
                UPDATE service_types 
                SET credits_required = ?, last_price_update = datetime('now')
                WHERE name = ?
            """, (
                override_request.override_price,
                override_request.service_type
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Pricing override set: {override_request.service_type} -> {override_request.override_price} credits")
            
            return {
                "success": True,
                "message": "Pricing override set successfully",
                "override_price": override_request.override_price,
                "expires_at": (datetime.now() + timedelta(hours=override_request.duration_hours)).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Pricing override error: {e}")
            return {
                "success": False,
                "message": f"Failed to set pricing override: {str(e)}"
            }
    
    async def get_pricing_alerts(self) -> List[Dict[str, Any]]:
        """Get pricing alerts for admin attention"""
        alerts = []
        
        try:
            if not DYNAMIC_PRICING_AVAILABLE:
                alerts.append({
                    "type": "warning",
                    "message": "Dynamic pricing system not available",
                    "priority": "medium",
                    "timestamp": datetime.now().isoformat()
                })
                return alerts
            
            pricing_engine = DynamicComprehensivePricing()
            current_pricing = await pricing_engine.get_current_price_info()
            new_calculation = await pricing_engine.calculate_comprehensive_reading_price()
            
            current_price = current_pricing.get("current_price", 12)
            recommended_price = new_calculation.get("current_price", 12)
            
            # Price change alerts
            if abs(recommended_price - current_price) > 2:
                alerts.append({
                    "type": "info",
                    "message": f"Significant price change recommended: {current_price} -> {recommended_price} credits",
                    "priority": "high",
                    "timestamp": datetime.now().isoformat()
                })
            
            # Demand alerts
            demand_factor = new_calculation.get("demand_factor", 1.0)
            if demand_factor > 1.3:
                alerts.append({
                    "type": "info",
                    "message": f"High demand detected (factor: {demand_factor:.2f}) - consider premium pricing",
                    "priority": "medium",
                    "timestamp": datetime.now().isoformat()
                })
            elif demand_factor < 0.7:
                alerts.append({
                    "type": "warning",
                    "message": f"Low demand detected (factor: {demand_factor:.2f}) - consider promotional pricing",
                    "priority": "medium",
                    "timestamp": datetime.now().isoformat()
                })
            
            # Cost alerts
            cost_breakdown = new_calculation.get("cost_breakdown", {})
            total_cost = cost_breakdown.get("total_operational_cost", 8.5)
            if current_price < total_cost * 1.1:
                alerts.append({
                    "type": "warning",
                    "message": f"Price ({current_price}) is close to operational cost ({total_cost:.1f})",
                    "priority": "high",
                    "timestamp": datetime.now().isoformat()
                })
            
            return alerts
            
        except Exception as e:
            logger.error(f"Pricing alerts error: {e}")
            alerts.append({
                "type": "error",
                "message": f"Failed to get pricing alerts: {str(e)}",
                "priority": "high",
                "timestamp": datetime.now().isoformat()
            })
            return alerts

# Router for admin pricing dashboard
admin_pricing_router = APIRouter(prefix="/api/admin/pricing", tags=["Admin Pricing Dashboard"])

# Initialize dashboard
pricing_dashboard = AdminPricingDashboard()

@admin_pricing_router.get("/overview")
async def get_pricing_overview():
    """Get comprehensive pricing overview for admin dashboard"""
    return await pricing_dashboard.get_pricing_overview()

@admin_pricing_router.get("/analytics")
async def get_pricing_analytics():
    """Get detailed pricing analytics"""
    try:
        overview = await pricing_dashboard.get_pricing_overview()
        return {
            "success": True,
            "analytics": {
                "demand_analytics": overview.get("demand_analytics", {}),
                "revenue_impact": overview.get("revenue_impact", {}),
                "pricing_history": overview.get("pricing_history", []),
                "system_health": overview.get("system_health", "unknown")
            }
        }
    except Exception as e:
        logger.error(f"Pricing analytics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@admin_pricing_router.post("/override")
async def set_pricing_override(override_request: PricingOverrideRequest):
    """Set a pricing override for specific conditions"""
    return await pricing_dashboard.set_pricing_override(override_request)

@admin_pricing_router.get("/alerts")
async def get_pricing_alerts():
    """Get pricing alerts for admin attention"""
    return await pricing_dashboard.get_pricing_alerts()

@admin_pricing_router.post("/trigger-update")
async def trigger_pricing_update():
    """Manually trigger pricing update"""
    try:
        if not DYNAMIC_PRICING_AVAILABLE:
            return {
                "success": False,
                "message": "Dynamic pricing system not available"
            }
        
        updated_pricing = await auto_update_comprehensive_pricing()
        
        return {
            "success": True,
            "message": "Pricing update triggered successfully",
            "new_pricing": updated_pricing
        }
    except Exception as e:
        logger.error(f"Pricing update trigger error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@admin_pricing_router.get("/health")
async def get_pricing_system_health():
    """Get pricing system health status"""
    return {
        "dynamic_pricing_available": DYNAMIC_PRICING_AVAILABLE,
        "system_status": "operational" if DYNAMIC_PRICING_AVAILABLE else "limited",
        "last_check": datetime.now().isoformat(),
        "capabilities": {
            "real_time_pricing": DYNAMIC_PRICING_AVAILABLE,
            "demand_analytics": DYNAMIC_PRICING_AVAILABLE,
            "automated_updates": DYNAMIC_PRICING_AVAILABLE,
            "manual_overrides": DYNAMIC_PRICING_AVAILABLE
        }
    }

# Export router for inclusion in main app
router = admin_pricing_router

if __name__ == "__main__":
    async def test_admin_dashboard():
        """Test the admin pricing dashboard"""
        print("🧪 Testing Admin Pricing Dashboard...")
        
        dashboard = AdminPricingDashboard()
        
        # Test overview
        overview = await dashboard.get_pricing_overview()
        print(f"✅ Overview status: {overview['status']}")
        
        # Test alerts
        alerts = await dashboard.get_pricing_alerts()
        print(f"📢 Alerts: {len(alerts)} active")
        
        print("\n🎉 Admin pricing dashboard is working!")
    
    asyncio.run(test_admin_dashboard())