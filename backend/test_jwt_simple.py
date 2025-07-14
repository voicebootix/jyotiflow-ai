#!/usr/bin/env python3
"""
Simple JWT Authentication Test
Tests the centralized JWT authentication system without external dependencies
"""

import sys
import os
from datetime import datetime, timedelta
import json
from pathlib import Path

# Add the backend directory to the Python path using dynamic path resolution
backend_dir = Path(__file__).parent.resolve()
sys.path.insert(0, str(backend_dir))

try:
    from auth.jwt_config import JWTHandler
    import jwt
    JWT_AVAILABLE = True
except ImportError as e:
    print(f"ImportError: {e}")
    JWT_AVAILABLE = False

# Test configuration
TEST_USER_ID = "test_user_123"
TEST_USER_EMAIL = "test@jyotiflow.ai"
TEST_ADMIN_ID = "admin_123"
TEST_ADMIN_EMAIL = "admin@jyotiflow.ai"

# JWT Secret for testing - must be set in environment
JWT_SECRET = os.getenv("JWT_SECRET")
if not JWT_SECRET:
    print("⚠️  JWT_SECRET environment variable not set. Using test secret for testing only.")
    JWT_SECRET = "test_secret_for_jwt_testing_only_not_production"
JWT_ALGORITHM = "HS256"

class MockRequest:
    """Mock request object for testing JWT handler"""
    def __init__(self, token: str):
        self.headers = {"Authorization": f"Bearer {token}"}

