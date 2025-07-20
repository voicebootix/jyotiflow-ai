#!/usr/bin/env python3
"""
🎯 FINAL FIX: Facebook service line 71 indentation issue
"""

def fix_line_71():
    with open("services/facebook_service.py", 'r') as f:
        content = f.read()
    
    # Fix the specific line 71 issue
    old_section = '''        except Exception as e:
            logger.error(f"Facebook credential validation error: {e}")
                        return {
                "success": False,
                "error": f"Facebook API validation failed: {str(e)}"
            }'''
    
    new_section = '''        except Exception as e:
            logger.error(f"Facebook credential validation error: {e}")
            return {
                "success": False,
                "error": f"Facebook API validation failed: {str(e)}"
            }'''
    
    content = content.replace(old_section, new_section)
    
    with open("services/facebook_service.py", 'w') as f:
        f.write(content)
    
    print("✅ Line 71 indentation fixed")

def final_test():
    try:
        with open("services/facebook_service.py", 'r') as f:
            compile(f.read(), "services/facebook_service.py", 'exec')
        print("✅ Facebook service - COMPLETELY FIXED!")
        return True
    except Exception as e:
        print(f"❌ Still has error: {e}")
        return False

if __name__ == "__main__":
    fix_line_71()
    final_test() 