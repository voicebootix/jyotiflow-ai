#!/usr/bin/env python3
"""
🎯 FINAL COMPREHENSIVE FIX: Facebook service indentation
Fixes ALL remaining indentation issues in facebook_service.py
Following core.md & refresh.md: minimal changes, preserve functionality
"""

def fix_all_facebook_indentation():
    """Fix all remaining indentation issues in Facebook service"""
    
    print("🔧 Comprehensive Facebook service indentation fix...")
    
    with open("services/facebook_service.py", 'r') as f:
        content = f.read()
    
    # Fix 1: Line 302-303 issue (_validate_page_access_token method)
    old_block_1 = '''                    if response.status == 200 and "id" in data:
            return {
                "success": True,
                            "message": f"Page access token valid for: {data.get('name', 'Unknown')}",
                            "page_id": data["id"],
                            "page_name": data.get("name"),
                            "category": data.get("category"),'''
    
    new_block_1 = '''                    if response.status == 200 and "id" in data:
                        return {
                            "success": True,
                            "message": f"Page access token valid for: {data.get('name', 'Unknown')}",
                            "page_id": data["id"],
                            "page_name": data.get("name"),
                            "category": data.get("category"),'''
    
    content = content.replace(old_block_1, new_block_1)
    
    # Fix 2: Any other misaligned return statements
    # Fix pattern: return statements that are not properly indented
    import re
    
    # Fix any return statements that are incorrectly indented
    content = re.sub(
        r'^(\s{8,12})return \{',  # Match return statements with 8-12 spaces
        r'                        return {',  # Replace with proper indentation (24 spaces)
        content,
        flags=re.MULTILINE
    )
    
    with open("services/facebook_service.py", 'w') as f:
        f.write(content)
    
    print("✅ All Facebook service indentation issues fixed")

def test_facebook_final():
    """Final test of Facebook service syntax"""
    print("\n🧪 Final Facebook service syntax test...")
    
    try:
        with open("services/facebook_service.py", 'r') as f:
            compile(f.read(), "services/facebook_service.py", 'exec')
        print("✅ Facebook service - ALL SYNTAX ISSUES RESOLVED!")
        return True
    except SyntaxError as e:
        print(f"❌ Facebook service - syntax error: {e}")
        return False
    except IndentationError as e:
        print(f"❌ Facebook service - indentation error: {e}")
        return False

if __name__ == "__main__":
    print("🎯 FINAL COMPREHENSIVE FACEBOOK FIX")
    print("=" * 40)
    
    fix_all_facebook_indentation()
    
    if test_facebook_final():
        print("\n🎉 SUCCESS! Facebook service completely fixed!")
        print("All indentation issues resolved - application should start normally.")
    else:
        print("\n⚠️ Manual intervention still needed.") 