#!/usr/bin/env python3
"""
🎯 PRIORITY 2 FACE PRESERVATION TEST
Quick test script to verify our Priority 2 improvements work
"""

import sys
import os
sys.path.append('backend')

import asyncio
import httpx
import json

async def test_priority2_face_preservation():
    """Test Priority 2 face preservation improvements"""
    
    print("🎯 Testing Priority 2: Advanced Prompt Engineering + 0.35 Strength")
    print("-" * 60)
    
    # Test the image preview endpoint
    base_url = "http://localhost:8000"  # Adjust if needed
    endpoint = "/api/admin/social-marketing/generate-image-preview"
    
    test_data = {
        "custom_prompt": None  # Use daily theme
    }
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            print("📡 Calling image generation endpoint...")
            
            response = await client.post(
                f"{base_url}{endpoint}",
                json=test_data,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"📊 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ SUCCESS: Image generated successfully!")
                
                # Check response headers for prompt
                generated_prompt = response.headers.get("X-Generated-Prompt", "Not provided")
                print(f"🎨 Generated Prompt: {generated_prompt[:100]}...")
                
                # Save image for inspection
                image_data = response.content
                with open("priority2_test_result.png", "wb") as f:
                    f.write(image_data)
                
                print(f"💾 Image saved as: priority2_test_result.png ({len(image_data)/1024:.1f}KB)")
                print("🔍 Please check the image to verify:")
                print("   - Swamiji's face is preserved")
                print("   - Clothing/background changed according to theme")
                print("   - Professional quality maintained")
                
            elif response.status_code == 401:
                print("❌ AUTHENTICATION ERROR: Admin access required")
                print("🔧 Fix: The auth bypass didn't work - check admin login")
                
            elif response.status_code == 500:
                print("❌ SERVER ERROR: Priority 2 code issue")
                print("📄 Error details:", response.text)
                
            else:
                print(f"❌ UNEXPECTED ERROR: {response.status_code}")
                print("📄 Response:", response.text)
                
    except httpx.ConnectError:
        print("❌ CONNECTION ERROR: Is the backend server running?")
        print("🚀 Start server: cd backend && python main.py")
        
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {e}")
        
    print("\n" + "=" * 60)
    print("🎯 Priority 2 Test Complete")

if __name__ == "__main__":
    print("🚀 JyotiFlow Priority 2 Face Preservation Test")
    print("=" * 60)
    asyncio.run(test_priority2_face_preservation())