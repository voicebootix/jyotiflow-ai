#!/usr/bin/env python3
"""Simple syntax test for all service files"""

import sys

def test_file(filename):
    try:
        with open(filename, 'r') as f:
            compile(f.read(), filename, 'exec')
        return True, "OK"
    except Exception as e:
        return False, str(e)

# Test all files
files = [
    'services/facebook_service.py',
    'services/instagram_service.py', 
    'services/tiktok_service.py',
    'routers/social_media_marketing_router.py'
]

print("Testing syntax for all files:")
print("=" * 40)

all_good = True
for filename in files:
    success, message = test_file(filename)
    status = "✅ OK" if success else "❌ ERROR"
    print(f"{status:10} {filename}")
    if not success:
        print(f"           {message}")
        all_good = False

print("=" * 40)
if all_good:
    print("🎉 ALL FILES SYNTAX OK!")
else:
    print("⚠️  Some files have syntax errors")

sys.exit(0 if all_good else 1) 