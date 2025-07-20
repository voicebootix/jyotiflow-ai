#!/usr/bin/env python3
"""
Manual fix for Facebook service indentation
"""

def fix_facebook_indentation():
    with open("services/facebook_service.py", 'r') as f:
        content = f.read()
    
    # Find and replace the problematic section
    old_section = '''                return {
                    "success": True,
                            "message": f"Access token valid for user: {data.get('name', 'Unknown')}",
                            "user_id": data["id"]
                }
            else:
                        error_msg = data.get("error", {}).get("message", "Invalid access token")
                        return {
                            "success": False,
                            "error": f"Access token validation failed: {error_msg}"
                        }'''
    
    new_section = '''                        return {
                            "success": True,
                            "message": f"Access token valid for user: {data.get('name', 'Unknown')}",
                            "user_id": data["id"]
                        }
                    else:
                        error_msg = data.get("error", {}).get("message", "Invalid access token")
                        return {
                            "success": False,
                            "error": f"Access token validation failed: {error_msg}"
                        }'''
    
    content = content.replace(old_section, new_section)
    
    with open("services/facebook_service.py", 'w') as f:
        f.write(content)
    
    print("✅ Facebook service indentation fixed")

if __name__ == "__main__":
    fix_facebook_indentation() 