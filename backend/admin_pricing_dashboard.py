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
import asyncpg
import os

# Try to import dynamic pricing system
try:
    from .dynamic_comprehensive_pricing import (
        DynamicComprehensivePricing, 
        generate_pricing_recommendations,
        apply_admin_approved_pricing,
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
    
    def __init__(self, database_url: str = None):
        self.database_url = database_url or os.getenv("DATABASE_URL")
        
        # Validate DATABASE_URL is set
        if not self.database_url:
            raise ValueError(
                "DATABASE_URL environment variable is missing or empty. "
                "Please set the DATABASE_URL environment variable or provide it as a parameter. "
                "Example: export DATABASE_URL='postgresql://user:password@localhost/dbname'"
            )
        
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
            import db
            pool = db.get_db_pool()
            if not pool:
                logger.warning("Shared database pool not available for pricing dashboard")
                return []
                
            async with pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT service_name, old_price, new_price, reasoning, changed_at
                    FROM pricing_history
                    WHERE service_name = 'comprehensive_life_reading_30min'
                    AND changed_at > NOW() - INTERVAL '30 days'
                    ORDER BY changed_at DESC
                    LIMIT 50
                """)
                
                history = []
                for row in rows:
                    history.append({
                        "service_name": row['service_name'],
                        "old_price": row['old_price'],
                        "new_price": row['new_price'],
                        "reasoning": row['reasoning'],
                        "changed_at": row['changed_at'].isoformat() if row['changed_at'] else None,
                        "price_change": row['new_price'] - row['old_price'] if row['old_price'] and row['new_price'] else 0
                    })
                
                return history
                
        except Exception as e:
            logger.error(f"Pricing history error: {e}")
            return []
    
    async def _get_demand_analytics(self) -> Dict[str, Any]:
        """Get demand analytics for pricing decisions"""
        try:
            import db
            pool = db.get_db_pool()
            if not pool:
                logger.warning("Database pool not available for demand analytics")
                return {
                    "daily_demand": [],
                    "hourly_demand": [],
                    "total_sessions_30_days": 0,
                    "avg_daily_sessions": 0,
                    "recent_7_day_avg": 0,
                    "trend": "unknown",
                    "peak_hours": []
                }
            async with pool.acquire() as conn:
                # Get session counts by day for last 30 days
                daily_rows = await conn.fetch("""
                    SELECT 
                        DATE(created_at) as session_date,
                        COUNT(*) as session_count,
                        AVG(credits_used) as avg_price_paid
                    FROM sessions
                    WHERE service_type = 'comprehensive_life_reading_30min'
                    AND created_at > NOW() - INTERVAL '30 days'
                    GROUP BY DATE(created_at)
                    ORDER BY session_date DESC
                """)
                
                daily_demand = []
                for row in daily_rows:
                    daily_demand.append({
                        "date": row['session_date'].isoformat() if row['session_date'] else None,
                        "sessions": row['session_count'],
                        "avg_price": float(row['avg_price_paid']) if row['avg_price_paid'] else 0
                    })
                
                # Get hourly demand patterns
                hourly_rows = await conn.fetch("""
                    SELECT 
                        EXTRACT(HOUR FROM created_at)::INTEGER as hour,
                        COUNT(*) as session_count
                    FROM sessions
                    WHERE service_type = 'comprehensive_life_reading_30min'
                    AND created_at > NOW() - INTERVAL '7 days'
                    GROUP BY EXTRACT(HOUR FROM created_at)
                    ORDER BY hour
                """)
                
                hourly_demand = []
                for row in hourly_rows:
                    hourly_demand.append({
                        "hour": row['hour'],
                        "sessions": row['session_count']
                    })
                
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
            import db
            pool = db.get_db_pool()
            if not pool:
                logger.warning("Database pool not available for revenue impact calculation")
                return {
                    "current_revenue_30_days": 0,
                    "current_sessions_30_days": 0,
                    "current_avg_price": 12,
                    "price_performance": [],
                    "price_scenarios": [],
                    "optimal_price_range": {"min": 11, "max": 13}
                }
            async with pool.acquire() as conn:
                # Get revenue for last 30 days
                revenue_row = await conn.fetchrow("""
                    SELECT 
                        SUM(credits_used) as total_revenue,
                        COUNT(*) as total_sessions,
                        AVG(credits_used) as avg_price_per_session
                    FROM sessions
                    WHERE service_type = 'comprehensive_life_reading_30min'
                    AND created_at > NOW() - INTERVAL '30 days'
                """)
                
                # Get revenue by price point
                price_rows = await conn.fetch("""
                    SELECT 
                        credits_used,
                        COUNT(*) as sessions,
                        SUM(credits_used) as revenue
                    FROM sessions
                    WHERE service_type = 'comprehensive_life_reading_30min'
                    AND created_at > NOW() - INTERVAL '30 days'
                    GROUP BY credits_used
                    ORDER BY credits_used
                """)
                
                price_performance = []
                for row in price_rows:
                    price_performance.append({
                        "price": row['credits_used'],
                        "sessions": row['sessions'],
                        "revenue": row['revenue'],
                        "revenue_per_session": row['credits_used']
                    })
                
                # Calculate projections
                total_revenue = float(revenue_row['total_revenue']) if revenue_row['total_revenue'] else 0
                total_sessions = revenue_row['total_sessions'] if revenue_row['total_sessions'] else 0
                avg_price = float(revenue_row['avg_price_per_session']) if revenue_row['avg_price_per_session'] else 0
                
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
            
            import db
            pool = db.get_db_pool()
            if not pool:
                logger.warning("Database pool not available for pricing override")
                return {
                    "success": False,
                    "message": "Database pool not available - pricing override failed"
                }
            async with pool.acquire() as conn:
                # Store pricing override
                await conn.execute("""
                    INSERT INTO pricing_overrides 
                    (service_type, override_price, duration_hours, reason, created_at, expires_at, status)
                    VALUES ($1, $2, $3, $4, NOW(), NOW() + INTERVAL '%s hours', 'active')
                """, 
                override_request.service_type,
                override_request.override_price,
                override_request.duration_hours,
                override_request.reason,
                override_request.duration_hours
                )
                
                # Update service price immediately
                await conn.execute("""
                    UPDATE service_types 
                    SET credits_required = $1, last_price_update = NOW()
                    WHERE name = $2
                """, 
                override_request.override_price,
                override_request.service_type
                )
                
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

@admin_pricing_router.post("/trigger-recommendation")
async def trigger_pricing_recommendation():
    """Trigger a new pricing recommendation calculation"""
    try:
        if not DYNAMIC_PRICING_AVAILABLE:
            return {
                "success": False,
                "message": "Dynamic pricing system not available"
            }
        
        # Generate new pricing recommendation
        recommendations = await generate_pricing_recommendations()
        
        return {
            "success": True,
            "message": "Pricing recommendation generated successfully",
            "recommendations": recommendations
        }
        
    except Exception as e:
        logger.error(f"Pricing recommendation error: {e}")
        return {
            "success": False,
            "message": f"Failed to generate pricing recommendation: {str(e)}"
        }

@admin_pricing_router.post("/apply-pricing")
async def apply_admin_approved_pricing_endpoint(
    approved_price: float,
    admin_notes: str = ""
):
    """Apply admin-approved pricing"""
    try:
        if not DYNAMIC_PRICING_AVAILABLE:
            return {
                "success": False,
                "message": "Dynamic pricing system not available"
            }
        
        result = await apply_admin_approved_pricing(approved_price, admin_notes)
        
        return {
            "success": True,
            "message": "Admin-approved pricing applied successfully",
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Apply pricing error: {e}")
        return {
            "success": False,
            "message": f"Failed to apply pricing: {str(e)}"
        }

@admin_pricing_router.get("/health")
async def get_pricing_system_health():
    """Get pricing system health status"""
    try:
        health_data = {
            "dynamic_pricing_available": DYNAMIC_PRICING_AVAILABLE,
            "database_connected": True,
            "timestamp": datetime.now().isoformat()
        }
        
        # Test database connection
        try:
            conn = await asyncpg.connect(pricing_dashboard.database_url)
            await conn.execute("SELECT 1")
            await conn.close()
            health_data["database_connected"] = True
        except Exception as e:
            health_data["database_connected"] = False
            health_data["database_error"] = str(e)
        
        return {
            "success": True,
            "health": health_data
        }
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {
            "success": False,
            "health": {
                "dynamic_pricing_available": False,
                "database_connected": False,
                "error": str(e)
            }
        }

if __name__ == "__main__":
    async def test_admin_dashboard():
        """Test the admin pricing dashboard"""
        print("🧪 Testing Admin Pricing Dashboard...")
        
        dashboard = AdminPricingDashboard()
        
        # Test pricing overview
        print("\n📊 Testing Pricing Overview:")
        overview = await dashboard.get_pricing_overview()
        print(f"   Status: {overview.get('status')}")
        print(f"   Current Price: {overview.get('current_pricing', {}).get('current_price', 'N/A')}")
        print(f"   System Health: {overview.get('system_health')}")
        
        # Test pricing alerts
        print("\n🚨 Testing Pricing Alerts:")
        alerts = await dashboard.get_pricing_alerts()
        print(f"   Total Alerts: {len(alerts)}")
        for alert in alerts[:3]:  # Show first 3 alerts
            print(f"   - {alert.get('type')}: {alert.get('message')}")
        
        print("\n✅ Admin Pricing Dashboard Test Complete!")
    
    asyncio.run(test_admin_dashboard())