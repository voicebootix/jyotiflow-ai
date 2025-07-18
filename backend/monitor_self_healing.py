"""
Production Monitoring for Database Self-Healing System
Run this to monitor the system once deployed
"""

import os
import asyncio
import asyncpg
import json
from datetime import datetime, timedelta, timezone
from collections import defaultdict

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")

class ProductionMonitor:
    """Monitor self-healing system in production"""
    
    def __init__(self):
        self.database_url = DATABASE_URL
        self.metrics = defaultdict(int)
        self.start_time = None
        
    async def monitor_continuous(self, duration_hours=24):
        """Monitor system for specified duration"""
        print(f"🔍 Starting {duration_hours}-hour production monitoring...")
        print("Press Ctrl+C to stop early\n")
        
        self.start_time = datetime.now(timezone.utc)
        end_time = self.start_time + timedelta(hours=duration_hours)
        
        try:
            while datetime.now(timezone.utc) < end_time:
                await self.check_health()
                await self.check_fixes()
                await self.check_errors()
                await self.check_performance()
                
                # Print summary
                self.print_summary()
                
                # Wait 5 minutes
                await asyncio.sleep(300)
                
        except KeyboardInterrupt:
            print("\n⏹️  Monitoring stopped by user")
        
        # Final report
        self.print_final_report()
    
    async def check_health(self):
        """Check system health status"""
        import db
        pool = db.get_db_pool()
        if not pool:
                return None
        async with pool.acquire() as conn:
            # Get latest health check
            result = await conn.fetchrow("""
                SELECT * FROM health_check_results
                ORDER BY timestamp DESC
                LIMIT 1
            """)
            
            if result:
                self.metrics['total_checks'] += 1
                self.metrics['issues_found'] += result['issues_found']
                self.metrics['issues_fixed'] += result['issues_fixed']
                
                if result['critical_count'] > 0:
                    self.metrics['checks_with_critical'] += 1
                
                # Check if health checks are running regularly
                from datetime import timezone
                now_utc = datetime.now(timezone.utc)
                timestamp = result['timestamp']
                if timestamp.tzinfo is None:
                    # If timestamp is naive, assume UTC
                    timestamp = timestamp.replace(tzinfo=timezone.utc)
                age = now_utc - timestamp
                if age > timedelta(minutes=10):
                    print(f"⚠️  Last health check was {age.total_seconds()/60:.0f} minutes ago")
                    self.metrics['missed_checks'] += 1
    
    async def check_fixes(self):
        """Check what fixes have been applied"""
        import db
        pool = db.get_db_pool()
        if not pool:
            return None
        async with pool.acquire() as conn:
            # Get recent fixes
            fixes = await conn.fetch("""
                SELECT * FROM database_backups
                WHERE created_at > NOW() - INTERVAL '1 hour'
                ORDER BY created_at DESC
            """)
            
            for fix in fixes:
                self.metrics[f'fix_{fix["issue_type"]}'] += 1
                print(f"🔧 Recent fix: {fix['table_name']}.{fix['column_name']} - {fix['issue_type']}")
    
    async def check_errors(self):
        """Check for any errors"""
        import db
        pool = db.get_db_pool()
        if not pool:
            return None
        async with pool.acquire() as conn:
            # Check for failed health checks
            failed = await conn.fetch("""
                SELECT * FROM health_check_results
                WHERE results::text LIKE '%"error":%'
                AND timestamp > NOW() - INTERVAL '1 hour'
            """)
            
            if failed:
                self.metrics['errors'] += len(failed)
                for record in failed:
                    results = json.loads(record['results'])
                    if 'error' in results:
                        print(f"❌ Error at {record['timestamp']}: {results['error']}")
    
    async def check_performance(self):
        """Check system performance"""
        import db
        pool = db.get_db_pool()
        if not pool:
                return None
        async with pool.acquire() as conn:
            # Get average health check duration
            perf_data = await conn.fetch("""
                SELECT 
                    results->'performance_metrics'->'full_check' as duration
                FROM health_check_results
                WHERE timestamp > NOW() - INTERVAL '1 hour'
                AND results->'performance_metrics' IS NOT NULL
            """)
            
            if perf_data:
                durations = [float(p['duration']) for p in perf_data if p['duration']]
                if durations:
                    avg_duration = sum(durations) / len(durations)
                    self.metrics['avg_check_duration'] = avg_duration
                    
                    if avg_duration > 60:
                        print(f"⚠️  Performance warning: Average check duration is {avg_duration:.1f}s")
    
    def print_summary(self):
        """Print current summary"""
        print(f"\n📊 Monitoring Summary @ {datetime.now().strftime('%H:%M:%S')}")
        print("="*50)
        print(f"Total Health Checks: {self.metrics['total_checks']}")
        print(f"Issues Found: {self.metrics['issues_found']}")
        print(f"Issues Fixed: {self.metrics['issues_fixed']}")
        print(f"Checks with Critical Issues: {self.metrics['checks_with_critical']}")
        print(f"Missed Checks: {self.metrics['missed_checks']}")
        print(f"Errors: {self.metrics['errors']}")
        
        if self.metrics['avg_check_duration']:
            print(f"Avg Check Duration: {self.metrics['avg_check_duration']:.1f}s")
        
        # Fix breakdown
        fix_types = [k for k in self.metrics.keys() if k.startswith('fix_')]
        if fix_types:
            print("\nFixes Applied:")
            for fix_type in fix_types:
                count = self.metrics[fix_type]
                issue_type = fix_type.replace('fix_', '')
                print(f"  - {issue_type}: {count}")
        
        print("="*50)
    
    def print_final_report(self):
        """Print final monitoring report"""
        print("\n" + "🏁 FINAL MONITORING REPORT ".center(60, "="))
        
        # Calculate success rate
        if self.metrics['total_checks'] > 0:
            success_rate = (1 - self.metrics['errors'] / self.metrics['total_checks']) * 100
        else:
            success_rate = 0
        
        print(f"\n📈 Success Rate: {success_rate:.1f}%")
        
        # Health status
        if success_rate >= 99:
            print("✅ System is running perfectly!")
        elif success_rate >= 95:
            print("⚠️  System is mostly stable with minor issues")
        else:
            print("❌ System needs attention")
        
        # Recommendations
        print("\n💡 Recommendations:")
        
        if self.metrics['missed_checks'] > 0:
            print("- Check why health checks are not running regularly")
        
        if self.metrics['errors'] > 0:
            print("- Review error logs and fix root causes")
        
        if self.metrics['avg_check_duration'] > 30:
            print("- Optimize performance - checks are taking too long")
        
        if self.metrics['checks_with_critical'] > self.metrics['total_checks'] * 0.1:
            print("- Too many critical issues - review auto-fix settings")
        
        # Save report
        report = {
            'monitoring_period': {
                'start': self.start_time.isoformat() if self.start_time else datetime.now(timezone.utc).isoformat(),
                'duration_hours': 24
            },
            'metrics': dict(self.metrics),
            'success_rate': success_rate
        }
        
        with open('monitoring_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        print("\n📁 Full report saved to monitoring_report.json")
        print("="*60)


async def verify_production_ready():
    """Verify system is production ready"""
    print("🚀 Verifying Production Readiness...\n")
    
    conn = await asyncpg.connect(DATABASE_URL)
    checks_passed = 0
    total_checks = 5
    
    try:
        # 1. Check tables exist
        print("1. Checking required tables...")
        tables = await conn.fetch("""
            SELECT table_name FROM information_schema.tables
            WHERE table_name IN ('database_backups', 'health_check_results')
        """)
        if len(tables) == 2:
            print("   ✅ Required tables exist")
            checks_passed += 1
        else:
            print("   ❌ Missing required tables")
        
        # 2. Check permissions
        print("2. Checking permissions...")
        can_alter = await conn.fetchval("""
            SELECT has_table_privilege(current_user, 'users', 'UPDATE')
        """)
        if can_alter:
            print("   ✅ Has required permissions")
            checks_passed += 1
        else:
            print("   ❌ Missing ALTER permissions")
        
        # 3. Check if monitoring is running
        print("3. Checking if monitoring is active...")
        latest = await conn.fetchrow("""
            SELECT * FROM health_check_results
            ORDER BY timestamp DESC
            LIMIT 1
        """)
        if latest:
            now_utc = datetime.now(timezone.utc)
            timestamp = latest['timestamp']
            if timestamp.tzinfo is None:
                timestamp = timestamp.replace(tzinfo=timezone.utc)
            if (now_utc - timestamp).total_seconds() < 600:
                print("   ✅ Monitoring is active")
                checks_passed += 1
        else:
            print("   ❌ Monitoring not active")
        
        # 4. Check for critical issues
        print("4. Checking for unresolved critical issues...")
        if latest and latest['critical_count'] == 0:
            print("   ✅ No critical issues")
            checks_passed += 1
        else:
            print(f"   ⚠️  {latest['critical_count'] if latest else 'Unknown'} critical issues")
        
        # 5. Check system performance
        print("5. Checking system performance...")
        if latest and latest['results']:
            results = json.loads(latest['results'])
            if 'performance_metrics' in results:
                duration = results['performance_metrics'].get('full_check', 999)
                if duration < 30:
                    print(f"   ✅ Good performance ({duration:.1f}s)")
                    checks_passed += 1
                else:
                    print(f"   ⚠️  Slow performance ({duration:.1f}s)")
    
        # Final verdict
        print(f"\n🎯 Production Readiness: {checks_passed}/{total_checks}")
        
        if checks_passed == total_checks:
            print("✅ System is ready for production!")
            return True
        elif checks_passed >= 3:
            print("⚠️  System is mostly ready but needs some fixes")
            return False
        else:
            print("❌ System is not ready for production")
            return False
    
    except Exception as e:
        print(f"❌ Error during production readiness check: {e}")
        return False
    finally:
        await conn.close()


async def main():
    """Main monitoring function"""
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "verify":
            # Just verify readiness
            ready = await verify_production_ready()
            sys.exit(0 if ready else 1)
        
        elif command == "monitor":
            # Run continuous monitoring
            duration = int(sys.argv[2]) if len(sys.argv) > 2 else 24
            monitor = ProductionMonitor()
            await monitor.monitor_continuous(duration)
        
    else:
        print("Usage:")
        print("  python monitor_self_healing.py verify     # Check if ready")
        print("  python monitor_self_healing.py monitor    # Monitor for 24 hours")
        print("  python monitor_self_healing.py monitor 48 # Monitor for 48 hours")


if __name__ == "__main__":
    asyncio.run(main())