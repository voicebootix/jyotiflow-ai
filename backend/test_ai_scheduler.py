#!/usr/bin/env python3
"""
Test AI Scheduler Functionality
தமிழ் - AI அட்டவணைப்படுத்தி செயல்பாட்டை சோதிக்கவும்
"""

import asyncio
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from ai_scheduler import AIScheduler
from db import EnhancedJyotiFlowDatabase

async def test_ai_scheduler():
    """Test the AI scheduler functionality"""
    print("🕉️ Testing AI Scheduler...")
    print("தமிழ் - AI அட்டவணைப்படுத்தி சோதிக்கப்படுகிறது...")
    
    try:
        # Initialize scheduler
        scheduler = AIScheduler()
        
        print("\n📊 Test 1: Initializing scheduler...")
        if await scheduler.initialize():
            print("✅ Scheduler initialized successfully")
        else:
            print("❌ Failed to initialize scheduler")
            return False
        
        print("\n📊 Test 2: Running daily analysis...")
        success = await scheduler.run_daily_analysis()
        
        if success:
            print("✅ Daily analysis completed successfully")
        else:
            print("❌ Daily analysis failed")
            return False
        
        print("\n📊 Test 3: Checking stored recommendations...")
        db = EnhancedJyotiFlowDatabase()
        await db.connect()
        
        # Check for daily analysis recommendations
        daily_recs = await db.fetch("""
            SELECT COUNT(*) as count, 
                   SUM(expected_impact) as total_impact,
                   AVG(confidence_level) as avg_confidence
            FROM ai_pricing_recommendations 
            WHERE metadata->>'daily_analysis' = 'true'
            AND created_at >= NOW() - INTERVAL '1 hour'
        """)
        
        if daily_recs and daily_recs[0]['count'] > 0:
            rec = daily_recs[0]
            print(f"✅ Found {rec['count']} daily analysis recommendations")
            print(f"   Total expected impact: ${rec['total_impact']:,.2f}")
            print(f"   Average confidence: {rec['avg_confidence']:.1%}")
        else:
            print("⚠️ No daily analysis recommendations found")
        
        # Check for daily analysis summary
        summary = await db.fetchval("""
            SELECT data FROM ai_insights_cache 
            WHERE insight_type = 'daily_analysis_summary' 
            AND expires_at > NOW()
        """)
        
        if summary:
            print(f"✅ Daily analysis summary found:")
            print(f"   Analysis date: {summary.get('analysis_date', 'Unknown')}")
            print(f"   Total recommendations: {summary.get('total_recommendations', 0)}")
            print(f"   Top recommendations: {summary.get('top_recommendations_count', 0)}")
            print(f"   Total impact: ${summary.get('total_expected_impact', 0):,.2f}")
        else:
            print("⚠️ No daily analysis summary found")
        
        await db.close()
        
        print("\n🎉 AI Scheduler Test Completed Successfully!")
        print("🎉 AI அட்டவணைப்படுத்தி சோதனை வெற்றிகரமாக முடிந்தது!")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        print(f"❌ சோதனை தோல்வியடைந்தது: {e}")
        return False
    
    finally:
        if 'scheduler' in locals():
            await scheduler.cleanup()

if __name__ == "__main__":
    success = asyncio.run(test_ai_scheduler())
    sys.exit(0 if success else 1) 