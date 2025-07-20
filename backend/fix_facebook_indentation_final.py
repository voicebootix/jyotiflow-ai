#!/usr/bin/env python3
"""
🎯 TARGETED FIX: Facebook _analyze_token_type function indentation
Fixes specific issue with return statements in lines 245-257
Following core.md & refresh.md: minimal changes, preserve functionality
"""

def fix_analyze_token_type_indentation():
    """Fix the specific indentation issue in _analyze_token_type function"""
    
    print("🔧 Fixing _analyze_token_type function indentation...")
    
    with open("services/facebook_service.py", 'r') as f:
        content = f.read()
    
    # Fix the excessive indentation on return statements
    old_problematic_block = '''                        if has_page_fields and not has_user_fields:
                                return {
                                "is_page_token": True, 
                                "token_type": "page",
                                "detection_method": "explicit_page_fields",
                                "page_name": data.get("name")
                                }
                        elif has_user_fields and not has_page_fields:
                                return {
                                "is_page_token": False, 
                                "token_type": "user",
                                "detection_method": "explicit_user_fields",
                                "user_name": data.get("name")
                                }'''
    
    new_correct_block = '''                        if has_page_fields and not has_user_fields:
                            return {
                                "is_page_token": True, 
                                "token_type": "page",
                                "detection_method": "explicit_page_fields",
                                "page_name": data.get("name")
                            }
                        elif has_user_fields and not has_page_fields:
                            return {
                                "is_page_token": False, 
                                "token_type": "user",
                                "detection_method": "explicit_user_fields",
                                "user_name": data.get("name")
                            }'''
    
    content = content.replace(old_problematic_block, new_correct_block)
    
    with open("services/facebook_service.py", 'w') as f:
        f.write(content)
    
    print("✅ _analyze_token_type function indentation fixed")

def test_facebook_syntax():
    """Test Facebook service for syntax errors after fix"""
    print("\n🧪 Testing Facebook service syntax...")
    
    try:
        with open("services/facebook_service.py", 'r') as f:
            compile(f.read(), "services/facebook_service.py", 'exec')
        print("✅ Facebook service - syntax OK")
        return True
    except SyntaxError as e:
        print(f"❌ Facebook service - syntax error: {e}")
        return False
    except IndentationError as e:
        print(f"❌ Facebook service - indentation error: {e}")
        return False

if __name__ == "__main__":
    print("🎯 TARGETED FACEBOOK INDENTATION FIX")
    print("=" * 45)
    
    fix_analyze_token_type_indentation()
    
    if test_facebook_syntax():
        print("\n🎉 Facebook service fixed successfully!")
        print("The _analyze_token_type function should now work correctly.")
    else:
        print("\n⚠️ Additional issues remain - manual inspection needed.") 