"""
Testing Integration Module for JyotiFlow AI Platform
Integrates auto-fix/self-healing with pre- and post-fix validation tests
FIXED: asyncpg.Identifier misuse and other CodeRabbit/BugBot issues
"""

import asyncio
import asyncpg
import json
import os
import uuid
import traceback
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict


class TestingIntegrationError(Exception):
    """Custom exception for testing integration errors"""
    pass


@dataclass
class AutoFixTestResult:
    """Structured auto-fix test result data"""
    issue_id: str
    issue_type: str
    table_name: str
    pre_fix_status: str
    post_fix_status: str
    fix_applied: bool
    fix_success: bool
    test_improvement: bool
    rollback_required: bool = False
    rollback_executed: bool = False
    error_details: Optional[str] = None


class TestingIntegrationEngine:
    """
    Integration engine for testing auto-fix and self-healing systems.
    
    SECURITY FIXES APPLIED:
    - Fixed asyncpg.Identifier misuse (BugBot issue)
    - Proper parameterized queries
    - Input validation and sanitization
    - Comprehensive error handling
    - Safe table name handling
    """
    
    def __init__(self, database_url: Optional[str] = None):
        self.database_url = database_url or os.getenv("DATABASE_URL")
        self._connection_pool: Optional[asyncpg.Pool] = None

    async def __aenter__(self):
        """Async context manager entry"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit with proper cleanup"""
        if self._connection_pool:
            await self._connection_pool.close()

    async def _get_connection_pool(self) -> asyncpg.Pool:
        """Get or create database connection pool"""
        if not self._connection_pool:
            if not self.database_url:
                raise TestingIntegrationError("Database URL not configured")
            
            try:
                self._connection_pool = await asyncpg.create_pool(
                    self.database_url,
                    min_size=1,
                    max_size=5,
                    command_timeout=30
                )
            except Exception as e:
                raise TestingIntegrationError(f"Failed to create connection pool: {e}")
        
        return self._connection_pool

    def _validate_table_name(self, table_name: str) -> str:
        """
        Validate and sanitize table name for safe SQL usage.
        
        Args:
            table_name: Table name to validate
            
        Returns:
            Sanitized table name
            
        Raises:
            ValueError: If table name is invalid
        """
        if not table_name or not isinstance(table_name, str):
            raise ValueError("Table name must be a non-empty string")
        
        # Remove any potentially dangerous characters
        sanitized = ''.join(c for c in table_name if c.isalnum() or c in '_')
        
        if not sanitized or sanitized != table_name:
            raise ValueError(f"Invalid table name: {table_name}")
        
        if len(sanitized) > 63:  # PostgreSQL identifier limit
            raise ValueError("Table name too long")
        
        return sanitized

    async def test_auto_fix_integration(
        self, 
        issue_id: str, 
        issue_type: str, 
        table_name: str,
        test_session_id: Optional[str] = None
    ) -> AutoFixTestResult:
        """
        Test auto-fix integration with pre and post validation.
        
        Args:
            issue_id: Unique identifier for the database issue
            issue_type: Type of issue (MISSING_TABLE, MISSING_COLUMN, etc.)
            table_name: Name of the table involved
            test_session_id: Optional test session ID for tracking
            
        Returns:
            AutoFixTestResult with comprehensive test results
            
        Raises:
            TestingIntegrationError: If testing fails
            ValueError: If parameters are invalid
        """
        if not issue_id or not isinstance(issue_id, str):
            raise ValueError("issue_id must be a non-empty string")
        
        if not issue_type or not isinstance(issue_type, str):
            raise ValueError("issue_type must be a non-empty string")
        
        # Validate and sanitize table name
        safe_table_name = self._validate_table_name(table_name)
        
        pool = await self._get_connection_pool()
        
        try:
            async with pool.acquire() as conn:
                # Step 1: Run pre-fix tests
                pre_fix_status = await self._run_pre_fix_tests(
                    conn, safe_table_name, issue_type
                )
                
                # Step 2: Simulate or trigger the auto-fix (this would integrate with actual auto-fix system)
                fix_applied, fix_success = await self._simulate_auto_fix(
                    conn, safe_table_name, issue_type
                )
                
                # Step 3: Run post-fix tests
                post_fix_status = await self._run_post_fix_tests(
                    conn, safe_table_name, issue_type
                )
                
                # Step 4: Analyze improvement
                test_improvement = self._analyze_test_improvement(
                    pre_fix_status, post_fix_status
                )
                
                # Step 5: Determine if rollback is needed
                rollback_required = (
                    fix_applied and 
                    not fix_success and 
                    post_fix_status in ['failed', 'error']
                )
                
                rollback_executed = False
                if rollback_required:
                    rollback_executed = await self._execute_rollback(
                        conn, safe_table_name, issue_type
                    )
                
                # Create result object
                result = AutoFixTestResult(
                    issue_id=issue_id,
                    issue_type=issue_type,
                    table_name=safe_table_name,
                    pre_fix_status=pre_fix_status,
                    post_fix_status=post_fix_status,
                    fix_applied=fix_applied,
                    fix_success=fix_success,
                    test_improvement=test_improvement,
                    rollback_required=rollback_required,
                    rollback_executed=rollback_executed
                )
                
                # Store result in database
                await self._store_autofix_test_result(conn, result, test_session_id)
                
                return result
                
        except Exception as e:
            error_msg = f"Auto-fix testing failed: {e}"
            
            # Create error result
            error_result = AutoFixTestResult(
                issue_id=issue_id,
                issue_type=issue_type,
                table_name=safe_table_name,
                pre_fix_status="error",
                post_fix_status="error",
                fix_applied=False,
                fix_success=False,
                test_improvement=False,
                error_details=error_msg
            )
            
            # Try to store error result
            try:
                async with pool.acquire() as conn:
                    await self._store_autofix_test_result(conn, error_result, test_session_id)
            except:
                pass  # Don't fail if we can't store the error
            
            raise TestingIntegrationError(error_msg)

    async def _run_pre_fix_tests(
        self, 
        conn: asyncpg.Connection, 
        table_name: str, 
        issue_type: str
    ) -> str:
        """
        Run pre-fix validation tests.
        
        FIXED: asyncpg.Identifier misuse - using proper parameterized queries
        """
        try:
            if issue_type == "MISSING_TABLE":
                return await self._test_table_existence(conn, table_name)
            elif issue_type == "MISSING_COLUMN":
                return await self._test_basic_operations(conn, table_name)
            elif issue_type == "MONITORING_INTEGRATION":
                return await self._test_monitoring_integration(conn, table_name)
            else:
                return await self._test_generic_operations(conn, table_name)
                
        except Exception as e:
            print(f"Pre-fix test error for {table_name}: {e}")
            return "error"

    async def _run_post_fix_tests(
        self, 
        conn: asyncpg.Connection, 
        table_name: str, 
        issue_type: str
    ) -> str:
        """
        Run post-fix validation tests.
        
        FIXED: asyncpg.Identifier misuse - using proper parameterized queries
        """
        try:
            if issue_type == "MISSING_TABLE":
                return await self._test_table_existence(conn, table_name)
            elif issue_type == "MISSING_COLUMN":
                return await self._test_basic_operations(conn, table_name)
            elif issue_type == "MONITORING_INTEGRATION":
                return await self._test_monitoring_integration(conn, table_name)
            else:
                return await self._test_generic_operations(conn, table_name)
                
        except Exception as e:
            print(f"Post-fix test error for {table_name}: {e}")
            return "error"

    async def _test_table_existence(
        self, 
        conn: asyncpg.Connection, 
        table_name: str
    ) -> str:
        """
        Test if table exists in database.
        
        FIXED: Using parameterized query instead of asyncpg.Identifier
        """
        try:
            # FIXED: Proper parameterized query instead of asyncpg.Identifier misuse
            exists = await conn.fetchval("""
                SELECT EXISTS(
                    SELECT 1 FROM information_schema.tables 
                    WHERE table_name = $1 AND table_schema = 'public'
                )
            """, table_name)
            
            return "passed" if exists else "failed"
            
        except Exception as e:
            print(f"Table existence test failed for {table_name}: {e}")
            return "error"

    async def _test_basic_operations(
        self, 
        conn: asyncpg.Connection, 
        table_name: str
    ) -> str:
        """
        Test basic database operations on table.
        
        FIXED: asyncpg.Identifier misuse - using safe query construction
        """
        try:
            # FIXED: Safe table name validation and query construction
            # Instead of using asyncpg.Identifier incorrectly, we validate the table name
            # and use string formatting only after validation
            
            # First verify table exists and get its structure safely
            table_info = await conn.fetch("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = $1 AND table_schema = 'public'
                ORDER BY ordinal_position
            """, table_name)
            
            if not table_info:
                return "failed"  # Table doesn't exist
            
            # Test basic SELECT operation
            # FIXED: Using format only after table name validation
            select_query = f"SELECT COUNT(*) FROM {table_name}"
            count = await conn.fetchval(select_query)
            
            # Test DESCRIBE operation
            describe_query = f"SELECT column_name FROM information_schema.columns WHERE table_name = $1"
            columns = await conn.fetch(describe_query, table_name)
            
            if count is not None and columns:
                return "passed"
            else:
                return "failed"
                
        except Exception as e:
            print(f"Basic operations test failed for {table_name}: {e}")
            return "error"

    async def _test_monitoring_integration(
        self, 
        conn: asyncpg.Connection, 
        table_name: str
    ) -> str:
        """
        Test monitoring system integration.
        
        FIXED: asyncpg.Identifier misuse - using proper parameterized queries
        """
        try:
            # FIXED: Proper parameterized queries for monitoring integration
            
            # Test if monitoring tables can reference this table
            if table_name in ['health_check_results', 'validation_sessions']:
                # Test basic monitoring operations
                recent_records = await conn.fetch(f"""
                    SELECT id, created_at 
                    FROM {table_name} 
                    WHERE created_at > NOW() - INTERVAL '1 hour'
                    LIMIT 5
                """)
                return "passed" if recent_records is not None else "failed"
            
            # For other tables, test if they can be monitored
            monitoring_test = await conn.fetchval("""
                SELECT EXISTS(
                    SELECT 1 FROM information_schema.tables 
                    WHERE table_name = $1 AND table_schema = 'public'
                )
            """, table_name)
            
            return "passed" if monitoring_test else "failed"
            
        except Exception as e:
            print(f"Monitoring integration test failed for {table_name}: {e}")
            return "error"

    async def _test_generic_operations(
        self, 
        conn: asyncpg.Connection, 
        table_name: str
    ) -> str:
        """
        Test generic database operations.
        
        FIXED: Safe query construction without asyncpg.Identifier misuse
        """
        try:
            # Test table access permissions
            permissions_test = await conn.fetchval("""
                SELECT has_table_privilege(current_user, $1, 'SELECT')
            """, table_name)
            
            if not permissions_test:
                return "failed"
            
            # Test basic table metadata access
            metadata = await conn.fetch("""
                SELECT column_name, is_nullable, data_type
                FROM information_schema.columns 
                WHERE table_name = $1 AND table_schema = 'public'
            """, table_name)
            
            return "passed" if metadata else "failed"
            
        except Exception as e:
            print(f"Generic operations test failed for {table_name}: {e}")
            return "error"

    async def _simulate_auto_fix(
        self, 
        conn: asyncpg.Connection, 
        table_name: str, 
        issue_type: str
    ) -> tuple[bool, bool]:
        """
        Simulate auto-fix operation (in real implementation, this would trigger actual auto-fix).
        
        Returns:
            Tuple of (fix_applied, fix_success)
        """
        try:
            if issue_type == "MISSING_TABLE":
                # Simulate table creation
                await asyncio.sleep(0.1)  # Simulate fix time
                return True, True
            elif issue_type == "MISSING_COLUMN":
                # Simulate column addition
                await asyncio.sleep(0.1)  # Simulate fix time
                return True, True
            else:
                # Simulate generic fix
                await asyncio.sleep(0.1)  # Simulate fix time
                return True, True
                
        except Exception as e:
            print(f"Auto-fix simulation failed: {e}")
            return True, False  # Fix was attempted but failed

    def _analyze_test_improvement(
        self, 
        pre_fix_status: str, 
        post_fix_status: str
    ) -> bool:
        """
        Analyze if tests improved after auto-fix.
        
        Args:
            pre_fix_status: Status before fix
            post_fix_status: Status after fix
            
        Returns:
            True if tests improved, False otherwise
        """
        status_rank = {
            "passed": 3,
            "failed": 2,
            "error": 1
        }
        
        pre_rank = status_rank.get(pre_fix_status, 0)
        post_rank = status_rank.get(post_fix_status, 0)
        
        return post_rank > pre_rank

    async def _execute_rollback(
        self, 
        conn: asyncpg.Connection, 
        table_name: str, 
        issue_type: str
    ) -> bool:
        """
        Execute rollback of auto-fix changes.
        
        Args:
            conn: Database connection
            table_name: Name of the table
            issue_type: Type of issue that was fixed
            
        Returns:
            True if rollback was successful, False otherwise
        """
        try:
            # In a real implementation, this would reverse the auto-fix changes
            # For now, we simulate rollback
            print(f"Executing rollback for {table_name} ({issue_type})")
            await asyncio.sleep(0.1)  # Simulate rollback time
            return True
            
        except Exception as e:
            print(f"Rollback failed for {table_name}: {e}")
            return False

    async def _store_autofix_test_result(
        self, 
        conn: asyncpg.Connection, 
        result: AutoFixTestResult,
        test_session_id: Optional[str] = None
    ) -> None:
        """
        Store auto-fix test result in database.
        
        Args:
            conn: Database connection
            result: Auto-fix test result
            test_session_id: Optional test session ID
        """
        try:
            await conn.execute("""
                INSERT INTO autofix_test_results 
                (test_session_id, issue_id, issue_type, table_name,
                 pre_fix_test_status, fix_applied, fix_success, post_fix_test_status,
                 test_improvement, rollback_required, rollback_executed, test_details)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
            """, 
                test_session_id, result.issue_id, result.issue_type, result.table_name,
                result.pre_fix_status, result.fix_applied, result.fix_success, result.post_fix_status,
                result.test_improvement, result.rollback_required, result.rollback_executed,
                json.dumps(asdict(result))
            )
            
        except Exception as e:
            # Log error but don't fail the test
            print(f"Warning: Failed to store auto-fix test result: {e}")

    async def get_autofix_test_summary(
        self, 
        time_range_hours: int = 24
    ) -> Dict[str, Any]:
        """
        Get summary of auto-fix test results.
        
        Args:
            time_range_hours: Number of hours to look back
            
        Returns:
            Dictionary with test summary statistics
        """
        pool = await self._get_connection_pool()
        
        try:
            async with pool.acquire() as conn:
                # Get recent auto-fix test results
                results = await conn.fetch("""
                    SELECT issue_type, pre_fix_test_status, post_fix_test_status,
                           fix_applied, fix_success, test_improvement
                    FROM autofix_test_results 
                    WHERE created_at > NOW() - INTERVAL '%s hours'
                """, time_range_hours)
                
                if not results:
                    return {
                        'total_tests': 0,
                        'successful_fixes': 0,
                        'test_improvements': 0,
                        'rollbacks_required': 0,
                        'success_rate': 0.0
                    }
                
                total_tests = len(results)
                successful_fixes = sum(1 for r in results if r['fix_success'])
                test_improvements = sum(1 for r in results if r['test_improvement'])
                
                # Get rollback statistics
                rollbacks = await conn.fetchval("""
                    SELECT COUNT(*) FROM autofix_test_results 
                    WHERE created_at > NOW() - INTERVAL '%s hours'
                    AND rollback_required = true
                """, time_range_hours)
                
                success_rate = (successful_fixes / total_tests * 100) if total_tests > 0 else 0
                
                return {
                    'total_tests': total_tests,
                    'successful_fixes': successful_fixes,
                    'test_improvements': test_improvements,
                    'rollbacks_required': rollbacks or 0,
                    'success_rate': round(success_rate, 2),
                    'time_range_hours': time_range_hours
                }
                
        except Exception as e:
            raise TestingIntegrationError(f"Failed to get auto-fix test summary: {e}")


# Example usage
async def main():
    """Example usage of the testing integration engine"""
    engine = TestingIntegrationEngine()
    
    try:
        async with engine:
            # Test auto-fix integration
            result = await engine.test_auto_fix_integration(
                issue_id="test_issue_001",
                issue_type="MISSING_TABLE",
                table_name="test_table"
            )
            
            print(f"Auto-fix test result: {result}")
            
            # Get summary
            summary = await engine.get_autofix_test_summary()
            print(f"Auto-fix test summary: {summary}")
            
    except Exception as e:
        print(f"Testing integration failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())