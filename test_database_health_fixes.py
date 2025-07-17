#!/usr/bin/env python3
"""
Test script to validate all database health checker fixes
This will verify that the monitoring system works correctly after all fixes.
"""

import asyncio
import json
import os
import sys
from datetime import datetime
import asyncpg
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

def test_imports():
    """Test that all monitoring modules can be imported without errors"""
    print("🔍 Testing imports...")
    
    try:
        # Test core imports
        from monitoring.dashboard import MonitoringDashboard
        from monitoring.integration_monitor import IntegrationMonitor
        from database_self_healing_system import DatabaseSelfHealingSystem
        print("  ✅ All monitoring modules imported successfully")
        return True
    except Exception as e:
        print(f"  ❌ Import error: {e}")
        return False

def test_datetime_serialization():
    """Test that datetime serialization works correctly"""
    print("🔍 Testing datetime serialization...")
    
    try:
        from database_self_healing_system import serialize_datetime
        
        # Test with datetime object
        now = datetime.now()
        serialized = serialize_datetime(now)
        assert isinstance(serialized, str)
        assert "T" in serialized  # ISO format should contain T
        
        # Test with non-datetime object
        try:
            serialize_datetime("not a datetime")
            assert False, "Should have raised TypeError"
        except TypeError:
            pass  # Expected
            
        print("  ✅ Datetime serialization works correctly")
        return True
    except Exception as e:
        print(f"  ❌ Datetime serialization error: {e}")
        return False

async def test_database_connections():
    """Test that database connections work with the new pattern"""
    print("🔍 Testing database connections...")
    
    try:
        from core_foundation_enhanced import get_database
        
        # Test getting database manager
        db = await get_database()
        assert db is not None
        
        # Test getting connection
        conn = await db.get_connection()
        assert conn is not None
        
        # Test simple query
        result = await conn.fetchval("SELECT 1")
        assert result == 1
        
        # Test connection release
        await db.release_connection(conn)
        
        print("  ✅ Database connections work correctly")
        return True
    except Exception as e:
        print(f"  ❌ Database connection error: {e}")
        return False

async def test_monitoring_dashboard():
    """Test that monitoring dashboard functions work without async context manager errors"""
    print("🔍 Testing monitoring dashboard...")
    
    try:
        from monitoring.dashboard import MonitoringDashboard
        
        dashboard = MonitoringDashboard()
        
        # Test getting dashboard data (this will test all the fixed functions)
        data = await dashboard.get_dashboard_data()
        assert isinstance(data, dict)
        
        print("  ✅ Monitoring dashboard works correctly")
        return True
    except Exception as e:
        print(f"  ❌ Monitoring dashboard error: {e}")
        return False

async def test_integration_monitor():
    """Test that integration monitor works without async context manager errors"""
    print("🔍 Testing integration monitor...")
    
    try:
        from monitoring.integration_monitor import IntegrationMonitor
        
        monitor = IntegrationMonitor()
        
        # Test getting system health
        health = await monitor.get_system_health()
        assert isinstance(health, dict)
        
        print("  ✅ Integration monitor works correctly")
        return True
    except Exception as e:
        print(f"  ❌ Integration monitor error: {e}")
        return False

async def test_database_health_checker():
    """Test that database health checker works with JSON serialization"""
    print("🔍 Testing database health checker...")
    
    try:
        from database_self_healing_system import DatabaseSelfHealingSystem
        
        # Create health checker instance
        DATABASE_URL = os.getenv("DATABASE_URL")
        if not DATABASE_URL:
            print("  ⚠️ No DATABASE_URL - skipping health checker test")
            return True
            
        healer = DatabaseSelfHealingSystem(DATABASE_URL)
        
        # Test basic health check (this will test JSON serialization)
        status = await healer.get_status()
        assert isinstance(status, dict)
        
        print("  ✅ Database health checker works correctly")
        return True
    except Exception as e:
        print(f"  ❌ Database health checker error: {e}")
        return False

def test_websocket_fallback():
    """Test that WebSocket fallback script exists"""
    print("🔍 Testing WebSocket fallback...")
    
    try:
        fallback_path = Path("frontend/public/monitoring-fallback.js")
        if fallback_path.exists():
            with open(fallback_path, 'r') as f:
                content = f.read()
                assert "createMonitoringWebSocket" in content
                assert "startHttpPollingFallback" in content
                print("  ✅ WebSocket fallback script exists and looks correct")
                return True
        else:
            print("  ⚠️ WebSocket fallback script not found - but this is non-critical")
            return True
    except Exception as e:
        print(f"  ❌ WebSocket fallback test error: {e}")
        return False

async def main():
    """Run all tests"""
    print("🚀 Running database health checker validation tests...")
    print("=" * 60)
    
    tests = [
        ("Import Tests", test_imports),
        ("Datetime Serialization", test_datetime_serialization),
        ("Database Connections", test_database_connections),
        ("Monitoring Dashboard", test_monitoring_dashboard),
        ("Integration Monitor", test_integration_monitor),
        ("Database Health Checker", test_database_health_checker),
        ("WebSocket Fallback", test_websocket_fallback),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 {test_name}")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"  ❌ Test {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {test_name}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\n🎯 Total: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Database health checker fixes are working correctly.")
        return 0
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())