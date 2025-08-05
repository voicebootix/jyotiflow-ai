#!/usr/bin/env python3
"""
🔍 ENVIRONMENT CHECK FOR JYOTIFLOW
Check all required environment variables and dependencies
"""

import os
import sys

def check_environment():
    """Check all environment variables and dependencies"""
    
    print("🔍 JyotiFlow Environment Check")
    print("=" * 50)
    
    # Critical Environment Variables
    critical_vars = {
        "STABILITY_API_KEY": "Stability AI image generation",
        "SUPABASE_URL": "Database and storage",
        "SUPABASE_SERVICE_KEY": "Database access",
        "JWT_SECRET": "Authentication security"
    }
    
    print("\n🔑 Critical Environment Variables:")
    print("-" * 35)
    
    missing_vars = []
    for var, description in critical_vars.items():
        value = os.getenv(var)
        if value:
            # Show first 10 chars for security
            display_value = value[:10] + "..." if len(value) > 10 else value
            print(f"✅ {var:<20}: {display_value} ({description})")
        else:
            print(f"❌ {var:<20}: MISSING - {description}")
            missing_vars.append(var)
    
    # Optional Environment Variables
    optional_vars = {
        "DEEP_IMAGE_API_KEY": "Deep Image AI (optional)",
        "OPENAI_API_KEY": "OpenAI services (optional)",
        "DB_HOST": "Database host",
        "DB_NAME": "Database name",
        "DB_USER": "Database user",
        "DB_PASSWORD": "Database password"
    }
    
    print("\n🔧 Optional Environment Variables:")
    print("-" * 35)
    
    for var, description in optional_vars.items():
        value = os.getenv(var)
        if value:
            display_value = value[:10] + "..." if len(value) > 10 else value
            print(f"✅ {var:<20}: {display_value} ({description})")
        else:
            print(f"⚠️  {var:<20}: Not set - {description}")
    
    # Python Dependencies Check
    print("\n📦 Python Dependencies:")
    print("-" * 25)
    
    critical_packages = [
        "fastapi", "httpx", "asyncpg", "pydantic", 
        "jwt", "PIL", "numpy", "uvicorn"
    ]
    
    missing_packages = []
    for package in critical_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - MISSING")
            missing_packages.append(package)
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 SUMMARY:")
    
    if missing_vars:
        print(f"❌ Missing Environment Variables: {', '.join(missing_vars)}")
    else:
        print("✅ All critical environment variables present")
    
    if missing_packages:
        print(f"❌ Missing Python Packages: {', '.join(missing_packages)}")
        print("🔧 Fix: pip install -r backend/requirements.txt")
    else:
        print("✅ All critical Python packages available")
    
    # Priority 2 Readiness Check
    print("\n🎯 Priority 2 Readiness:")
    stability_ready = bool(os.getenv("STABILITY_API_KEY"))
    supabase_ready = bool(os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_SERVICE_KEY"))
    
    if stability_ready and supabase_ready:
        print("✅ Ready for Priority 2 face preservation testing!")
    else:
        if not stability_ready:
            print("❌ STABILITY_API_KEY required for image generation")
        if not supabase_ready:
            print("❌ SUPABASE_URL and SUPABASE_SERVICE_KEY required for storage")
    
    print("=" * 50)

if __name__ == "__main__":
    check_environment()