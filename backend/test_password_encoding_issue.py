#!/usr/bin/env python3
"""
Test script to verify password encoding issue in authentication system
"""

import bcrypt

def test_password_encoding_issue():
    """Test the password encoding issue that might cause login failures"""
    
    print("🧪 Testing Password Encoding Issue")
    print("=" * 50)
    
    # Test password
    test_password = "testpassword123"
    
    # 1. Simulate REGISTRATION process (from auth.py line 66)
    print("\n1. 📝 REGISTRATION PROCESS:")
    print(f"   Original password: {test_password}")
    
    # Hash password and decode to string (as done in registration)
    password_hash = bcrypt.hashpw(test_password.encode(), bcrypt.gensalt()).decode()
    print(f"   Hashed and decoded: {password_hash}")
    print(f"   Hash type: {type(password_hash)}")
    
    # 2. Simulate LOGIN process (from auth.py line 44)  
    print("\n2. 🔐 LOGIN PROCESS:")
    print(f"   Stored hash: {password_hash}")
    print(f"   Stored hash type: {type(password_hash)}")
    
    # Re-encode the hash before verification (as done in login)
    encoded_hash = password_hash.encode()
    print(f"   Re-encoded hash: {encoded_hash}")
    print(f"   Re-encoded hash type: {type(encoded_hash)}")
    
    # 3. Test password verification
    print("\n3. ✅ PASSWORD VERIFICATION:")
    
    # Test with correct approach (no double encoding)
    correct_result = bcrypt.checkpw(test_password.encode(), password_hash.encode())
    print(f"   Correct verification: {correct_result}")
    
    # Test with wrong password
    wrong_result = bcrypt.checkpw("wrongpassword".encode(), password_hash.encode())
    print(f"   Wrong password verification: {wrong_result}")
    
    # 4. Test potential issue with string vs bytes
    print("\n4. 🔍 POTENTIAL ISSUES:")
    
    # Test if the hash is properly formatted
    try:
        # This should work if hash is properly formatted
        bcrypt_result = bcrypt.checkpw(test_password.encode(), password_hash.encode())
        print(f"   bcrypt.checkpw() result: {bcrypt_result}")
    except Exception as e:
        print(f"   ❌ bcrypt.checkpw() failed: {e}")
    
    # 5. Test different encoding scenarios
    print("\n5. 🧪 ENCODING SCENARIOS:")
    
    # Scenario A: Store as bytes (wrong)
    try:
        hash_as_bytes = bcrypt.hashpw(test_password.encode(), bcrypt.gensalt())
        print(f"   Hash as bytes: {hash_as_bytes}")
        print(f"   Hash as bytes type: {type(hash_as_bytes)}")
        
        # This might fail if stored as bytes in database
        verify_bytes = bcrypt.checkpw(test_password.encode(), hash_as_bytes)
        print(f"   Verify from bytes: {verify_bytes}")
    except Exception as e:
        print(f"   ❌ Bytes scenario failed: {e}")
    
    # Scenario B: Store as string (current approach)
    try:
        hash_as_string = bcrypt.hashpw(test_password.encode(), bcrypt.gensalt()).decode()
        print(f"   Hash as string: {hash_as_string}")
        print(f"   Hash as string type: {type(hash_as_string)}")
        
        # Verify from string (re-encode)
        verify_string = bcrypt.checkpw(test_password.encode(), hash_as_string.encode())
        print(f"   Verify from string: {verify_string}")
    except Exception as e:
        print(f"   ❌ String scenario failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 CONCLUSION:")
    if correct_result:
        print("✅ Password encoding is working correctly")
        print("   Issue might be elsewhere in the authentication flow")
    else:
        print("❌ Password encoding issue detected")
        print("   This could cause login failures after registration")

if __name__ == "__main__":
    test_password_encoding_issue()