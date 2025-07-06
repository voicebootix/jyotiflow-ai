#!/usr/bin/env python3
"""
Test AI Pricing Recommendations Functionality
தமிழ் - AI விலை பரிந்துரைகள் செயல்பாட்டை சோதிக்கவும்
"""

import asyncio
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from enhanced_business_logic import MonetizationOptimizer
from db import EnhancedJyotiFlowDatabase

async def test_ai_pricing_recommendations():
    """Test the AI pricing recommendations functionality"""
    print("🕉️ Testing AI Pricing Recommendations...")
    print("தமிழ் - AI விலை பரிந்துரைகள் சோதிக்கப்படுகிறது...")
    
    try:
        # Initialize database and optimizer
        db = EnhancedJyotiFlowDatabase()
        await db.connect()
        
        optimizer = MonetizationOptimizer()
        optimizer.db = db
        
        print("✅ Database and optimizer initialized")
        
        # Test 1: Generate pricing recommendations
        print("\n📊 Test 1: Generating pricing recommendations...")
        recommendations = await optimizer.generate_pricing_recommendations("monthly")
        
        if recommendations and 'pricing_recommendations' in recommendations:
            print(f"✅ Generated {len(recommendations['pricing_recommendations'])} pricing recommendations")
            
            for i, rec in enumerate(recommendations['pricing_recommendations'][:3], 1):
                print(f"  {i}. {rec.get('service_name', 'Unknown')}: "
                      f"${rec.get('current_value', 0)} → ${rec.get('suggested_value', 0)} "
                      f"(Impact: ${rec.get('expected_revenue_impact', 0)})")
        else:
            print("⚠️ No pricing recommendations generated")
        
        # Test 2: Get recommendations from database
        print("\n📋 Test 2: Retrieving recommendations from database...")
        db_recommendations = await optimizer.get_ai_pricing_recommendations()
        
        if db_recommendations:
            print(f"✅ Found {len(db_recommendations)} recommendations in database")
            
            for i, rec in enumerate(db_recommendations[:3], 1):
                print(f"  {i}. {rec.get('service_name', 'Unknown')}: "
                      f"{rec.get('recommendation_type', 'Unknown')} "
                      f"(Priority: {rec.get('priority_level', 'Unknown')})")
        else:
            print("⚠️ No recommendations found in database")
        
        # Test 3: Check recommendation types
        print("\n🔍 Test 3: Analyzing recommendation types...")
        type_counts = {}
        for rec in db_recommendations:
            rec_type = rec.get('recommendation_type', 'unknown')
            type_counts[rec_type] = type_counts.get(rec_type, 0) + 1
        
        for rec_type, count in type_counts.items():
            print(f"  - {rec_type}: {count} recommendations")
        
        # Test 4: Check priority distribution
        print("\n🎯 Test 4: Checking priority distribution...")
        priority_counts = {}
        for rec in db_recommendations:
            priority = rec.get('priority_level', 'unknown')
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
        
        for priority, count in priority_counts.items():
            print(f"  - {priority}: {count} recommendations")
        
        # Test 5: Calculate total expected impact
        print("\n💰 Test 5: Calculating total expected impact...")
        total_impact = sum(rec.get('expected_impact', 0) for rec in db_recommendations)
        print(f"  Total expected revenue impact: ${total_impact:,.2f}")
        
        # Test 6: Check confidence levels
        print("\n🎯 Test 6: Analyzing confidence levels...")
        if db_recommendations:
            avg_confidence = sum(rec.get('confidence_level', 0) for rec in db_recommendations) / len(db_recommendations)
            print(f"  Average confidence level: {avg_confidence:.2%}")
            
            high_confidence = [rec for rec in db_recommendations if rec.get('confidence_level', 0) > 0.8]
            print(f"  High confidence recommendations (>80%): {len(high_confidence)}")
        
        print("\n🎉 AI Pricing Recommendations Test Completed Successfully!")
        print("🎉 AI விலை பரிந்துரைகள் சோதனை வெற்றிகரமாக முடிந்தது!")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        print(f"❌ சோதனை தோல்வியடைந்தது: {e}")
        return False
    
    finally:
        if 'db' in locals():
            await db.close()

if __name__ == "__main__":
    success = asyncio.run(test_ai_pricing_recommendations())
    sys.exit(0 if success else 1) 