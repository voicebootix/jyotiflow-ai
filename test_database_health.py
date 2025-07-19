#!/usr/bin/env python3
"""Test script for database self-healing system"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

async def test_database_health():
    """Test the database health system"""
    print("Testing Database Self-Healing System...")
    
    try:
        # Import the database self-healing system
        from database_self_healing_system import DatabaseHealthMonitor, SchemaAnalyzer
        
        # Initialize the schema analyzer
        analyzer = SchemaAnalyzer()
        
        print("\n1. Testing Schema Analysis...")
        try:
            schema = await analyzer.analyze_schema()
            print(f"✅ Schema analysis successful:")
            print(f"   - Tables found: {len(schema.get('tables', []))}")
            print(f"   - Columns found: {len(schema.get('columns', {}))}")
            print(f"   - Constraints found: {len(schema.get('constraints', {}))}")
            print(f"   - Indexes found: {len(schema.get('indexes', {}))}")
            print(f"   - Functions found: {len(schema.get('functions', []))}")
            print(f"   - Triggers found: {len(schema.get('triggers', []))}")
        except Exception as e:
            print(f"❌ Schema analysis failed: {e}")
            print(f"   Error type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
        
        print("\n2. Testing Health Monitor...")
        try:
            monitor = DatabaseHealthMonitor()
            results = await monitor.check_health()
            print(f"✅ Health check completed:")
            print(f"   - Issues found: {results.get('issues_found', 0)}")
            print(f"   - Critical issues: {len(results.get('critical_issues', []))}")
            print(f"   - Warnings: {len(results.get('warnings', []))}")
            if results.get('error'):
                print(f"   - Error: {results['error']}")
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            print(f"   Error type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            
    except Exception as e:
        print(f"❌ Failed to import database self-healing system: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_database_health())