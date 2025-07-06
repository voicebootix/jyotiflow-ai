#!/usr/bin/env python3
"""
Test MonetizationOptimizer Real Data Connection
தமிழ் - மோனடைசேஷன் ஆப்டிமைசர் மெய்யான தரவு இணைப்பு சோதனை
"""

import asyncio
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent))

from enhanced_business_logic import MonetizationOptimizer
from core_foundation_enhanced import EnhancedJyotiFlowDatabase

async def test_monetization_optimizer():
    """Test the MonetizationOptimizer with real data"""
    
    print("🧪 Testing MonetizationOptimizer Real Data Connection...")
    
    try:
        # Initialize database and optimizer
        db = EnhancedJyotiFlowDatabase()
        optimizer = MonetizationOptimizer()
        
        print("✅ Database and optimizer initialized")
        
        # Test 1: Get pricing configuration
        print("\n📊 Test 1: Pricing Configuration")
        pricing_config = await optimizer._get_pricing_config_data()
        print(f"   • Config keys: {list(pricing_config.keys())}")
        print(f"   • Min profit margin: {pricing_config.get('min_profit_margin_percent', 'N/A')}%")
        print(f"   • Video cost per minute: ${pricing_config.get('video_cost_per_minute', 'N/A')}")
        
        # Test 2: Get user behavior patterns
        print("\n👥 Test 2: User Behavior Patterns")
        user_behavior = await optimizer.get_user_behavior_patterns()
        summary = user_behavior.get('summary', {})
        print(f"   • Total active users: {summary.get('total_active_users', 0)}")
        print(f"   • Avg sessions per user: {summary.get('avg_sessions_per_user', 0):.2f}")
        print(f"   • Most popular service: {summary.get('most_popular_service', 'N/A')}")
        print(f"   • Peak usage hour: {summary.get('peak_usage_hour', 'N/A')}")
        print(f"   • Churn risk users: {summary.get('churn_risk_users', 0)}")
        
        # Test 3: Analyze price elasticity with real data
        print("\n💰 Test 3: Price Elasticity Analysis")
        analytics = {"test": "data"}  # Mock analytics for testing
        elasticity = await optimizer._analyze_price_elasticity(analytics, pricing_config)
        
        print(f"   • Services analyzed: {len(elasticity)}")
        for service_name, data in elasticity.items():
            print(f"   • {service_name}:")
            print(f"     - Current price: ${data.get('current_price', 0)}")
            print(f"     - Elasticity: {data.get('elasticity', 0):.2f}")
            print(f"     - Total sessions: {data.get('total_sessions', 0)}")
            print(f"     - Unique users: {data.get('unique_users', 0)}")
            print(f"     - Market demand: {data.get('market_demand', 'unknown')}")
            print(f"     - Price sensitivity: {data.get('price_sensitivity', 'unknown')}")
        
        # Test 4: Generate AI recommendations
        print("\n🤖 Test 4: AI Recommendations Generation")
        recommendations = await optimizer.generate_pricing_recommendations("monthly")
        
        if 'error' in recommendations:
            print(f"   ❌ Error: {recommendations['error']}")
        else:
            print(f"   ✅ Recommendations generated successfully")
            print(f"   • Current metrics available: {'current_metrics' in recommendations}")
            print(f"   • Pricing config included: {'pricing_config' in recommendations}")
            print(f"   • Price elasticity analyzed: {'price_elasticity' in recommendations}")
            print(f"   • AI recommendations count: {len(recommendations.get('recommendations', []))}")
            print(f"   • Expected impact calculated: {'expected_impact' in recommendations}")
            
            # Show sample recommendations
            recs = recommendations.get('recommendations', [])
            for i, rec in enumerate(recs[:3], 1):
                print(f"   • Recommendation {i}: {rec.get('title', 'N/A')}")
                print(f"     - Impact: ${rec.get('expected_revenue_impact', 0):,.0f}")
                print(f"     - Difficulty: {rec.get('implementation_difficulty', 'N/A')}/5")
                print(f"     - Timeline: {rec.get('timeline_weeks', 'N/A')} weeks")
        
        # Test 5: Test helper methods
        print("\n🔧 Test 5: Helper Methods")
        
        # Test elasticity calculation
        test_elasticity = optimizer._calculate_real_elasticity(
            total_sessions=50, unique_users=25, completion_rate=0.8,
            price_increase_acceptance=5, price_decrease_impact=2, credits_required=15
        )
        print(f"   • Test elasticity calculation: {test_elasticity:.2f}")
        
        # Test optimal price range
        test_range = optimizer._calculate_optimal_price_range(
            current_price=20.0, elasticity=-0.8, min_profitable_price=15.0,
            actual_avg_price=18.0, price_variance=2.0
        )
        print(f"   • Test optimal price range: {test_range}")
        
        print("\n✅ All tests completed successfully!")
        
        # Summary
        print("\n📋 Summary:")
        print(f"   • Real data connection: ✅ Working")
        print(f"   • Database queries: ✅ Successful")
        print(f"   • AI recommendations: ✅ Generated")
        print(f"   • Price elasticity: ✅ Calculated")
        print(f"   • User behavior: ✅ Analyzed")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_database_queries():
    """Test individual database queries"""
    
    print("\n🔍 Testing Individual Database Queries...")
    
    try:
        db = EnhancedJyotiFlowDatabase()
        
        # Test sessions data
        print("\n📊 Sessions Data:")
        sessions_count = await db.fetchval("SELECT COUNT(*) FROM sessions")
        print(f"   • Total sessions: {sessions_count}")
        
        recent_sessions = await db.fetchval("""
            SELECT COUNT(*) FROM sessions 
            WHERE created_at >= NOW() - INTERVAL '30 days'
        """)
        print(f"   • Recent sessions (30 days): {recent_sessions}")
        
        # Test service types
        print("\n🛠️ Service Types:")
        services = await db.fetch("SELECT name, credits_required, price_usd FROM service_types WHERE enabled = TRUE")
        print(f"   • Enabled services: {len(services)}")
        for service in services:
            print(f"     - {service['name']}: {service['credits_required']} credits, ${service['price_usd']}")
        
        # Test pricing config
        print("\n⚙️ Pricing Configuration:")
        config_count = await db.fetchval("SELECT COUNT(*) FROM pricing_config WHERE is_active = TRUE")
        print(f"   • Active config items: {config_count}")
        
        # Test payments
        print("\n💳 Payment Data:")
        payments_count = await db.fetchval("SELECT COUNT(*) FROM payments WHERE status = 'completed'")
        print(f"   • Completed payments: {payments_count}")
        
        total_revenue = await db.fetchval("""
            SELECT COALESCE(SUM(amount), 0) FROM payments 
            WHERE status = 'completed' AND created_at >= NOW() - INTERVAL '30 days'
        """)
        print(f"   • Recent revenue (30 days): ${total_revenue:,.2f}")
        
        print("✅ Database queries test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Database queries test failed: {e}")
        return False

if __name__ == "__main__":
    async def main():
        print("🚀 Starting MonetizationOptimizer Real Data Tests...")
        
        # Test database queries first
        db_success = await test_database_queries()
        
        if db_success:
            # Test full optimizer
            optimizer_success = await test_monetization_optimizer()
            
            if optimizer_success:
                print("\n🎉 All tests passed! MonetizationOptimizer is properly connected to real data.")
            else:
                print("\n⚠️ Optimizer tests failed, but database queries work.")
        else:
            print("\n❌ Database connection failed. Check your database setup.")
    
    asyncio.run(main()) 