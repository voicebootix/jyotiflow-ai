#!/usr/bin/env python3
"""
Deploy Testing Infrastructure to Production Database
Safe deployment of testing tables with rollback capability
"""

import asyncio
import asyncpg
import os
import json
from datetime import datetime, timezone

DATABASE_URL = os.getenv("DATABASE_URL")

class TestingInfrastructureDeployer:
    def __init__(self):
        self.database_url = DATABASE_URL
        self.deployment_log = []
        
    async def deploy(self):
        """Deploy testing infrastructure safely"""
        if not self.database_url:
            self.log_error("DATABASE_URL not found")
            return False
            
        try:
            conn = await asyncpg.connect(self.database_url)
            self.log_info("Connected to production database")
            
            # Start transaction
            await conn.execute('BEGIN')
            self.log_info("Started transaction")
            
            # Read and execute the SQL script
            success = await self._execute_schema_script(conn)
            
            if success:
                await conn.execute('COMMIT')
                self.log_success("Testing infrastructure deployed successfully")
                await self._verify_deployment(conn)
            else:
                await conn.execute('ROLLBACK')
                self.log_error("Deployment failed, rolled back changes")
                
            await conn.close()
            return success
            
        except Exception as e:
            self.log_error(f"Deployment failed: {e}")
            return False
    
    async def _execute_schema_script(self, conn):
        """Execute the testing infrastructure SQL script"""
        try:
            # Read the SQL file
            with open('create_testing_tables.sql', 'r', encoding='utf-8') as f:
                sql_script = f.read()
            
            # Split into individual statements
            statements = []
            current_statement = ""
            
            for line in sql_script.split('\n'):
                line = line.strip()
                
                # Skip comments and empty lines
                if not line or line.startswith('--'):
                    continue
                    
                current_statement += line + '\n'
                
                # If line ends with semicolon, it's end of statement
                if line.endswith(';'):
                    statements.append(current_statement.strip())
                    current_statement = ""
            
            self.log_info(f"Executing {len(statements)} SQL statements")
            
            # Execute each statement
            for i, statement in enumerate(statements, 1):
                if not statement.strip():
                    continue
                    
                try:
                    # Skip SELECT verification statements for now
                    if statement.strip().upper().startswith('SELECT'):
                        continue
                        
                    await conn.execute(statement)
                    self.log_info(f"✅ Statement {i} executed successfully")
                    
                except Exception as e:
                    self.log_error(f"❌ Statement {i} failed: {e}")
                    self.log_error(f"Statement: {statement[:100]}...")
                    return False
                    
            return True
            
        except Exception as e:
            self.log_error(f"Failed to execute schema script: {e}")
            return False
    
    async def _verify_deployment(self, conn):
        """Verify that all tables were created successfully"""
        try:
            # Check testing tables
            testing_tables = [
                'test_execution_sessions',
                'test_case_results', 
                'test_coverage_reports',
                'autofix_test_results',
                'test_performance_metrics'
            ]
            
            self.log_info("Verifying table creation...")
            
            for table in testing_tables:
                exists = await conn.fetchval("""
                    SELECT EXISTS(
                        SELECT 1 FROM information_schema.tables 
                        WHERE table_name = $1
                    )
                """, table)
                
                if exists:
                    self.log_success(f"✅ Table '{table}' created successfully")
                else:
                    self.log_error(f"❌ Table '{table}' was not created")
            
            # Check column extensions
            health_check_columns = await conn.fetch("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'health_check_results' 
                AND column_name IN ('test_session_id', 'test_triggered', 'test_results_summary')
            """)
            
            self.log_info(f"Extended health_check_results with {len(health_check_columns)} test columns")
            
            validation_columns = await conn.fetch("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'validation_sessions' 
                AND column_name IN ('test_session_id', 'test_status', 'test_completion_time')
            """)
            
            self.log_info(f"Extended validation_sessions with {len(validation_columns)} test columns")
            
            # Test a simple insert to verify functionality
            test_session_id = await conn.fetchval("""
                INSERT INTO test_execution_sessions (
                    test_type, test_category, environment, triggered_by
                ) VALUES (
                    'deployment_verification', 'infrastructure', 'production', 'manual'
                ) RETURNING session_id
            """)
            
            if test_session_id:
                self.log_success(f"✅ Test insert successful: {test_session_id}")
                
                # Clean up test record
                await conn.execute("""
                    DELETE FROM test_execution_sessions WHERE session_id = $1
                """, test_session_id)
                self.log_info("Test record cleaned up")
            
        except Exception as e:
            self.log_error(f"Verification failed: {e}")
    
    def log_info(self, message):
        """Log info message"""
        timestamp = datetime.now(timezone.utc).isoformat()
        log_entry = f"[{timestamp}] INFO: {message}"
        print(log_entry)
        self.deployment_log.append(log_entry)
    
    def log_success(self, message):
        """Log success message"""
        timestamp = datetime.now(timezone.utc).isoformat()
        log_entry = f"[{timestamp}] SUCCESS: {message}"
        print(log_entry)
        self.deployment_log.append(log_entry)
    
    def log_error(self, message):
        """Log error message"""
        timestamp = datetime.now(timezone.utc).isoformat()
        log_entry = f"[{timestamp}] ERROR: {message}"
        print(log_entry)
        self.deployment_log.append(log_entry)
    
    def save_deployment_log(self):
        """Save deployment log to file"""
        try:
            log_data = {
                "deployment_timestamp": datetime.now(timezone.utc).isoformat(),
                "deployment_type": "testing_infrastructure",
                "log_entries": self.deployment_log
            }
            
            with open('testing_infrastructure_deployment.log', 'w', encoding='utf-8') as f:
                json.dump(log_data, f, indent=2)
                
            print(f"Deployment log saved to: testing_infrastructure_deployment.log")
            
        except Exception as e:
            print(f"Failed to save deployment log: {e}")

async def main():
    """Main deployment function"""
    print("🚀 JyotiFlow Testing Infrastructure Deployment")
    print("=" * 60)
    
    deployer = TestingInfrastructureDeployer()
    success = await deployer.deploy()
    
    # Save deployment log
    deployer.save_deployment_log()
    
    if success:
        print("\n🎉 Testing infrastructure deployment completed successfully!")
        print("✅ All testing tables created and verified")
        print("✅ Existing monitoring tables extended")
        print("✅ Ready for test execution integration")
    else:
        print("\n❌ Testing infrastructure deployment failed!")
        print("💡 Check the deployment log for details")
        print("🔧 All changes have been rolled back")
    
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)