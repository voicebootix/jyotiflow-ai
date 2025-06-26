#!/usr/bin/env python3
"""
Test script to debug route registration issues
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

def test_route_imports():
    """Test importing and checking routes"""
    print("🔍 Testing route imports...")
    
    # Test 1: Import core foundation app
    try:
        from core_foundation_enhanced import app as core_app
        print(f"✅ Core foundation app imported successfully")
        core_routes = [r.path for r in core_app.routes if hasattr(r, 'path')]
        print(f"📊 Core foundation has {len(core_routes)} routes")
        print(f"🔐 Core auth routes: {[r for r in core_routes if '/auth/' in r]}")
        print(f"👤 Core user routes: {[r for r in core_routes if '/user/' in r]}")
    except Exception as e:
        print(f"❌ Core foundation import failed: {e}")
        return False
    
    # Test 2: Import enhanced app
    try:
        from enhanced_production_deployment import enhanced_app
        print(f"✅ Enhanced app imported successfully")
        enhanced_routes = [r.path for r in enhanced_app.routes if hasattr(r, 'path')]
        print(f"📊 Enhanced app has {len(enhanced_routes)} routes")
        print(f"🔐 Enhanced auth routes: {[r for r in enhanced_routes if '/auth/' in r]}")
        print(f"👤 Enhanced user routes: {[r for r in enhanced_routes if '/user/' in r]}")
    except Exception as e:
        print(f"❌ Enhanced app import failed: {e}")
        return False
    
    # Test 3: Check if routes are properly mounted
    missing_auth = [r for r in core_routes if '/auth/' in r and r not in enhanced_routes]
    missing_user = [r for r in core_routes if '/user/' in r and r not in enhanced_routes]
    
    if missing_auth or missing_user:
        print(f"❌ Missing routes in enhanced app:")
        print(f"   Missing auth: {missing_auth}")
        print(f"   Missing user: {missing_user}")
        return False
    else:
        print(f"✅ All routes properly mounted!")
        return True

def test_endpoint_functions():
    """Test if endpoint functions are available"""
    print("\n🔍 Testing endpoint function imports...")
    
    try:
        from core_foundation_enhanced import (
            register_user, login_user,
            get_user_profile, get_user_sessions, get_user_credits
        )
        print("✅ All endpoint functions imported successfully")
        return True
    except Exception as e:
        print(f"❌ Endpoint function import failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting route debugging...")
    
    success = True
    success &= test_route_imports()
    success &= test_endpoint_functions()
    
    if success:
        print("\n✅ All tests passed! Routes should be working.")
    else:
        print("\n❌ Some tests failed. Routes may not be working properly.") 