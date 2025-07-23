#!/usr/bin/env python3
"""
Test Execution Engine for JyotiFlow AI Platform
Executes comprehensive test suites and reports results
"""

import os
import sys
import json
import uuid
import asyncio
import asyncpg
import traceback
import importlib
import ast
import secrets
import string
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Callable, Union
import logging

# Add current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")

class TestExecutionError(Exception):
    """Custom exception for test execution failures"""
    pass

class TestExecutionEngine:
    """
    Executes test suites and reports results to monitoring system
    Integrates with the testing infrastructure and auto-fix validation
    """
    
    def __init__(self):
        self.database_url = DATABASE_URL
        self.current_session_id = None
        self.results = {}
        
    async def execute_test_suite(self, suite_name: str, test_category: str = "manual") -> Dict[str, Any]:
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
            DatabaseConnectionError: If unable to connect to database
            TestExecutionError: If test execution fails
            TimeoutError: If test execution exceeds timeout
        """
        logger.info("🧪 Executing test suite: %s", suite_name.replace('"', '').replace("'", ""))
        
        # Create test execution session
        session_id = await self._create_test_session(suite_name, test_category)
        self.current_session_id = session_id
        
        try:
            # Get test cases for this suite
            test_cases = await self._get_test_cases(suite_name)
            
            if not test_cases:
                logger.warning(f"No test cases found for suite: {suite_name}")
                return {
                    "session_id": session_id,
                    "status": "error",
                    "message": "No test cases found",
                    "results": {}
                }
            
            # Execute all test cases
            results = {}
            total_tests = len(test_cases)
            passed_tests = 0
            failed_tests = 0
            
            for test_case in test_cases:
                logger.info(f"  ▶️ Running: {test_case['test_name']}")
                
                test_result = await self._execute_single_test(test_case)
                results[test_case['test_name']] = test_result
                
                if test_result['status'] == 'passed':
                    passed_tests += 1
                elif test_result['status'] == 'failed':
                    failed_tests += 1
                
                # Store individual test result
                await self._store_test_result(session_id, test_case, test_result)
            
            # Calculate overall status
            overall_status = self._calculate_overall_status(passed_tests, failed_tests, total_tests)
            
            # Update session with final results
            await self._update_test_session(session_id, overall_status, total_tests, passed_tests, failed_tests)
            
            execution_summary = {
                "session_id": session_id,
                "status": overall_status,
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": round((passed_tests / total_tests) * 100, 2) if total_tests > 0 else 0,
                "results": results
            }
            
            logger.info(f"✅ Test suite '{suite_name}' completed: {passed_tests}/{total_tests} passed")
            return execution_summary
            
        except Exception as e:
            logger.error(f"❌ Test suite execution failed: {e}")
            await self._update_test_session(session_id, "error", 0, 0, 0, str(e))
            return {
                "session_id": session_id,
                "status": "error", 
                "error": str(e),
                "results": {}
            }
    
    async def execute_all_test_suites(self) -> Dict[str, Any]:
        """Execute all available test suites"""
        logger.info("🚀 Executing ALL test suites...")
        
        # Get all available test suites
        test_suites = await self._get_available_test_suites()
        
        if not test_suites:
            logger.warning("No test suites found")
            return {"status": "error", "message": "No test suites found"}
        
        all_results = {}
        overall_summary = {
            "total_suites": len(test_suites),
            "passed_suites": 0,
            "failed_suites": 0,
            "total_tests": 0,
            "total_passed": 0,
            "total_failed": 0
        }
        
        for suite in test_suites:
            suite_name = suite['test_type']
            suite_category = suite['test_category']
            
            suite_result = await self.execute_test_suite(suite_name, suite_category)
            all_results[suite_name] = suite_result
            
            # Update overall summary
            if suite_result['status'] == 'passed':
                overall_summary['passed_suites'] += 1
            else:
                overall_summary['failed_suites'] += 1
                
            overall_summary['total_tests'] += suite_result.get('total_tests', 0)
            overall_summary['total_passed'] += suite_result.get('passed_tests', 0)
            overall_summary['total_failed'] += suite_result.get('failed_tests', 0)
        
        # Calculate overall success rate
        if overall_summary['total_tests'] > 0:
            overall_summary['success_rate'] = round(
                (overall_summary['total_passed'] / overall_summary['total_tests']) * 100, 2
            )
        else:
            overall_summary['success_rate'] = 0
        
        logger.info(f"🎯 ALL TEST SUITES COMPLETED: {overall_summary['total_passed']}/{overall_summary['total_tests']} tests passed")
        
        return {
            "status": "completed",
            "summary": overall_summary,
            "suite_results": all_results
        }
    
    async def execute_quick_health_check(self) -> Dict[str, Any]:
        """Execute a quick health check test suite for monitoring"""
        logger.info("⚡ Executing quick health check...")
        
        session_id = await self._create_test_session("Quick Health Check", "health_check")
        
        health_checks = [
            {
                "test_name": "database_connectivity",
                "test_function": self._test_database_connectivity
            },
            {
                "test_name": "api_health_endpoint",
                "test_function": self._test_api_health_endpoint
            },
            {
                "test_name": "critical_tables_exist",
                "test_function": self._test_critical_tables_exist
            }
        ]
        
        results = {}
        passed = 0
        failed = 0
        
        for check in health_checks:
            try:
                result = await check["test_function"]()
                results[check["test_name"]] = result
                if result.get("status") == "passed":
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                results[check["test_name"]] = {
                    "status": "failed",
                    "error": str(e)
                }
                failed += 1
        
        overall_status = "passed" if failed == 0 else "failed"
        total = len(health_checks)
        
        await self._update_test_session(session_id, overall_status, total, passed, failed)
        
        return {
            "session_id": session_id,
            "status": overall_status,
            "total_checks": total,
            "passed_checks": passed,
            "failed_checks": failed,
            "results": results
        }
    
    async def _execute_single_test(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single test case"""
        start_time = datetime.now(timezone.utc)
        
        try:
            test_code = test_case.get('test_code', '')
            timeout = test_case.get('timeout_seconds', 30)
            
            if not test_code:
                return {
                    "status": "failed",
                    "error": "No test code provided",
                    "execution_time_ms": 0
                }
            
            # Execute test code with timeout
            result = await asyncio.wait_for(
                self._execute_test_code(test_code, test_case),
                timeout=timeout
            )
            
            execution_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            
            if isinstance(result, dict) and result.get('status'):
                result['execution_time_ms'] = execution_time
                return result
            else:
                return {
                    "status": "passed",
                    "message": "Test completed successfully",
                    "execution_time_ms": execution_time,
                    "result": result
                }
                
        except asyncio.TimeoutError:
            execution_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            return {
                "status": "failed",
                "error": f"Test timed out after {test_case.get('timeout_seconds', 30)}s",
                "execution_time_ms": execution_time
            }
        except Exception as e:
            execution_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            return {
                "status": "failed",
                "error": str(e),
                "traceback": traceback.format_exc(),
                "execution_time_ms": execution_time
            }
    

    
    async def _execute_test_code(self, test_code: str, test_case: Dict[str, Any]) -> Union[Dict[str, Any], Any]:
        """
        Safely execute test code with proper validation and security measures.
        
        Args:
            test_code: The test code to execute
            test_case: Test case metadata and configuration
            
        Returns:
            Test execution result
            
        Raises:
            TestExecutionError: If test execution fails
            SyntaxError: If test code has syntax errors
        """
        # Validate test case input
        self._validate_test_input(test_case)
        
        # Create a restricted execution environment
        test_globals = {
            '__builtins__': {
                'len': len, 'str': str, 'int': int, 'float': float, 'bool': bool,
                'dict': dict, 'list': list, 'tuple': tuple, 'set': set,
                'range': range, 'enumerate': enumerate, 'zip': zip,
                'print': print, 'Exception': Exception, 'ValueError': ValueError,
                'TypeError': TypeError, 'AssertionError': AssertionError
            },
            'asyncio': asyncio,
            'asyncpg': asyncpg,
            'uuid': uuid,
            'json': json,
            'datetime': datetime,
            'timezone': timezone,
            'DATABASE_URL': DATABASE_URL,
            'logger': logger
        }
        
        # Add test case data to globals
        test_globals.update(test_case)
        
        try:
            # Import additional modules if needed (with validation)
            if 'httpx' in test_code:
                import httpx
                test_globals['httpx'] = httpx
            
            if 'database_self_healing_system' in test_code:
                try:
                    from database_self_healing_system import DatabaseSelfHealingSystem, extract_table_from_query
                    test_globals['DatabaseSelfHealingSystem'] = DatabaseSelfHealingSystem
                    test_globals['extract_table_from_query'] = extract_table_from_query
                except ImportError as e:
                    logger.warning("Could not import database_self_healing_system: %s", str(e))
            
            # SECURITY FIX: Use AST parsing instead of direct exec()
            try:
                # Parse and validate syntax first
                parsed = ast.parse(test_code, mode='exec')
                
                # Validate AST for dangerous operations
                self._validate_ast_safety(parsed)
                
                # Compile to bytecode
                compiled = compile(parsed, '<test_code>', 'exec')
                
                # Execute with restricted globals
                exec(compiled, test_globals)
                
            except SyntaxError as e:
                raise TestExecutionError(f"Invalid test code syntax: {e}") from e
            except Exception as e:
                raise TestExecutionError(f"Test code compilation failed: {e}") from e
            
            # Find and execute the test function
            test_function_name = test_case.get('test_name', 'test_function')
            if test_function_name in test_globals:
                test_function = test_globals[test_function_name]
                if asyncio.iscoroutinefunction(test_function):
                    return await test_function()
                else:
                    return test_function()
            else:
                # Look for any async function in the globals
                for name, obj in test_globals.items():
                    if name.startswith('test_') and asyncio.iscoroutinefunction(obj):
                        return await obj()
                
                raise TestExecutionError(f"No test function found: {test_function_name}")
                
        except (SyntaxError, NameError, TypeError) as e:
            logger.error("Test code execution failed: %s", str(e))
            raise TestExecutionError(f"Test failed: {e}") from e
        except Exception as e:
            logger.error("Unexpected error in test execution: %s", str(e))
            raise
    
    def _validate_test_input(self, test_case: Dict[str, Any]) -> None:
        """Validate test case input for required fields and types."""
        required_fields = ['test_name', 'test_code', 'test_type']
        for field in required_fields:
            if field not in test_case:
                raise ValueError(f"Missing required field: {field}")
        
        if not isinstance(test_case['test_name'], str):
            raise TypeError("test_name must be a string")
        
        if not isinstance(test_case['test_code'], str):
            raise TypeError("test_code must be a string")
    
    def _validate_ast_safety(self, node: ast.AST) -> None:
        """
        Validate AST for potentially dangerous operations.
        
        Args:
            node: AST node to validate
            
        Raises:
            TestExecutionError: If dangerous operations are detected
        """
        dangerous_functions = {
            'eval', 'exec', 'compile', '__import__',
            'open', 'file', 'input', 'raw_input',
            'reload', 'vars', 'locals', 'globals'
        }
        
        safe_modules = {
            'asyncio', 'asyncpg', 'uuid', 'json', 'datetime', 'httpx',
            'secrets', 'string'  # Added for password generation
        }
        
        for child in ast.walk(node):
            # Check for dangerous function calls
            if isinstance(child, ast.Call) and isinstance(child.func, ast.Name):
                if child.func.id in dangerous_functions:
                    raise TestExecutionError(f"Unsafe function call detected: {child.func.id}")
            
            # Check for dangerous imports
            if isinstance(child, ast.Import):
                for alias in child.names:
                    if alias.name not in safe_modules:
                        raise TestExecutionError(f"Unsafe import detected: {alias.name}")
            
            if isinstance(child, ast.ImportFrom):
                if child.module and child.module not in safe_modules:
                    raise TestExecutionError(f"Unsafe module import: {child.module}")
            
            # Check for attribute access to dangerous modules (like os.system)
            if isinstance(child, ast.Attribute):
                if isinstance(child.value, ast.Name):
                    # Block dangerous module usage
                    dangerous_attrs = {
                        'os': ['system', 'popen', 'spawn', 'exec', 'remove', 'rmdir'],
                        'subprocess': ['call', 'run', 'Popen', 'check_output'],
                        'shutil': ['rmtree', 'move', 'copy'],
                        'sys': ['exit', 'path']
                    }
                    
                    module_name = child.value.id
                    attr_name = child.attr
                    
                    if module_name in dangerous_attrs and attr_name in dangerous_attrs[module_name]:
                        raise TestExecutionError(f"Unsafe module operation: {module_name}.{attr_name}")
    
    async def _test_database_connectivity(self) -> Dict[str, Any]:
        """Quick database connectivity test"""
        try:
            conn = await asyncpg.connect(self.database_url)
            await conn.fetchval("SELECT 1")
            await conn.close()
            return {"status": "passed", "message": "Database connectivity OK"}
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    async def _test_api_health_endpoint(self) -> Dict[str, Any]:
        """Test API health endpoint"""
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.get("https://jyotiflow-ai.onrender.com/health", timeout=10)
                if response.status_code == 200:
                    return {"status": "passed", "message": "API health endpoint OK"}
                else:
                    return {"status": "failed", "error": f"Health endpoint returned {response.status_code}"}
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    async def _test_critical_tables_exist(self) -> Dict[str, Any]:
        """Test that critical tables exist"""
        try:
            conn = await asyncpg.connect(self.database_url)
            
            critical_tables = ['users', 'sessions', 'rag_knowledge_base']
            missing_tables = []
            
            for table in critical_tables:
                exists = await conn.fetchval('''
                    SELECT EXISTS(
                        SELECT 1 FROM information_schema.tables 
                        WHERE table_name = $1
                    )
                ''', table)
                
                if not exists:
                    missing_tables.append(table)
            
            await conn.close()
            
            if missing_tables:
                return {"status": "failed", "error": f"Missing critical tables: {missing_tables}"}
            else:
                return {"status": "passed", "message": "All critical tables exist"}
                
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    async def _create_test_session(self, test_type: str, test_category: str) -> str:
        """Create a new test execution session"""
        if not self.database_url:
            return str(uuid.uuid4())
            
        session_id = str(uuid.uuid4())
        
        try:
            conn = await asyncpg.connect(self.database_url)
            await conn.execute('''
                INSERT INTO test_execution_sessions 
                (session_id, test_type, test_category, environment, triggered_by, status)
                VALUES ($1, $2, $3, $4, $5, $6)
            ''', session_id, test_type, test_category, "production", "test_engine", "running")
            await conn.close()
        except Exception as e:
            logger.warning(f"Could not create test session in database: {e}")
        
        return session_id
    
    async def _update_test_session(self, session_id: str, status: str, total_tests: int, 
                                 passed_tests: int, failed_tests: int, error_message: str = None):
        """Update test session with results"""
        if not self.database_url:
            return
            
        try:
            conn = await asyncpg.connect(self.database_url)
            await conn.execute('''
                UPDATE test_execution_sessions SET
                    status = $2,
                    completed_at = NOW(),
                    total_tests = $3,
                    passed_tests = $4,
                    failed_tests = $5,
                    error_message = $6
                WHERE session_id = $1
            ''', session_id, status, total_tests, passed_tests, failed_tests, error_message)
            await conn.close()
        except Exception as e:
            logger.warning(f"Could not update test session: {e}")
    
    async def _store_test_result(self, session_id: str, test_case: Dict[str, Any], result: Dict[str, Any]):
        """Store individual test result"""
        if not self.database_url:
            return
            
        try:
            conn = await asyncpg.connect(self.database_url)
            await conn.execute('''
                INSERT INTO test_case_results 
                (session_id, test_name, test_category, status, execution_time_ms, error_message, output_data)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
            ''', 
                session_id,
                test_case.get('test_name'),
                test_case.get('test_category', 'unknown'),
                result.get('status'),
                result.get('execution_time_ms', 0),
                result.get('error'),
                json.dumps(result)
            )
            await conn.close()
        except Exception as e:
            logger.warning(f"Could not store test result: {e}")
    
    async def _get_test_cases(self, suite_name: str) -> List[Dict[str, Any]]:
        """Get test cases for a specific suite from database or generate them"""
        if not self.database_url:
            return []
            
        try:
            conn = await asyncpg.connect(self.database_url)
            
            # Get test cases from database (generated by TestSuiteGenerator)
            results = await conn.fetch('''
                SELECT tcr.test_name, tcr.test_category, tcr.test_data, tcr.output_data
                FROM test_case_results tcr
                JOIN test_execution_sessions tes ON tcr.session_id = tes.session_id
                WHERE tes.test_type = $1 AND tcr.status = 'generated'
                ORDER BY tcr.created_at DESC
            ''', suite_name)
            
            await conn.close()
            
            test_cases = []
            for row in results:
                try:
                    # Use test_data first, fall back to output_data
                    test_data = json.loads(row['test_data']) if row['test_data'] else {}
                    if not test_data and row['output_data']:
                        test_data = json.loads(row['output_data'])
                    
                    test_cases.append({
                        'test_name': row['test_name'],
                        'test_category': row['test_category'],
                        **test_data
                    })
                except Exception as e:
                    logger.warning(f"Could not parse test case data: {e}")
            
            # If no test cases found, generate them using TestSuiteGenerator
            if not test_cases:
                logger.info(f"No test cases found for {suite_name}, generating...")
                test_cases = await self._generate_test_cases(suite_name)
            
            return test_cases
            
        except Exception as e:
            logger.warning(f"Could not get test cases from database: {e}")
            # Fallback to generation
            return await self._generate_test_cases(suite_name)
    
    async def _get_available_test_suites(self) -> List[Dict[str, Any]]:
        """Get all available test suites"""
        if not self.database_url:
            return []
            
        try:
            conn = await asyncpg.connect(self.database_url)
            
            # Get test suites from database (generated by TestSuiteGenerator)
            results = await conn.fetch('''
                SELECT DISTINCT test_type, test_category
                FROM test_execution_sessions
                WHERE triggered_by = 'test_suite_generator'
                ORDER BY test_type
            ''')
            
            await conn.close()
            
            # If no test suites found, generate them using TestSuiteGenerator
            if not results:
                logger.info("No test suites found in database, generating...")
                test_suites = await self._initialize_test_suites()
                return test_suites
            
            return [dict(row) for row in results]
            
        except Exception as e:
            logger.warning(f"Could not get test suites from database: {e}")
            # Fallback to generation
            return await self._initialize_test_suites()
    
    async def _initialize_test_suites(self) -> List[Dict[str, Any]]:
        """Initialize test suites using TestSuiteGenerator"""
        try:
            from test_suite_generator import TestSuiteGenerator
            
            logger.info("Initializing test suites using TestSuiteGenerator...")
            generator = TestSuiteGenerator()
            
            # Generate all test suites
            test_suites = await generator.generate_all_test_suites()
            
            # Store test suites in database
            await generator.store_test_suites(test_suites)
            
            # Convert to the format expected by TestExecutionEngine
            suite_list = []
            for suite_name, suite_data in test_suites.items():
                if isinstance(suite_data, dict) and 'test_category' in suite_data:
                    suite_list.append({
                        'test_type': suite_name,
                        'test_category': suite_data['test_category']
                    })
            
            logger.info(f"Initialized {len(suite_list)} test suites")
            return suite_list
            
        except ImportError as import_error:
            logger.error(f"Failed to import TestSuiteGenerator: {import_error}")
            logger.error("TestSuiteGenerator module is not available - test suite initialization failed")
            return []
        except Exception as e:
            logger.error(f"Failed to initialize test suites: {e}")
            return []
    
    async def _generate_test_cases(self, suite_name: str) -> List[Dict[str, Any]]:
        """Generate test cases for a specific suite using TestSuiteGenerator"""
        try:
            from test_suite_generator import TestSuiteGenerator
            
            generator = TestSuiteGenerator()
            
            # Generate the specific test suite
            if suite_name == "authentication_tests":
                suite_data = await generator.generate_security_tests()
            elif suite_name == "database_tests":
                suite_data = await generator.generate_database_tests()
            elif suite_name == "api_endpoints_tests":
                suite_data = await generator.generate_api_tests()
            elif suite_name == "monitoring_tests":
                suite_data = await generator.generate_analytics_monitoring_tests()
            elif suite_name == "spiritual_services_tests":
                suite_data = await generator.generate_spiritual_services_tests()
            elif suite_name == "self_healing_tests":
                suite_data = await generator.generate_auto_healing_tests()
            else:
                # Generate integration tests as fallback
                suite_data = await generator.generate_integration_tests()
            
            # Extract test cases from suite data
            if isinstance(suite_data, dict) and 'test_cases' in suite_data:
                return suite_data['test_cases']
            else:
                logger.warning(f"No test cases found in generated suite: {suite_name}")
                return []
                
        except Exception as e:
            logger.error(f"Failed to generate test cases for {suite_name}: {e}")
            return []
    
    def _calculate_overall_status(self, passed: int, failed: int, total: int) -> str:
        """Calculate overall test status"""
        if total == 0:
            return "error"
        elif failed == 0:
            return "passed"
        elif passed == 0:
            return "failed"
        else:
            return "partial"

# CLI interface
async def main():
    """Main CLI interface for test execution"""
    import sys
    
    engine = TestExecutionEngine()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "quick":
            result = await engine.execute_quick_health_check()
            print(json.dumps(result, indent=2))
        elif command == "all":
            result = await engine.execute_all_test_suites()
            print(json.dumps(result, indent=2))
        elif command.startswith("suite:"):
            suite_name = command.replace("suite:", "")
            result = await engine.execute_test_suite(suite_name)
            print(json.dumps(result, indent=2))
        else:
            print("Usage: python test_execution_engine.py [quick|all|suite:<name>]")
    else:
        # Default: run quick health check
        result = await engine.execute_quick_health_check()
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    asyncio.run(main())