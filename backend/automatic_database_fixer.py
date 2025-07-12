#!/usr/bin/env python3
"""
JyotiFlow.ai Automatic Database Fixer
This script automatically detects and fixes all database schema issues
"""

import asyncio
import logging
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional

try:
    import asyncpg
except ImportError:
    asyncpg = None
    logging.warning("asyncpg not installed. Install with: pip install asyncpg")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DatabaseFixer:
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.conn = None
        self.missing_tables = []
        self.missing_columns = []
        self.constraint_issues = []
        
    async def connect(self):
        """Establish database connection"""
        try:
            self.conn = await asyncpg.connect(self.database_url)
            logger.info("✅ Connected to database")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to connect to database: {e}")
            return False
    
    async def disconnect(self):
        """Close database connection"""
        if self.conn:
            await self.conn.close()
            logger.info("Disconnected from database")
    
    async def get_existing_tables(self) -> List[str]:
        """Get list of existing tables"""
        query = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        ORDER BY table_name
        """
        rows = await self.conn.fetch(query)
        return [row['table_name'] for row in rows]
    
    async def check_table_exists(self, table_name: str) -> bool:
        """Check if a specific table exists"""
        query = """
        SELECT EXISTS (
            SELECT 1 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = $1
        )
        """
        return await self.conn.fetchval(query, table_name)
    
    async def check_column_exists(self, table_name: str, column_name: str) -> bool:
        """Check if a specific column exists in a table"""
        query = """
        SELECT EXISTS (
            SELECT 1 
            FROM information_schema.columns 
            WHERE table_schema = 'public' 
            AND table_name = $1 
            AND column_name = $2
        )
        """
        return await self.conn.fetchval(query, table_name, column_name)
    
    async def analyze_database(self):
        """Analyze database and identify all issues"""
        logger.info("🔍 Analyzing database schema...")
        
        # Define all required tables
        required_tables = [
            # Core tables (from existing schema)
            'users', 'sessions', 'service_types', 'payments', 'credit_packages',
            'donations', 'feature_flags', 'platform_settings', 'pricing_config',
            'system_configuration', 'system_logs', 'schema_migrations',
            
            # Avatar generation
            'avatar_templates', 'avatar_sessions', 'avatar_generation_queue',
            
            # Live chat
            'live_chat_sessions', 'session_participants', 'agora_usage_logs',
            
            # Analytics
            'admin_analytics', 'user_analytics', 'revenue_analytics',
            'performance_analytics', 'feature_usage_analytics', 'api_usage_metrics',
            
            # AI features
            'ai_recommendations', 'ai_insights_cache', 'ai_pricing_recommendations',
            'rag_knowledge_base', 'birth_chart_cache',
            
            # Marketing
            'marketing_campaigns', 'marketing_insights', 'monetization_experiments',
            'monetization_insights',
            
            # Social media
            'social_campaigns', 'social_content', 'social_posts',
            
            # User management
            'user_sessions', 'user_purchases', 'service_usage_logs',
            
            # Admin
            'admin_notifications',
            
            # Critical missing tables
            'service_configuration_cache', 'credit_transactions',
            'donation_transactions', 'session_donations', 'followup_interactions',
            'email_logs', 'sms_logs', 'webhook_logs', 'notification_templates',
            'notification_queue', 'subscription_plans', 'subscription_history',
            'refunds', 'coupons', 'user_coupons', 'chat_messages',
            'spiritual_practitioners', 'practitioner_availability', 'appointments',
            'reviews', 'support_tickets', 'knowledge_articles', 'audit_logs',
            'rate_limits', 'session_transcripts', 'remedy_recommendations',
            'user_birth_charts', 'compatibility_reports', 'consent_logs',
            'data_exports'
        ]
        
        # Check existing tables
        existing_tables = await self.get_existing_tables()
        logger.info(f"Found {len(existing_tables)} existing tables")
        
        # Identify missing tables
        self.missing_tables = [t for t in required_tables if t not in existing_tables]
        if self.missing_tables:
            logger.warning(f"Missing {len(self.missing_tables)} tables: {', '.join(self.missing_tables[:5])}...")
        
        # Check critical columns
        column_checks = [
            ('users', 'last_login_at'),
            ('service_types', 'is_premium'),
            ('service_types', 'display_name'),
            ('service_types', 'enabled'),
            ('service_types', 'price_usd'),
            ('credit_packages', 'credits_amount'),
            ('api_usage_metrics', 'api_name')
        ]
        
        for table, column in column_checks:
            if table in existing_tables:
                exists = await self.check_column_exists(table, column)
                if not exists:
                    self.missing_columns.append((table, column))
        
        if self.missing_columns:
            logger.warning(f"Missing {len(self.missing_columns)} columns")
        
        # Summary
        logger.info(f"""
