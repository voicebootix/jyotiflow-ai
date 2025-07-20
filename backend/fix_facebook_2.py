#!/usr/bin/env python3
"""
Second targeted fix for Facebook service indentation issue at line 129
"""

def fix_facebook_line_129():
    with open("services/facebook_service.py", 'r') as f:
        content = f.read()
    
    # Fix the excessive indentation on return statement
    old_section = '''                        error_msg = data.get("error", {}).get("message", "Invalid app credentials")
                                                 return {
                             "success": False,
                            "error": f"App credentials validation failed: {error_msg}"
                         }'''
    
    new_section = '''                        error_msg = data.get("error", {}).get("message", "Invalid app credentials")
                        return {
                            "success": False,
                            "error": f"App credentials validation failed: {error_msg}"
                        }'''
    
    content = content.replace(old_section, new_section)
    
    with open("services/facebook_service.py", 'w') as f:
        f.write(content)
    
    print("✅ Facebook service line 129 indentation fixed")

if __name__ == "__main__":
    fix_facebook_line_129() 