"""
🔍 MONITORING SYSTEM STATUS CHECK
Shows the current state of the integrated monitoring system
"""

import os
import sys
import asyncio
from datetime import datetime
from typing import Dict, Any

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def print_section(title: str, emoji: str = "📊"):
    """Print a formatted section header"""
    print(f"\n{emoji} {title}")
    print("=" * (len(title) + 4))

def print_status(item: str, status: bool, details: str = ""):
    """Print a status line"""
    emoji = "✅" if status else "❌"
    print(f"{emoji} {item}: {'Working' if status else 'Not Working'}")
    if details:
        print(f"   → {details}")

async def check_monitoring_imports():
    """Check if monitoring modules can be imported"""
    print_section("Import Status", "📦")
    
    modules = {
        "monitoring.register_monitoring": ["register_monitoring_system", "init_monitoring"],
        "monitoring.core_integration": ["get_monitoring_middleware", "monitor_endpoint"],
        "monitoring.integration_monitor": ["IntegrationMonitor"],
        "monitoring.context_tracker": ["ContextTracker"],
        "monitoring.business_validator": ["BusinessValidator"],
        "monitoring.dashboard": ["router"]
    }
    
    all_good = True
    for module_name, imports in modules.items():
        try:
            module = __import__(module_name, fromlist=imports)
            for import_name in imports:
                if hasattr(module, import_name):
                    print_status(f"{module_name}.{import_name}", True)
                else:
                    print_status(f"{module_name}.{import_name}", False, "Import exists but attribute missing")
                    all_good = False
        except ImportError as e:
            print_status(module_name, False, str(e))
            all_good = False
    
    return all_good

async def check_database_tables():
    """Check if monitoring tables exist"""
    print_section("Database Tables", "🗄️")
    
    try:
        import asyncpg
        DATABASE_URL = os.getenv("DATABASE_URL")
        
        if not DATABASE_URL:
            print_status("Database Connection", False, "DATABASE_URL not set")
            return False
        
        # Try to connect
        try:
            conn = await asyncpg.connect(DATABASE_URL)
        except:
            print_status("Database Connection", False, "Cannot connect to database")
            return False
        
        # Check tables
        tables = [
            "monitoring_api_calls",
            "monitoring_sessions",
            "monitoring_integration_health",
            "monitoring_integration_metrics",
            "monitoring_alerts",
            "monitoring_context",
            "monitoring_business_metrics"
        ]
        
        all_good = True
        for table in tables:
            exists = await conn.fetchval(f"""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = '{table}'
                )
            """)
            
            if exists:
                count = await conn.fetchval(f"SELECT COUNT(*) FROM {table}")
                print_status(table, True, f"{count} records")
            else:
                print_status(table, False, "Table does not exist")
                all_good = False
        
        await conn.close()
        return all_good
        
    except Exception as e:
        print_status("Database Check", False, str(e))
        return False

async def check_api_endpoints():
    """Check if monitoring API endpoints are accessible"""
    print_section("API Endpoints", "🌐")
    
    try:
        import aiohttp
        
        endpoints = [
            ("/monitoring/dashboard", "GET", "Dashboard"),
            ("/monitoring/api/metrics", "GET", "Metrics API"),
            ("/monitoring/api/health", "GET", "Health API"),
            ("/monitoring/api/sessions", "GET", "Sessions API"),
            ("/monitoring/api/alerts", "GET", "Alerts API")
        ]
        
        all_good = True
        async with aiohttp.ClientSession() as session:
            for endpoint, method, name in endpoints:
                try:
                    url = f"http://localhost:10000{endpoint}"
                    async with session.request(method, url) as response:
                        if response.status == 200:
                            print_status(f"{name} ({endpoint})", True, f"Status: {response.status}")
                        else:
                            print_status(f"{name} ({endpoint})", False, f"Status: {response.status}")
                            all_good = False
                except Exception as e:
                    print_status(f"{name} ({endpoint})", False, f"Error: {str(e)}")
                    all_good = False
        
        return all_good
        
    except ImportError:
        print_status("API Check", False, "aiohttp not installed")
        return False
    except Exception as e:
        print_status("API Check", False, str(e))
        return False

