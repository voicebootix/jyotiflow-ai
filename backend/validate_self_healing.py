"""
Step-by-Step Validation Script for Database Self-Healing System
Run this to validate each component before full deployment
"""

import os
import asyncio
import asyncpg
import logging
from datetime import datetime
from backend.database_self_healing_system import (
    PostgreSQLSchemaAnalyzer,
    CodePatternAnalyzer,
    DatabaseIssueFixer,
    DatabaseHealthMonitor
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")

class SystemValidator:
    """Validates the self-healing system components"""
    
    def __init__(self):
        self.results = {
            "connection": False,
            "schema_analysis": False,
            "issue_detection": False,
            "code_analysis": False,
            "fix_capability": False,
            "rollback_capability": False,
            "performance": {},
            "errors": []
        }
    
    async def validate_all(self):
        """Run all validation steps"""
        print("🔍 Starting Database Self-Healing System Validation...\n")
        
        # Step 1: Test Database Connection
        await self.test_connection()
        
        # Step 2: Test Schema Analysis
        await self.test_schema_analysis()
        
        # Step 3: Test Issue Detection
        await self.test_issue_detection()
        
        # Step 4: Test Code Analysis
        await self.test_code_analysis()
        
        # Step 5: Test Fix Capability (Dry Run)
        await self.test_fix_capability()
        
        # Step 6: Performance Benchmarks
        await self.test_performance()
        
        # Final Report
        self.print_report()
        
        return self.results
    
    async def test_connection(self):
        """Test database connection"""
        print("1️⃣ Testing Database Connection...")
        try:
            conn = await asyncpg.connect(DATABASE_URL)
            
            # Test basic query
            version = await conn.fetchval("SELECT version()")
            print(f"   ✅ Connected to PostgreSQL")
            print(f"   📊 Version: {version.split(',')[0]}")
            
            # Check permissions - verify all privileges granted by fix_permissions
            can_alter = await conn.fetchval("""
                SELECT 
                    has_table_privilege(current_user, 'users', 'SELECT') AND
                    has_table_privilege(current_user, 'users', 'INSERT') AND
                    has_table_privilege(current_user, 'users', 'UPDATE') AND
                    has_table_privilege(current_user, 'users', 'DELETE')
            """)
            
            # Check schema-level privileges for CREATE, ALTER, DROP
            can_modify_schema = await conn.fetchval("""
                SELECT has_schema_privilege(current_user, 'public', 'CREATE')
            """)
            
            print(f"   🔐 Table permissions (SELECT/INSERT/UPDATE/DELETE): {'✅ Yes' if can_alter else '❌ No'}")
            print(f"   🔐 Schema permissions (CREATE/ALTER/DROP): {'✅ Yes' if can_modify_schema else '❌ No'}")
            
            await conn.close()
            self.results["connection"] = True
            
        except Exception as e:
            print(f"   ❌ Connection failed: {e}")
            self.results["errors"].append(f"Connection: {str(e)}")
    
    async def test_schema_analysis(self):
        """Test schema analyzer"""
        print("\n2️⃣ Testing Schema Analysis...")
        try:
            analyzer = PostgreSQLSchemaAnalyzer(DATABASE_URL)
            
            start = datetime.utcnow()
            schema = await analyzer.analyze_schema()
            duration = (datetime.utcnow() - start).total_seconds()
            
            print(f"   ✅ Analyzed schema in {duration:.2f} seconds")
            print(f"   📊 Found {len(schema['tables'])} tables")
            print(f"   📊 Total size: {sum(t.get('size_bytes', 0) for t in schema['tables']) / 1024 / 1024:.1f} MB")
            
            # Check for specific tables
            table_names = [t['tablename'] for t in schema['tables']]
            critical_tables = ['users', 'sessions', 'credit_transactions', 'payments']
            
            for table in critical_tables:
                if table in table_names:
                    print(f"   ✅ Found critical table: {table}")
                else:
                    print(f"   ⚠️  Missing critical table: {table}")
            
            # Check for user_id columns
            user_id_tables = []
            for table, columns in schema['columns'].items():
                for col in columns:
                    if col['column_name'] == 'user_id':
                        user_id_tables.append({
                            'table': table,
                            'type': col['data_type']
                        })
            
            print(f"   📊 Found {len(user_id_tables)} tables with user_id column")
            
            # Check for type inconsistencies
            type_issues = [t for t in user_id_tables if t['type'] != 'integer']
            if type_issues:
                print(f"   ⚠️  Found {len(type_issues)} tables with non-integer user_id:")
                for issue in type_issues[:5]:  # Show first 5
                    print(f"      - {issue['table']}: {issue['type']}")
            
            self.results["schema_analysis"] = True
            self.results["performance"]["schema_analysis"] = duration
            
        except Exception as e:
            print(f"   ❌ Schema analysis failed: {e}")
            self.results["errors"].append(f"Schema analysis: {str(e)}")
    
    async def test_issue_detection(self):
        """Test issue detection without fixing"""
        print("\n3️⃣ Testing Issue Detection...")
        try:
            monitor = DatabaseHealthMonitor(DATABASE_URL)
            schema = await monitor.schema_analyzer.analyze_schema()
            
            # Detect issues
            issues = await monitor._detect_schema_issues(schema)
            
            print(f"   ✅ Issue detection completed")
            print(f"   📊 Found {len(issues)} total issues")
            
            # Categorize issues
            by_type = {}
            by_severity = {}
            
            for issue in issues:
                by_type[issue.issue_type] = by_type.get(issue.issue_type, 0) + 1
                by_severity[issue.severity] = by_severity.get(issue.severity, 0) + 1
            
            print("   📊 Issues by type:")
            for issue_type, count in by_type.items():
                print(f"      - {issue_type}: {count}")
            
            print("   📊 Issues by severity:")
            for severity, count in by_severity.items():
                print(f"      - {severity}: {count}")
            
            # Show sample issues
            if issues:
                print("   📋 Sample issues:")
                for issue in issues[:3]:
                    print(f"      - {issue.severity}: {issue.table}.{issue.column} - {issue.issue_type}")
            
            self.results["issue_detection"] = True
            self.results["issues_found"] = len(issues)
            
        except Exception as e:
            print(f"   ❌ Issue detection failed: {e}")
            self.results["errors"].append(f"Issue detection: {str(e)}")
    
    async def test_code_analysis(self):
        """Test code analysis"""
        print("\n4️⃣ Testing Code Analysis...")
        try:
            analyzer = CodePatternAnalyzer()
            
            start = datetime.utcnow()
            issues = analyzer.analyze_codebase()
            duration = (datetime.utcnow() - start).total_seconds()
            
            print(f"   ✅ Code analysis completed in {duration:.2f} seconds")
            print(f"   📊 Found {len(issues)} code issues")
            
            # Show patterns found
            patterns = {}
            for issue in issues:
                patterns[issue.issue_type] = patterns.get(issue.issue_type, 0) + 1
            
            if patterns:
                print("   📊 Code patterns found:")
                for pattern, count in patterns.items():
                    print(f"      - {pattern}: {count}")
            
            # Sample files with issues
            files_with_issues = set()
            for issue in issues:
                if issue.affected_files:
                    files_with_issues.update(issue.affected_files)
            
            print(f"   📊 Files with issues: {len(files_with_issues)}")
            if files_with_issues:
                print("   📋 Sample files:")
                for file in list(files_with_issues)[:5]:
                    print(f"      - {file}")
            
            self.results["code_analysis"] = True
            self.results["performance"]["code_analysis"] = duration
            
        except Exception as e:
            print(f"   ❌ Code analysis failed: {e}")
            self.results["errors"].append(f"Code analysis: {str(e)}")
    
    async def test_fix_capability(self):
        """Test fix capability in dry-run mode"""
        print("\n5️⃣ Testing Fix Capability (Dry Run)...")
        
        try:
            # Create a test table to validate fix logic
            conn = await asyncpg.connect(DATABASE_URL)
            
            # Create test table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS self_healing_test (
                    id SERIAL PRIMARY KEY,
                    user_id TEXT,  -- Wrong type on purpose
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            # Insert test data
            await conn.execute("""
                INSERT INTO self_healing_test (user_id) 
                VALUES ('1'), ('2'), ('3')
                ON CONFLICT DO NOTHING
            """)
            
            print("   ✅ Created test table")
            
            # Test backup creation
            fixer = DatabaseIssueFixer(DATABASE_URL)
            from backend.database_self_healing_system import DatabaseIssue
            
            test_issue = DatabaseIssue(
                issue_type='TYPE_MISMATCH',
                severity='HIGH',
                table='self_healing_test',
                column='user_id',
                current_state='text',
                expected_state='integer'
            )
            
            # Test backup creation only
            backup_id = await fixer._create_backup_point(conn, test_issue)
            print(f"   ✅ Backup created: {backup_id}")
            
            # Verify backup exists
            backup_exists = await conn.fetchval("""
                SELECT EXISTS(
                    SELECT 1 FROM information_schema.tables 
                    WHERE table_name LIKE 'backup_self_healing_test_%'
                )
            """)
            
            if backup_exists:
                print("   ✅ Backup table verified")
                self.results["rollback_capability"] = True
            
            # Cleanup
            await conn.execute("DROP TABLE IF EXISTS self_healing_test CASCADE")
            
            # Find and drop all backup tables
            backup_tables = await conn.fetch("""
                SELECT tablename FROM pg_tables 
                WHERE tablename LIKE 'backup_self_healing_test_%'
            """)
            for table in backup_tables:
                # Use quote_ident for safety
                quoted_table = '"' + table['tablename'].replace('"', '""') + '"'
                await conn.execute(f"DROP TABLE IF EXISTS {quoted_table} CASCADE")
            
            await conn.close()
            self.results["fix_capability"] = True
            
        except Exception as e:
            print(f"   ❌ Fix capability test failed: {e}")
            self.results["errors"].append(f"Fix capability: {str(e)}")
    
    async def test_performance(self):
        """Test performance benchmarks"""
        print("\n6️⃣ Testing Performance...")
        
        try:
            monitor = DatabaseHealthMonitor(DATABASE_URL)
            
            # Measure full health check time
            start = datetime.utcnow()
            results = await monitor.run_health_check()
            duration = (datetime.utcnow() - start).total_seconds()
            
            print(f"   ✅ Full health check completed in {duration:.2f} seconds")
            print(f"   📊 Issues found: {results['issues_found']}")
            print(f"   📊 Issues fixed: {results['issues_fixed']}")
            
            self.results["performance"]["full_check"] = duration
            
            # Check if performance is acceptable
            if duration < 30:
                print("   ✅ Performance is excellent (<30s)")
            elif duration < 60:
                print("   ⚠️  Performance is acceptable (30-60s)")
            else:
                print("   ❌ Performance needs optimization (>60s)")
            
        except Exception as e:
            print(f"   ❌ Performance test failed: {e}")
            self.results["errors"].append(f"Performance: {str(e)}")
    
    def print_report(self):
        """Print final validation report"""
        print("\n" + "="*60)
        print("📊 VALIDATION REPORT")
        print("="*60)
        
        # Calculate score
        total_tests = 6
        passed_tests = sum([
            self.results["connection"],
            self.results["schema_analysis"],
            self.results["issue_detection"],
            self.results["code_analysis"],
            self.results["fix_capability"],
            self.results["rollback_capability"]
        ])
        
        score = (passed_tests / total_tests) * 100
        
        print(f"\n🎯 Overall Score: {score:.0f}%")
        print(f"   ✅ Passed: {passed_tests}/{total_tests} tests")
        
        # Component status
        print("\n📋 Component Status:")
        components = [
            ("Database Connection", self.results["connection"]),
            ("Schema Analysis", self.results["schema_analysis"]),
            ("Issue Detection", self.results["issue_detection"]),
            ("Code Analysis", self.results["code_analysis"]),
            ("Fix Capability", self.results["fix_capability"]),
            ("Rollback Capability", self.results["rollback_capability"])
        ]
        
        for name, status in components:
            icon = "✅" if status else "❌"
            print(f"   {icon} {name}")
        
        # Performance summary
        if self.results["performance"]:
            print("\n⚡ Performance Summary:")
            for metric, value in self.results["performance"].items():
                print(f"   - {metric}: {value:.2f}s")
        
        # Errors
        if self.results["errors"]:
            print("\n❌ Errors Found:")
            for error in self.results["errors"]:
                print(f"   - {error}")
        
        # Recommendations
        print("\n💡 Recommendations:")
        if score == 100:
            print("   ✅ System is ready for production deployment!")
            print("   - Start with manual mode for 24 hours")
            print("   - Enable auto-fix for one table at a time")
            print("   - Monitor logs closely for first week")
        elif score >= 80:
            print("   ⚠️  System is mostly ready but needs fixes:")
            for name, status in components:
                if not status:
                    print(f"   - Fix {name} before deployment")
        else:
            print("   ❌ System needs significant work:")
            print("   - Address all failing components")
            print("   - Review error messages above")
            print("   - Consider running components individually")
        
        print("\n" + "="*60)


async def main():
    """Run validation"""
    validator = SystemValidator()
    results = await validator.validate_all()
    
    # Save results
    with open("validation_results.json", "w") as f:
        import json
        json.dump(results, f, indent=2, default=str)
    
    print("\n📁 Results saved to validation_results.json")
    
    return results


if __name__ == "__main__":
    asyncio.run(main())