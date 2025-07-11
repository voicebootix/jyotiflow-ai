#!/usr/bin/env python3
"""
Database State Validation Script
Ensures all tables, columns, and dependencies are correctly set up
"""

import asyncio
import asyncpg
import os
from datetime import datetime
import json

class DatabaseValidator:
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL")
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable is required")
        
        self.issues = []
        self.warnings = []
        self.successes = []
    
    async def validate(self):
        """Run comprehensive database validation"""
        print("🔍 Starting Database Validation...")
        
        conn = await asyncpg.connect(self.database_url)
        try:
            # 1. Check required tables
            await self._check_required_tables(conn)
            
            # 2. Check column names and types
            await self._check_column_specifications(conn)
            
            # 3. Check foreign key dependencies
            await self._check_foreign_keys(conn)
            
            # 4. Check for data integrity
            await self._check_data_integrity(conn)
            
            # 5. Check for duplications
            await self._check_duplications(conn)
            
            # Generate report
            self._generate_report()
            
            return len(self.issues) == 0
            
        finally:
            await conn.close()
    
    async def _check_required_tables(self, conn):
        """Check all required tables exist"""
        required_tables = [
            # Core tables
            ('users', 'User authentication and profiles'),
            ('service_types', 'Service configurations'),
            ('sessions', 'User session tracking'),
            ('credit_packages', 'Credit package offerings'),
            ('credit_transactions', 'Credit purchase history'),
            ('payments', 'Payment records'),
            
            # Admin tables
            ('ai_recommendations', 'AI-generated recommendations'),
            ('ai_pricing_recommendations', 'AI pricing suggestions'),
            ('monetization_experiments', 'A/B test tracking'),
            ('ai_insights_cache', 'Cached AI insights'),
            
            # Feature tables
            ('social_campaigns', 'Social media campaigns'),
            ('social_posts', 'Social media posts'),
            ('platform_settings', 'Platform configuration'),
            ('avatar_templates', 'Avatar generation templates'),
            ('live_chat_sessions', 'Agora live chat sessions'),
            ('rag_knowledge_base', 'RAG knowledge storage'),
            ('birth_chart_cache', 'Cached birth charts'),
            
            # Analytics tables
            ('user_analytics', 'User behavior tracking'),
            ('revenue_analytics', 'Revenue tracking'),
            ('api_usage_metrics', 'API usage tracking')
        ]
        
        existing_tables = await conn.fetch("""
            SELECT tablename FROM pg_tables 
            WHERE schemaname = 'public' 
            AND tablename NOT LIKE 'pg_%'
        """)
        existing_set = {row['tablename'] for row in existing_tables}
        
        for table_name, description in required_tables:
            if table_name in existing_set:
                self.successes.append(f"✅ Table '{table_name}' exists - {description}")
            else:
                self.issues.append({
                    'type': 'missing_table',
                    'table': table_name,
                    'description': description,
                    'severity': 'HIGH'
                })
    
    async def _check_column_specifications(self, conn):
        """Check critical column names and types"""
        critical_columns = [
            # Table, Column, Expected Type, Description
            ('users', 'last_login_at', 'timestamp', 'User last login time'),
            ('users', 'id', 'integer', 'User primary key'),
            ('credit_packages', 'credits_amount', 'integer', 'Package credits'),
            ('credit_packages', 'credits', 'integer', 'Backward compatibility alias'),
            ('service_types', 'enabled', 'boolean', 'Service active status'),
            ('service_types', 'price_usd', 'numeric', 'Service price'),
            ('service_types', 'service_category', 'character varying', 'Service category'),
            ('pricing_config', 'key', 'character varying', 'Config key'),
            ('pricing_config', 'value', 'character varying', 'Config value'),
            ('sessions', 'user_email', 'character varying', 'Session user'),
            ('sessions', 'service_type', 'character varying', 'Session service')
        ]
        
        for table_name, column_name, expected_type, description in critical_columns:
            result = await conn.fetchrow("""
                SELECT data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = $1 AND column_name = $2
            """, table_name, column_name)
            
            if result:
                if expected_type in result['data_type']:
                    self.successes.append(f"✅ {table_name}.{column_name} - {description}")
                else:
                    self.warnings.append({
                        'type': 'type_mismatch',
                        'table': table_name,
                        'column': column_name,
                        'expected': expected_type,
                        'actual': result['data_type']
                    })
            else:
                self.issues.append({
                    'type': 'missing_column',
                    'table': table_name,
                    'column': column_name,
                    'description': description,
                    'severity': 'HIGH'
                })
    
    async def _check_foreign_keys(self, conn):
        """Check foreign key dependencies"""
        # Check if service_types are referenced properly
        fk_checks = [
            ('sessions', 'service_type', 'service_types', 'name'),
            ('sessions', 'user_email', 'users', 'email'),
            ('credit_transactions', 'user_id', 'users', 'id'),
            ('credit_transactions', 'package_id', 'credit_packages', 'id'),
            ('payments', 'user_email', 'users', 'email')
        ]
        
        for table, column, ref_table, ref_column in fk_checks:
            # Check if tables exist
            tables_exist = await conn.fetchval("""
                SELECT COUNT(*) FROM information_schema.tables 
                WHERE table_name IN ($1, $2)
            """, table, ref_table)
            
            if tables_exist == 2:
                # Check for orphaned records
                orphans = await conn.fetchval(f"""
                    SELECT COUNT(*) FROM {table} t1
                    LEFT JOIN {ref_table} t2 ON t1.{column} = t2.{ref_column}
                    WHERE t2.{ref_column} IS NULL AND t1.{column} IS NOT NULL
                """)
                
                if orphans > 0:
                    self.warnings.append({
                        'type': 'orphaned_records',
                        'table': table,
                        'count': orphans,
                        'foreign_key': f"{column} -> {ref_table}.{ref_column}"
                    })
                else:
                    self.successes.append(f"✅ Foreign key {table}.{column} -> {ref_table}.{ref_column} valid")
    
    async def _check_data_integrity(self, conn):
        """Check data integrity issues"""
        # Check if admin user exists
        admin_exists = await conn.fetchval(
            "SELECT 1 FROM users WHERE email = 'admin@jyotiflow.ai'"
        )
        if admin_exists:
            self.successes.append("✅ Admin user exists")
        else:
            self.warnings.append({
                'type': 'missing_admin',
                'description': 'Admin user not found'
            })
        
        # Check if credit packages exist
        package_count = await conn.fetchval("SELECT COUNT(*) FROM credit_packages")
        if package_count > 0:
            self.successes.append(f"✅ {package_count} credit packages found")
        else:
            self.issues.append({
                'type': 'no_credit_packages',
                'description': 'No credit packages defined',
                'severity': 'MEDIUM'
            })
        
        # Check service types
        service_count = await conn.fetchval("SELECT COUNT(*) FROM service_types")
        if service_count > 0:
            self.successes.append(f"✅ {service_count} service types found")
        else:
            self.warnings.append({
                'type': 'no_service_types',
                'description': 'No service types defined'
            })
    
    async def _check_duplications(self, conn):
        """Check for potential duplication issues"""
        # Check for duplicate indexes
        duplicate_indexes = await conn.fetch("""
            SELECT indexname, COUNT(*) as count
            FROM pg_indexes
            WHERE schemaname = 'public'
            GROUP BY indexname
            HAVING COUNT(*) > 1
        """)
        
        if duplicate_indexes:
            for idx in duplicate_indexes:
                self.warnings.append({
                    'type': 'duplicate_index',
                    'index': idx['indexname'],
                    'count': idx['count']
                })
    
    def _generate_report(self):
        """Generate validation report"""
        print("\n" + "="*60)
        print("DATABASE VALIDATION REPORT")
        print("="*60)
        print(f"Timestamp: {datetime.now().isoformat()}")
        print(f"\n✅ Successes: {len(self.successes)}")
        print(f"⚠️  Warnings: {len(self.warnings)}")
        print(f"❌ Issues: {len(self.issues)}")
        
        if self.issues:
            print("\n❌ CRITICAL ISSUES:")
            for issue in self.issues:
                print(f"  - {issue['type']}: {issue.get('description', '')} ({issue.get('table', '')})")
        
        if self.warnings:
            print("\n⚠️  WARNINGS:")
            for warning in self.warnings:
                print(f"  - {warning['type']}: {warning.get('description', '')}")
        
        if self.successes and len(self.successes) < 20:  # Don't spam with success messages
            print("\n✅ VALIDATED:")
            for success in self.successes:
                print(f"  {success}")
        
        # Save detailed report
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'successes': len(self.successes),
                'warnings': len(self.warnings),
                'issues': len(self.issues)
            },
            'issues': self.issues,
            'warnings': self.warnings,
            'successes': self.successes
        }
        
        report_file = f"validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Detailed report saved to {report_file}")
        
        if not self.issues:
            print("\n✅ DATABASE IS READY FOR PRODUCTION!")
        else:
            print("\n❌ DATABASE HAS CRITICAL ISSUES - DO NOT DEPLOY!")

async def main():
    validator = DatabaseValidator()
    success = await validator.validate()
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)