async def check_monitoring_hooks():
    """Check if monitoring hooks are applied to endpoints"""
    print_section("Monitoring Hooks", "🪝")
    
    try:
        # Check if decorators are applied
        from routers import spiritual, sessions
        
        endpoints_to_check = [
            (spiritual.router, "spiritual_guidance", "Spiritual Guidance"),
            (spiritual.router, "birth_chart", "Birth Chart"),
            (sessions.router, "start_session", "Start Session")
        ]
        
        all_good = True
        for router, endpoint_name, display_name in endpoints_to_check:
            # Check if endpoint has monitoring
            found = False
            for route in router.routes:
                if hasattr(route, 'endpoint') and route.endpoint.__name__ == endpoint_name:
                    # Check if monitoring decorator is applied
                    if hasattr(route.endpoint, '__wrapped__'):
                        print_status(f"{display_name} endpoint", True, "Monitoring hook applied")
                        found = True
                    else:
                        print_status(f"{display_name} endpoint", False, "No monitoring hook")
                        all_good = False
                    break
            
            if not found:
                print_status(f"{display_name} endpoint", False, "Endpoint not found")
                all_good = False
        
        return all_good
        
    except Exception as e:
        print_status("Hook Check", False, str(e))
        return False

async def check_integration_status():
    """Check overall integration status"""
    print_section("Integration Status", "🔌")
    
    try:
        # Check if monitoring is initialized in main.py
        with open("main.py", "r") as f:
            main_content = f.read()
        
        checks = [
            ("Monitoring import", "from monitoring.register_monitoring" in main_content),
            ("Monitoring registration", "register_monitoring_system(app)" in main_content),
            ("Monitoring initialization", "await init_monitoring()" in main_content),
            ("Middleware integration", "get_monitoring_middleware" in main_content)
        ]
        
        all_good = True
        for check_name, check_result in checks:
            print_status(check_name, check_result)
            if not check_result:
                all_good = False
        
        return all_good
        
    except Exception as e:
        print_status("Integration Check", False, str(e))
        return False

async def main():
    """Run all monitoring checks"""
    print("🚀 JyotiFlow.ai Integrated Monitoring System Status")
    print("=" * 50)
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Run all checks
    results = {
        "imports": await check_monitoring_imports(),
        "database": await check_database_tables(),
        "api": await check_api_endpoints(),
        "hooks": await check_monitoring_hooks(),
        "integration": await check_integration_status()
    }
    
    # Summary
    print_section("Summary", "📈")
    
    total_checks = len(results)
    passed_checks = sum(1 for v in results.values() if v)
    
    print(f"Total Checks: {total_checks}")
    print(f"Passed: {passed_checks}")
    print(f"Failed: {total_checks - passed_checks}")
    
    if all(results.values()):
        print("\n✅ MONITORING SYSTEM IS FULLY OPERATIONAL!")
        print("The integrated monitoring system is working as intended.")
    else:
        print("\n⚠️  MONITORING SYSTEM NEEDS ATTENTION")
        print("Some components are not working properly:")
        for component, status in results.items():
            if not status:
                print(f"  - Fix {component}")
    
    # Recommendations
    if not results["database"]:
        print("\n💡 To fix database issues:")
        print("   1. Set DATABASE_URL environment variable")
        print("   2. Run: python create_monitoring_tables.py")
    
    if not results["api"]:
        print("\n💡 To fix API issues:")
        print("   1. Ensure the application is running on port 10000")
        print("   2. Check that monitoring router is registered")
    
    if not results["hooks"]:
        print("\n💡 To fix hook issues:")
        print("   1. Apply @MonitoringHooks.monitor_session decorators")
        print("   2. Or use the new @monitor_endpoint decorator")

if __name__ == "__main__":
    asyncio.run(main())