"""
📊 MONITORING DASHBOARD - Real-time integration monitoring for JyotiFlow admin
Integrates seamlessly with existing admin dashboard UI.
"""
import json
import asyncio
import asyncpg
import uuid
import os
from datetime import datetime, timezone
from typing import Dict, List

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from db import db_manager
import logging
logger = logging.getLogger(__name__)

# Database connection managed through db_manager
from pydantic import BaseModel, Field, model_validator
from typing import Optional, Dict, Any

class StandardResponse(BaseModel):
    status: str
    message: str
    data: Dict[str, Any] = Field(default_factory=dict)
    success: bool = Field(default=True, description="Backward compatibility field")
    
    @model_validator(mode='after')
    def set_success_from_status(self) -> 'StandardResponse':
        """Set success field based on status for backward compatibility"""
        self.success = self.status == "success"
        return self
    
    model_config = {
        "extra": "forbid",
        "json_schema_extra": {
            "examples": [
                {
                    "status": "success",
                    "message": "Operation completed",
                    "data": {},
                    "success": True
                }
            ]
        }
    }

class LegacyStandardResponse(BaseModel):
    """Legacy response format for backward compatibility"""
    success: bool
    message: str
    data: dict = {}
    
    @classmethod
    def from_standard(cls, response: StandardResponse):
        """Convert from new format to legacy format"""
        return cls(
            success=response.status == "success",
            message=response.message,
            data=response.data
        )
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from deps import get_current_admin_dependency

from .integration_monitor import integration_monitor, IntegrationStatus
from .business_validator import BusinessLogicValidator

# Create router for monitoring endpoints
router = APIRouter(prefix="/api/monitoring", tags=["monitoring"])

# WebSocket manager for real-time updates
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        
    def disconnect(self, websocket: WebSocket):
        try:
            self.active_connections.remove(websocket)
        except ValueError:
            # WebSocket was not in the list, ignore
            pass
        
    async def broadcast(self, message: dict):
        """Broadcast message to all connected admin clients"""
        dead_connections = []
        for connection in self.active_connections[:]:  # Create a copy to iterate safely
            try:
                await connection.send_json(message)
            except WebSocketDisconnect:
                logger.info("WebSocket client disconnected during broadcast")
                dead_connections.append(connection)
            except (ConnectionResetError, ConnectionAbortedError, OSError) as conn_error:
                logger.warning(f"Connection closed during broadcast: {conn_error}")
                dead_connections.append(connection)
            except Exception as e:
                logger.error(f"Unexpected error broadcasting to client: {e}")
                dead_connections.append(connection)
        
        # Remove dead connections
        for dead_conn in dead_connections:
            self.disconnect(dead_conn)

connection_manager = ConnectionManager()

