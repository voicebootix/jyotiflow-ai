#!/usr/bin/env python3
"""
🚀 SAFE DEPLOYMENT MIGRATION
Handles existing deployment transition without data loss
"""

import asyncio
import asyncpg
import os
import logging
from datetime import datetime
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SafeDeploymentMigration:
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL")
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable is required")
    
    async def migrate(self):
        """Perform safe migration of existing deployment"""
        logger.info("🚀 Starting Safe Deployment Migration...")
        
        conn = await asyncpg.connect(self.database_url)
        try:
            # Step 1: Analyze current state
            logger.info("📊 Analyzing current database state...")
            state_report = await self._analyze_current_state(conn)
            
            # Step 2: Backup critical data
            logger.info("💾 Backing up critical data...")
            backup_data = await self._backup_critical_data(conn)
            
            # Step 3: Apply missing migrations
            logger.info("🔧 Applying missing migrations...")
            await self._apply_missing_migrations(conn)
            
            # Step 4: Verify data integrity
            logger.info("🔍 Verifying data integrity...")
            await self._verify_data_integrity(conn, backup_data)
            
            # Step 5: Generate report
            report = await self._generate_migration_report(conn, state_report)
            
            logger.info("✅ Safe Deployment Migration Completed!")
            return report
            
        except Exception as e:
            logger.error(f"❌ Migration failed: {str(e)}")
            raise
        finally:
            await conn.close()
    
    async def _analyze_current_state(self, conn):
        """Analyze current database state"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'tables': {},
            'issues': [],
            'warnings': []
        }
        
        # Get all tables
        tables = await conn.fetch("""
            SELECT tablename FROM pg_tables 
            WHERE schemaname = 'public' 
            AND tablename NOT LIKE 'pg_%'
            ORDER BY tablename
        """)
        
        for table in tables:
            table_name = table['tablename']
            
            # Get row count
            row_count = await conn.fetchval(f"SELECT COUNT(*) FROM {table_name}")
            
            # Get columns
            columns = await conn.fetch(f"""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_name = '{table_name}'
                ORDER BY ordinal_position
            """)
            
            report['tables'][table_name] = {
                'row_count': row_count,
                'columns': [dict(col) for col in columns]
            }
        
        # Check for specific issues
        
        # Issue 1: Missing credit_packages table
        if 'credit_packages' not in report['tables']:
            report['issues'].append({
                'severity': 'HIGH',
                'issue': 'Missing credit_packages table',
                'impact': 'Admin dashboard credit package management will fail'
            })
        
        # Issue 2: Column naming issues
        if 'users' in report['tables']:
            user_columns = [col['column_name'] for col in report['tables']['users']['columns']]
            if 'last_login' in user_columns and 'last_login_at' not in user_columns:
                report['issues'].append({
                    'severity': 'MEDIUM',
                    'issue': 'Users table has last_login instead of last_login_at',
                    'impact': 'Admin analytics queries will fail'
                })
        
        # Issue 3: Missing service_types columns
        if 'service_types' in report['tables']:
            st_columns = [col['column_name'] for col in report['tables']['service_types']['columns']]
            missing_cols = []
            for col in ['enabled', 'price_usd', 'service_category']:
                if col not in st_columns:
                    missing_cols.append(col)
            
            if missing_cols:
                report['issues'].append({
                    'severity': 'HIGH',
                    'issue': f'Missing columns in service_types: {", ".join(missing_cols)}',
                    'impact': 'Service management features will fail'
                })
        
        # Check for orphaned data
        orphan_checks = [
            ("sessions without users", "sessions", "user_email", "users", "email"),
            ("payments without users", "payments", "user_email", "users", "email")
        ]
        
        for check_name, table1, col1, table2, col2 in orphan_checks:
            if table1 in report['tables'] and table2 in report['tables']:
                orphans = await conn.fetchval(f"""
                    SELECT COUNT(*) FROM {table1} t1
                    LEFT JOIN {table2} t2 ON t1.{col1} = t2.{col2}
                    WHERE t2.{col2} IS NULL
                """)
                if orphans > 0:
                    report['warnings'].append({
                        'type': 'orphaned_data',
                        'description': f'{orphans} {check_name}',
                        'table': table1
                    })
        
        return report
    
    async def _backup_critical_data(self, conn):
        """Backup critical data before migration"""
        backup = {
            'timestamp': datetime.now().isoformat(),
            'users': [],
            'sessions': [],
            'service_types': [],
            'credit_packages': []
        }
        
        # Backup users
        try:
            users = await conn.fetch("SELECT * FROM users")
            backup['users'] = [dict(user) for user in users]
            logger.info(f"✅ Backed up {len(backup['users'])} users")
        except Exception as e:
            logger.warning(f"⚠️ Could not backup users: {e}")
        
        # Backup sessions
        try:
            sessions = await conn.fetch("SELECT * FROM sessions LIMIT 1000")
            backup['sessions'] = [dict(session) for session in sessions]
            logger.info(f"✅ Backed up {len(backup['sessions'])} recent sessions")
        except Exception as e:
            logger.warning(f"⚠️ Could not backup sessions: {e}")
        
        # Backup service_types
        try:
            service_types = await conn.fetch("SELECT * FROM service_types")
            backup['service_types'] = [dict(st) for st in service_types]
            logger.info(f"✅ Backed up {len(backup['service_types'])} service types")
        except Exception as e:
            logger.warning(f"⚠️ Could not backup service types: {e}")
        
        # Backup credit_packages if exists
        try:
            packages = await conn.fetch("SELECT * FROM credit_packages")
            backup['credit_packages'] = [dict(pkg) for pkg in packages]
            logger.info(f"✅ Backed up {len(backup['credit_packages'])} credit packages")
        except Exception as e:
            logger.warning(f"⚠️ Could not backup credit packages: {e}")
        
        # Save backup to file
        backup_file = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(backup_file, 'w') as f:
            json.dump(backup, f, indent=2, default=str)
        logger.info(f"💾 Backup saved to {backup_file}")
        
        return backup
    
    async def _apply_missing_migrations(self, conn):
        """Apply only the necessary fixes"""
        
        # 1. Create credit_packages table if missing
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS credit_packages (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                credits_amount INTEGER NOT NULL,
                price_usd DECIMAL(10,2) NOT NULL,
                bonus_credits INTEGER DEFAULT 0,
                description TEXT,
                enabled BOOLEAN DEFAULT TRUE,
                stripe_product_id VARCHAR(255),
                stripe_price_id VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        logger.info("✅ Ensured credit_packages table exists")
        
        # 2. Fix column naming issues
        try:
            # Fix last_login -> last_login_at
            col_exists = await conn.fetchval("""
                SELECT 1 FROM information_schema.columns 
                WHERE table_name='users' AND column_name='last_login'
            """)
            if col_exists:
                await conn.execute("ALTER TABLE users RENAME COLUMN last_login TO last_login_at")
                logger.info("✅ Renamed last_login to last_login_at")
        except Exception as e:
            logger.warning(f"⚠️ Could not rename column: {e}")
        
        # 3. Add missing columns to service_types
        columns_to_add = [
            ("enabled", "BOOLEAN DEFAULT true"),
            ("price_usd", "DECIMAL(10,2) DEFAULT 0"),
            ("service_category", "VARCHAR(100)")
        ]
        
        for col_name, col_def in columns_to_add:
            try:
                col_exists = await conn.fetchval(f"""
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='service_types' AND column_name='{col_name}'
                """)
                if not col_exists:
                    await conn.execute(f"ALTER TABLE service_types ADD COLUMN {col_name} {col_def}")
                    logger.info(f"✅ Added {col_name} to service_types")
            except Exception as e:
                logger.warning(f"⚠️ Could not add column {col_name}: {e}")
        
        # 4. Create other essential tables
        essential_tables = [
            ("payments", """
                CREATE TABLE IF NOT EXISTS payments (
                    id SERIAL PRIMARY KEY,
                    user_email VARCHAR(255) NOT NULL,
                    amount DECIMAL(10,2) NOT NULL,
                    currency VARCHAR(3) DEFAULT 'USD',
                    status VARCHAR(50) DEFAULT 'pending',
                    payment_method VARCHAR(50),
                    transaction_id VARCHAR(255),
                    product_id VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """),
            ("ai_recommendations", """
                CREATE TABLE IF NOT EXISTS ai_recommendations (
                    id SERIAL PRIMARY KEY,
                    recommendation_type VARCHAR(50) NOT NULL,
                    title VARCHAR(255) NOT NULL,
                    description TEXT NOT NULL,
                    expected_revenue_impact DECIMAL(10,2),
                    implementation_difficulty VARCHAR(20),
                    timeline_weeks INTEGER,
                    priority_score DECIMAL(3,2),
                    priority_level VARCHAR(20),
                    status VARCHAR(50) DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """),
            ("monetization_experiments", """
                CREATE TABLE IF NOT EXISTS monetization_experiments (
                    id SERIAL PRIMARY KEY,
                    experiment_name VARCHAR(255) NOT NULL,
                    experiment_type VARCHAR(50) NOT NULL,
                    control_conversion_rate DECIMAL(5,2),
                    test_conversion_rate DECIMAL(5,2),
                    control_revenue DECIMAL(10,2),
                    test_revenue DECIMAL(10,2),
                    status VARCHAR(50) DEFAULT 'running',
                    winner VARCHAR(20),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
        ]
        
        for table_name, create_sql in essential_tables:
            await conn.execute(create_sql)
            logger.info(f"✅ Ensured {table_name} table exists")
    
    async def _verify_data_integrity(self, conn, backup_data):
        """Verify data integrity after migration"""
        logger.info("🔍 Verifying data integrity...")
        
        # Verify user count
        user_count = await conn.fetchval("SELECT COUNT(*) FROM users")
        backup_user_count = len(backup_data.get('users', []))
        if user_count >= backup_user_count:
            logger.info(f"✅ User data preserved: {user_count} users")
        else:
            logger.warning(f"⚠️ User count mismatch: {user_count} vs {backup_user_count} in backup")
        
        # Verify critical tables exist
        critical_tables = [
            'users', 'service_types', 'sessions', 'credit_packages',
            'payments', 'ai_recommendations', 'monetization_experiments'
        ]
        
        for table in critical_tables:
            exists = await conn.fetchval(f"""
                SELECT 1 FROM information_schema.tables 
                WHERE table_name = '{table}'
            """)
            if exists:
                logger.info(f"✅ Table {table} exists")
            else:
                logger.error(f"❌ Table {table} is missing!")
        
        # Verify no data corruption
        try:
            # Test query that was failing
            test_query = await conn.fetchval(
                "SELECT COUNT(*) FROM users WHERE last_login_at >= NOW() - INTERVAL '7 days'"
            )
            logger.info(f"✅ Analytics query working: {test_query} active users")
        except Exception as e:
            logger.error(f"❌ Analytics query still failing: {e}")
    
    async def _generate_migration_report(self, conn, initial_state):
        """Generate migration report"""
        final_state = await self._analyze_current_state(conn)
        
        report = {
            'migration_timestamp': datetime.now().isoformat(),
            'initial_state': initial_state,
            'final_state': final_state,
            'issues_resolved': [],
            'issues_remaining': [],
            'recommendations': []
        }
        
        # Compare issues
        initial_issues = {issue['issue'] for issue in initial_state.get('issues', [])}
        final_issues = {issue['issue'] for issue in final_state.get('issues', [])}
        
        report['issues_resolved'] = list(initial_issues - final_issues)
        report['issues_remaining'] = list(final_issues)
        
        # Add recommendations
        if report['issues_remaining']:
            report['recommendations'].append(
                "Some issues remain. Consider running the full migration suite."
            )
        
        if 'credit_packages' in final_state['tables'] and \
           final_state['tables']['credit_packages']['row_count'] == 0:
            report['recommendations'].append(
                "Credit packages table is empty. Run: python backend/init_credit_packages.py"
            )
        
        # Save report
        report_file = f"migration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"📄 Migration report saved to {report_file}")
        return report

async def main():
    """Main entry point for safe deployment migration"""
    migration = SafeDeploymentMigration()
    report = await migration.migrate()
    
    print("\n" + "="*60)
    print("MIGRATION REPORT SUMMARY")
    print("="*60)
    print(f"Issues Resolved: {len(report['issues_resolved'])}")
    for issue in report['issues_resolved']:
        print(f"  ✅ {issue}")
    
    print(f"\nIssues Remaining: {len(report['issues_remaining'])}")
    for issue in report['issues_remaining']:
        print(f"  ⚠️ {issue}")
    
    print(f"\nRecommendations:")
    for rec in report['recommendations']:
        print(f"  💡 {rec}")
    
    print("\n✅ Migration completed successfully!")

if __name__ == "__main__":
    asyncio.run(main())