#!/usr/bin/env python3
"""
Test Real Usage Data-Based Recommendations
தமிழ் - உண்மையான பயன்பாட்டு தரவு அடிப்படையிலான பரிந்துரைகளை சோதிக்கவும்
"""

import asyncio
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from enhanced_business_logic import MonetizationOptimizer
from db import EnhancedJyotiFlowDatabase

async def test_real_usage_recommendations():
    """Test real usage data-based recommendations"""
    print("🕉️ Testing Real Usage Data-Based Recommendations...")
    print("தமிழ் - உண்மையான பயன்பாட்டு தரவு அடிப்படையிலான பரிந்துரைகள் சோதிக்கப்படுகிறது...")
    
    try:
        # Initialize database and optimizer
        db = EnhancedJyotiFlowDatabase()
        await db.connect()
        
        optimizer = MonetizationOptimizer()
        optimizer.db = db
        
        print("✅ Database and optimizer initialized")
        
        # Test 1: Get real usage analytics
        print("\n📊 Test 1: Getting real usage analytics...")
        usage_analytics = await optimizer._get_real_usage_analytics()
        
        if usage_analytics:
            print(f"✅ Found analytics for {len(usage_analytics)} services")
            
            for service_name, data in usage_analytics.items():
                print(f"  📈 {service_name}:")
                print(f"    - Sessions: {data.get('total_sessions', 0)}")
                print(f"    - Completion Rate: {data.get('completion_rate', 0):.1%}")
                print(f"    - Satisfaction: {data.get('satisfaction_score', 0):.1%}")
                print(f"    - Market Demand: {data.get('market_demand', 'unknown')}")
                print(f"    - Engagement Score: {data.get('engagement_score', 0):.1%}")
        else:
            print("⚠️ No usage analytics found")
        
        # Test 2: Generate recommendations with real data
        print("\n📊 Test 2: Generating recommendations with real data...")
        recommendations = await optimizer.generate_pricing_recommendations("daily")
        
        if recommendations and 'pricing_recommendations' in recommendations:
            pricing_recs = recommendations['pricing_recommendations']
            print(f"✅ Generated {len(pricing_recs)} pricing recommendations")
            
            for i, rec in enumerate(pricing_recs[:3], 1):
                print(f"\n  📋 Recommendation {i}: {rec.get('service_name', 'Unknown')}")
                print(f"    - Current: ${rec.get('current_value', 0)}")
                print(f"    - Suggested: ${rec.get('suggested_value', 0)}")
                print(f"    - Expected Impact: ${rec.get('expected_revenue_impact', 0):,.2f}")
                print(f"    - Confidence: {rec.get('confidence_level', 0):.1%}")
                print(f"    - Priority: {rec.get('priority_level', 'unknown')}")
                
                # Show real data indicators
                metadata = rec.get('metadata', {})
                if metadata:
                    print(f"    - Real Data Indicators:")
                    if metadata.get('completion_rate'):
                        print(f"      * Completion Rate: {metadata['completion_rate']:.1%}")
                    if metadata.get('user_satisfaction'):
                        print(f"      * User Satisfaction: {metadata['user_satisfaction']:.1%}")
                    if metadata.get('total_sessions'):
                        print(f"      * Total Sessions: {metadata['total_sessions']}")
                    if metadata.get('data_quality'):
                        print(f"      * Data Quality: {metadata['data_quality']}")
                
                print(f"    - Reasoning: {rec.get('reasoning', 'No reasoning provided')}")
        else:
            print("⚠️ No recommendations generated")
        
        # Test 3: Check database for stored recommendations
        print("\n📊 Test 3: Checking stored recommendations...")
        stored_recs = await optimizer.get_ai_pricing_recommendations()
        
        if stored_recs:
            print(f"✅ Found {len(stored_recs)} stored recommendations")
            
            # Count recommendations with real data
            real_data_recs = [rec for rec in stored_recs if rec.get('metadata', {}).get('completion_rate')]
            print(f"  - Recommendations with real data: {len(real_data_recs)}")
            
            # Show sample with real data
            if real_data_recs:
                sample = real_data_recs[0]
                print(f"\n  📋 Sample Real Data Recommendation:")
                print(f"    - Service: {sample.get('service_name', 'Unknown')}")
                print(f"    - Type: {sample.get('recommendation_type', 'Unknown')}")
                print(f"    - Impact: ${sample.get('expected_impact', 0):,.2f}")
                
                metadata = sample.get('metadata', {})
                if metadata:
                    print(f"    - Real Data:")
                    print(f"      * Completion Rate: {metadata.get('completion_rate', 0):.1%}")
                    print(f"      * User Satisfaction: {metadata.get('user_satisfaction', 0):.1%}")
                    print(f"      * Total Sessions: {metadata.get('total_sessions', 0)}")
                    print(f"      * Data Quality: {metadata.get('data_quality', 'Unknown')}")
        else:
            print("⚠️ No stored recommendations found")
        
        # Test 4: Analyze data quality distribution
        print("\n📊 Test 4: Analyzing data quality...")
        if stored_recs:
            high_quality = [rec for rec in stored_recs if rec.get('metadata', {}).get('data_quality') == 'high']
            medium_quality = [rec for rec in stored_recs if rec.get('metadata', {}).get('data_quality') == 'medium']
            
            print(f"  - High quality data: {len(high_quality)} recommendations")
            print(f"  - Medium quality data: {len(medium_quality)} recommendations")
            
            # Calculate average confidence by data quality
            if high_quality:
                avg_confidence_high = sum(rec.get('confidence_level', 0) for rec in high_quality) / len(high_quality)
                print(f"  - Average confidence (high quality): {avg_confidence_high:.1%}")
            
            if medium_quality:
                avg_confidence_medium = sum(rec.get('confidence_level', 0) for rec in medium_quality) / len(medium_quality)
                print(f"  - Average confidence (medium quality): {avg_confidence_medium:.1%}")
        
        print("\n🎉 Real Usage Data Recommendations Test Completed Successfully!")
        print("🎉 உண்மையான பயன்பாட்டு தரவு பரிந்துரைகள் சோதனை வெற்றிகரமாக முடிந்தது!")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        print(f"❌ சோதனை தோல்வியடைந்தது: {e}")
        return False
    
    finally:
        if 'db' in locals():
            await db.close()

if __name__ == "__main__":
    success = asyncio.run(test_real_usage_recommendations())
    sys.exit(0 if success else 1) 