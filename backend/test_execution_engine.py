"""
Secure Test Execution Engine for JyotiFlow AI Platform
Executes test suites safely with AST validation and comprehensive monitoring
"""

import asyncio
import asyncpg
import json
import os
import ast
import uuid
import secrets
import string
import traceback
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass


class TestExecutionError(Exception):
    """Custom exception for test execution errors"""
    pass


class SecurityValidationError(Exception):
    """Exception raised when test code fails security validation"""
    pass


@dataclass
class TestResult:
    """Structured test result data"""
    test_name: str
    status: str
    execution_time_ms: int
    error_message: Optional[str] = None
    stack_trace: Optional[str] = None
    assertions_passed: int = 0
    assertions_failed: int = 0


class SecureTestExecutionEngine:
    """
    Secure test execution engine with AST validation and restricted execution environment.
    
    Security Features:
    - AST parsing and validation before execution
    - Restricted builtin functions
    - Safe module imports only
    - Input sanitization and validation
    - Comprehensive error handling
    """
    
    def __init__(self, database_url: Optional[str] = None):
        self.database_url = database_url or os.getenv("DATABASE_URL")
        self._connection_pool: Optional[asyncpg.Pool] = None
        
        # Security: Define safe builtins for test execution
        self.safe_builtins = {
            'len', 'str', 'int', 'float', 'bool', 'dict', 'list', 'tuple', 'set',
            'range', 'enumerate', 'zip', 'print', 'abs', 'min', 'max', 'sum',
            'Exception', 'ValueError', 'TypeError', 'AssertionError', 'RuntimeError'
        }
        
        # Security: Define allowed modules for imports
        self.safe_modules = {
            'asyncio', 'asyncpg', 'uuid', 'json', 'datetime', 
            'httpx', 're', 'math', 'random', 'time'
        }
        
        # Security: Define dangerous functions that should never be executed
        self.dangerous_functions = {
            'eval', 'exec', 'compile', '__import__', 'open', 'file', 
            'input', 'raw_input', 'reload', 'vars', 'locals', 'globals',
            'getattr', 'setattr', 'delattr', 'hasattr'
        }

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
                raise TestExecutionError("Database URL not configured")
            
            try:
                self._connection_pool = await asyncpg.create_pool(
                    self.database_url,
                    min_size=1,
                    max_size=5,
                    command_timeout=30
                )
            except Exception as e:
                raise TestExecutionError(f"Failed to create connection pool: {e}")
        
        return self._connection_pool

    def _validate_test_input(self, test_case: Dict[str, Any]) -> None:
        """
        Validate test input data for security and completeness.
        
        Args:
            test_case: Dictionary containing test case data
            
        Raises:
            ValueError: If required fields are missing
            TypeError: If field types are incorrect
            SecurityValidationError: If content fails security checks
        """
        required_fields = ['test_name', 'test_code', 'test_type']
        
        for field in required_fields:
            if field not in test_case:
                raise ValueError(f"Missing required field: {field}")
        
        if not isinstance(test_case['test_name'], str):
            raise TypeError("test_name must be a string")
        
        if not isinstance(test_case['test_code'], str):
            raise TypeError("test_code must be a string")
        
        # Security: Basic content validation
        if len(test_case['test_code']) > 50000:  # 50KB limit
            raise SecurityValidationError("Test code exceeds maximum length")
        
        # Security: Check for suspicious patterns
        suspicious_patterns = ['__import__', 'eval(', 'exec(', 'compile(']
        for pattern in suspicious_patterns:
            if pattern in test_case['test_code']:
                raise SecurityValidationError(f"Suspicious pattern detected: {pattern}")

    def _validate_ast_safety(self, parsed_ast: ast.AST) -> None:
        """
        Validate AST for dangerous operations.
        
        Args:
            parsed_ast: Parsed AST tree
            
        Raises:
            SecurityValidationError: If dangerous operations are detected
        """
        for node in ast.walk(parsed_ast):
            # Check for dangerous function calls
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in self.dangerous_functions:
                        raise SecurityValidationError(f"Dangerous function call: {node.func.id}")
            
            # Check for dangerous imports
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name not in self.safe_modules:
                        raise SecurityValidationError(f"Unsafe import: {alias.name}")
            
            elif isinstance(node, ast.ImportFrom):
                if node.module and node.module not in self.safe_modules:
                    raise SecurityValidationError(f"Unsafe import from: {node.module}")

    def _create_safe_globals(self) -> Dict[str, Any]:
        """
        Create a safe global namespace for test execution.
        
        Returns:
            Dictionary with safe built-in functions and modules
        """
        safe_globals = {
            '__builtins__': {name: getattr(__builtins__, name) 
                           for name in self.safe_builtins 
                           if hasattr(__builtins__, name)},
            'asyncio': asyncio,
            'asyncpg': asyncpg,
            'uuid': uuid,
            'json': json,
            'datetime': datetime,
        }
        return safe_globals

    async def _execute_test_code_safely(
        self, 
        test_code: str, 
        test_case: Dict[str, Any]
    ) -> Union[Dict[str, Any], Any]:
        """
        Execute test code safely with AST validation and restricted environment.
        
        Args:
            test_code: Python code to execute
            test_case: Test case context data
            
        Returns:
            Test execution result
            
        Raises:
            TestExecutionError: If execution fails
            SecurityValidationError: If code fails security validation
        """
        try:
            # Security: Parse and validate syntax first
            parsed = ast.parse(test_code, mode='exec')
            
            # Security: Validate AST for dangerous operations
            self._validate_ast_safety(parsed)
            
            # Security: Compile to bytecode
            compiled = compile(parsed, '<test_code>', 'exec')
            
            # Security: Create restricted execution environment
            test_globals = self._create_safe_globals()
            test_globals.update({
                'test_case': test_case,
                'database_url': self.database_url,
                'TestExecutionError': TestExecutionError
            })
            
            # Execute with restricted globals
            exec(compiled, test_globals)
            
            # Extract result if available
            return test_globals.get('result', {'status': 'completed'})
            
        except SyntaxError as e:
            raise TestExecutionError(f"Syntax error in test code: {e}")
        except SecurityValidationError:
            raise  # Re-raise security errors
        except (NameError, TypeError, AttributeError) as e:
            raise TestExecutionError(f"Test code execution error: {e}")
        except Exception as e:
            raise TestExecutionError(f"Unexpected error in test execution: {e}")

    async def execute_test_suite(
        self, 
        suite_name: str, 
        test_category: str = "manual"
    ) -> Dict[str, Any]:
        """
        Execute a specific test suite and return comprehensive results.
        
        Args:
            suite_name: Name of the test suite to execute
            test_category: Category for organizing test results (default: "manual")
            
        Returns:
            Dict containing:
                - session_id: Unique identifier for this test run
                - status: Overall test status ("passed", "failed", "partial", "error")
                - total_tests: Number of tests executed
                - passed_tests: Number of tests that passed
                - failed_tests: Number of tests that failed
                - success_rate: Percentage of tests that passed
                - results: Detailed results for each test case
                
        Raises:
            TestExecutionError: If test execution fails
            ValueError: If parameters are invalid
        """
        if not suite_name or not isinstance(suite_name, str):
            raise ValueError("suite_name must be a non-empty string")
        
        session_id = str(uuid.uuid4())
        start_time = datetime.now(timezone.utc)
        
        try:
            pool = await self._get_connection_pool()
            
            # Create test session record
            async with pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO test_execution_sessions 
                    (session_id, test_type, test_category, started_at, triggered_by, status)
                    VALUES ($1, $2, $3, $4, $5, $6)
                """, session_id, "suite", test_category, start_time, "manual", "running")
            
            # Get test cases for this suite
            test_cases = await self._get_test_cases_for_suite(suite_name)
            
            if not test_cases:
                raise TestExecutionError(f"No test cases found for suite: {suite_name}")
            
            results = []
            passed_count = 0
            failed_count = 0
            
            # Execute each test case
            for test_case in test_cases:
                try:
                    self._validate_test_input(test_case)
                    
                    test_start = datetime.now(timezone.utc)
                    
                    # Execute the test safely
                    test_result = await self._execute_test_code_safely(
                        test_case['test_code'], 
                        test_case
                    )
                    
                    test_end = datetime.now(timezone.utc)
                    execution_time_ms = int((test_end - test_start).total_seconds() * 1000)
                    
                    # Determine test status
                    status = "passed" if test_result.get('status') == 'passed' else "failed"
                    if status == "passed":
                        passed_count += 1
                    else:
                        failed_count += 1
                    
                    result = TestResult(
                        test_name=test_case['test_name'],
                        status=status,
                        execution_time_ms=execution_time_ms,
                        assertions_passed=test_result.get('assertions_passed', 0),
                        assertions_failed=test_result.get('assertions_failed', 0)
                    )
                    
                    results.append(result)
                    
                    # Store individual test result
                    await self._store_test_result(conn, session_id, test_case, result)
                    
                except Exception as e:
                    failed_count += 1
                    error_result = TestResult(
                        test_name=test_case.get('test_name', 'Unknown'),
                        status="error",
                        execution_time_ms=0,
                        error_message=str(e),
                        stack_trace=traceback.format_exc()
                    )
                    results.append(error_result)
                    
                    # Store error result
                    await self._store_test_result(conn, session_id, test_case, error_result)
            
            # Calculate overall status and metrics
            total_tests = len(test_cases)
            success_rate = (passed_count / total_tests * 100) if total_tests > 0 else 0
            
            overall_status = "passed" if failed_count == 0 else "failed"
            if passed_count > 0 and failed_count > 0:
                overall_status = "partial"
            
            end_time = datetime.now(timezone.utc)
            execution_time_seconds = int((end_time - start_time).total_seconds())
            
            # Update session with final results
            async with pool.acquire() as conn:
                await conn.execute("""
                    UPDATE test_execution_sessions 
                    SET completed_at = $1, status = $2, total_tests = $3, 
                        passed_tests = $4, failed_tests = $5, execution_time_seconds = $6
                    WHERE session_id = $7
                """, end_time, overall_status, total_tests, passed_count, 
                    failed_count, execution_time_seconds, session_id)
            
            return {
                'session_id': session_id,
                'status': overall_status,
                'total_tests': total_tests,
                'passed_tests': passed_count,
                'failed_tests': failed_count,
                'success_rate': round(success_rate, 2),
                'execution_time_seconds': execution_time_seconds,
                'results': [
                    {
                        'test_name': r.test_name,
                        'status': r.status,
                        'execution_time_ms': r.execution_time_ms,
                        'error_message': r.error_message,
                        'assertions_passed': r.assertions_passed,
                        'assertions_failed': r.assertions_failed
                    } for r in results
                ]
            }
            
        except Exception as e:
            # Update session with error status
            try:
                async with pool.acquire() as conn:
                    await conn.execute("""
                        UPDATE test_execution_sessions 
                        SET completed_at = $1, status = $2 
                        WHERE session_id = $3
                    """, datetime.now(timezone.utc), "error", session_id)
            except:
                pass  # Don't fail if we can't update the session
            
            raise TestExecutionError(f"Test suite execution failed: {e}")

    async def _get_test_cases_for_suite(self, suite_name: str) -> List[Dict[str, Any]]:
        """
        Get test cases for a specific test suite.
        
        Args:
            suite_name: Name of the test suite
            
        Returns:
            List of test case dictionaries
        """
        # For now, return sample test cases
        # In production, this would query a test registry or file system
        sample_tests = {
            'Database Operations': [
                {
                    'test_name': 'Test Database Connection',
                    'test_code': '''
import asyncpg
async def test_connection():
    try:
        conn = await asyncpg.connect(database_url)
        await conn.execute("SELECT 1")
        await conn.close()
        result = {"status": "passed", "assertions_passed": 1}
    except Exception as e:
        result = {"status": "failed", "error": str(e), "assertions_failed": 1}
    return result
result = asyncio.run(test_connection())
''',
                    'test_type': 'integration',
                    'test_category': 'database'
                }
            ],
            'API Endpoints': [
                {
                    'test_name': 'Test Health Check Endpoint',
                    'test_code': '''
import httpx
async def test_health():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("https://jyotiflow-ai.onrender.com/health")
            assert response.status_code == 200
            result = {"status": "passed", "assertions_passed": 1}
    except Exception as e:
        result = {"status": "failed", "error": str(e), "assertions_failed": 1}
    return result
result = asyncio.run(test_health())
''',
                    'test_type': 'integration',
                    'test_category': 'api'
                }
            ]
        }
        
        return sample_tests.get(suite_name, [])

    async def _store_test_result(
        self, 
        conn: asyncpg.Connection, 
        session_id: str, 
        test_case: Dict[str, Any], 
        result: TestResult
    ) -> None:
        """
        Store individual test result in database.
        
        Args:
            conn: Database connection
            session_id: Test session ID
            test_case: Original test case data
            result: Test execution result
        """
        try:
            await conn.execute("""
                INSERT INTO test_case_results 
                (session_id, test_name, test_category, status, execution_time_ms,
                 error_message, stack_trace, assertions_passed, assertions_failed)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            """, session_id, result.test_name, test_case.get('test_category'),
                result.status, result.execution_time_ms, result.error_message,
                result.stack_trace, result.assertions_passed, result.assertions_failed)
        except Exception as e:
            # Log error but don't fail the test execution
            print(f"Warning: Failed to store test result: {e}")


# Example usage and testing
async def main():
    """Example usage of the secure test execution engine"""
    engine = SecureTestExecutionEngine()
    
    try:
        async with engine:
            result = await engine.execute_test_suite("Database Operations", "automated")
            print(f"Test execution completed: {result}")
    except Exception as e:
        print(f"Test execution failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())