📊 Database Analysis Summary:
   - Existing tables: {len(existing_tables)}
   - Required tables: {len(required_tables)}
   - Missing tables: {len(self.missing_tables)}
   - Missing columns: {len(self.missing_columns)}
        """)
        
        return len(self.missing_tables) > 0 or len(self.missing_columns) > 0
    
    async def fix_database(self):
        """Apply all database fixes"""
        logger.info("🔧 Starting database fix process...")
        
        try:
            # Read the comprehensive fix SQL script
            sql_file_path = '/workspace/comprehensive_database_fix.sql'
            with open(sql_file_path, 'r') as f:
                sql_script = f.read()
            
            # Execute the script
            logger.info("Executing comprehensive database fix script...")
            await self.conn.execute(sql_script)
            logger.info("✅ Database fix script executed successfully!")
            
            # Verify fixes
            await self.verify_fixes()
            
        except FileNotFoundError:
            logger.error(f"SQL script not found at {sql_file_path}")
            return False
        except Exception as e:
            logger.error(f"Error applying database fixes: {e}")
            return False
        
        return True
    
    async def verify_fixes(self):
        """Verify that all fixes were applied successfully"""
        logger.info("🔍 Verifying database fixes...")
        
        # Re-analyze database
        issues_remain = await self.analyze_database()
        
        if not issues_remain:
            logger.info("✅ All database issues have been resolved!")
        else:
            logger.warning("⚠️ Some issues may still remain")
            if self.missing_tables:
                logger.warning(f"Still missing tables: {', '.join(self.missing_tables[:10])}")
            if self.missing_columns:
                logger.warning(f"Still missing columns: {self.missing_columns}")
    
    async def create_verification_report(self):
        """Create a detailed verification report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "database_url": self.database_url.split('@')[1] if '@' in self.database_url else 'local',
            "analysis": {
                "existing_tables": len(await self.get_existing_tables()),
                "missing_tables": self.missing_tables,
                "missing_columns": self.missing_columns,
                "constraint_issues": self.constraint_issues
            },
            "status": "fixed" if not self.missing_tables and not self.missing_columns else "issues_remain"
        }
        
        # Save report
        report_path = '/workspace/database_fix_report.json'
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"📄 Verification report saved to {report_path}")
        return report

async def main():
    """Main execution function"""
    logger.info("🚀 JyotiFlow.ai Automatic Database Fixer")
    logger.info("=" * 50)
    
    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        logger.error("DATABASE_URL environment variable not set!")
        return
    
    # Initialize fixer
    fixer = DatabaseFixer(database_url)
    
    # Connect to database
    if not await fixer.connect():
        return
    
    try:
        # Analyze database
        has_issues = await fixer.analyze_database()
        
        if has_issues:
            logger.info("Issues detected. Applying fixes...")
            
            # Apply fixes
            success = await fixer.fix_database()
            
            if success:
                logger.info("✅ Database fixes applied successfully!")
            else:
                logger.error("❌ Failed to apply some database fixes")
        else:
            logger.info("✅ No database issues detected!")
        
        # Create verification report
        report = await fixer.create_verification_report()
        
        # Print summary
        logger.info(f"""
🎉 Database Fix Process Complete!
   Status: {report['status']}
   Existing Tables: {report['analysis']['existing_tables']}
   Report: /workspace/database_fix_report.json
        """)
        
    finally:
        await fixer.disconnect()

if __name__ == "__main__":
    asyncio.run(main())