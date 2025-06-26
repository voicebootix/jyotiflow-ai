#!/usr/bin/env python3
"""
Simple test to verify routes are working
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

def test_imports():
    """Test basic imports"""
    print("🔍 Testing imports...")
    
    try:
        from enhanced_production_deployment import enhanced_app
        print("✅ Enhanced app imported successfully")
        
        # Check routes
        routes = [r.path for r in enhanced_app.routes if hasattr(r, 'path')]
        auth_routes = [r for r in routes if '/auth/' in r]
        user_routes = [r for r in routes if '/user/' in r]
        
        print(f"📊 Total routes: {len(routes)}")
        print(f"🔐 Auth routes: {auth_routes}")
        print(f"👤 User routes: {user_routes}")
        
        # Check if critical routes exist
        critical_routes = [
            "/api/auth/login",
            "/api/auth/register", 
            "/api/user/profile",
            "/api/user/sessions",
            "/api/user/credits"
        ]
        
        missing_routes = [r for r in critical_routes if r not in routes]
        if missing_routes:
            print(f"❌ Missing critical routes: {missing_routes}")
            return False
        else:
            print("✅ All critical routes found!")
            return True
            
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting simple route test...")
    
    if test_imports():
        print("\n✅ Test passed! Routes should be working.")
    else:
        print("\n❌ Test failed. Routes may not be working properly.") 