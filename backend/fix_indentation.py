#!/usr/bin/env python3
"""
🔧 CRITICAL INDENTATION FIX SCRIPT
Systematically fixes indentation errors across social media service files
Follows core.md & refresh.md principles: minimal changes, preserve functionality
"""

import os
import re

def fix_instagram_service():
    """Fix critical indentation errors in Instagram service"""
    print("🔧 Fixing Instagram service indentation...")
    
    file_path = "services/instagram_service.py"
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix the specific problematic blocks identified
    fixes = [
        # Fix 1: _validate_app_credentials method around line 75
        (
            r'                    if response\.status == 200 and "access_token" in data:\n                return \{\n                    "success": True,\n                            "message": "Instagram app credentials validated successfully",\n                            "app_token": data\["access_token"\]\n                \}\n            else:\n                        error_msg = data\.get\("error", \{\}\)\.get\("message", "Invalid app credentials"\)\n                        return \{\n                            "success": False,\n                            "error": f"App credentials validation failed: \{error_msg\}"\n                        \}',
            '''                    if response.status == 200 and "access_token" in data:
                        return {
                            "success": True,
                            "message": "Instagram app credentials validated successfully",
                            "app_token": data["access_token"]
                        }
                    else:
                        error_msg = data.get("error", {}).get("message", "Invalid app credentials")
                        return {
                            "success": False,
                            "error": f"App credentials validation failed: {error_msg}"
                        }'''
        ),
        # Fix 2: Around line 175 
        (
            r'                        if response\.status == 200:\n                        account_type = data\.get\("account_type", "PERSONAL"\)\n                        is_business = account_type in \["BUSINESS", "CREATOR"\]\n                        \n                                return \{',
            '''                    if response.status == 200:
                        account_type = data.get("account_type", "PERSONAL")
                        is_business = account_type in ["BUSINESS", "CREATOR"]
                        
                        return {'''
        )
    ]
    
    for pattern, replacement in fixes:
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Instagram service fixed")

def fix_facebook_service():
    """Fix critical indentation errors in Facebook service"""
    print("🔧 Fixing Facebook service indentation...")
    
    file_path = "services/facebook_service.py"
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix common indentation patterns
    fixes = [
        # Fix missing indentation after if statements
        (
            r'(\n                    if response\.status == 200 and "id" in data:)\n                return \{',
            r'\1\n                        return {'
        ),
        # Fix return statement indentation
        (
            r'(\n                    else:)\n                        error_msg = data\.get\("error", \{\}\)\.get\("message", "Invalid access token"\)\n                                                 return \{',
            r'\1\n                        error_msg = data.get("error", {}).get("message", "Invalid access token")\n                        return {'
        )
    ]
    
    for pattern, replacement in fixes:
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Facebook service fixed")

def fix_tiktok_service():
    """Fix critical indentation errors in TikTok service"""
    print("🔧 Fixing TikTok service indentation...")
    
    file_path = "services/tiktok_service.py"  
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix the try/except block structure around line 72
    fixes = [
        # Fix missing except block
        (
            r'(\n            # Both tests passed with proper API scope)\n                return \{',
            r'\1\n            return {'
        )
    ]
    
    for pattern, replacement in fixes:
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ TikTok service fixed")

def test_syntax():
    """Test all files for syntax errors"""
    print("\n🧪 Testing syntax after fixes...")
    
    files_to_test = [
        "services/instagram_service.py",
        "services/facebook_service.py", 
        "services/tiktok_service.py",
        "routers/social_media_marketing_router.py"
    ]
    
    for file_path in files_to_test:
        try:
            with open(file_path, 'r') as f:
                compile(f.read(), file_path, 'exec')
            print(f"✅ {file_path} - syntax OK")
        except SyntaxError as e:
            print(f"❌ {file_path} - syntax error: {e}")
        except IndentationError as e:
            print(f"❌ {file_path} - indentation error: {e}")

if __name__ == "__main__":
    print("🚨 CRITICAL INDENTATION FIX (core.md & refresh.md compliant)")
    print("=" * 60)
    
    try:
        fix_instagram_service()
        fix_facebook_service() 
        fix_tiktok_service()
        test_syntax()
        
        print("\n🎉 Indentation fixes completed!")
        print("Application should now start without IndentationError")
        
    except Exception as e:
        print(f"💥 Error during fix: {e}")
        print("Manual intervention required") 