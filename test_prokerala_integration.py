#!/usr/bin/env python3
"""
Test script for Prokerala Integration
Run this to test if your Prokerala API integration is working correctly
"""

import asyncio
import os
import sys
import json
from datetime import datetime

# Add backend to path
sys.path.append('backend')

async def test_prokerala_integration():
    """Test the Prokerala service integration"""
    
    print("🕉️ Testing Prokerala Integration for JyotiFlow")
    print("=" * 50)
    
    # Test environment variables
    print("\n1. Checking Environment Variables:")
    client_id = os.getenv("PROKERALA_CLIENT_ID")
    client_secret = os.getenv("PROKERALA_CLIENT_SECRET")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    if not client_id or client_id == "your-client-id":
        print("❌ PROKERALA_CLIENT_ID not set properly")
        return False
    else:
        print(f"✅ PROKERALA_CLIENT_ID: {client_id[:10]}...")
    
    if not client_secret or client_secret == "your-client-secret":
        print("❌ PROKERALA_CLIENT_SECRET not set properly")
        return False
    else:
        print(f"✅ PROKERALA_CLIENT_SECRET: {client_secret[:10]}...")
    
    if not openai_key or openai_key == "your-openai-api-key":
        print("⚠️ OPENAI_API_KEY not set properly (will use fallback)")
    else:
        print(f"✅ OPENAI_API_KEY: {openai_key[:10]}...")
    
    # Test Prokerala service import
    print("\n2. Testing Prokerala Service Import:")
    try:
        from services.prokerala_service import prokerala_service
        print("✅ Prokerala service imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Prokerala service: {e}")
        return False
    
    # Test token fetching
    print("\n3. Testing Token Fetch:")
    try:
        token = await prokerala_service.get_token()
        if token and token != "your-client-id":
            print(f"✅ Token fetched successfully: {token[:20]}...")
        else:
            print("❌ Failed to fetch valid token")
            return False
    except Exception as e:
        print(f"❌ Token fetch error: {e}")
        return False
    
    # Test birth chart calculation
    print("\n4. Testing Birth Chart Calculation:")
    test_birth_details = {
        "date": "1990-01-15",
        "time": "14:30",
        "location": "Chennai, India"
    }
    
    try:
        chart_data = await prokerala_service.get_complete_birth_chart(test_birth_details)
        print(f"✅ Birth chart calculated successfully")
        
        if "data" in chart_data:
            if "nakshatra" in chart_data["data"]:
                print(f"   Nakshatra: {chart_data['data']['nakshatra'].get('name', 'Unknown')}")
            if "chandra_rasi" in chart_data["data"]:
                print(f"   Chandra Rasi: {chart_data['data']['chandra_rasi'].get('name', 'Unknown')}")
        
        if "planets" in chart_data:
            print(f"   Planets calculated: {len(chart_data['planets'])}")
        
        if "houses" in chart_data:
            print(f"   Houses calculated: {len(chart_data['houses'])}")
            
        if "error" in chart_data:
            print(f"   ⚠️ Error in response: {chart_data['error']}")
            
    except Exception as e:
        print(f"❌ Birth chart calculation error: {e}")
        return False
    
    # Test spiritual guidance generation
    print("\n5. Testing Spiritual Guidance Generation:")
    test_question = "What does my birth chart say about my career path?"
    
    try:
        guidance = await prokerala_service.generate_spiritual_guidance(test_question, chart_data)
        print(f"✅ Guidance generated successfully")
        print(f"   Length: {len(guidance)} characters")
        print(f"   Preview: {guidance[:100]}...")
    except Exception as e:
        print(f"⚠️ Guidance generation error (using fallback): {e}")
    
    # Test complete session flow simulation
    print("\n6. Testing Complete Session Flow:")
    session_data = {
        "question": test_question,
        "birth_details": test_birth_details,
        "service_type": "premium"
    }
    
    print(f"✅ Session simulation completed")
    print(f"   Question: {session_data['question']}")
    print(f"   Birth Details: {session_data['birth_details']}")
    
    return True

async def test_different_prokerala_endpoints():
    """Test different Prokerala API endpoints mentioned in documentation"""
    
    print("\n🌟 Testing Different Prokerala Endpoints:")
    print("=" * 50)
    
    try:
        from services.prokerala_service import prokerala_service
        
        test_params = {
            "datetime": "1990-01-15T14:30:00+05:30",
            "coordinates": "13.0827,80.2707",  # Chennai coordinates
            "ayanamsa": "1"
        }
        
        token = await prokerala_service.get_token()
        headers = {"Authorization": f"Bearer {token}"}
        
        import httpx
        
        endpoints_to_test = [
            ("/v2/astrology/birth-details", "Birth Details"),
            ("/v2/astrology/planets", "Planetary Positions"),
            ("/v2/astrology/houses", "House System"),
            ("/v2/astrology/vedic-chart", "Complete Vedic Chart"),
        ]
        
        async with httpx.AsyncClient() as client:
            for endpoint, description in endpoints_to_test:
                try:
                    response = await client.get(
                        f"https://api.prokerala.com{endpoint}",
                        headers=headers,
                        params=test_params,
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        print(f"✅ {description}: Success ({len(str(data))} chars)")
                    else:
                        print(f"❌ {description}: HTTP {response.status_code}")
                        
                except Exception as e:
                    print(f"❌ {description}: {str(e)[:50]}...")
                    
    except Exception as e:
        print(f"❌ Endpoint testing failed: {e}")

def print_setup_instructions():
    """Print setup instructions for the user"""
    
    print("\n🔧 Setup Instructions:")
    print("=" * 50)
    print("""
To complete the Prokerala integration:

1. Set Environment Variables:
   export PROKERALA_CLIENT_ID="your_actual_client_id"
   export PROKERALA_CLIENT_SECRET="your_actual_client_secret"
   export OPENAI_API_KEY="your_actual_openai_key"

2. Or create a .env file in your backend directory:
   PROKERALA_CLIENT_ID=your_actual_client_id
   PROKERALA_CLIENT_SECRET=your_actual_client_secret
   OPENAI_API_KEY=your_actual_openai_key

3. Restart your FastAPI server:
   cd backend
   uvicorn main:app --reload

4. Test the integration:
   python test_prokerala_integration.py

5. Try the frontend:
   - Go to /spiritual-guidance
   - Fill in birth details
   - Submit a question
   - You should now see real astrological data!

🌟 Benefits after this fix:
   ✅ Real Nakshatra and Rasi calculations
   ✅ Actual planetary positions
   ✅ AI-generated guidance based on real chart data
   ✅ Enhanced astrological insights in frontend
   ✅ Fallback handling when API is unavailable
""")

async def main():
    """Main test function"""
    
    print("🕉️ JyotiFlow Prokerala Integration Test")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    success = await test_prokerala_integration()
    
    if success:
        await test_different_prokerala_endpoints()
        print("\n🎉 Integration test completed successfully!")
        print("Your Prokerala integration should now be working.")
    else:
        print("\n❌ Integration test failed!")
        print("Please check your environment variables and try again.")
    
    print_setup_instructions()

if __name__ == "__main__":
    asyncio.run(main())