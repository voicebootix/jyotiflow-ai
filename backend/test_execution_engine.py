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
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Callable
import logging

# Add current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")

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
        """Execute a specific test suite and return results"""
        logger.info(f"🧪 Executing test suite: {suite_name}")
        
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
    
    async def _execute_test_code(self, test_code: str, test_case: Dict[str, Any]) -> Any:
        """Execute test code in a safe environment"""
        
        # Create a safe execution environment
        test_globals = {
            '__builtins__': __builtins__,
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
            # Import additional modules if needed
            if 'httpx' in test_code:
                import httpx
                test_globals['httpx'] = httpx
            
            if 'database_self_healing_system' in test_code:
                try:
                    from database_self_healing_system import DatabaseSelfHealingSystem, extract_table_from_query
                    test_globals['DatabaseSelfHealingSystem'] = DatabaseSelfHealingSystem
                    test_globals['extract_table_from_query'] = extract_table_from_query
                except ImportError as e:
                    logger.warning(f"Could not import database_self_healing_system: {e}")
            
            # Execute the test code
            exec(test_code, test_globals)
            
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
                
                raise Exception(f"No test function found: {test_function_name}")
                
        except Exception as e:
            logger.error(f"Test code execution failed: {e}")
            raise
    
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
        """Get test cases for a specific suite"""
        if not self.database_url:
            return []
            
        try:
            conn = await asyncpg.connect(self.database_url)
            
            # Get test cases from database
            results = await conn.fetch('''
                SELECT tcr.test_name, tcr.test_category, tcr.output_data
                FROM test_case_results tcr
                JOIN test_execution_sessions tes ON tcr.session_id = tes.session_id
                WHERE tes.test_type = $1 AND tcr.status = 'generated'
                ORDER BY tcr.created_at DESC
            ''', suite_name)
            
            await conn.close()
            
            test_cases = []
            for row in results:
                try:
                    test_data = json.loads(row['output_data'])
                    test_cases.append(test_data)
                except Exception as e:
                    logger.warning(f"Could not parse test case data: {e}")
            
            return test_cases
            
        except Exception as e:
            logger.warning(f"Could not get test cases from database: {e}")
            return []
    
    async def _get_available_test_suites(self) -> List[Dict[str, Any]]:
        """Get all available test suites"""
        if not self.database_url:
            return []
            
        try:
            conn = await asyncpg.connect(self.database_url)
            
            results = await conn.fetch('''
                SELECT DISTINCT test_type, test_category
                FROM test_execution_sessions
                WHERE triggered_by = 'test_suite_generator'
                ORDER BY test_type
            ''')
            
            await conn.close()
            
            return [dict(row) for row in results]
            
        except Exception as e:
            logger.warning(f"Could not get test suites from database: {e}")
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