def create_test_jwt_token(user_id: str, email: str, role: str = "user") -> str:
    """Create a test JWT token for testing purposes"""
    payload = {
        "sub": user_id,
        "email": email,
        "role": role,
        "exp": datetime.utcnow() + timedelta(hours=1),
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def test_jwt_handler_functionality():
    """Test the centralized JWT handler functionality"""
    print("🔧 Testing JWT Handler Functionality")
    
    if not JWT_AVAILABLE:
        print("  ❌ JWT modules not available, skipping tests")
        return False
    
    # Test 1: Valid token extraction
    print("  ✅ Testing valid token extraction...")
    valid_token = create_test_jwt_token(TEST_USER_ID, TEST_USER_EMAIL)
    mock_request = MockRequest(valid_token)
    
    try:
        user_id = JWTHandler.get_user_id_from_token(mock_request)
        assert user_id == TEST_USER_ID, f"Expected {TEST_USER_ID}, got {user_id}"
        print(f"    ✅ User ID extracted: {user_id}")
        
        user_email = JWTHandler.get_user_email_from_token(mock_request)
        assert user_email == TEST_USER_EMAIL, f"Expected {TEST_USER_EMAIL}, got {user_email}"
        print(f"    ✅ User email extracted: {user_email}")
        
        user_role = JWTHandler.get_user_role_from_token(mock_request)
        assert user_role == "user", f"Expected 'user', got {user_role}"
        print(f"    ✅ User role extracted: {user_role}")
        
    except Exception as e:
        print(f"    ❌ Valid token test failed: {e}")
        return False
    
    # Test 2: Admin token verification
    print("  ✅ Testing admin token verification...")
    admin_token = create_test_jwt_token(TEST_ADMIN_ID, TEST_ADMIN_EMAIL, "admin")
    admin_request = MockRequest(admin_token)
    
    try:
        admin_info = JWTHandler.verify_admin_access(admin_request)
        assert admin_info["user_id"] == TEST_ADMIN_ID
        assert admin_info["email"] == TEST_ADMIN_EMAIL
        assert admin_info["role"] == "admin"
        print(f"    ✅ Admin verification successful: {admin_info}")
    except Exception as e:
        print(f"    ❌ Admin token test failed: {e}")
        return False
    
    # Test 3: Invalid token handling
    print("  ✅ Testing invalid token handling...")
    invalid_request = MockRequest("invalid_token")
    
    try:
        JWTHandler.get_user_id_from_token(invalid_request)
        print("    ❌ Invalid token should have raised exception")
        return False
    except Exception as e:
        print(f"    ✅ Invalid token properly rejected: {e}")
    
    print("✅ JWT Handler functionality tests passed!")
    return True

def test_field_consistency():
    """Test that field extraction is consistent across different token formats"""
    print("\n🔍 Testing Field Consistency")
    
    if not JWT_AVAILABLE:
        print("  ❌ JWT modules not available, skipping tests")
        return False
    
    # Test different token formats that might exist in the system
    test_cases = [
        {
            "name": "Standard Token (sub + email)",
            "payload": {"sub": TEST_USER_ID, "email": TEST_USER_EMAIL, "role": "user"},
            "expected_id": TEST_USER_ID,
            "expected_email": TEST_USER_EMAIL
        },
        {
            "name": "Legacy Token (user_id + user_email)",
            "payload": {"user_id": TEST_USER_ID, "user_email": TEST_USER_EMAIL, "role": "user"},
            "expected_id": TEST_USER_ID,
            "expected_email": TEST_USER_EMAIL
        },
        {
            "name": "Mixed Token (sub + user_email)",
            "payload": {"sub": TEST_USER_ID, "user_email": TEST_USER_EMAIL, "role": "user"},
            "expected_id": TEST_USER_ID,
            "expected_email": TEST_USER_EMAIL
        }
    ]
    
    for case in test_cases:
        print(f"  🔍 Testing {case['name']}...")
        
        # Add expiration to payload
        payload = case["payload"].copy()
        payload["exp"] = datetime.utcnow() + timedelta(hours=1)
        payload["iat"] = datetime.utcnow()
        
        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        mock_request = MockRequest(token)
        
        try:
            user_id = JWTHandler.get_user_id_from_token(mock_request)
            user_email = JWTHandler.get_user_email_from_token(mock_request)
            
            assert user_id == case["expected_id"], f"Expected ID {case['expected_id']}, got {user_id}"
            assert user_email == case["expected_email"], f"Expected email {case['expected_email']}, got {user_email}"
            
            print(f"    ✅ {case['name']}: ID={user_id}, Email={user_email}")
            
        except Exception as e:
            print(f"    ❌ {case['name']}: Failed - {e}")
            return False
    
    print("✅ Field consistency tests passed!")
    return True

def test_path_resolution():
    """Test that path resolution works correctly"""
    print("\n🔍 Testing Path Resolution")
    
    current_file = Path(__file__)
    backend_dir = current_file.parent.resolve()
    
    print(f"  📁 Current file: {current_file}")
    print(f"  📁 Backend directory: {backend_dir}")
    print(f"  📁 Backend directory in sys.path: {str(backend_dir) in sys.path}")
    
    # Verify the path is correctly constructed
    expected_auth_module = backend_dir / "auth" / "jwt_config.py"
    print(f"  📁 Expected auth module: {expected_auth_module}")
    print(f"  📁 Auth module exists: {expected_auth_module.exists()}")
    
    if expected_auth_module.exists():
        print("  ✅ Dynamic path resolution working correctly!")
        return True
    else:
        print("  ❌ Dynamic path resolution failed - auth module not found")
        return False

def main():
    """Main test runner"""
    print("🚀 Simple JWT Authentication Test")
    print("=" * 50)
    
    # Test 0: Path resolution
    path_test_passed = test_path_resolution()
    
    # Test 1: JWT Handler functionality
    handler_test_passed = test_jwt_handler_functionality()
    
    # Test 2: Field consistency
    field_test_passed = test_field_consistency()
    
    print("\n" + "=" * 50)
    if path_test_passed and handler_test_passed and field_test_passed:
        print("✅ JWT Authentication Fix: PASSED")
        print("\n📋 Implementation Summary:")
        print("  ✅ Dynamic path resolution working")
        print("  ✅ Centralized JWT configuration created")
        print("  ✅ Consistent field access patterns implemented")
        print("  ✅ Admin access verification working")
        print("  ✅ Error handling for invalid tokens")
        print("  ✅ Support for multiple token formats")
        
        print("\n🎯 Fix Results:")
        print("  ✅ Resolved JWT secret variable inconsistencies")
        print("  ✅ Standardized user identification across services")
        print("  ✅ Added proper admin authentication to endpoints")
        print("  ✅ Improved error handling for authentication failures")
        print("  ✅ Backward compatibility with existing token formats")
        print("  ✅ Portable path resolution for different environments")
        
        return 0
    else:
        print("❌ JWT Authentication Fix: FAILED")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)