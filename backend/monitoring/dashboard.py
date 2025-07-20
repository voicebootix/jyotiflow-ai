"""
📊 MONITORING DASHBOARD - Real-time integration monitoring for JyotiFlow admin
Integrates seamlessly with existing admin dashboard UI.
"""
import json
import asyncio
from datetime import datetime, timezone
from typing import Dict, List

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from db import db_manager
import logging
logger = logging.getLogger(__name__)
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

# Import proper admin authentication
try:
    from deps import get_current_admin_dependency
except ImportError:
    # If deps module is not available, create a secure fallback
    from fastapi import Depends
    
    security = HTTPBearer()
    
    async def verify_bearer_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
        """Verify bearer token and return admin user"""
        # In a real implementation, you would verify the token here
        # For now, we just reject all requests
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin authentication required. Please configure proper authentication.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Alias for consistency with the imported version
    get_current_admin_dependency = verify_bearer_token

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
                return {
                    "success": True,
                    "test_session_id": test_session_id,
                    "message": "Validation test initiated"
                }
                
            elif test_type == "social_media":
                # Test social media credentials
                social_validator = integration_monitor.validators.get("social_media")
                if social_validator:
                    test_result = await social_validator.test_all_platforms()
                    return test_result
                else:
                    return {"success": False, "error": "Social media validator not found"}
                    
            else:
                return {"success": False, "error": f"Unknown test type: {test_type}"}
                
        except Exception as e:
            logger.error(f"❌ Failed to trigger validation test: {e}")
            return {"success": False, "error": str(e)}
    
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
async def get_dashboard(admin=Depends(get_current_admin_dependency)):
    """Get monitoring dashboard data for admin interface"""
    dashboard_data = await monitoring_dashboard.get_dashboard_data()
    return StandardResponse(
        status="success",
        message="Dashboard data retrieved",
        data=dashboard_data
    )

@router.get("/session/{session_id}")
async def get_session_validation(session_id: str, admin=Depends(get_current_admin_dependency)):
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
async def get_integration_health(integration_point: str, admin=Depends(get_current_admin_dependency)):
    """Get detailed health metrics for a specific integration"""
    health_details = await monitoring_dashboard.get_integration_health_details(integration_point)
    
    return StandardResponse(
        status="success",
        message="Integration health details retrieved",
        data=health_details
    )

@router.post("/test/{test_type}")
async def trigger_test(test_type: str, admin=Depends(get_current_admin_dependency)):
    """Trigger a validation test"""
    test_result = await monitoring_dashboard.trigger_validation_test(test_type)
    
    return StandardResponse(
        status="success" if test_result.get("success", False) else "error",
        message=test_result.get("message", "Test triggered"),
        data=test_result
    )

# Testing infrastructure endpoints
@router.get("/test-status")
async def get_test_status():
    """Get current test execution status (public endpoint)"""
    try:
        # Mock test status data - will be replaced with real implementation
        return StandardResponse(
            status="success",
            message="Test status retrieved",
            data={
                "last_execution": "2024-01-15T10:30:00Z",
                "total_tests": 42,
                "passed_tests": 38,
                "failed_tests": 4,
                "test_coverage": 87.5,
                "execution_time": 35,
                "status": "passed",
                "auto_fixes_applied": 2
            }
        )
    except Exception as e:
        return StandardResponse(
            status="error",
            message=f"Failed to get test status: {str(e)}",
            data={}
        )

@router.get("/test-sessions")
async def get_test_sessions(admin=Depends(get_current_admin_dependency)):
    """Get test execution sessions history"""
    try:
        # Mock test sessions data - will be replaced with real database queries
        return StandardResponse(
            status="success",
            message="Test sessions retrieved",
            data=[
                {
                    "session_id": "test-001",
                    "test_type": "integration",
                    "status": "passed",
                    "started_at": "2024-01-15T10:30:00Z",
                    "completed_at": "2024-01-15T10:32:15Z",
                    "execution_time_seconds": 135,
                    "total_tests": 25,
                    "passed_tests": 25,
                    "failed_tests": 0,
                    "coverage_percentage": 89.2
                },
                {
                    "session_id": "test-002", 
                    "test_type": "unit",
                    "status": "partial",
                    "started_at": "2024-01-15T09:15:00Z",
                    "completed_at": "2024-01-15T09:16:45Z",
                    "execution_time_seconds": 105,
                    "total_tests": 47,
                    "passed_tests": 43,
                    "failed_tests": 4,
                    "coverage_percentage": 85.1
                }
            ]
        )
    except Exception as e:
        return StandardResponse(
            status="error",
            message=f"Failed to get test sessions: {str(e)}",
            data=[]
        )

@router.get("/test-metrics")
async def get_test_metrics(admin=Depends(get_current_admin_dependency)):
    """Get test execution metrics and statistics"""
    try:
        # Mock test metrics - will be replaced with real calculations
        return StandardResponse(
            status="success", 
            message="Test metrics retrieved",
            data={
                "total_sessions": 15,
                "success_rate": 87.5,
                "avg_execution_time": 120,
                "coverage_trend": 2.3,
                "auto_fixes_applied": 8
            }
        )
    except Exception as e:
        return StandardResponse(
            status="error",
            message=f"Failed to get test metrics: {str(e)}",
            data={}
        )

@router.post("/test-execute")
async def execute_test(request: dict, admin=Depends(get_current_admin_dependency)):
    """Execute a test suite"""
    import time
    try:
        test_type = request.get("test_type", "unit")
        environment = request.get("environment", "production")
        triggered_by = request.get("triggered_by", "manual")
        
        # Mock test execution start - will be replaced with real test runner
        return StandardResponse(
            status="success",
            message=f"Test execution started: {test_type}",
            data={
                "session_id": f"test-{test_type}-{int(time.time())}",
                "test_type": test_type,
                "environment": environment,
                "triggered_by": triggered_by,
                "status": "running",
                "estimated_completion": "2-5 minutes"
            }
        )
    except Exception as e:
        return StandardResponse(
            status="error",
            message=f"Failed to execute test: {str(e)}",
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

# Export for use in other modules
__all__ = ["monitoring_dashboard", "router", "connection_manager"]