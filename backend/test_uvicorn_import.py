#!/usr/bin/env python3
"""Test how uvicorn loads the main module"""

import sys
import os

# When running "python -m uvicorn main:app" from backend directory,
# the current directory is added to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

print(f"Current directory: {os.getcwd()}")
print(f"Script directory: {current_dir}")
print(f"Python path includes backend: {current_dir in sys.path}")

# Test importing main module
try:
    import main
    print("✅ Can import main module")
    
    # Now test if main can import simple_unified_startup
    # This simulates what happens in the lifespan function
    try:
        from simple_unified_startup import initialize_unified_jyotiflow, cleanup_unified_system
        print("✅ SUCCESS: Absolute import of simple_unified_startup works!")
    except ImportError as e:
        print(f"❌ FAILED: Cannot import simple_unified_startup: {e}")
        
except ImportError as e:
    print(f"❌ Cannot import main: {e}")