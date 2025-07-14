#!/usr/bin/env python3
"""
JWT Secret Generator for JyotiFlow.ai
Generates cryptographically secure JWT secrets for production use
"""

import secrets
import string
import hashlib
import os
import base64

def generate_secure_jwt_secret(length=64):
    """
    Generate a cryptographically secure JWT secret
    
    Args:
        length (int): Length of the secret (minimum 32, recommended 64)
    
    Returns:
        str: Secure JWT secret
    """
    if length < 32:
        raise ValueError("JWT secret must be at least 32 characters long")
    
    # Use a mix of characters including letters, numbers, and symbols
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*()-_=+[]{}|;:,.<>?"
    secret = ''.join(secrets.choice(alphabet) for _ in range(length))
    
    return secret

def generate_base64_jwt_secret(length=48):
    """
    Generate a base64-encoded JWT secret (URL-safe)
    
    Args:
        length (int): Length of the random bytes (will be longer when base64 encoded)
    
    Returns:
        str: Base64-encoded JWT secret
    """
    random_bytes = secrets.token_bytes(length)
    return base64.urlsafe_b64encode(random_bytes).decode('utf-8')

def generate_hex_jwt_secret(length=32):
    """
    Generate a hexadecimal JWT secret
    
    Args:
        length (int): Length of the random bytes (will be double when hex encoded)
    
    Returns:
        str: Hexadecimal JWT secret
    """
    random_bytes = secrets.token_bytes(length)
    return random_bytes.hex()

def validate_jwt_secret_strength(secret):
    """
    Validate the strength of a JWT secret
    
    Args:
        secret (str): JWT secret to validate
    
    Returns:
        dict: Validation results
    """
    results = {
        "valid": True,
        "length_check": len(secret) >= 32,
        "has_uppercase": any(c.isupper() for c in secret),
        "has_lowercase": any(c.islower() for c in secret),
        "has_digits": any(c.isdigit() for c in secret),
        "has_symbols": any(c in "!@#$%^&*()-_=+[]{}|;:,.<>?" for c in secret),
        "entropy_score": len(set(secret)) / len(secret) if secret else 0,
        "warnings": []
    }
    
    # Check for common issues
    if not results["length_check"]:
        results["warnings"].append(f"Secret too short ({len(secret)} chars). Minimum: 32 chars")
        results["valid"] = False
    
    if not results["has_uppercase"]:
        results["warnings"].append("Secret should contain uppercase letters")
    
    if not results["has_lowercase"]:
        results["warnings"].append("Secret should contain lowercase letters")
    
    if not results["has_digits"]:
        results["warnings"].append("Secret should contain digits")
    
    if not results["has_symbols"]:
        results["warnings"].append("Secret should contain symbols for maximum security")
    
    if results["entropy_score"] < 0.5:
        results["warnings"].append("Secret has low entropy (too many repeated characters)")
    
    # Check for predictable patterns
    insecure_patterns = [
        "jyotiflow_secret",
        "secret",
        "jwt_secret",
        "your-secret-key",
        "change-me",
        "default",
        "test",
        "password",
        "123456"
    ]
    
    if secret.lower() in insecure_patterns:
        results["warnings"].append("Secret matches common insecure default")
        results["valid"] = False
    
    return results

def main():
    """Main function to generate and display JWT secrets"""
    print("🔐 JWT Secret Generator for JyotiFlow.ai")
    print("=" * 50)
    
    # Generate different types of secrets
    print("\n1. Standard Mixed Character Secret (Recommended):")
    standard_secret = generate_secure_jwt_secret(64)
    print(f"   {standard_secret}")
    
    print("\n2. Base64 URL-Safe Secret:")
    base64_secret = generate_base64_jwt_secret(48)
    print(f"   {base64_secret}")
    
    print("\n3. Hexadecimal Secret:")
    hex_secret = generate_hex_jwt_secret(32)
    print(f"   {hex_secret}")
    
    # Validate the generated secrets
    print("\n🔍 Security Validation:")
    print("-" * 30)
    
    secrets_to_validate = [
        ("Standard", standard_secret),
        ("Base64", base64_secret),
        ("Hex", hex_secret)
    ]
    
    for name, secret in secrets_to_validate:
        validation = validate_jwt_secret_strength(secret)
        status = "✅ VALID" if validation["valid"] else "❌ INVALID"
        print(f"{name}: {status} (Length: {len(secret)}, Entropy: {validation['entropy_score']:.2f})")
        
        if validation["warnings"]:
            for warning in validation["warnings"]:
                print(f"  ⚠️  {warning}")
    
    # Usage instructions
    print("\n📋 Usage Instructions:")
    print("-" * 30)
    print("1. Copy one of the generated secrets above")
    print("2. Set it as an environment variable:")
    print("   export JWT_SECRET='your_generated_secret_here'")
    print("3. For production deployment, add to your .env file:")
    print("   JWT_SECRET=your_generated_secret_here")
    print("4. Never commit JWT secrets to version control!")
    print("5. Rotate JWT secrets regularly in production")
    
    print("\n⚠️  Security Notes:")
    print("-" * 30)
    print("• Use different secrets for different environments")
    print("• Store secrets securely (environment variables, secret managers)")
    print("• Rotate secrets regularly (every 3-6 months)")
    print("• Monitor for any unauthorized access attempts")
    print("• The secret should be at least 32 characters long")
    print("• Include mixed case, numbers, and symbols for maximum security")

if __name__ == "__main__":
    main()