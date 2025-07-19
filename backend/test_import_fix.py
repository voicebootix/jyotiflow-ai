#!/usr/bin/env python3
"""Test script to verify import fix for simple_unified_startup"""

import sys
import os

# Add backend directory to path to simulate running from backend/
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Test absolute import
    from simple_unified_startup import initialize_unified_jyotiflow, cleanup_unified_system
    print("✅ SUCCESS: Absolute import works!")
    print(f"   - initialize_unified_jyotiflow: {initialize_unified_jyotiflow}")
    print(f"   - cleanup_unified_system: {cleanup_unified_system}")
except ImportError as e:
    print(f"❌ FAILED: Absolute import failed with error: {e}")

try:
    # Test relative import (this should fail)
    from .simple_unified_startup import initialize_unified_jyotiflow, cleanup_unified_system
    print("✅ Relative import works (unexpected)")
except ImportError as e:
    print(f"❌ Relative import failed (expected): {e}")