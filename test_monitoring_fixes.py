#!/usr/bin/env python3
"""
Test script to verify the monitoring dashboard fixes work correctly
"""
import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

async def test_standard_response():
    """Test if StandardResponse accepts both dict and list data"""
    print("🧪 Testing StandardResponse data type flexibility...")
    
    try:
        from monitoring.dashboard import StandardResponse
        
        # Test with dict data
        response_dict = StandardResponse(
            status="success",
            message="Test with dict",
            data={"key": "value"}
        )
        print(f"✅ Dict data works: {response_dict.data}")
        
        # Test with list data (this was failing before)
        response_list = StandardResponse(
            status="success", 
            message="Test with list",
            data=[{"item": 1}, {"item": 2}]
        )
        print(f"✅ List data works: {response_list.data}")
        
        # Test with empty list (the actual failing case)
        response_empty = StandardResponse(
            status="success",
            message="Test with empty list",
            data=[]
        )
        print(f"✅ Empty list works: {response_empty.data}")
        
        return True
        
    except Exception as e:
        print(f"❌ StandardResponse test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    print("🚀 Testing monitoring dashboard fixes...\n")
    result = await test_standard_response()
    
    if result:
        print("🎉 StandardResponse fix appears to work!")
    else:
        print("⚠️ StandardResponse fix has issues")
    
    return result

if __name__ == "__main__":
    asyncio.run(main())
