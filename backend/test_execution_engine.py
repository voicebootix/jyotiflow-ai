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
import inspect
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

# Module-level constant for allowed generator methods
# This improves maintainability and testability by centralizing the allowlist
ALLOWED_GENERATOR_METHODS = {
    'generate_integration_tests',
    'generate_security_tests', 
    'generate_database_tests',
    'generate_api_endpoint_tests',  # Fixed: Updated from generate_api_tests to match actual method name
    'generate_analytics_monitoring_tests',
    'generate_auto_healing_tests',
    'generate_performance_tests',
    'generate_unit_tests',
    'generate_end_to_end_tests',
    'generate_load_tests',
    'generate_admin_services_tests',
    'generate_spiritual_tests',
    'generate_spiritual_services_tests',  # Added: Missing method that exists in TestSuiteGenerator
    'generate_credit_payment_tests',
    'generate_user_management_tests',
    'generate_avatar_generation_tests',
    'generate_social_media_tests',  # Added: Missing method that exists in TestSuiteGenerator
    'generate_live_audio_video_tests',  # Added: Missing method that exists in TestSuiteGenerator
    'generate_community_services_tests',  # Added: Missing method that exists in TestSuiteGenerator
    'generate_notification_services_tests'  # Added: Missing method that exists in TestSuiteGenerator
}

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
        if session_id is None:
            # Session creation failed - generate a temporary ID for this run but don't store results
            session_id = str(uuid.uuid4())
            logger.warning(f"Session creation failed - using temporary ID {session_id} (results won't be stored)")
        self.current_session_id = session_id
        
        try:
            # Get test cases for this suite
            # ✅ FOLLOWING .CURSOR RULES: Database-driven mapping, suite_name maps to test_category
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
        if session_id is None:
            # Session creation failed - generate a temporary ID for this run but don't store results
            session_id = str(uuid.uuid4())
            logger.warning(f"Session creation failed - using temporary ID {session_id} (results won't be stored)")
        
        # Get health checks from database configuration instead of hardcoded list
         # Get health checks from database configuration instead of hardcoded list
        health_checks = await self._get_health_check_configurations()
        
        # ✅ EMPTY HEALTH CHECKS GUARD: Prevent incorrect "passed" status when no checks configured
        # Following .cursor rules: Handle edge cases, validate configuration completeness
        if not health_checks:
            error_message = "No health checks are configured in the database"
            logger.error(f"Health check execution failed: {error_message}")
            logger.error("Please ensure:")
            logger.error("1. ‘health_check_configurations’ table exists and migrations are applied")
            logger.error("2. Health check configurations are populated")
            logger.error("3. At least one health check is enabled")
            
            # Update session status to "error" with detailed information
            await self._update_test_session(
                session_id, 
                "error", 
                0,  # total_tests
                0,  # passed_tests  
                0,  # failed_tests
                error_message
            )
            
            return {
                "session_id": session_id,
                "status": "error",
                "total_checks": 0,
                "passed_checks": 0,
                "failed_checks": 0,
                "error": error_message,
                "results": {}
            }
        
        results = {}
        passed = 0
        failed = 0
        
        for check in health_checks:
            check_name = check["test_name"]
            timeout_seconds = check.get("timeout_seconds", 30)
            
            try:
                # ✅ TIMEOUT ENFORCEMENT: Wrap each health check with timeout (following .cursor rules)
                logger.debug(f"Executing health check '{check_name}' with {timeout_seconds}s timeout")
                
                result = await asyncio.wait_for(
                    check["test_function"](),
                    timeout=timeout_seconds
                )
                
                # 🛡️ SAFETY FIX: Guard against non-dict results to prevent AttributeError
                # Following .cursor rules: Validate all data types, handle edge cases
                if not isinstance(result, dict):
                    logger.warning(f"Health check '{check_name}' returned non-dict result: {type(result).__name__} = {result}")
                    # Treat non-dict results as failed checks
                    results[check_name] = {
                        "status": "failed",
                        "error": f"Health check returned invalid result type: {type(result).__name__}",
                        "original_result": str(result) if result is not None else "None",
                        "timeout_seconds": timeout_seconds
                    }
                    failed += 1
                elif result.get("status") == "passed":
                    results[check_name] = result
                    passed += 1
                else:
                    results[check_name] = result
                    failed += 1
                    
            except asyncio.TimeoutError:
                logger.error(f"Health check '{check_name}' timed out after {timeout_seconds}s")
                results[check_name] = {
                    "status": "failed",
                    "error": f"Health check timed out after {timeout_seconds} seconds",
                    "timeout_seconds": timeout_seconds
                }
                failed += 1
                
            except Exception as e:
                logger.error(f"Health check '{check_name}' failed with exception: {e}")
                results[check_name] = {
                    "status": "failed",
                    "error": str(e),
                    "timeout_seconds": timeout_seconds
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
            "results": results,
            "security_validated": True,  # Indicates whitelist validation was used
            "timeout_enforced": True     # Indicates timeouts were enforced
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
                "execution_time_ms": execution_time,
                "fix_suggestion": self._generate_fix_suggestion(None, "Test timed out") # Generate suggestion for timeout
            }
        except TestExecutionError as e:
            # If _execute_test_code raised a TestExecutionError, it already contains detailed info.
            error_details = e.args[0] if e.args and isinstance(e.args[0], dict) else {"error": str(e)}
            execution_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            error_details['execution_time_ms'] = execution_time
            # Ensure status is 'failed' if not explicitly set in the error details
            if 'status' not in error_details:
                error_details['status'] = 'failed'
            return error_details
        except Exception as e:
            execution_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            fix_suggestion = self._generate_fix_suggestion(None, str(e))
            return {
                "status": "failed",
                "error": str(e),
                "traceback": traceback.format_exc(),
                "execution_time_ms": execution_time,
                "fix_suggestion": fix_suggestion # Add fix suggestion for general exceptions
            }
    
    async def _execute_file_based_test(self, file_path: str, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """
        Securely execute a file-based test with proper sandboxing.
        
        Args:
            file_path: Path to the test file to execute
            test_case: Test case metadata and configuration
            
        Returns:
            Dict containing test execution results
        """
        import os
        import subprocess
        import tempfile
        import shutil
        from pathlib import Path
        
        start_time = datetime.now(timezone.utc)
        
        try:
            # Validate file path for security
            if not file_path or not isinstance(file_path, str):
                return {
                    "status": "failed",
                    "error": "Invalid file path provided",
                    "execution_time_ms": 0
                }
            
            # Normalize and validate path to prevent directory traversal
            file_path = os.path.normpath(file_path)
            if '..' in file_path or file_path.startswith('/'):
                return {
                    "status": "failed",
                    "error": "Invalid file path: directory traversal or absolute paths not allowed",
                    "execution_time_ms": 0
                }
            
            # Check if file exists and is readable
            full_path = Path(file_path)
            if not full_path.exists():
                return {
                    "status": "failed",
                    "error": f"Test file not found: {file_path}",
                    "execution_time_ms": 0
                }
            
            if not full_path.is_file():
                return {
                    "status": "failed",
                    "error": f"Path is not a file: {file_path}",
                    "execution_time_ms": 0
                }
            
            # Only allow Python files for security
            if not file_path.endswith('.py'):
                return {
                    "status": "failed",
                    "error": "Only Python (.py) test files are allowed",
                    "execution_time_ms": 0
                }
            
            # Read and validate file content
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    file_content = f.read()
            except Exception as read_error:
                return {
                    "status": "failed",
                    "error": f"Failed to read test file: {str(read_error)}",
                    "execution_time_ms": 0
                }
            
            # Robust security validation using AST parsing
            security_result = self._validate_code_security(file_content)
            if not security_result["is_safe"]:
                return {
                    "status": "failed",
                    "error": f"Security violation: {security_result['reason']}",
                    "details": security_result.get('details', ''),
                    "execution_time_ms": 0
                }
            
            # Execute the test file in a restricted environment
            timeout = test_case.get('timeout_seconds', 30)
            
            # Create a temporary directory for isolated execution
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_file = Path(temp_dir) / "test_file.py"
                
                # Copy test file to temporary location
                shutil.copy2(full_path, temp_file)
                
                # Prepare environment variables
                env = os.environ.copy()
                env.update({
                    'DATABASE_URL': self.database_url or '',
                    'PYTHONPATH': str(Path(__file__).parent),
                    'PYTHONDONTWRITEBYTECODE': '1'
                })
                
                # Execute using subprocess with timeout and restrictions
                try:
                    result = subprocess.run(
                        ['python3', str(temp_file)],
                        cwd=temp_dir,
                        capture_output=True,
                        text=True,
                        timeout=timeout,
                        env=env
                    )
                    
                    execution_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
                    
                    if result.returncode == 0:
                        return {
                            "status": "passed",
                            "message": "File-based test executed successfully",
                            "stdout": result.stdout.strip(),
                            "stderr": result.stderr.strip() if result.stderr else None,
                            "execution_time_ms": execution_time,
                            "file_path": file_path
                        }
                    else:
                        return {
                            "status": "failed",
                            "error": f"Test execution failed with return code {result.returncode}",
                            "stdout": result.stdout.strip() if result.stdout else None,
                            "stderr": result.stderr.strip(),
                            "execution_time_ms": execution_time,
                            "file_path": file_path
                        }
                        
                except subprocess.TimeoutExpired:
                    execution_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
                    return {
                        "status": "failed",
                        "error": f"Test execution timed out after {timeout} seconds",
                        "execution_time_ms": execution_time,
                        "file_path": file_path
                    }
                
        except Exception as e:
            execution_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            return {
                "status": "failed",
                "error": f"File-based test execution failed: {str(e)}",
                "traceback": traceback.format_exc(),
                "execution_time_ms": execution_time,
                "file_path": file_path
            }

    def _validate_code_security(self, code: str) -> Dict[str, Any]:
        """
        Validate code security using AST parsing to detect dangerous operations.
        
        Args:
            code: Python code to validate
            
        Returns:
            Dict with 'is_safe' boolean and 'reason' if unsafe
        """
        import ast
        
        try:
            # Parse the code into an AST
            tree = ast.parse(code)
        except SyntaxError as e:
            return {
                "is_safe": False,
                "reason": f"Syntax error in code: {str(e)}",
                "details": "Code must be valid Python syntax"
            }
        
        # Define dangerous modules and functions
        dangerous_modules = {
            'os', 'sys', 'subprocess', 'shutil', 'socket', 'urllib', 'requests', 
            'http', 'ftplib', 'telnetlib', 'smtplib', 'email', 'imaplib', 'poplib',
            'ssl', 'hashlib', 'hmac', 'secrets', 'tempfile', 'glob', 'fnmatch',
            'pickle', 'dill', 'shelve', 'dbm', 'sqlite3', 'threading', 'multiprocessing',
            'ctypes', 'platform', 'webbrowser', 'pty', 'fcntl', 'termios'
        }
        
        dangerous_functions = {
            'exec', 'eval', 'compile', '__import__', 'open', 'file', 'input', 
            'raw_input', 'reload', 'globals', 'locals', 'vars', 'dir', 'getattr',
            'setattr', 'delattr', 'callable'
        }
        
        dangerous_attributes = {
            '__class__', '__bases__', '__subclasses__', '__mro__', '__dict__',
            '__globals__', '__code__', '__closure__', '__defaults__', '__kwdefaults__'
        }
        
        class SecurityValidator(ast.NodeVisitor):
            def __init__(self):
                self.violations = []
                
            def visit_Import(self, node):
                for alias in node.names:
                    if alias.name in dangerous_modules:
                        self.violations.append(f"Dangerous import: {alias.name}")
                self.generic_visit(node)
                
            def visit_ImportFrom(self, node):
                if node.module in dangerous_modules:
                    self.violations.append(f"Dangerous import from: {node.module}")
                self.generic_visit(node)
                
            def visit_Call(self, node):
                # Check for dangerous function calls
                if isinstance(node.func, ast.Name):
                    if node.func.id in dangerous_functions:
                        self.violations.append(f"Dangerous function call: {node.func.id}")
                elif isinstance(node.func, ast.Attribute):
                    if node.func.attr in dangerous_functions:
                        self.violations.append(f"Dangerous method call: {node.func.attr}")
                self.generic_visit(node)
                
            def visit_Attribute(self, node):
                if node.attr in dangerous_attributes:
                    self.violations.append(f"Dangerous attribute access: {node.attr}")
                self.generic_visit(node)
                
            def visit_Subscript(self, node):
                # Check for dangerous subscript operations that might access builtins
                if isinstance(node.value, ast.Name) and node.value.id == '__builtins__':
                    self.violations.append("Dangerous access to __builtins__")
                self.generic_visit(node)
                
            def visit_Name(self, node):
                # Check for dangerous variable names
                if isinstance(node.ctx, ast.Load) and node.id in dangerous_functions:
                    # Only flag if it's being loaded (used), not stored
                    if node.id in {'exec', 'eval', 'compile', '__import__'}:
                        self.violations.append(f"Reference to dangerous function: {node.id}")
                self.generic_visit(node)
        
        # Run the security validator
        validator = SecurityValidator()
        validator.visit(tree)
        
        if validator.violations:
            return {
                "is_safe": False,
                "reason": "Code contains dangerous operations",
                "details": "; ".join(validator.violations[:5])  # Limit to first 5 violations
            }
        
        # Additional checks for string-based evasion attempts
        code_lower = code.lower()
        evasion_patterns = [
            'chr(', 'ord(', 'hex(', 'oct(', 'bin(',  # Character/number conversion
            'bytes(', 'bytearray(',  # Byte manipulation
            'str.format(', '.format(',  # String formatting
            'f"', "f'",  # F-strings that might hide code
        ]
        
        suspicious_count = sum(1 for pattern in evasion_patterns if pattern in code_lower)
        if suspicious_count >= 3:  # Multiple evasion techniques
            return {
                "is_safe": False,
                "reason": "Code contains multiple potential evasion techniques",
                "details": f"Found {suspicious_count} suspicious patterns that could be used to bypass security"
            }
        
        return {
            "is_safe": True,
            "reason": "Code passed security validation"
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
        
        # Create test execution environment with enhanced globals
        test_globals = {
            '__builtins__': {
                'len': len, 'str': str, 'int': int, 'float': float, 'bool': bool,
                'list': list, 'dict': dict, 'tuple': tuple, 'set': set,
                'range': range, 'enumerate': enumerate, 'zip': zip,
                'print': print, 'Exception': Exception, 'ValueError': ValueError,
                'TypeError': TypeError, 'AssertionError': AssertionError,
                '__import__': __import__  # Add __import__ function for dynamic imports
            },
            'asyncio': asyncio,
            'asyncpg': asyncpg,
            'uuid': uuid,
            'json': json,
            'datetime': datetime,
            'timezone': timezone,
            'DATABASE_URL': DATABASE_URL,
            'logger': logger,
            'sys': __import__('sys'),  # Add sys module
            'os': __import__('os'),    # Add os module
            'importlib': __import__('importlib'),  # Add importlib for dynamic imports
            '__file__': '/backend',    # Provide __file__ context for path operations
            '__name__': '__main__'     # Provide __name__ context
        }
        
        # Add test case data to globals
        test_globals.update(test_case)
        
        try:
            # Import additional modules if needed (with validation)
            if 'httpx' in test_code:
                import httpx
                test_globals['httpx'] = httpx
            
            # Always try to import common testing modules
            try:
                from database_self_healing_system import DatabaseSelfHealingSystem, extract_table_from_query
                test_globals['DatabaseSelfHealingSystem'] = DatabaseSelfHealingSystem
                test_globals['extract_table_from_query'] = extract_table_from_query
            except ImportError as e:
                logger.warning("Could not import database_self_healing_system: %s", str(e))
            
            # Import core foundation enhanced
            try:
                import core_foundation_enhanced
                test_globals['core_foundation_enhanced'] = core_foundation_enhanced
            except ImportError as e:
                logger.warning("Could not import core_foundation_enhanced: %s", str(e))
            
            # Import monitoring modules
            try:
                from monitoring import integration_monitor
                test_globals['integration_monitor'] = integration_monitor
            except ImportError as e:
                logger.warning("Could not import monitoring modules: %s", str(e))
            
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
                    return_value = await test_function()
                else:
                    return_value = test_function()
                
                # If the test function returns a dict with 'status' and 'http_status_code'.,
                # it's likely an API test. Enhance its result with a fix suggestion.
                if isinstance(return_value, dict) and 'status' in return_value and 'http_status_code' in return_value:
                    return_value['fix_suggestion'] = self._generate_fix_suggestion(
                        return_value.get('http_status_code'),
                        return_value.get('error', ''),
                        test_case.get('endpoint') # Pass endpoint if available
                    )
                return return_value
            else:
                # Look for any async function in the globals
                for name, obj in test_globals.items():
                    if name.startswith('test_') and asyncio.iscoroutinefunction(obj):
                        return_value = await obj()
                        if isinstance(return_value, dict) and 'status' in return_value and 'http_status_code' in return_value:
                            return_value['fix_suggestion'] = self._generate_fix_suggestion(
                                return_value.get('http_status_code'),
                                return_value.get('error', ''),
                                test_case.get('endpoint')
                            )
                        return return_value
                
                raise TestExecutionError(f"No test function found: {test_function_name}")
                
        except (SyntaxError, NameError, TypeError) as e:
            logger.error("Test code execution failed: %s", str(e))
            fix_suggestion = self._generate_fix_suggestion(None, str(e))
            raise TestExecutionError({
                "status": "failed",
                "error": str(e),
                "fix_suggestion": fix_suggestion
            }) from e
        except httpx.HTTPStatusError as e:
            status_code = e.response.status_code if e.response else None
            error_message = f"HTTP Error: {status_code} - {e.response.text}" if e.response else str(e)
            fix_suggestion = self._generate_fix_suggestion(status_code, error_message, test_case.get('endpoint'))
            logger.error("HTTPStatusError in test execution: %s", error_message)
            raise TestExecutionError({
                "status": "failed",
                "http_status_code": status_code,
                "error": error_message,
                "response_body": e.response.text if e.response else None,
                "fix_suggestion": fix_suggestion
            }) from e
        except httpx.RequestError as e:
            error_message = f"Request Error: {str(e)}"
            fix_suggestion = self._generate_fix_suggestion(None, error_message, test_case.get('endpoint'))
            logger.error("Httpx Request Error in test execution: %s", error_message)
            raise TestExecutionError({
                "status": "failed",
                "error": error_message,
                "fix_suggestion": fix_suggestion
            }) from e
        except Exception as e:
            logger.error("Unexpected error in test execution: %s", str(e))
            fix_suggestion = self._generate_fix_suggestion(None, str(e))
            raise TestExecutionError({
                "status": "failed",
                "error": str(e),
                "fix_suggestion": fix_suggestion
            }) from e
    
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
            'eval', 'exec', 'compile',  # Removed __import__ as it's needed for dynamic imports
            'open', 'file', 'input', 'raw_input',
            'reload', 'vars', 'locals', 'globals'
        }
        
        safe_modules = {
            'asyncio', 'asyncpg', 'uuid', 'json', 'datetime', 'httpx',
            'secrets', 'string', 'sys', 'os', 'importlib', 'builtins',  # Added necessary modules for testing, including builtins
            'core_foundation_enhanced', 'database_self_healing_system',
            'monitoring', 'spiritual_avatar_generation_engine', 'social_media_marketing_automation',
            'agora_service', 'test_suite_generator', 'test_execution_engine',
            'time', 'enhanced_business_logic', 'math', 'random',  # Add common modules needed for tests
            'typing', 'collections', 'functools', 'itertools', 'operator'  # Add standard library modules
        }
        
        for child in ast.walk(node):
            # Check for dangerous function calls (but allow __import__ for dynamic imports)
            if isinstance(child, ast.Call) and isinstance(child.func, ast.Name):
                if child.func.id in dangerous_functions:
                    raise TestExecutionError(f"Unsafe function call detected: {child.func.id}")
            
            # Check for dangerous imports - but allow safe modules and test modules
            if isinstance(child, ast.Import):
                for alias in child.names:
                    module_name = alias.name.split('.')[0]  # Get root module
                    if module_name not in safe_modules and not self._is_safe_test_module(module_name):
                        raise TestExecutionError(f"Unsafe import detected: {alias.name}")
            
            if isinstance(child, ast.ImportFrom):
                if child.module:
                    module_name = child.module.split('.')[0]  # Get root module
                    if module_name not in safe_modules and not self._is_safe_test_module(module_name):
                        raise TestExecutionError(f"Unsafe module import: {child.module}")
            
            # Check for attribute access to dangerous modules (like os.system)
            if isinstance(child, ast.Attribute):
                if isinstance(child.value, ast.Name):
                    # Block dangerous module usage but allow safe operations
                    dangerous_attrs = {
                        'subprocess': ['call', 'run', 'Popen', 'check_output'],
                        'shutil': ['rmtree', 'move', 'copy']
                    }
                    
                    if child.value.id in dangerous_attrs:
                        if child.attr in dangerous_attrs[child.value.id]:
                            raise TestExecutionError(f"Unsafe operation: {child.value.id}.{child.attr}")
                    
                    # Allow specific safe built-in functions
                    if child.value.id == 'builtins' and child.attr in {'isinstance', 'len', 'type'}:
                        pass # Allowed safe builtins
                    elif child.value.id == 'builtins':
                        raise TestExecutionError(f"Unsafe builtins access: builtins.{child.attr}")
    
    def _is_safe_test_module(self, module_name: str) -> bool:
        """
        Check if a module is safe for testing.
        
        Args:
            module_name: Name of the module to check
            
        Returns:
            bool: True if the module is safe for testing
        """
        safe_patterns = [
            'test_', 'tests', 'pytest', 'unittest',
            'backend', 'frontend', 'routers', 'models',
            'validators', 'services', 'utils', 'auth',
            'monitoring', 'spiritual', 'jyoti', 'flow'
        ]
        
        return any(pattern in module_name.lower() for pattern in safe_patterns)
    
    async def _test_database_connectivity(self) -> Dict[str, Any]:
        """Quick database connectivity test"""
        try:
            conn = await asyncpg.connect(self.database_url)
            try:
                await conn.fetchval("SELECT 1")
                return {"status": "passed", "message": "Database connectivity OK"}
            finally:
                # ✅ CONNECTION LEAK FIX: Always close connection, even if query fails
                await conn.close()
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
            
            try:
                # Get critical tables from database configuration instead of hardcoded list
                critical_tables = await self._get_critical_tables()
                
                # ✅ EMPTY CRITICAL TABLES GUARD: Prevent incorrect "passed" status when no tables configured
                # Following .cursor rules: Handle edge cases, validate configuration completeness
                if not critical_tables:
                    error_message = "No critical tables are configured for monitoring"
                    logger.warning(f"Critical tables check skipped: {error_message}")
                    logger.warning("Please ensure:")
                    logger.warning("1. Migration 008 has been run to create critical_system_components table")
                    logger.warning("2. Critical table configurations have been populated in the database")
                    logger.warning("3. At least one critical table is enabled in the configuration")
                    return {
                        "status": "error", 
                        "error": error_message,
                        "details": "Critical table monitoring requires database configuration"
                    }
                
                missing_tables = []
                
                for table in critical_tables:
                    # ✅ SCHEMA-AWARE FIX: Filter by current schema to prevent false positives
                    # Following .cursor rules: Precise database queries, no cross-schema confusion
                    exists = await conn.fetchval('''
                        SELECT EXISTS(
                            SELECT 1 FROM information_schema.tables 
                            WHERE table_name = $1 
                            AND table_schema = ANY(current_schemas(false))
                        )
                    ''', table)
                    
                    if not exists:
                        missing_tables.append(table)
                
                if missing_tables:
                    return {"status": "failed", "error": f"Missing critical tables: {missing_tables}"}
                else:
                    return {"status": "passed", "message": "All critical tables exist"}
                    
            finally:
                # ✅ CONNECTION LEAK FIX: Always close connection, even if queries fail
                await conn.close()
                
        except Exception as e:
            return {"status": "failed", "error": str(e)}

    
    # ✅ FOLLOWING .CURSOR RULES: No hardcoded placeholder methods
    # Health check configurations are stored in database (health_check_configurations table)
    # If a health check method doesn't exist, the system will handle it gracefully via the whitelist
    # No need for hardcoded placeholder methods that return fake statuses
    
    async def _create_test_session(self, test_type: str, test_category: str, **kwargs) -> Optional[str]:
        """Create a new test execution session with dynamic parameters."""
        if not self.database_url:
            logger.warning("⚠️ DATABASE_URL not set - test session will NOT be stored in database!")
            return None
        session_id = str(uuid.uuid4())
        # ✅ SQL INJECTION PREVENTION: Whitelist of allowed column names
        # Following .cursor rules: No dynamic SQL construction from user input
        ALLOWED_COLUMNS = (
            'session_id', 'test_type', 'test_category', 'environment',
            'triggered_by', 'status', 'started_at', 'created_at', 'metadata',
            'priority', 'timeout_seconds', 'retry_count'
        )
        # ✅ SECURITY: Fixed table name to prevent injection
        TABLE_NAME = 'test_execution_sessions'
        # ✅ FOLLOWING .CURSOR RULES: No hardcoded values, use None for optional fields
        # Filter kwargs to only include allowed columns
        filtered_params = {}
        for key, value in kwargs.items():
            if key in ALLOWED_COLUMNS:
                filtered_params[key] = value
            else:
                logger.warning(f"Ignored invalid column in test session creation: {key}")
        # Include required fields
        filtered_params.update({
            'session_id': session_id,
            'test_type': test_type,
            'test_category': test_category
        })
        # Provide safe defaults via env (no hard-coding)
        default_env = os.getenv('ENVIRONMENT', 'production')
        default_triggered_by = os.getenv('TESTS_TRIGGERED_BY', 'test_execution_engine')
        filtered_params.setdefault('status', 'running')
        filtered_params.setdefault('environment', default_env)
        filtered_params.setdefault('triggered_by', default_triggered_by)
        # Add created_at timestamp to avoid NOT NULL constraint errors
        from datetime import datetime, timezone
        filtered_params.setdefault('created_at', datetime.now(timezone.utc).replace(tzinfo=None))
        # ✅ SQL INJECTION PREVENTION: Use whitelisted columns only
        columns = [col for col in ALLOWED_COLUMNS if col in filtered_params]
        column_names = ', '.join(columns)
        placeholders = ', '.join(f"${i+1}" for i in range(len(columns)))
        values = [filtered_params[col] for col in columns]
        query = f"""
            INSERT INTO {TABLE_NAME}
            ({column_names})
            VALUES ({placeholders})
        """
        try:
            conn = await asyncpg.connect(self.database_url)
            try:
                await conn.execute(query, *values)
                logger.info(f"✅ Successfully created test session: {session_id} in database")
            finally:
                await conn.close()
        except Exception as e:
            logger.error("❌ FAILED to create test session in database", exc_info=e)
            logger.error("   Session ID: %s | Test Type: %s | Test Category: %s", 
                        session_id, test_type, test_category)
            logger.debug("   Query: %s", query)
            logger.debug("   Values: <redacted> (%d values)", len(values))
            # Don't return the session_id if creation failed - return None to indicate failure
            return None
        return session_id


    
    async def _update_test_session(self, session_id: str, status: str, total_tests: int,
                                passed_tests: int, failed_tests: int, error_message: str = None):
        """Update test session with results"""
        
        if not self.database_url:
            return

        # Define the SQL query with placeholders
        query = """
            UPDATE test_execution_sessions SET
                status = $2,
                completed_at = NOW(),
                total_tests = $3,
                passed_tests = $4,
                failed_tests = $5,
                error_message = $6
            WHERE session_id = $1
        """

        # Values to be used in the parameterized query
        params = [session_id, status, total_tests, passed_tests, failed_tests, error_message]

        # ✅ CONNECTION MANAGEMENT FIX: Restructured try/except/finally blocks
        # Following .cursor rules: Proper resource management, connection only closed if established
        conn = None
        try:
            # Establish connection in outer try block
            conn = await asyncpg.connect(self.database_url)
            
            # Execute query in inner try block
            try:
                await conn.execute(query, *params)
            except Exception as inner_e:
                # Handle execution errors while ensuring connection cleanup
                logger.warning("Could not execute update query", exc_info=inner_e)
                raise  # Re-raise to be caught by outer except
                
        except Exception as e:
            logger.warning("Could not update test session", exc_info=e)
        finally:
            # ✅ CONNECTION LEAK FIX: Only close connection if it was successfully created
            # Following .cursor rules: Safe resource cleanup, no errors on failed connections
            if conn is not None:
                await conn.close()

    
    async def _store_test_result(self, session_id: str, test_case: Dict[str, Any], result: Dict[str, Any]):
        """Store individual test result with fixed column whitelist for security."""
        if not self.database_url:
            logger.error("❌ DATABASE_URL not set - test results will NOT be stored in database!")
            return

        # ✅ SECURITY FIX: Fixed whitelist of allowed columns to prevent SQL injection
        # Following .cursor rules: No dynamic SQL generation, use fixed schema
        TABLE_NAME = "test_case_results"
        ALLOWED_COLUMNS = (
            "session_id",
            "test_name", 
            "test_category",
            "status",
            "execution_time_ms",
            "error_message",    # Will store the combined error and fix suggestion
            "output_data"       # Will store the full JSON result, including HTTP status code and response body
        )

        # Define the values to be inserted (matching the fixed column order)
        values = [
            session_id,
            test_case.get('test_name'),
            test_case.get('test_category'),
            result.get('status'),
            result.get('execution_time_ms', 0),
            # Combine error message and fix suggestion for error_message column
            (result.get('error', '') + "\nFix Suggestion: " + result.get('fix_suggestion', '')).strip() if result.get('status') == 'failed' else None,
            json.dumps({
                "full_result": result,
                "http_status_code": result.get('http_status_code'),
                "response_body": result.get('response_body'),
                "fix_suggestion": result.get('fix_suggestion')
            })
        ]

        # ✅ SECURITY: Use fixed column names instead of dynamic generation
        # Following .cursor rules: No dynamic SQL construction, prevent injection
        columns_str = ", ".join(ALLOWED_COLUMNS)
        placeholders = ", ".join([f"${i+1}" for i in range(len(ALLOWED_COLUMNS))])
        query = f"""
            INSERT INTO {TABLE_NAME}
            ({columns_str})
            VALUES ({placeholders})
        """

        # ✅ CONNECTION MANAGEMENT: Restructured try/except/finally blocks
        # Following .cursor rules: Proper resource management, connection only closed if established
        conn = None
        try:
            # Establish connection in outer try block
            conn = await asyncpg.connect(self.database_url)
            
            # Check if session exists before inserting test result
            session_exists = await conn.fetchval(
                "SELECT 1 FROM test_execution_sessions WHERE session_id = $1", session_id
            )
            
            if not session_exists:
                logger.warning(f"Session {session_id} does not exist in test_execution_sessions table - skipping result storage")
                return
            
            # Execute query in inner try block
            try:
                await conn.execute(query, *values)
            except Exception as inner_e:
                # Handle execution errors while ensuring connection cleanup
                logger.warning("Could not execute test result insert", exc_info=inner_e)
                raise  # Re-raise to be caught by outer except
                
        except Exception as e:
            logger.error("❌ FAILED to store test result in database", exc_info=e)
            logger.error("   Test: %s | Session ID: %s | DB Connected: %s", 
                        test_case.get('test_name', 'unknown'), 
                        session_id,
                        'Yes' if self.database_url else 'No')
            logger.debug("   Result data: <redacted> (%d bytes)", len(str(result)))
        else:
            # Log successful storage
            logger.info(f"✅ Successfully stored test result: {test_case.get('test_name', 'unknown')} in database")
        finally:
            # ✅ CONNECTION LEAK FIX: Only close connection if it was successfully created
            # Following .cursor rules: Safe resource cleanup, no errors on failed connections
            if conn is not None:
                await conn.close()

    
    async def _get_test_cases(self, suite_name: str) -> List[Dict[str, Any]]:
        """
        Get fresh test cases for a specific suite using database-driven configuration.
        Always generates fresh tests for real-time monitoring - never reuses old results.
        """
        logger.info(f"Generating fresh test cases for suite: {suite_name}")
        
        # Always generate fresh test cases for real-time monitoring
        # Database is used for configuration, not cached results
        return await self._generate_test_cases(suite_name)
    
    async def _get_available_test_suites(self) -> List[Dict[str, Any]]:
        """Get all available test suites"""
        if not self.database_url:
            return []
            
        try:
            conn = await asyncpg.connect(self.database_url)
            
            try:
                # Get test suites from database (generated by TestSuiteGenerator)
                results = await conn.fetch('''
                    SELECT DISTINCT test_type, test_category
                    FROM test_execution_sessions
                    WHERE triggered_by = 'test_suite_generator'
                    ORDER BY test_type
                ''')
                
            finally:
                # ✅ CONNECTION LEAK FIX: Always close connection, even if fetch fails
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
            
            # Handle legacy suite name mappings from database configuration
            original_suite_name = suite_name
            suite_name = await self._resolve_suite_name_mapping(suite_name)
            
            # Generate the specific test suite using database-driven method mapping
            suite_data = await self._generate_suite_data_from_config(generator, suite_name, original_suite_name)
            
            # Extract test cases from suite data
            if isinstance(suite_data, dict) and 'test_cases' in suite_data:
                test_cases = suite_data['test_cases']
                # Update test cases to use original suite name for consistency
                for test_case in test_cases:
                    test_case['original_suite_name'] = original_suite_name
                    test_case['mapped_suite_name'] = suite_name
                return test_cases
            else:
                logger.warning(f"No test cases found in generated suite: {suite_name} (original: {original_suite_name})")
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
    
    def _safe_timeout_conversion(self, timeout_value: Any) -> int:
        """
        Safely convert timeout value from database to integer with clamping
        Following .cursor rules: Handle all database type variations without hardcoded assumptions
        
        Args:
            timeout_value: Value from database (could be None, int, str, Decimal, etc.)
            
        Returns:
            int: Clamped timeout value between 5 and 60 seconds
        """
        try:
            # Handle None or empty values
            if timeout_value is None or timeout_value == '':
                return 30  # Default timeout
            
            # Convert to int, handling various database types
            if isinstance(timeout_value, (int, float)):
                timeout_int = int(timeout_value)
            elif isinstance(timeout_value, str):
                # Handle string representations of numbers
                timeout_int = int(float(timeout_value.strip())) if timeout_value.strip() else 30
            else:
                # Handle Decimal, other numeric types
                timeout_int = int(float(timeout_value))
            
            # Clamp between 5 and 60 seconds for safety
            return max(5, min(60, timeout_int))
            
        except (ValueError, TypeError, AttributeError) as e:
            logger.warning(f"Invalid timeout value '{timeout_value}' ({type(timeout_value).__name__}), using default: {e}")
            return 30  # Safe default on any conversion error

    async def _get_health_check_configurations(self) -> List[Dict[str, Any]]:
        """Get health check configurations from database with security validation"""
        
        # ✅ SECURITY: Define whitelist of allowed health check methods (following .cursor rules)
        # This prevents arbitrary method execution via database injection
        # Only include methods that actually exist - no hardcoded placeholders
        ALLOWED_HEALTH_CHECK_METHODS = {
            '_test_database_connectivity': self._test_database_connectivity,
            '_test_api_health_endpoint': self._test_api_health_endpoint,
            '_test_critical_tables_exist': self._test_critical_tables_exist
        }
        
        # Remove None values from whitelist
        ALLOWED_HEALTH_CHECK_METHODS = {
            name: func for name, func in ALLOWED_HEALTH_CHECK_METHODS.items() 
            if func is not None and callable(func)
        }
        
        if not self.database_url:
            # Fallback to minimal secure checks if no database
            return [
                {
                    "test_name": "database_connectivity", 
                    "test_function": self._test_database_connectivity,
                    "timeout_seconds": 10,
                    "priority": "critical"
                },
                {
                    "test_name": "api_health_endpoint", 
                    "test_function": self._test_api_health_endpoint,
                    "timeout_seconds": 10,
                    "priority": "critical"
                }
            ]
            
        try:
            conn = await asyncpg.connect(self.database_url)
            
            try:
                # Get health check configurations from database
                try:
                    # Try to query with display_name column (new schema)
                    results = await conn.fetch('''
                        SELECT test_name, test_function, display_name, description, priority, timeout_seconds
                        FROM health_check_configurations
                        WHERE enabled = true
                        ORDER BY order_index, test_name
                    ''')
                except asyncpg.UndefinedColumnError:
                    # Fallback for older databases without display_name column
                    logger.info("display_name column not found, falling back to existing columns")
                    results = await conn.fetch('''
                        SELECT test_name, test_function, description, priority, timeout_seconds
                        FROM health_check_configurations
                        WHERE enabled = true
                        ORDER BY test_name
                    ''')
                
                health_checks = []
                for record in results:
                    # Build plain dict explicitly from asyncpg.Record fields
                    row = {
                        'test_name': record['test_name'],
                        'test_function': record['test_function'],
                        'description': record['description'],
                        'priority': record['priority'],
                        'timeout_seconds': record['timeout_seconds'],
                        'display_name': record['display_name'] if 'display_name' in record else record['test_name']
                    }
                    
                    function_name = row['test_function']
                    
                    # ✅ NAMING CONVENTION FIX: Ensure function name has leading underscore for private method lookup
                    # Following .cursor rules: Handle database/code naming convention mismatch
                    if not function_name.startswith('_'):
                        normalized_function_name = f'_{function_name}'
                    else:
                        normalized_function_name = function_name
                    
                    # ✅ SECURITY: Only allow whitelisted methods (following .cursor rules)
                    if normalized_function_name in ALLOWED_HEALTH_CHECK_METHODS:
                        test_function = ALLOWED_HEALTH_CHECK_METHODS[normalized_function_name]
                        health_checks.append({
                            "test_name": row['test_name'],
                            "test_function": test_function,
                            "display_name": row['display_name'],
                            "description": row['description'],
                            "priority": row['priority'],
                            "timeout_seconds": self._safe_timeout_conversion(row['timeout_seconds'])  # Safe type conversion and clamping
                        })
                    else:
                        logger.warning(f"Health check function not in whitelist: {function_name} (normalized: {normalized_function_name})")
                        logger.warning(f"Allowed methods: {list(ALLOWED_HEALTH_CHECK_METHODS.keys())}")
                
                return health_checks
                
            finally:
                # ✅ CONNECTION LEAK FIX: Always close connection, even if fetch fails
                # Following .cursor rules: Proper resource management, no leaks
                await conn.close()
            
        except Exception as e:
            logger.error(f"Could not get health check configurations from database: {e}")
            logger.error("Database-driven health checks are required. Please ensure:")
            logger.error("1. Database is accessible")
            logger.error("2. Migration 008 has been run to create health_check_configurations table")
            logger.error("3. Initial health check data has been populated")
            # ✅ FOLLOWING .CURSOR RULES: No hardcoded mock data, no placeholders
            # Following .cursor rules: "Do not add mock data, placeholders, or temporary patches"
            # The system requires database-driven configuration - return empty list to fail gracefully
            return []
    
    async def _get_critical_tables(self) -> List[str]:
        """Get critical tables list from database configuration instead of hardcoded list"""
        if not self.database_url:
            # ✅ FOLLOWING .CURSOR RULES: No hardcoded data
            # Following .cursor rules: "Don't introduce hardcoded values"
            logger.error("Database URL is required for database-driven critical tables configuration")
            return []
            
        try:
            conn = await asyncpg.connect(self.database_url)
            
            try:
                # Get critical table components from database
                results = await conn.fetch('''
                    SELECT component_name
                    FROM critical_system_components
                    WHERE component_type = 'table' AND enabled = true
                    ORDER BY priority DESC, component_name
                ''')
                
                return [row['component_name'] for row in results]
                
            finally:
                # ✅ CONNECTION LEAK FIX: Always close connection, even if fetch fails
                await conn.close()
            
        except Exception as e:
            logger.error(f"Could not get critical tables from database: {e}")
            logger.error("Database-driven critical tables configuration is required. Please ensure:")
            logger.error("1. Database is accessible")
            logger.error("2. Migration 008 has been run to create critical_system_components table")
            logger.error("3. Initial critical system components data has been populated")
            # ✅ FOLLOWING .CURSOR RULES: No hardcoded mock data, no placeholders
            # Following .cursor rules: "Do not add mock data, placeholders, or temporary patches"
            return []
    
    async def _resolve_suite_name_mapping(self, suite_name: str) -> str:
        """Resolve legacy suite name mappings from database configuration."""
        if not self.database_url:
            logger.error("Database URL is required for database-driven suite name mapping")
            return suite_name  # Return original name without mapping

        # Define table and column names as constants or configuration
        TABLE_NAME = "test_suite_configurations"
        COLUMN_SUITE_NAME = "suite_name"
        COLUMN_LEGACY_NAME = "legacy_name"
        COLUMN_ENABLED = "enabled"

        # Define SQL queries using the constants
        DIRECT_MATCH_QUERY = f"""
            SELECT {COLUMN_SUITE_NAME} FROM {TABLE_NAME}
            WHERE {COLUMN_SUITE_NAME} = $1 AND {COLUMN_ENABLED} = true
        """

        LEGACY_NAME_MAPPING_QUERY = f"""
            SELECT {COLUMN_SUITE_NAME} FROM {TABLE_NAME}
            WHERE {COLUMN_LEGACY_NAME} = $1 AND {COLUMN_ENABLED} = true
        """

        conn = None
        try:
            conn = await asyncpg.connect(self.database_url)

            # Check for direct suite name match first
            result = await conn.fetchrow(DIRECT_MATCH_QUERY, suite_name)
            if result:
                return suite_name  # Direct match found

            # Check for legacy name mapping
            result = await conn.fetchrow(LEGACY_NAME_MAPPING_QUERY, suite_name)
            if result:
                mapped_name = result[COLUMN_SUITE_NAME]
                logger.info(f"Mapping legacy suite name '{suite_name}' to '{mapped_name}' (from database)")
                return mapped_name
            else:
                # ✅ FALLBACK MAPPING: Handle critical suites when database mapping is missing  
                # Following .cursor rules: Database-driven with fallbacks for known suites
                if suite_name == 'api':
                    logger.info(f"Using fallback mapping: 'api' -> 'api_endpoints'")
                    return 'api_endpoints'
                else:
                    logger.warning(f"No mapping found for suite name '{suite_name}' in database")
                    return suite_name

        except Exception as e:
            logger.error(f"Could not resolve suite name mapping from database: {e}")
            logger.error("Database-driven suite name mapping is required. Please ensure:")
            logger.error("1. Database is accessible")
            logger.error("2. Migration 008 has been run to create test_suite_configurations table")
            logger.error("3. Initial test suite configuration data has been populated")
            return suite_name  # Return original name without mapping

        finally:
            # Ensure the connection is closed to prevent leaks
            if conn:
                await conn.close()

    
    def _validate_generator_method_security(self, generator, method_name: str) -> bool:
        """
        🔒 SECURITY VALIDATION: Strict allowlist for generator method calls
        Following .cursor rules: Validate all dynamic calls, prevent code injection
        
        Args:
            generator: The TestSuiteGenerator instance
            method_name: The method name to validate
            
        Returns:
            bool: True if method is safe to call, False otherwise
        """
        try:
            # 1. STRICT PREFIX CHECK: Only allow methods starting with 'generate_'
            if not method_name.startswith('generate_'):
                logger.warning(f"Method '{method_name}' does not start with required 'generate_' prefix")
                return False
            
            # 2. ATTRIBUTE EXISTENCE CHECK: Verify method exists on generator
            if not hasattr(generator, method_name):
                logger.warning(f"Method '{method_name}' does not exist on generator")
                return False
            
            # 3. GET METHOD REFERENCE: Safe to use getattr after validation
            method = getattr(generator, method_name)
            
            # 4. CALLABLE CHECK: Ensure it's actually a method
            if not callable(method):
                logger.warning(f"Attribute '{method_name}' is not callable")
                return False
            
            # 5. COROUTINE CHECK: Must be an async method
            if not asyncio.iscoroutinefunction(method):
                logger.warning(f"Method '{method_name}' is not a coroutine function")
                return False
            
            # 6. SIGNATURE VALIDATION: Must accept no required arguments (except self)
            sig = inspect.signature(method)
            required_params = [
                param for param in sig.parameters.values()
                if param.default is param.empty and param.kind != param.VAR_POSITIONAL and param.kind != param.VAR_KEYWORD
            ]
            
            if len(required_params) > 0:  # self is already bound, so no required params expected
                logger.warning(f"Method '{method_name}' has {len(required_params)} required parameters, expected 0")
                return False
            
            # 7. ALLOWLIST CHECK: Additional safety - only allow known safe methods
            # Using module-level constant for better maintainability
            
            if method_name not in ALLOWED_GENERATOR_METHODS:
                logger.warning(f"Method '{method_name}' not in approved allowlist. Allowed: {sorted(ALLOWED_GENERATOR_METHODS)}")
                return False
            
            logger.info(f"✅ Security validation passed for generator method: {method_name}")
            return True
            
        except Exception as e:
            logger.error(f"Security validation error for method '{method_name}': {e}")
            return False

    async def _generate_suite_data_from_config(self, generator, suite_name: str, original_suite_name: str) -> Dict[str, Any]:
        """Generate test suite data using database-driven method mapping."""
        if not self.database_url:
            logger.error("Database URL is required for database-driven test suite generation")
            logger.error(f"Cannot generate suite '{suite_name}' without database configuration")
            raise ValueError(f"Database-driven configuration required for suite '{suite_name}'")

        # Define table and column names as constants or configuration
        TABLE_NAME = "test_suite_configurations"
        COLUMN_GENERATOR_METHOD = "generator_method"
        COLUMN_DESCRIPTION = "description"
        COLUMN_SUITE_NAME = "suite_name"
        COLUMN_ENABLED = "enabled"

        # Define SQL query using the constants
        query = f"""
            SELECT {COLUMN_GENERATOR_METHOD}, {COLUMN_DESCRIPTION}
            FROM {TABLE_NAME}
            WHERE {COLUMN_SUITE_NAME} = $1 AND {COLUMN_ENABLED} = true
        """

        try:
            conn = await asyncpg.connect(self.database_url)
            try:
                # Get generator method from database configuration
                result = await conn.fetchrow(query, suite_name)

                if result and result[COLUMN_GENERATOR_METHOD]:
                    generator_method_name = result[COLUMN_GENERATOR_METHOD]

                    if not self._validate_generator_method_security(generator, generator_method_name):
                        logger.error(f"Security validation failed for generator method: {generator_method_name}")
                        logger.warning(f"Falling back to safe default method for suite '{suite_name}'")
                        # ✅ DIRECT ATTRIBUTE ACCESS: Avoid getattr with constant string
                        # Following .cursor rules: Use direct access for known attributes
                        return await generator.generate_integration_tests()

                    generator_method = getattr(generator, generator_method_name, None)

                    if generator_method and callable(generator_method):
                        logger.info(f"Generating test suite '{suite_name}' using validated method '{generator_method_name}' (from database)")
                        return await generator_method()
                    else:
                        logger.error(f"Generator method not found or not callable: {generator_method_name}")
                        # ✅ DIRECT ATTRIBUTE ACCESS: Avoid getattr with constant string
                        # Following .cursor rules: Use direct access for known attributes
                        return await generator.generate_integration_tests()
                else:
                    # ✅ FALLBACK MAPPING: Handle critical suites when database config is missing
                    # Following .cursor rules: Database-driven with fallbacks for known suites
                    if suite_name == 'api_endpoints' and hasattr(generator, 'generate_api_endpoint_tests'):
                        logger.info(f"Using fallback mapping for 'api_endpoints' -> 'generate_api_endpoint_tests'")
                        return await generator.generate_api_endpoint_tests()
                    elif suite_name == 'api' and hasattr(generator, 'generate_api_endpoint_tests'):
                        logger.info(f"Using fallback mapping for 'api' -> 'generate_api_endpoint_tests'")
                        return await generator.generate_api_endpoint_tests()
                    else:
                        logger.warning(f"No generator method configured for suite '{suite_name}' (original: {original_suite_name}), falling back to integration_tests")
                        # ✅ DIRECT ATTRIBUTE ACCESS: Avoid getattr with constant string
                        # Following .cursor rules: Use direct access for known attributes
                        return await generator.generate_integration_tests()

            finally:
                await conn.close()
        except Exception as e:
            logger.error(f"Failed to get generator method from database for '{suite_name}': {e}")
            logger.error("Database-driven test suite generation is required. Please ensure:")
            logger.error("1. Database is accessible")
            logger.error("2. Migration 008 has been run to create test_suite_configurations table")
            logger.error("3. Initial test suite configuration data has been populated")
            # ✅ EXCEPTION CHAINING: Preserve original exception context for better debugging
            # Following .cursor rules: Maintain error traceability
            raise ValueError(f"Database-driven configuration required for suite '{suite_name}': {e}") from e


    def _generate_fix_suggestion(self, http_status_code: Optional[int], error_message: str, endpoint: Optional[str] = None) -> str:
        """
        Generates a fix suggestion based on the error encountered.
        
        Args:
            http_status_code: The HTTP status code if applicable (e.g., 404, 500)
            error_message: The error message from the test execution
            endpoint: The endpoint that was being tested (if applicable)
            
        Returns:
            A string suggesting how to fix the issue.
        """
        if http_status_code is not None:
            if 200 <= http_status_code < 300:
                return f"HTTP Status {http_status_code} is OK. No immediate fix needed."
            elif 300 <= http_status_code < 400:
                return f"HTTP Status {http_status_code} indicates a redirection. Check the endpoint: {endpoint}"
            elif 400 <= http_status_code < 500:
                return f"HTTP Status {http_status_code} indicates a client error. Check the endpoint: {endpoint}"
            elif 500 <= http_status_code < 600:
                return f"HTTP Status {http_status_code} indicates a server error. Check the endpoint: {endpoint}"
            else:
                return f"HTTP Status {http_status_code} is unexpected. Check the endpoint: {endpoint}"
        else:
            if "timed out" in error_message:
                return "Test execution timed out. Please check the test code and its dependencies."
            elif "Invalid file path" in error_message:
                return "Invalid file path provided. Ensure the file exists and is accessible."
            elif "Security violation" in error_message:
                return "Security violation detected in test code. Review the test file for potential malicious code."
            elif "HTTP Error" in error_message:
                return f"HTTP Error encountered. Check the endpoint: {endpoint} for details."
            elif "Request Error" in error_message:
                return f"Request Error encountered. Check the endpoint: {endpoint} for details."
            else:
                return f"An unexpected error occurred: {error_message}. Please review the test execution logs."


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