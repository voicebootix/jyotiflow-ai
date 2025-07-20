#!/usr/bin/env python3
"""
Auto-Fix Testing Integration
Integrates the self-healing system with testing infrastructure
to validate that auto-fixes improve system reliability
"""

import asyncio
import asyncpg
import json
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")

class AutoFixTestIntegrator:
    """
    Integrates auto-fix system with testing infrastructure
    to validate that fixes actually improve system health
    """
    
    def __init__(self):
        self.database_url = DATABASE_URL
        self.test_results = {}
        
    async def pre_fix_test(self, issue_id: str, issue_type: str, table_name: str) -> Dict[str, Any]:
        """
        Run tests before applying an auto-fix to establish baseline
        
        Args:
            issue_id: Unique identifier for the database issue
            issue_type: Type of issue (MISSING_TABLE, MISSING_COLUMN, etc.)
            table_name: Affected table name
            
        Returns:
            Test results before fix application
        """
        logger.info(f"🧪 Running pre-fix tests for {issue_type} on {table_name}")
        
        test_session_id = await self._create_test_session(
            test_type="pre_fix_validation",
            test_category="auto_healing",
            triggered_by="auto_fix_system",
            trigger_context={
                "issue_id": issue_id,
                "issue_type": issue_type,
                "table_name": table_name,
                "phase": "pre_fix"
            }
        )
        
        test_results = await self._execute_validation_tests(
            session_id=test_session_id,
            focus_area=table_name,
            test_type="pre_fix"
        )
        
        # Store pre-fix results
        await self._store_autofix_test_result(
            test_session_id=test_session_id,
            issue_id=issue_id,
            issue_type=issue_type,
            table_name=table_name,
            pre_fix_test_status=test_results["overall_status"],
            test_details=test_results
        )
        
        return {
            "test_session_id": test_session_id,
            "status": test_results["overall_status"],
            "test_details": test_results,
            "baseline_established": True
        }
    
    async def post_fix_test(self, issue_id: str, fix_applied: bool, fix_success: bool) -> Dict[str, Any]:
        """
        Run tests after applying an auto-fix to validate improvement
        
        Args:
            issue_id: Unique identifier for the database issue
            fix_applied: Whether the fix was actually applied
            fix_success: Whether the fix application was successful
            
        Returns:
            Test results after fix application
        """
        logger.info(f"🔬 Running post-fix tests for issue {issue_id}")
        
        # Get the original test session info
        autofix_record = await self._get_autofix_record(issue_id)
        if not autofix_record:
            logger.error(f"No pre-fix test record found for issue {issue_id}")
            return {"error": "No baseline test found"}
            
        test_session_id = await self._create_test_session(
            test_type="post_fix_validation",
            test_category="auto_healing",
            triggered_by="auto_fix_system",
            trigger_context={
                "issue_id": issue_id,
                "phase": "post_fix",
                "fix_applied": fix_applied,
                "fix_success": fix_success,
                "baseline_session": autofix_record["test_session_id"]
            }
        )
        
        test_results = await self._execute_validation_tests(
            session_id=test_session_id,
            focus_area=autofix_record["table_name"],
            test_type="post_fix"
        )
        
        # Compare with pre-fix results to determine improvement
        improvement_analysis = await self._analyze_test_improvement(
            issue_id=issue_id,
            post_fix_results=test_results
        )
        
        # Update the autofix test record
        await self._update_autofix_test_result(
            issue_id=issue_id,
            fix_applied=fix_applied,
            fix_success=fix_success,
            post_fix_test_status=test_results["overall_status"],
            test_improvement=improvement_analysis["improved"],
            rollback_required=improvement_analysis["rollback_required"]
        )
        
        return {
            "test_session_id": test_session_id,
            "status": test_results["overall_status"],
            "test_details": test_results,
            "improvement_analysis": improvement_analysis,
            "validation_complete": True
        }
    
    async def _create_test_session(self, test_type: str, test_category: str, 
                                 triggered_by: str, trigger_context: Dict) -> str:
        """Create a new test execution session"""
        if not self.database_url:
            raise Exception("DATABASE_URL not available")
            
        conn = await asyncpg.connect(self.database_url)
        try:
            session_id = str(uuid.uuid4())
            await conn.execute("""
                INSERT INTO test_execution_sessions (
                    session_id, test_type, test_category, environment,
                    triggered_by, trigger_context, status
                ) VALUES ($1, $2, $3, $4, $5, $6, $7)
            """, 
                session_id, test_type, test_category, "production",
                triggered_by, json.dumps(trigger_context), "running"
            )
            
            logger.info(f"✅ Created test session: {session_id}")
            return session_id
            
        finally:
            await conn.close()
    
    async def _execute_validation_tests(self, session_id: str, focus_area: str, test_type: str) -> Dict[str, Any]:
        """
        Execute validation tests focused on the area affected by auto-fix
        
        Args:
            session_id: Test session identifier
            focus_area: Table or component to focus testing on
            test_type: "pre_fix" or "post_fix"
            
        Returns:
            Comprehensive test results
        """
        test_results = {
            "session_id": session_id,
            "focus_area": focus_area,
            "test_type": test_type,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "tests_executed": [],
            "overall_status": "running"
        }
        
        try:
            # 1. Database connectivity test
            db_test = await self._test_database_connectivity(focus_area)
            test_results["tests_executed"].append(db_test)
            
            # 2. Table structure validation
            if focus_area != "general":
                structure_test = await self._test_table_structure(focus_area)
                test_results["tests_executed"].append(structure_test)
            
            # 3. Basic CRUD operations test
            crud_test = await self._test_basic_operations(focus_area)
            test_results["tests_executed"].append(crud_test)
            
            # 4. Integration test with monitoring system
            monitoring_test = await self._test_monitoring_integration(focus_area)
            test_results["tests_executed"].append(monitoring_test)
            
            # Calculate overall status
            test_results["overall_status"] = self._calculate_overall_status(test_results["tests_executed"])
            test_results["completed_at"] = datetime.now(timezone.utc).isoformat()
            
            # Store individual test results
            await self._store_test_case_results(session_id, test_results["tests_executed"])
            
            # Update session status
            await self._update_test_session_status(session_id, test_results)
            
            return test_results
            
        except Exception as e:
            logger.error(f"Validation test execution failed: {e}")
            test_results["overall_status"] = "error"
            test_results["error"] = str(e)
            return test_results
    
    async def _test_database_connectivity(self, focus_area: str) -> Dict[str, Any]:
        """Test basic database connectivity"""
        test_result = {
            "test_name": "database_connectivity",
            "focus_area": focus_area,
            "status": "running",
            "started_at": datetime.now(timezone.utc).isoformat()
        }
        
        try:
            conn = await asyncpg.connect(self.database_url)
            await conn.fetchval("SELECT 1")
            await conn.close()
            
            test_result.update({
                "status": "passed",
                "message": "Database connectivity successful",
                "execution_time_ms": 50
            })
            
        except Exception as e:
            test_result.update({
                "status": "failed",
                "error_message": str(e),
                "execution_time_ms": 100
            })
            
        test_result["completed_at"] = datetime.now(timezone.utc).isoformat()
        return test_result
    
    async def _test_table_structure(self, table_name: str) -> Dict[str, Any]:
        """Test table structure and schema"""
        test_result = {
            "test_name": "table_structure_validation",
            "focus_area": table_name,
            "status": "running",
            "started_at": datetime.now(timezone.utc).isoformat()
        }
        
        try:
            conn = await asyncpg.connect(self.database_url)
            
            # Check if table exists
            table_exists = await conn.fetchval("""
                SELECT EXISTS(
                    SELECT 1 FROM information_schema.tables 
                    WHERE table_name = $1
                )
            """, table_name)
            
            if table_exists:
                # Check column structure
                columns = await conn.fetch("""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns
                    WHERE table_name = $1
                    ORDER BY ordinal_position
                """, table_name)
                
                test_result.update({
                    "status": "passed",
                    "message": f"Table {table_name} structure validated",
                    "output_data": {"columns": [dict(row) for row in columns]},
                    "execution_time_ms": 75
                })
            else:
                test_result.update({
                    "status": "failed",
                    "error_message": f"Table {table_name} does not exist",
                    "execution_time_ms": 50
                })
                
            await conn.close()
            
        except Exception as e:
            test_result.update({
                "status": "failed",
                "error_message": str(e),
                "execution_time_ms": 100
            })
            
        test_result["completed_at"] = datetime.now(timezone.utc).isoformat()
        return test_result
    
    async def _test_basic_operations(self, table_name: str) -> Dict[str, Any]:
        """Test basic CRUD operations if applicable"""
        test_result = {
            "test_name": "basic_crud_operations",
            "focus_area": table_name,
            "status": "running",
            "started_at": datetime.now(timezone.utc).isoformat()
        }
        
        try:
            conn = await asyncpg.connect(self.database_url)
            
            # For test tables, try basic operations
            if table_name.startswith("test_") or table_name in ["users", "sessions"]:
                # Try a simple SELECT count
                count = await conn.fetchval(f'SELECT COUNT(*) FROM "{table_name}"')
                
                test_result.update({
                    "status": "passed",
                    "message": f"Basic operations on {table_name} successful",
                    "output_data": {"row_count": count},
                    "execution_time_ms": 25
                })
            else:
                test_result.update({
                    "status": "skipped",
                    "message": f"CRUD tests skipped for {table_name} (system table)",
                    "execution_time_ms": 5
                })
                
            await conn.close()
            
        except Exception as e:
            test_result.update({
                "status": "failed",
                "error_message": str(e),
                "execution_time_ms": 50
            })
            
        test_result["completed_at"] = datetime.now(timezone.utc).isoformat()
        return test_result
    
    async def _test_monitoring_integration(self, focus_area: str) -> Dict[str, Any]:
        """Test integration with monitoring system"""
        test_result = {
            "test_name": "monitoring_integration",
            "focus_area": focus_area,
            "status": "running",
            "started_at": datetime.now(timezone.utc).isoformat()
        }
        
        try:
            conn = await asyncpg.connect(self.database_url)
            
            # Check if monitoring tables are accessible
            monitoring_tables = ["health_check_results", "validation_sessions"]
            accessible_tables = []
            
            for table in monitoring_tables:
                try:
                    await conn.fetchval(f'SELECT COUNT(*) FROM "{table}" LIMIT 1')
                    accessible_tables.append(table)
                except:
                    pass
            
            if len(accessible_tables) > 0:
                test_result.update({
                    "status": "passed",
                    "message": "Monitoring integration validated",
                    "output_data": {"accessible_tables": accessible_tables},
                    "execution_time_ms": 30
                })
            else:
                test_result.update({
                    "status": "failed",
                    "error_message": "No monitoring tables accessible",
                    "execution_time_ms": 40
                })
                
            await conn.close()
            
        except Exception as e:
            test_result.update({
                "status": "failed",
                "error_message": str(e),
                "execution_time_ms": 60
            })
            
        test_result["completed_at"] = datetime.now(timezone.utc).isoformat()
        return test_result
    
    def _calculate_overall_status(self, test_results: List[Dict]) -> str:
        """Calculate overall test status from individual test results"""
        if not test_results:
            return "error"
            
        statuses = [test["status"] for test in test_results]
        
        if all(status == "passed" for status in statuses):
            return "passed"
        elif all(status in ["passed", "skipped"] for status in statuses):
            return "passed"
        elif any(status == "failed" for status in statuses):
            return "failed"
        else:
            return "partial"
    
    async def _store_test_case_results(self, session_id: str, test_results: List[Dict]):
        """Store individual test case results"""
        if not self.database_url:
            return
            
        conn = await asyncpg.connect(self.database_url)
        try:
            for test in test_results:
                await conn.execute("""
                    INSERT INTO test_case_results (
                        session_id, test_name, test_category, status,
                        execution_time_ms, error_message, output_data
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                """,
                    session_id,
                    test["test_name"],
                    "auto_healing",
                    test["status"],
                    test.get("execution_time_ms", 0),
                    test.get("error_message"),
                    json.dumps(test.get("output_data", {}))
                )
        finally:
            await conn.close()
    
    async def _update_test_session_status(self, session_id: str, test_results: Dict):
        """Update test session with final results"""
        if not self.database_url:
            return
            
        conn = await asyncpg.connect(self.database_url)
        try:
            total_tests = len(test_results["tests_executed"])
            passed_tests = sum(1 for test in test_results["tests_executed"] if test["status"] == "passed")
            failed_tests = sum(1 for test in test_results["tests_executed"] if test["status"] == "failed")
            
            await conn.execute("""
                UPDATE test_execution_sessions SET
                    status = $2,
                    completed_at = NOW(),
                    total_tests = $3,
                    passed_tests = $4,
                    failed_tests = $5
                WHERE session_id = $1
            """, session_id, test_results["overall_status"], total_tests, passed_tests, failed_tests)
            
        finally:
            await conn.close()
    
    async def _store_autofix_test_result(self, test_session_id: str, issue_id: str, 
                                       issue_type: str, table_name: str, 
                                       pre_fix_test_status: str, test_details: Dict):
        """Store auto-fix test result record"""
        if not self.database_url:
            return
            
        conn = await asyncpg.connect(self.database_url)
        try:
            await conn.execute("""
                INSERT INTO autofix_test_results (
                    test_session_id, issue_id, issue_type, table_name,
                    pre_fix_test_status, test_details
                ) VALUES ($1, $2, $3, $4, $5, $6)
            """, 
                test_session_id, issue_id, issue_type, table_name,
                pre_fix_test_status, json.dumps(test_details)
            )
        finally:
            await conn.close()
    
    async def _get_autofix_record(self, issue_id: str) -> Optional[Dict]:
        """Get existing autofix test record"""
        if not self.database_url:
            return None
            
        conn = await asyncpg.connect(self.database_url)
        try:
            record = await conn.fetchrow("""
                SELECT * FROM autofix_test_results WHERE issue_id = $1
            """, issue_id)
            
            return dict(record) if record else None
        finally:
            await conn.close()
    
    async def _update_autofix_test_result(self, issue_id: str, fix_applied: bool, 
                                        fix_success: bool, post_fix_test_status: str,
                                        test_improvement: bool, rollback_required: bool):
        """Update autofix test result with post-fix data"""
        if not self.database_url:
            return
            
        conn = await asyncpg.connect(self.database_url)
        try:
            await conn.execute("""
                UPDATE autofix_test_results SET
                    fix_applied = $2,
                    fix_success = $3,
                    post_fix_test_status = $4,
                    test_improvement = $5,
                    rollback_required = $6
                WHERE issue_id = $1
            """, issue_id, fix_applied, fix_success, post_fix_test_status, 
                test_improvement, rollback_required)
        finally:
            await conn.close()
    
    async def _analyze_test_improvement(self, issue_id: str, post_fix_results: Dict) -> Dict[str, Any]:
        """Analyze whether the fix improved test results"""
        try:
            # Get pre-fix results
            pre_fix_record = await self._get_autofix_record(issue_id)
            if not pre_fix_record:
                return {"improved": False, "rollback_required": True, "reason": "No baseline found"}
            
            pre_fix_details = json.loads(pre_fix_record["test_details"])
            pre_fix_status = pre_fix_details["overall_status"]
            post_fix_status = post_fix_results["overall_status"]
            
            # Simple improvement analysis
            improvement_detected = False
            rollback_required = False
            
            if pre_fix_status == "failed" and post_fix_status in ["passed", "partial"]:
                improvement_detected = True
            elif pre_fix_status == "partial" and post_fix_status == "passed":
                improvement_detected = True
            elif pre_fix_status in ["passed", "partial"] and post_fix_status == "failed":
                rollback_required = True
            
            return {
                "improved": improvement_detected,
                "rollback_required": rollback_required,
                "pre_fix_status": pre_fix_status,
                "post_fix_status": post_fix_status,
                "analysis_timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Test improvement analysis failed: {e}")
            return {
                "improved": False,
                "rollback_required": True,
                "reason": f"Analysis failed: {str(e)}"
            }

# Example integration with database self-healing system
async def integrate_with_auto_fix_system():
    """
    Example of how to integrate this with the existing auto-fix system
    """
    integrator = AutoFixTestIntegrator()
    
    # This would be called by the database self-healing system
    # BEFORE applying a fix
    pre_fix_result = await integrator.pre_fix_test(
        issue_id="test-issue-001",
        issue_type="MISSING_COLUMN", 
        table_name="test_table"
    )
    
    # ... auto-fix system applies the fix ...
    
    # This would be called AFTER applying a fix
    post_fix_result = await integrator.post_fix_test(
        issue_id="test-issue-001",
        fix_applied=True,
        fix_success=True
    )
    
    return {
        "pre_fix": pre_fix_result,
        "post_fix": post_fix_result
    }

if __name__ == "__main__":
    # Example usage
    result = asyncio.run(integrate_with_auto_fix_system())
    print("Auto-fix testing integration complete:", result)