class MonitoringDashboard:
    """
    Real-time monitoring dashboard that integrates with
    existing JyotiFlow admin interface.
    """
    
    def __init__(self):
        self.business_validator = BusinessLogicValidator()
        
    async def get_dashboard_data(self) -> Dict:
        """Get comprehensive dashboard data for admin interface"""
        try:
            # Get system health
            system_health = await integration_monitor.get_system_health()
            
            # Get recent sessions
            recent_sessions = await self._get_recent_sessions()
            
            # Get integration statistics
            integration_stats = await self._get_integration_statistics()
            
            # Get critical issues
            critical_issues = await self._get_critical_issues()
            
            # Get social media health
            social_media_health = await self._get_social_media_health()
            
            # Calculate overall metrics
            overall_metrics = await self._calculate_overall_metrics()
            
            dashboard_data = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "system_health": system_health,
                "active_sessions": len(integration_monitor.active_sessions),
                "recent_sessions": recent_sessions,
                "integration_statistics": integration_stats,
                "critical_issues": critical_issues,
                "social_media_health": social_media_health,
                "overall_metrics": overall_metrics,
                "alerts": await self._get_active_alerts()
            }
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"❌ Failed to get dashboard data: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    async def get_session_details(self, session_id: str) -> Dict:
        """Get detailed validation report for a specific session"""
        try:
            conn = await db_manager.get_connection()
            try:
                # Get session data
                session_data = await conn.fetchrow("""
                    SELECT * FROM validation_sessions
                    WHERE session_id = $1
                """, session_id)
                
                if not session_data:
                    return {"error": "Session not found"}
                
                # Get integration validations
                validations = await conn.fetch("""
                    SELECT * FROM integration_validations
                    WHERE session_id = $1
                    ORDER BY validation_time
                """, session_id)
                
                # Get business logic issues
                issues = await conn.fetch("""
                    SELECT * FROM business_logic_issues
                    WHERE session_id = $1
                    ORDER BY created_at
                """, session_id)
                
                # Get context flow
                context_flow = None
                if session_id in integration_monitor.active_sessions:
                    context_flow = await integration_monitor.context_tracker.get_context_flow_report(session_id)
                
                return {
                    "session": dict(session_data),
                    "validations": [dict(v) for v in validations],
                    "issues": [dict(i) for i in issues],
                    "context_flow": context_flow,
                    "recommendations": await self._generate_session_recommendations(session_id)
                }
            finally:
                await db_manager.release_connection(conn)
                
        except Exception as e:
            logger.error(f"❌ Failed to get session details: {e}")
            return {"error": str(e)}
    
    async def get_integration_health_details(self, integration_point: str) -> Dict:
        """Get detailed health information for a specific integration"""
        try:
            conn = await db_manager.get_connection()
            try:
                # Get recent performance metrics
                performance = await conn.fetch("""
                    SELECT 
                        DATE_TRUNC('hour', validation_time) as hour,
                        AVG(CAST(actual_value->>'duration_ms' AS INTEGER)) as avg_duration,
                        COUNT(*) as total_calls,
                        SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as successful_calls
                    FROM integration_validations
                    WHERE integration_name = $1
                    AND validation_time > NOW() - INTERVAL '24 hours'
                    GROUP BY hour
                    ORDER BY hour DESC
                """, integration_point)
                
                # Get recent errors
                recent_errors = await conn.fetch("""
                    SELECT error_message, COUNT(*) as count, MAX(validation_time) as last_occurred
                    FROM integration_validations
                    WHERE integration_name = $1
                    AND status = 'failed'
                    AND validation_time > NOW() - INTERVAL '24 hours'
                    AND error_message IS NOT NULL
                    GROUP BY error_message
                    ORDER BY count DESC
                    LIMIT 5
                """, integration_point)
                
                # Get auto-fix statistics
                auto_fix_stats = await conn.fetchrow("""
                    SELECT 
                        COUNT(*) as total_issues,
                        SUM(CASE WHEN auto_fixed = true THEN 1 ELSE 0 END) as auto_fixed_count
                    FROM integration_validations
                    WHERE integration_name = $1
                    AND status = 'failed'
                    AND validation_time > NOW() - INTERVAL '7 days'
                """, integration_point)
                
                return {
                    "integration_point": integration_point,
                    "performance_history": [dict(p) for p in performance],
                    "recent_errors": [dict(e) for e in recent_errors],
                    "auto_fix_effectiveness": {
                        "total_issues": auto_fix_stats["total_issues"] if auto_fix_stats else 0,
                        "auto_fixed": auto_fix_stats["auto_fixed_count"] if auto_fix_stats else 0,
                        "success_rate": (
                            auto_fix_stats["auto_fixed_count"] / auto_fix_stats["total_issues"] * 100
                            if (auto_fix_stats and 
                                auto_fix_stats.get("total_issues") is not None and 
                                auto_fix_stats.get("total_issues") > 0 and
                                auto_fix_stats.get("auto_fixed_count") is not None)
                            else 0
                        )
                    }
                }
            finally:
                await db_manager.release_connection(conn)
                
        except Exception as e:
            logger.error(f"❌ Failed to get integration health details: {e}")
            return {"error": str(e)}
    
    async def trigger_validation_test(self, test_type: str) -> Dict:
        """Trigger a validation test for debugging"""
        try:
            if test_type == "full_flow":
                # Create a test session
                test_session_id = f"test_{datetime.now(timezone.utc).timestamp()}"
                test_context = {
                    "session_id": test_session_id,
                    "user_id": 0,  # Test user
                    "birth_details": {
                        "date": "1990-01-15",
                        "time": "14:30",
                        "location": "Chennai, India"
                    },
                    "spiritual_question": "What does my career future hold?",
                    "service_type": "comprehensive_reading"
                }
                
                # Start monitoring
                await integration_monitor.start_session_monitoring(
                    test_session_id, 
                    test_context["user_id"],
                    test_context["birth_details"],
                    test_context["spiritual_question"],
                    test_context["service_type"]
                )
                
                # Run validations
                # This would trigger actual API calls in production
                return StandardResponse(
                    status="success",
                    message="Validation test initiated",
                    data={"test_session_id": test_session_id}
                )
                
            elif test_type == "social_media":
                # Test social media credentials
                social_validator = integration_monitor.validators.get("social_media")
                if social_validator:
                    test_result = await social_validator.test_all_platforms()
                    return test_result
                else:
                    return StandardResponse(
                        status="error", 
                        message="Social media validator not found",
                        data={}
                    )
                    
            else:
                return StandardResponse(
                    status="error",
                    message=f"Unknown test type: {test_type}",
                    data={}
                )
                
        except Exception as e:
            logger.error(f"❌ Failed to trigger validation test: {e}")
            return StandardResponse(
                status="error",
                message=str(e),
                data={}
            )
    
    # Private helper methods
    async def _get_recent_sessions(self) -> List[Dict]:
        """Get recent session summaries"""
        try:
            conn = await db_manager.get_connection()
            try:
                sessions = await conn.fetch("""
                    SELECT 
                        vs.session_id,
                        vs.user_id,
                        vs.started_at,
                        vs.completed_at,
                        vs.overall_status,
                        u.email as user_email,
                        COUNT(DISTINCT iv.integration_name) as integrations_validated,
                        COUNT(DISTINCT bli.id) as issues_found
                    FROM validation_sessions vs
                    LEFT JOIN users u ON vs.user_id = u.id
                    LEFT JOIN integration_validations iv ON vs.session_id = iv.session_id
                    LEFT JOIN business_logic_issues bli ON vs.session_id = bli.session_id
                    WHERE vs.started_at > NOW() - INTERVAL '1 hour'
                    GROUP BY vs.session_id, vs.user_id, vs.started_at, 
                             vs.completed_at, vs.overall_status, u.email
                    ORDER BY vs.started_at DESC
                    LIMIT 20
                """)
                
                return [dict(s) for s in sessions]
            finally:
                await db_manager.release_connection(conn)
                
        except Exception as e:
            logger.error(f"Failed to get recent sessions: {e}")
            return []
    
    async def _get_integration_statistics(self) -> Dict:
        """Get integration performance statistics
        
        Note: Consider creating a database view for even better maintainability:
        
        CREATE OR REPLACE VIEW integration_metrics_24h AS
        SELECT 
            session_id,
            integration_name,
            status,
            CASE 
                WHEN actual_value IS NOT NULL AND actual_value->>'duration_ms' IS NOT NULL 
                THEN (actual_value->>'duration_ms')::INTEGER 
                ELSE NULL
            END as duration_ms,
            validation_time
        FROM integration_validations
        WHERE validation_time > NOW() - INTERVAL '24 hours';
        
        Then queries would simply be:
        - SELECT ... FROM integration_metrics_24h
        - SELECT ... FROM integration_metrics_24h GROUP BY integration_name
        """
        try:
            conn = await db_manager.get_connection()
            try:
                # Use CTE to centralize duration calculation logic
                integration_stats_query = """
                    WITH integration_metrics AS (
                        SELECT 
                            session_id,
                            integration_name,
                            status,
                            CASE 
                                WHEN actual_value IS NOT NULL AND actual_value->>'duration_ms' IS NOT NULL 
                                THEN (actual_value->>'duration_ms')::INTEGER 
                                ELSE NULL
                            END as duration_ms
                        FROM integration_validations
                        WHERE validation_time > NOW() - INTERVAL '24 hours'
                    )
                """
                
                # Overall statistics
                stats = await conn.fetchrow(integration_stats_query + """
                    SELECT
                        COUNT(DISTINCT session_id) as total_sessions,
                        COUNT(*) as total_validations,
                        SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as successful_validations,
                        COALESCE(AVG(duration_ms), 0)::INTEGER as avg_duration_ms
                    FROM integration_metrics
                """)
                
                # Per-integration statistics
                by_integration = await conn.fetch(integration_stats_query + """
                    SELECT 
                        integration_name,
                        COUNT(*) as total_calls,
                        SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as successful_calls,
                        COALESCE(AVG(duration_ms), 0)::INTEGER as avg_duration_ms
                    FROM integration_metrics
                    GROUP BY integration_name
                """)
                
                return {
                    "overall": dict(stats) if stats else {},
                    "by_integration": [dict(i) for i in by_integration]
                }
            finally:
                await db_manager.release_connection(conn)
                
        except Exception as e:
            logger.error(f"Failed to get integration statistics: {e}")
            return {"overall": {}, "by_integration": []}
    
    async def _get_critical_issues(self) -> List[Dict]:
        """Get current critical issues requiring attention"""
        try:
            conn = await db_manager.get_connection()
            try:
                issues = await conn.fetch("""
                    SELECT 
                        bli.*,
                        vs.user_id,
                        u.email as user_email
                    FROM business_logic_issues bli
                    JOIN validation_sessions vs ON bli.session_id = vs.session_id
                    LEFT JOIN users u ON vs.user_id = u.id
                    WHERE bli.severity = 'critical'
                    AND bli.fixed = false
                    AND bli.created_at > NOW() - INTERVAL '24 hours'
                    ORDER BY bli.created_at DESC
                    LIMIT 10
                """)
                
                return [dict(i) for i in issues]
            finally:
                await db_manager.release_connection(conn)
                
        except Exception as e:
            logger.error(f"Failed to get critical issues: {e}")
            return []
    
    async def _get_social_media_health(self) -> Dict:
        """Get social media integration health status"""
        try:
            conn = await db_manager.get_connection()
            try:
                # Get platform credentials status
                platforms = await conn.fetch("""
                    SELECT 
                        key,
                        value->>'platform' as platform,
                        value->>'last_validated' as last_validated,
                        value->>'is_valid' as is_valid
                    FROM platform_settings
                    WHERE key LIKE '%_credentials'
                """)
                
                # Get recent social media posts
                recent_posts = await conn.fetch("""
                    SELECT 
                        platform,
                        status,
                        COUNT(*) as count
                    FROM social_posts
                    WHERE created_at > NOW() - INTERVAL '24 hours'
                    GROUP BY platform, status
                """)
                
                # Get social media errors
                social_errors = await conn.fetch("""
                    SELECT 
                        platform,
                        COUNT(*) as error_count,
                        MAX(created_at) as last_error
                    FROM social_posts
                    WHERE status = 'failed'
                    AND created_at > NOW() - INTERVAL '24 hours'
                    GROUP BY platform
                """)
                
                return {
                    "platform_status": [dict(p) for p in platforms],
                    "recent_activity": [dict(r) for r in recent_posts],
                    "errors": [dict(e) for e in social_errors]
                }
            finally:
                await db_manager.release_connection(conn)
                
        except Exception as e:
            logger.error(f"Failed to get social media health: {e}")
            return {
                "platform_status": [],
                "recent_activity": [],
                "errors": []
            }
    
    async def _calculate_overall_metrics(self) -> Dict:
        """Calculate overall system metrics"""
        try:
            conn = await db_manager.get_connection()
            try:
                # Get success rate
                success_rate = await conn.fetchrow("""
                    SELECT 
                        COUNT(CASE WHEN overall_status = 'success' THEN 1 END)::float / 
                        NULLIF(COUNT(*), 0) * 100 as success_rate
                    FROM validation_sessions
                    WHERE started_at > NOW() - INTERVAL '24 hours'
                """)
                
                # Get average session duration
                avg_duration = await conn.fetchrow("""
                    SELECT AVG(
                        EXTRACT(EPOCH FROM (completed_at - started_at))
                    ) as avg_duration_seconds
                    FROM validation_sessions
                    WHERE completed_at IS NOT NULL
                    AND started_at > NOW() - INTERVAL '24 hours'
                """)
                
                # Get quality scores
                quality_scores = await conn.fetchrow("""
                    SELECT 
                        AVG(((validation_results->'quality_scores')->>'rag_relevance_score')::float) as avg_rag_score,
                        AVG(((validation_results->'quality_scores')->>'openai_quality_score')::float) as avg_openai_score
                    FROM validation_sessions
                    WHERE validation_results IS NOT NULL
                    AND started_at > NOW() - INTERVAL '24 hours'
                """)
                
                return {
                    "success_rate": success_rate["success_rate"] if success_rate else 0,
                    "avg_session_duration": avg_duration["avg_duration_seconds"] if avg_duration else 0,
                    "quality_scores": {
                        "rag_relevance": quality_scores["avg_rag_score"] if quality_scores else 0,
                        "openai_quality": quality_scores["avg_openai_score"] if quality_scores else 0
                    }
                }
            finally:
                await db_manager.release_connection(conn)
                
        except Exception as e:
            logger.error(f"Failed to calculate overall metrics: {e}")
            return {
                "success_rate": 0,
                "avg_session_duration": 0,
                "quality_scores": {}
            }
    
    async def _get_active_alerts(self) -> List[Dict]:
        """Get active alerts for admin attention"""
        alerts = []
        
        try:
            # Check system health
            system_health = await integration_monitor.get_system_health()
            
            if system_health.get("system_status") == "critical":
                alerts.append({
                    "type": "critical",
                    "message": "System health critical - multiple integrations failing",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
            
            # Check for high error rates with proper NULL handling
            conn = await db_manager.get_connection()
            try:
                error_rate = await conn.fetchrow("""
                    SELECT 
                        CASE 
                            WHEN COUNT(*) = 0 THEN 0
                            ELSE COUNT(CASE WHEN status = 'failed' THEN 1 END)::float / COUNT(*) * 100
                        END as error_rate
                    FROM integration_validations
                    WHERE validation_time > NOW() - INTERVAL '1 hour'
                """)
                
                if error_rate and error_rate["error_rate"] > 20:
                    alerts.append({
                        "type": "warning",
                        "message": f"High error rate detected: {error_rate['error_rate']:.1f}%",
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    })
            finally:
                await db_manager.release_connection(conn)
            
            return alerts
            
        except Exception as e:
            logger.error(f"Failed to get active alerts: {e}")
            return []
    
    async def _generate_session_recommendations(self, session_id: str) -> List[str]:
        """Generate specific recommendations for a session"""
        try:
            conn = await db_manager.get_connection()
            try:
                # Get validation results
                validation_data = await conn.fetchrow("""
                    SELECT validation_results
                    FROM validation_sessions
                    WHERE session_id = $1
                """, session_id)
                
                if not validation_data or not validation_data["validation_results"]:
                    return []
                
                try:
                    validation_results = json.loads(validation_data["validation_results"])
                except json.JSONDecodeError as json_error:
                    logger.error(f"Failed to parse validation results JSON: {json_error}")
                    validation_results = {}
                
                # Use business validator to generate recommendations
                return validation_results.get("recommendations", [])
            finally:
                await db_manager.release_connection(conn)
                
        except Exception as e:
            logger.error(f"Failed to generate session recommendations: {e}")
            return []

# Create singleton instance
monitoring_dashboard = MonitoringDashboard()

# API Endpoints
@router.get("/health")
async def get_monitoring_health():
    """Public endpoint to get basic monitoring system health (no auth required)"""
    try:
        system_health = await integration_monitor.get_system_health()
        return StandardResponse(
            status="success",
            message="Monitoring system health retrieved",
            data={
                "monitoring_active": True,
                "integrations": system_health.get("integrations", {}),
                "last_check": system_health.get("last_check"),
                "system_status": system_health.get("system_status", "operational")
            }
        )
    except Exception as e:
        return StandardResponse(
            status="error",
            message=f"Failed to get monitoring health: {str(e)}",
            data={
                "monitoring_active": False,
                "system_status": "error"
            }
        )

@router.get("/dashboard")
async def get_dashboard(admin: dict = Depends(get_current_admin_dependency)):
    """Get monitoring dashboard data for admin interface"""
    dashboard_data = await monitoring_dashboard.get_dashboard_data()
    return StandardResponse(
        status="success",
        message="Dashboard data retrieved",
        data=dashboard_data
    )

@router.get("/session/{session_id}")
async def get_session_validation(session_id: str, admin: dict = Depends(get_current_admin_dependency)):
    """Get detailed validation report for a specific session"""
    session_details = await monitoring_dashboard.get_session_details(session_id)
    
    if "error" in session_details:
        raise HTTPException(status_code=404, detail=session_details["error"])
    
    return StandardResponse(
        status="success",
        message="Session validation details retrieved",
        data=session_details
    )

@router.get("/integration/{integration_point}/health")
async def get_integration_health(integration_point: str, admin: dict = Depends(get_current_admin_dependency)):
    """Get detailed health metrics for a specific integration"""
    health_details = await monitoring_dashboard.get_integration_health_details(integration_point)
    
    return StandardResponse(
        status="success",
        message="Integration health details retrieved",
        data=health_details
    )

@router.post("/test/{test_type}")
async def trigger_test(test_type: str, admin: dict = Depends(get_current_admin_dependency)):
    """Trigger a validation test"""
    test_result = await monitoring_dashboard.trigger_validation_test(test_type)
    
    # trigger_validation_test now returns a StandardResponse object, so return it directly
    return test_result

# Testing infrastructure endpoints
@router.get("/test-status")
async def get_test_status():
    """Get current test execution status (public endpoint)"""
    try:
        conn = await db_manager.get_connection()
        try:
            # Get the latest completed test execution
            latest_execution = await conn.fetchrow("""
                SELECT completed_at, total_tests, passed_tests, failed_tests, 
                       coverage_percentage, execution_time_seconds, status
                FROM test_execution_sessions
                WHERE status IN ('passed', 'failed', 'partial')
                ORDER BY completed_at DESC NULLS LAST, started_at DESC
                LIMIT 1
            """)
            
            if latest_execution:
                return StandardResponse(
                    status="success",
                    message="Test status retrieved",
                    data={
                        "last_execution": latest_execution['completed_at'].isoformat() if latest_execution['completed_at'] else None,
                        "total_tests": latest_execution['total_tests'] or 0,
                        "passed_tests": latest_execution['passed_tests'] or 0,
                        "failed_tests": latest_execution['failed_tests'] or 0,
                        "test_coverage": float(latest_execution['coverage_percentage'] or 0),
                        "execution_time": latest_execution['execution_time_seconds'] or 0,
                        "status": latest_execution['status'] or 'unknown',
                        "auto_fixes_applied": 0  # Set to 0 for now as requested
                    }
                )
            else:
                # No test executions found
                return StandardResponse(
                    status="success", 
                    message="No test executions found",
                    data={
                        "last_execution": None,
                        "total_tests": 0,
                        "passed_tests": 0,
                        "failed_tests": 0,
                        "test_coverage": 0,
                        "execution_time": 0,
                        "status": "not_available",
                        "auto_fixes_applied": 0
                    }
                )
        finally:
            await db_manager.release_connection(conn)
    except Exception as e:
        return StandardResponse(
            status="error",
            message=f"Failed to get test status: {str(e)}",
            data={}
        )

@router.get("/test-sessions")
async def get_test_sessions(admin: dict = Depends(get_current_admin_dependency)):
    """Get test execution sessions history"""
    try:
        # Use db_manager connection pooling like other endpoints
        conn = await db_manager.get_connection()
        try:
            # Check if test_execution_sessions table exists
            table_exists = await conn.fetchval("""
                SELECT EXISTS(
                    SELECT 1 FROM information_schema.tables 
                    WHERE table_name = 'test_execution_sessions' AND table_schema = 'public'
                )
            """)
            
            if not table_exists:
                # Return empty data if table doesn't exist yet
                return StandardResponse(
                    status="success",
                    message="Test sessions table not yet created",
                    data=[]
                )
            
            # Fetch recent test sessions (last 50, ordered by most recent)
            sessions = await conn.fetch("""
                SELECT 
                    session_id,
                    test_type,
                    test_category,
                    environment,
                    started_at,
                    completed_at,
                    status,
                    total_tests,
                    passed_tests,
                    failed_tests,
                    skipped_tests,
                    coverage_percentage,
                    execution_time_seconds,
                    triggered_by,
                    created_at
                FROM test_execution_sessions
                ORDER BY started_at DESC
                LIMIT 50
            """)
            
            # Format sessions for API response
            formatted_sessions = []
            for session in sessions:
                formatted_session = {
                    "session_id": str(session['session_id']),
                    "test_type": session['test_type'],
                    "test_category": session['test_category'],
                    "environment": session['environment'],
                    "status": session['status'],
                    "started_at": session['started_at'].isoformat() if session['started_at'] else None,
                    "completed_at": session['completed_at'].isoformat() if session['completed_at'] else None,
                    "execution_time_seconds": session['execution_time_seconds'],
                    "total_tests": session['total_tests'] or 0,
                    "passed_tests": session['passed_tests'] or 0,
                    "failed_tests": session['failed_tests'] or 0,
                    "skipped_tests": session['skipped_tests'] or 0,
                    "coverage_percentage": float(session['coverage_percentage']) if session['coverage_percentage'] else None,
                    "triggered_by": session['triggered_by'],
                    "created_at": session['created_at'].isoformat() if session['created_at'] else None
                }
                formatted_sessions.append(formatted_session)
            
            return StandardResponse(
                status="success",
                message=f"Retrieved {len(formatted_sessions)} test sessions",
                data=formatted_sessions
            )
            
        finally:
            await db_manager.release_connection(conn)
            
    except asyncpg.PostgresConnectionError as e:
        logger.error(f"Database connection error: {e}")
        return StandardResponse(
            status="error",
            message="Database connection failed",
            data=[]
        )
    except asyncpg.PostgresError as e:
        logger.error(f"Database query error: {e}")
        return StandardResponse(
            status="error",
            message=f"Database query failed: {str(e)}",
            data=[]
        )
    except Exception as e:
        logger.error(f"Unexpected error getting test sessions: {e}")
        return StandardResponse(
            status="error",
            message=f"Failed to get test sessions: {str(e)}",
            data=[]
        )

@router.get("/test-metrics")
async def get_test_metrics(admin: dict = Depends(get_current_admin_dependency)):
    """Get test execution metrics and statistics"""
    try:
        conn = await db_manager.get_connection()
        try:
            # Get total test sessions
            total_sessions = await conn.fetchval("""
                SELECT COUNT(*) FROM test_execution_sessions
            """) or 0
            
            # Calculate success rate
            successful_sessions = await conn.fetchval("""
                SELECT COUNT(*) FROM test_execution_sessions 
                WHERE status = 'passed'
            """) or 0
            
            success_rate = (successful_sessions / max(total_sessions, 1)) * 100
            
            # Get average execution time
            avg_execution_time = await conn.fetchval("""
                SELECT AVG(execution_time_seconds) FROM test_execution_sessions
                WHERE execution_time_seconds IS NOT NULL
            """) or 0
            
            # Get coverage trend (comparing last 7 days to previous 7 days)
            recent_coverage = await conn.fetchval("""
                SELECT AVG(coverage_percentage) FROM test_execution_sessions
                WHERE started_at >= NOW() - INTERVAL '7 days'
                AND coverage_percentage IS NOT NULL
            """) or 0
            
            previous_coverage = await conn.fetchval("""
                SELECT AVG(coverage_percentage) FROM test_execution_sessions
                WHERE started_at >= NOW() - INTERVAL '14 days'
                AND started_at < NOW() - INTERVAL '7 days'
                AND coverage_percentage IS NOT NULL
            """) or 0
            
            coverage_trend = "improving" if recent_coverage > previous_coverage else "declining" if recent_coverage < previous_coverage else "stable"
            
            # Get auto-fixes applied
            auto_fixes_applied = await conn.fetchval("""
                SELECT COUNT(*) FROM autofix_test_results
                WHERE fix_applied = true
                AND created_at >= NOW() - INTERVAL '30 days'
            """) or 0
            
            return StandardResponse(
                status="success", 
                message="Test metrics retrieved",
                data={
                    "total_sessions": total_sessions,
                    "success_rate": round(success_rate, 1),
                    "avg_execution_time": round(avg_execution_time, 1),
                    "coverage_trend": coverage_trend,
                    "auto_fixes_applied": auto_fixes_applied
                }
            )
        finally:
            await db_manager.release_connection(conn)
    except Exception as e:
        return StandardResponse(
            status="error",
            message=f"Failed to get test metrics: {str(e)}",
            data={}
        )

@router.post("/test-execute")
async def execute_test(request: dict, admin: dict = Depends(get_current_admin_dependency)):
    """Execute a test suite using our actual test execution engine"""
    try:
        from test_execution_engine import TestExecutionEngine
        
        test_type = request.get("test_type", "unit")
        test_suite = request.get("test_suite", None)
        
        # Initialize test execution engine
        engine = TestExecutionEngine()
        
        if test_suite:
            # Execute specific test suite
            result = await engine.execute_test_suite(test_suite, test_type)
        else:
            # Execute all test suites
            result = await engine.execute_all_test_suites()
        
        return StandardResponse(
            status="success",
            message=f"Test execution completed: {test_type}",
            data=result
        )
    except Exception as e:
        logger.error(f"Test execution failed: {e}")
        return StandardResponse(
            status="error",
            message=f"Failed to execute test: {str(e)}",
            data={}
        )

@router.get("/test-suites")
async def get_available_test_suites(admin: dict = Depends(get_current_admin_dependency)):
    """Get all available test suites that can be executed"""
    try:
        from test_suite_generator import TestSuiteGenerator
        
        generator = TestSuiteGenerator()
        test_suites = await generator.generate_all_test_suites()
        
        # Format for UI consumption
        suite_info = []
        for suite_name, suite_data in test_suites.items():
            suite_info.append({
                "name": suite_name,
                "display_name": suite_data.get("test_suite_name", suite_name),
                "category": suite_data.get("test_category", "unknown"),
                "description": suite_data.get("description", ""),
                "test_count": len(suite_data.get("test_cases", [])),
                "test_cases": [
                    {
                        "name": test.get("test_name", ""),
                        "description": test.get("description", ""),
                        "priority": test.get("priority", "medium"),
                        "test_type": test.get("test_type", "unit")
                    }
                    for test in suite_data.get("test_cases", [])
                ]
            })
        
        return StandardResponse(
            status="success",
            message="Test suites retrieved",
            data=suite_info
        )
    except Exception as e:
        logger.error(f"Failed to get test suites: {e}")
        return StandardResponse(
            status="error",
            message=f"Failed to get test suites: {str(e)}",
            data=[]
        )

@router.get("/business-logic-validation")
async def get_business_logic_validation_status(admin: dict = Depends(get_current_admin_dependency)):
    """Get business logic validation status and recent results"""
    try:
        conn = await db_manager.get_connection()
        try:
            # Get recent business logic validation results
            recent_validations = await conn.fetch("""
                SELECT 
                    session_id,
                    validation_type,
                    validation_result,
                    quality_score,
                    issues_found,
                    created_at
                FROM business_logic_issues 
                WHERE created_at >= NOW() - INTERVAL '24 hours'
                ORDER BY created_at DESC
                LIMIT 50
            """)
            
            # Calculate summary statistics
            total_validations = len(recent_validations)
            passed_validations = sum(1 for v in recent_validations 
                                   if v['validation_result'] == 'passed')
            avg_quality_score = sum(v['quality_score'] or 0 for v in recent_validations) / max(total_validations, 1)
            
            validation_data = [dict(v) for v in recent_validations]
            
            return StandardResponse(
                status="success",
                message="Business logic validation status retrieved",
                data={
                    "summary": {
                        "total_validations": total_validations,
                        "passed_validations": passed_validations,
                        "success_rate": (passed_validations / max(total_validations, 1)) * 100,
                        "avg_quality_score": round(avg_quality_score, 2)
                    },
                    "recent_validations": validation_data
                }
            )
        finally:
            await db_manager.release_connection(conn)
    except Exception as e:
        logger.error(f"Failed to get business logic validation status: {e}")
        return StandardResponse(
            status="error",
            message=f"Failed to get validation status: {str(e)}",
            data={}
        )

@router.post("/business-logic-validate")
async def trigger_business_logic_validation(request: dict, admin: dict = Depends(get_current_admin_dependency)):
    """Trigger business logic validation for spiritual content"""
    try:
        from monitoring.business_validator import BusinessLogicValidator
        
        validator = BusinessLogicValidator()
        
        # Get validation request parameters
        session_context = request.get("session_context", {})
        # If no session context provided, create a test context
        if not session_context:
            session_context = {
                "spiritual_question": "How can I find inner peace through meditation?",
                "birth_details": {
                    "date": "1990-01-01",
                    "time": "12:00",
                    "location": "Mumbai, India"
                },
                "integration_results": {
                    "rag_knowledge": {
                        "passed": True,
                        "actual": {
                            "knowledge": "Meditation is a sacred practice that connects us with divine consciousness."
                        }
                    }
                }
            }
        
        # Run validation
        validation_result = await validator.validate_session(session_context)
        
        return StandardResponse(
            status="success",
            message="Business logic validation completed",
            data={
                "validation_result": validation_result,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )
    except Exception as e:
        logger.error(f"Business logic validation failed: {e}")
        return StandardResponse(
            status="error",
            message=f"Validation failed: {str(e)}",
            data={}
        )

@router.get("/spiritual-services-status")
async def get_spiritual_services_status():
    """Get spiritual services health and validation status (public endpoint)"""
    try:
        from enhanced_business_logic import SpiritualAvatarEngine, MonetizationOptimizer
        
        # Test SpiritualAvatarEngine
        avatar_status = {"available": False, "error": None}
        try:
            SpiritualAvatarEngine()
            avatar_status["available"] = True
        except Exception as e:
            avatar_status["error"] = str(e)
        
        # Test MonetizationOptimizer
        monetization_status = {"available": False, "error": None}
        try:
            MonetizationOptimizer()
            monetization_status["available"] = True
        except Exception as e:
            monetization_status["error"] = str(e)
        
        # Get recent spiritual service metrics
        try:
            conn = await db_manager.get_connection()
            try:
                # Count recent spiritual sessions
                recent_sessions = await conn.fetchval("""
                    SELECT COUNT(*) FROM sessions 
                    WHERE created_at >= NOW() - INTERVAL '24 hours'
                    AND session_type = 'spiritual_guidance'
                """)
                
                # Count successful validations
                successful_validations = await conn.fetchval("""
                    SELECT COUNT(*) FROM business_logic_issues
                    WHERE created_at >= NOW() - INTERVAL '24 hours'
                    AND validation_result = 'passed'
                """)
                 
            finally:
                await db_manager.release_connection(conn)
        except Exception:
            recent_sessions = 0
            successful_validations = 0
        
        return StandardResponse(
            status="success",
            message="Spiritual services status retrieved",
            data={
                "spiritual_avatar_engine": avatar_status,
                "monetization_optimizer": monetization_status,
                "recent_metrics": {
                    "sessions_24h": recent_sessions,
                    "successful_validations_24h": successful_validations
                },
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
        )
    except Exception as e:
        logger.error(f"Failed to get spiritual services status: {e}")
        return StandardResponse(
            status="error",
            message=f"Failed to get spiritual services status: {str(e)}",
            data={}
        )

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time monitoring updates"""
    await connection_manager.connect(websocket)
    try:
        while True:
            # Check if connection is still active
            if websocket.client_state.name != "CONNECTED":
                logger.info("WebSocket disconnected, ending monitoring")
                break
                
            try:
                # Send heartbeat and system status every 5 seconds
                system_health = await integration_monitor.get_system_health()
                await websocket.send_json({
                    "type": "system_health",
                    "data": system_health,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
            except Exception as send_error:
                # Don't log error if it's just a disconnection
                if "1005" not in str(send_error) and "no status received" not in str(send_error):
                    logger.error(f"Error sending WebSocket message: {send_error}")
                break
            
            # Wait for 5 seconds
            try:
                await asyncio.sleep(5)
            except Exception as sleep_error:
                logger.error(f"Error during WebSocket sleep: {sleep_error}")
                break
            
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"Unexpected WebSocket error: {e}")
    finally:
        connection_manager.disconnect(websocket)

@router.get("/social-media-status")
async def get_social_media_status():
    """Get social media automation status and campaign metrics (public endpoint)"""
    try:
        from social_media_marketing_automation import SocialMediaMarketingEngine
        from validators.social_media_validator import SocialMediaValidator
        
        # Test SocialMediaMarketingEngine availability
        social_engine_status = {"available": False, "error": None}
        try:
            SocialMediaMarketingEngine()
            social_engine_status["available"] = True
        except Exception as e:
            social_engine_status["error"] = str(e)
        
        # Test SocialMediaValidator availability
        validator_status = {"available": False, "error": None}
        try:
            SocialMediaValidator()
            validator_status["available"] = True
        except Exception as e:
            validator_status["error"] = str(e)
        
        # Get recent social media metrics
        try:
            conn = await db_manager.get_connection()
            try:
                # Count recent campaigns
                recent_campaigns = await conn.fetchval("""
                    SELECT COUNT(*) FROM social_campaigns 
                    WHERE created_at >= NOW() - INTERVAL '7 days'
                """)
                
                # Count recent posts
                recent_posts = await conn.fetchval("""
                    SELECT COUNT(*) FROM social_posts 
                    WHERE created_at >= NOW() - INTERVAL '24 hours'
                """)
                
                # Count social media validation logs
                recent_validations = await conn.fetchval("""
                    SELECT COUNT(*) FROM social_media_validation_log
                    WHERE created_at >= NOW() - INTERVAL '24 hours'
                """)
                
                # Get active campaigns
                active_campaigns = await conn.fetchval("""
                    SELECT COUNT(*) FROM social_campaigns 
                    WHERE status = 'active'
                """)
                
            finally:
                await db_manager.release_connection(conn)
        except Exception:
            recent_campaigns = 0
            recent_posts = 0
            recent_validations = 0
            active_campaigns = 0
        
        return StandardResponse(
            status="success",
            message="Social media status retrieved",
            data={
                "social_media_engine": social_engine_status,
                "social_media_validator": validator_status,
                "metrics": {
                    "campaigns_7d": recent_campaigns,
                    "posts_24h": recent_posts,
                    "validations_24h": recent_validations,
                    "active_campaigns": active_campaigns
                },
                "automation_health": {
                    "engine_operational": social_engine_status["available"],
                    "validator_operational": validator_status["available"],
                    "overall_status": "healthy" if social_engine_status["available"] and validator_status["available"] else "degraded"
                },
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
        )
    except Exception as e:
        logger.error(f"Failed to get social media status: {e}")
        return StandardResponse(
            status="error",
            message=f"Failed to get social media status: {str(e)}",
            data={}
        )

@router.get("/social-media-campaigns")
async def get_social_media_campaigns(admin: dict = Depends(get_current_admin_dependency)):
    """Get social media campaign performance and analytics"""
    try:
        conn = await db_manager.get_connection()
        try:
            # Get recent campaigns with performance data
            campaigns = await conn.fetch("""
                SELECT 
                    c.id,
                    c.name,
                    c.platform,
                    c.status,
                    c.budget,
                    c.created_at,
                    c.updated_at,
                    COUNT(p.id) as total_posts,
                    AVG(CAST(p.engagement_metrics->>'likes' AS INTEGER)) as avg_likes,
                    AVG(CAST(p.engagement_metrics->>'comments' AS INTEGER)) as avg_comments,
                    SUM(CAST(p.engagement_metrics->>'reach' AS INTEGER)) as total_reach
                FROM social_campaigns c
                LEFT JOIN social_posts p ON c.id = p.campaign_id
                WHERE c.created_at >= NOW() - INTERVAL '30 days'
                GROUP BY c.id, c.name, c.platform, c.status, c.budget, c.created_at, c.updated_at
                ORDER BY c.created_at DESC
                LIMIT 20
            """)
            
            campaign_data = [dict(campaign) for campaign in campaigns]
            
            # Calculate summary metrics
            total_campaigns = len(campaign_data)
            active_campaigns = sum(1 for c in campaign_data if c['status'] == 'active')
            total_reach = sum(c['total_reach'] or 0 for c in campaign_data)
            
            return StandardResponse(
                status="success",
                message="Social media campaigns retrieved",
                data={
                    "campaigns": campaign_data,
                    "summary": {
                        "total_campaigns": total_campaigns,
                        "active_campaigns": active_campaigns,
                        "total_reach": total_reach,
                        "avg_engagement": sum(c['avg_likes'] or 0 for c in campaign_data) / max(total_campaigns, 1)
                    }
                }
            )
        finally:
            await db_manager.release_connection(conn)
    except Exception as e:
        logger.error(f"Failed to get social media campaigns: {e}")
        return StandardResponse(
            status="error",
            message=f"Failed to get campaigns: {str(e)}",
            data={"campaigns": [], "summary": {}}
        )

@router.post("/social-media-test")
async def test_social_media_automation(admin: dict = Depends(get_current_admin_dependency)):
    """Test social media automation functionality"""
    try:
        from social_media_marketing_automation import SocialMediaMarketingEngine
        from validators.social_media_validator import SocialMediaValidator
        
        test_results = {}
        
        # Test SocialMediaMarketingEngine
        try:
            engine = SocialMediaMarketingEngine()
            
            # Test content generation
            test_content = await engine.generate_content_plan(
                platform="instagram",
                content_type="daily_wisdom",
                target_audience={"age": "25-45", "interests": ["spirituality"]}
            )
            
            test_results["marketing_engine"] = {
                "status": "passed",
                "content_generated": test_content is not None,
                "has_platform_configs": bool(engine.platform_configs)
            }
        except Exception as e:
            test_results["marketing_engine"] = {
                "status": "failed",
                "error": str(e)
            }
        
        # Test SocialMediaValidator
        try:
            validator = SocialMediaValidator()
            
            validation_result = await validator.validate(
                {"platform": "instagram", "content": "Test content"},
                {"status": "posted", "post_id": "test123"},
                {}
            )
            
            test_results["validator"] = {
                "status": "passed",
                "validation_working": validation_result is not None
            }
        except Exception as e:
            test_results["validator"] = {
                "status": "failed", 
                "error": str(e)
            }
        
        # Overall test status
        overall_status = "passed" if all(
            result.get("status") == "passed" 
            for result in test_results.values()
        ) else "failed"
        
        return StandardResponse(
            status="success",
            message="Social media automation test completed",
            data={
                "overall_status": overall_status,
                "test_results": test_results,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )
    except Exception as e:
        logger.error(f"Social media automation test failed: {e}")
        return StandardResponse(
            status="error",
            message=f"Test failed: {str(e)}",
            data={}
        )

@router.get("/live-audio-video-status")
async def get_live_audio_video_status():
    """Get comprehensive live audio/video system status - BUSINESS CRITICAL"""
    try:
        # Check Agora service availability
        agora_status = {"available": False, "error": None}
        try:
            from agora_service import AgoraService
            agora_service = AgoraService()
            agora_status = {
                "available": True,
                "app_id_configured": bool(getattr(agora_service, 'app_id', None)),
                "certificate_configured": bool(getattr(agora_service, 'app_certificate', None))
            }
        except Exception as agora_error:
            agora_status = {"available": False, "error": str(agora_error)}
        
        # Check LiveChat router availability
        livechat_router_status = {"available": False, "error": None}
        try:
            from routers.livechat import livechat_router
            livechat_router_status = {"available": True, "endpoints_count": len(livechat_router.routes)}
        except Exception as router_error:
            livechat_router_status = {"available": False, "error": str(router_error)}
        
        # Check database tables
        database_status = {"available": False, "tables": {}}
        try:
            conn = await db_manager.get_connection()
            
            tables_to_check = ['live_chat_sessions', 'video_chat_sessions', 'video_chat_recordings', 'video_chat_analytics']
            for table in tables_to_check:
                table_exists = await conn.fetchrow('''
                    SELECT table_name FROM information_schema.tables 
                    WHERE table_name = $1 AND table_schema = 'public'
                ''', table)
                database_status["tables"][table] = bool(table_exists)
            
            database_status["available"] = any(database_status["tables"].values())
            await db_manager.release_connection(conn)
            
        except Exception as db_error:
            database_status = {"available": False, "error": str(db_error)}
        
        # Get recent session metrics
        session_metrics = {
            "active_sessions": 0,
            "sessions_24h": 0,
            "total_revenue_24h": 0.0,
            "avg_session_duration": 0.0
        }
        
        try:
            conn = await db_manager.get_connection()
            
            # Active sessions
            if database_status["tables"].get("live_chat_sessions"):
                active_count = await conn.fetchval(
                    "SELECT COUNT(*) FROM live_chat_sessions WHERE status = 'active'"
                )
                session_metrics["active_sessions"] = active_count or 0
            
            # Sessions in last 24 hours
            if database_status["tables"].get("video_chat_sessions"):
                sessions_24h = await conn.fetchval('''
                    SELECT COUNT(*) FROM video_chat_sessions 
                    WHERE start_time >= NOW() - INTERVAL '24 hours'
                ''')
                session_metrics["sessions_24h"] = sessions_24h or 0
                
                # Revenue in last 24 hours
                revenue_24h = await conn.fetchval('''
                    SELECT COALESCE(SUM(cost), 0) FROM video_chat_sessions 
                    WHERE start_time >= NOW() - INTERVAL '24 hours'
                ''')
                session_metrics["total_revenue_24h"] = float(revenue_24h or 0.0)
            
            await db_manager.release_connection(conn)
            
        except Exception as metrics_error:
            print(f"Error fetching session metrics: {metrics_error}")
        
        # Check frontend components availability
        frontend_status = {"available": True, "components": {}}
        frontend_components = ['LiveChat.jsx', 'InteractiveAudioChat.jsx', 'AgoraVideoCall.jsx']
        
        for component in frontend_components:
            try:
                import os
                component_path = os.path.join('frontend', 'src', 'components', component)
                frontend_status["components"][component] = os.path.exists(component_path)
            except Exception:
                frontend_status["components"][component] = False
        
        frontend_status["available"] = any(frontend_status["components"].values())
        
        # Calculate overall system health
        critical_systems = [agora_status["available"], livechat_router_status["available"], database_status["available"]]
        system_health_score = (sum(critical_systems) / len(critical_systems)) * 100
        
        if system_health_score >= 90:
            overall_status = "healthy"
        elif system_health_score >= 70:
            overall_status = "degraded"
        else:
            overall_status = "critical"
        
        return {
            "success": True,
            "data": {
                "overall_status": overall_status,
                "system_health_score": system_health_score,
                "agora_service": agora_status,
                "livechat_router": livechat_router_status,
                "database": database_status,
                "frontend_components": frontend_status,
                "session_metrics": session_metrics,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to get live audio/video status: {str(e)}",
            "data": {
                "overall_status": "critical",
                "system_health_score": 0,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        }

@router.get("/live-audio-video-sessions")
async def get_live_audio_video_sessions():
    """Get recent live audio/video sessions data"""
    try:
        conn = await db_manager.get_connection()
        
        # Get recent sessions
        sessions = []
        try:
            sessions_data = await conn.fetch('''
                SELECT session_id, user_id, service_type, status, start_time, end_time, 
                       duration, cost, agora_channel
                FROM video_chat_sessions 
                WHERE start_time >= NOW() - INTERVAL '7 days'
                ORDER BY start_time DESC
                LIMIT 20
            ''')
            
            for session in sessions_data:
                sessions.append({
                    "session_id": session['session_id'],
                    "user_id": session['user_id'],
                    "service_type": session['service_type'],
                    "status": session['status'],
                    "start_time": session['start_time'].isoformat() if session['start_time'] else None,
                    "end_time": session['end_time'].isoformat() if session['end_time'] else None,
                    "duration": session['duration'],
                    "cost": float(session['cost']) if session['cost'] else 0.0,
                    "agora_channel": session['agora_channel']
                })
        except Exception as sessions_error:
            print(f"Error fetching sessions: {sessions_error}")
        
        await db_manager.release_connection(conn)
        
        return {
            "success": True,
            "data": {
                "recent_sessions": sessions,
                "total_sessions": len(sessions)
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to get live audio/video sessions: {str(e)}",
            "data": {"recent_sessions": [], "total_sessions": 0}
        }

@router.post("/live-audio-video-test")
async def test_live_audio_video_system():
    """Test live audio/video system functionality"""
    try:
        test_results = {}
        
        # Test 1: Agora service
        try:
            from agora_service import AgoraService
            agora_service = AgoraService()
            
            # Test token generation
            test_channel = f"test_channel_{uuid.uuid4()}"
            token_result = await agora_service.generate_token(
                channel_name=test_channel,
                uid=str(uuid.uuid4()),
                role="publisher"
            )
            
            test_results["agora_service"] = {
                "status": "passed" if token_result and token_result.get("token") else "failed",
                "token_generated": bool(token_result.get("token") if token_result else False),
                "test_details": "Token generation test"
            }
            
        except Exception as agora_error:
            test_results["agora_service"] = {
                "status": "failed",
                "error": str(agora_error),
                "test_details": "Agora service initialization test"
            }
        
        # Test 2: Database operations
        try:
            conn = await db_manager.get_connection()
            
            # Test session creation
            session_id = str(uuid.uuid4())
            await conn.execute('''
                INSERT INTO live_chat_sessions (session_id, user_id, agora_token, status, created_at)
                VALUES ($1, $2, $3, $4, $5)
            ''', session_id, "test_user", "test_token", "active", datetime.now(timezone.utc))
            
            # Verify and cleanup
            session = await conn.fetchrow(
                "SELECT status FROM live_chat_sessions WHERE session_id = $1", session_id
            )
            await conn.execute("DELETE FROM live_chat_sessions WHERE session_id = $1", session_id)
            await db_manager.release_connection(conn)
            
            test_results["database"] = {
                "status": "passed" if session else "failed",
                "session_created": bool(session),
                "test_details": "Session creation and cleanup test"
            }
            
        except Exception as db_error:
            test_results["database"] = {
                "status": "failed",
                "error": str(db_error),
                "test_details": "Database operations test"
            }
        
        # Test 3: API endpoints
        try:
            # Test internal endpoint availability
            livechat_available = True
            try:
                from routers.livechat import livechat_router
            except ImportError:
                livechat_available = False
            
            test_results["api_endpoints"] = {
                "status": "passed" if livechat_available else "failed",
                "livechat_router_available": livechat_available,
                "test_details": "API router availability test"
            }
            
        except Exception as api_error:
            test_results["api_endpoints"] = {
                "status": "failed",
                "error": str(api_error),
                "test_details": "API endpoints test"
            }
        
        # Calculate overall test result
        passed_tests = sum(1 for result in test_results.values() if result.get("status") == "passed")
        total_tests = len(test_results)
        test_success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        overall_status = "passed" if test_success_rate >= 70 else "failed"
        
        return StandardResponse(
            status="success",
            message="Live audio/video system test completed",
            data={
                "overall_status": overall_status,
                "test_success_rate": test_success_rate,
                "passed_tests": passed_tests,
                "total_tests": total_tests,
                "test_results": test_results,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )
        
    except Exception as e:
        return StandardResponse(
            status="error",
            message=f"Failed to test live audio/video system: {str(e)}",
            data={
                "overall_status": "failed",
                "test_success_rate": 0,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )

# Export for use in other modules
__all__ = ["monitoring_dashboard", "router", "connection_manager"]