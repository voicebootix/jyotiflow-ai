#!/usr/bin/env python3
"""
🎯 FINAL TARGETED FIX: Fix indentation in committed code
Line 86 return statement is incorrectly dedented in facebook_service.py
Following core.md & refresh.md: minimal precise fix
"""

def fix_committed_indentation():
    """Fix the specific indentation issue in the committed code"""
    
    print("🔧 Fixing indentation in committed facebook_service.py...")
    
    with open("services/facebook_service.py", 'r') as f:
        content = f.read()
    
    # Fix the specific issue: line 86 return statement
    old_section = '''                    if response.status == 200 and "id" in data:
                return {
                    "success": True,
                            "message": f"Access token valid for user: {data.get('name', 'Unknown')}",
                            "user_id": data["id"]
                }'''
    
    new_section = '''                    if response.status == 200 and "id" in data:
                        return {
                            "success": True,
                            "message": f"Access token valid for user: {data.get('name', 'Unknown')}",
                            "user_id": data["id"]
                        }'''
    
    content = content.replace(old_section, new_section)
    
    with open("services/facebook_service.py", 'w') as f:
        f.write(content)
    
    print("✅ Specific indentation issue fixed")

def test_all_services():
    """Test all service files for syntax errors"""
    services = ['facebook_service.py', 'instagram_service.py', 'tiktok_service.py']
    all_good = True
    
    for service in services:
        try:
            with open(f"services/{service}", 'r') as f:
                compile(f.read(), f"services/{service}", 'exec')
            print(f"✅ {service} - syntax OK")
        except Exception as e:
            print(f"❌ {service} - error: {e}")
            all_good = False
    
    return all_good

if __name__ == "__main__":
    print("🎯 FINAL COMMITTED CODE FIX")
    print("=" * 35)
    
    fix_committed_indentation()
    
    if test_all_services():
        print("\n🎉 ALL SERVICES FIXED SUCCESSFULLY!")
        print("Application should start normally now.")
    else:
        print("\n⚠️ Some issues remain - checking other services...") 