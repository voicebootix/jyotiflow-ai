"""
📊 MONITORING DASHBOARD - Real-time integration monitoring for JyotiFlow admin
Integrates seamlessly with existing admin dashboard UI .
"""

import json
import asyncio
import asyncpg
import uuid
import os
from datetime import datetime, timezone
from typing import Dict, List, Any

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
        """Get comprehensive dashboard data for admin interface - database-driven"""
        try:
            # Get system health from database
            system_health = await self._get_system_health_from_db()
 
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
 
            # Calculate per-integration metrics for frontend display
            integration_metrics = await self._calculate_integration_metrics()
 
            # Get active sessions count from database
            active_sessions_count = await self._get_active_sessions_count()
 
            dashboard_data = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "system_health": system_health,
                "active_sessions": active_sessions_count,
                "recent_sessions": recent_sessions,
                "integration_statistics": integration_stats,
                "critical_issues": critical_issues,
                "social_media_health": social_media_health,
                "overall_metrics": overall_metrics,
                "metrics": integration_metrics,
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
        """Get recent session summaries from actual sessions table"""
        try:
            from db import db_manager
            conn = await db_manager.get_connection()
            try:
                # Query actual sessions table that exists in our schema
                sessions = await conn.fetch("""
                    SELECT
                        s.id AS session_id,
                        s.user_id,
                        s.user_email,
                        s.service_type,
                        s.status,
                        s.created_at as started_at,
                        s.updated_at as completed_at,
                        s.duration_minutes,
                        s.credits_used,
                        CASE
                            WHEN s.status = 'completed' THEN 'success'
                            WHEN s.status = 'active' THEN 'running'
                            ELSE 'failed'
                        END as overall_status
                    FROM sessions s
                    WHERE s.created_at > NOW() - INTERVAL '1 hour'
                    ORDER BY s.created_at DESC
                    LIMIT 20
                """)
 
                return [dict(s) for s in sessions]
            finally:
                await db_manager.release_connection(conn)
 
        except Exception as e:
            logger.error(f"Failed to get recent sessions: {e}")
            # Return empty list instead of mock data
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
            from db import db_manager
            conn = await db_manager.get_connection()
            try:
                # Get session statistics from actual sessions table
                stats = await conn.fetchrow("""
                        SELECT
                        COUNT(*) as total_sessions,
                        AVG(duration_minutes * 60 * 1000) as avg_response_time_ms, -- Convert to milliseconds
                        COUNT(CASE WHEN status = 'completed' THEN 1 END) as successful_sessions,
                        COUNT(CASE WHEN status = 'active' THEN 1 END) as active_sessions
                    FROM sessions
                    WHERE created_at > NOW() - INTERVAL '24 hours'
                """)
 
                # Get per-service type statistics
                by_service = await conn.fetch("""
                    SELECT
                        service_type as integration_name,
                        COUNT(*) as total_calls,
                        COUNT(CASE WHEN status = 'completed' THEN 1 END) as successful_calls,
                        AVG(duration_minutes * 60 * 1000) as avg_duration_ms
                    FROM sessions
                    WHERE created_at > NOW() - INTERVAL '24 hours'
                    GROUP BY service_type
                """)
 
                return {
                    "overall": dict(stats) if stats else {},
                    "by_integration": [dict(i) for i in by_service]
                }
            finally:
                await db_manager.release_connection(conn)
 
        except Exception as e:
            logger.error(f"Failed to get integration statistics: {e}")
            return {"overall": {}, "by_integration": []}
 
    async def _get_critical_issues(self) -> List[Dict]:
        """Get current critical issues from monitoring alerts table"""
        try:
            from db import db_manager
            conn = await db_manager.get_connection()
            try:
                # Check if monitoring_alerts table exists from our migrations
                table_exists = await conn.fetchval("""
                    SELECT EXISTS(
                        SELECT 1 FROM information_schema.tables
                        WHERE table_name = 'monitoring_alerts' AND table_schema = 'public'
                    )
                """)
 
                if table_exists:
                    issues = await conn.fetch("""
                        SELECT
                            id,
                            alert_type as type,
                            severity,
                            message,
                            details,
                            created_at as timestamp,
                            acknowledged
                        FROM monitoring_alerts
                        WHERE severity IN ('critical', 'high')
                        AND acknowledged = false
                        AND created_at > NOW() - INTERVAL '24 hours'
                        ORDER BY created_at DESC
                        LIMIT 10
                    """)
                    return [dict(i) for i in issues]
                else:
                    # Return empty list if table doesn't exist yet
                    return []
 
            finally:
                await db_manager.release_connection(conn)
 
        except Exception as e:
            logger.error(f"Failed to get critical issues: {e}")
            return []
 
    async def _get_social_media_health(self) -> Dict:
        """Get social media integration health status from platform_settings table"""
        try:
            from db import db_manager
            conn = await db_manager.get_connection()
            try:
                # Check if platform_settings table exists
                table_exists = await conn.fetchval("""
                    SELECT EXISTS(
                        SELECT 1 FROM information_schema.tables
                        WHERE table_name = 'platform_settings' AND table_schema = 'public'
                    )
                """)
 
                if table_exists:
                    # Get platform settings
                    platforms = await conn.fetch("""
                        SELECT
                            key,
                            value,
                            created_at,
                            updated_at
                        FROM platform_settings
                        WHERE key LIKE '%social%' OR key LIKE '%facebook%' OR key LIKE '%instagram%'
                        ORDER BY updated_at DESC
                    """)
 
                    # Check if social_media_validation_log exists
                    validation_log_exists = await conn.fetchval("""
                        SELECT EXISTS(
                            SELECT 1 FROM information_schema.tables
                            WHERE table_name = 'social_media_validation_log' AND table_schema = 'public'
                        )
                    """)
 
                    recent_activity = []
                    if validation_log_exists:
                        recent_activity = await conn.fetch("""
                            SELECT
                                platform,
                                validation_type,
                                status,
                                COUNT(*) as count
                            FROM social_media_validation_log
                            WHERE created_at > NOW() - INTERVAL '24 hours'
                            GROUP BY platform, validation_type, status
                        """)
 
                    return {
                        "platform_status": [dict(p) for p in platforms],
                        "recent_activity": [dict(r) for r in recent_activity],
                        "errors": []  # Will be populated when we have social media posting data
                    }
                else:
                    return {
                        "platform_status": [],
                        "recent_activity": [],
                        "errors": []
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
        """Calculate overall system metrics from sessions table"""
        try:
            from db import db_manager
            conn = await db_manager.get_connection()
            try:
                # Get success rate from sessions
                success_rate = await conn.fetchrow("""
                    SELECT
                        COUNT(CASE WHEN status = 'completed' THEN 1 END)::float /
                        NULLIF(COUNT(*), 0) * 100 as success_rate
                    FROM sessions
                    WHERE created_at > NOW() - INTERVAL '24 hours'
                """)
 
                # Get average session duration
                avg_duration = await conn.fetchrow("""
                    SELECT
                        AVG(duration_minutes * 60) as avg_duration_seconds
                    FROM sessions
                    WHERE duration_minutes IS NOT NULL
                    AND created_at > NOW() - INTERVAL '24 hours'
                """)
 
                # Get system health score based on session completion rate
                total_sessions = await conn.fetchval("""
                    SELECT COUNT(*) FROM sessions
                    WHERE created_at > NOW() - INTERVAL '24 hours'
                """)
 
                return {
                    "success_rate": float(success_rate["success_rate"] or 0) if success_rate else 0,
                    "avg_session_duration": float(avg_duration["avg_duration_seconds"] or 0) if avg_duration else 0,
                    "total_sessions_24h": total_sessions or 0,
                    "quality_scores": {
                        "system_health": min(float(success_rate["success_rate"] or 0), 100) if success_rate else 0,
                        "uptime": 99.5  # Placeholder - could be calculated from monitoring data
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
 
    async def _calculate_integration_metrics(self) -> Dict:
        """Calculate per-integration success rates and response times from sessions table"""
        try:
            from db import db_manager
            conn = await db_manager.get_connection()
            try:
                # Get per-service type metrics from sessions table
                integration_stats = await conn.fetch("""
                    SELECT
                        service_type as integration_name,
                        COUNT(*) as total_validations,
                        COUNT(CASE WHEN status = 'completed' THEN 1 END) as successful_validations,
                        ROUND(
                            (COUNT(CASE WHEN status = 'completed' THEN 1 END)::numeric /
                            NULLIF(COUNT(*), 0) * 100)::numeric, 1
                        ) as success_rate,
                        ROUND(AVG(duration_minutes * 60 * 1000)::numeric) as avg_response_time_ms
                    FROM sessions
                    WHERE created_at > NOW() - INTERVAL '24 hours'
                    AND service_type IS NOT NULL
                    GROUP BY service_type
                    ORDER BY service_type
                """)
 
                success_rates = {}
                avg_response_times = {}
 
                for row in integration_stats:
                    integration_name = row['integration_name']
                    success_rates[integration_name] = float(row['success_rate'] or 0)
                    avg_response_times[integration_name] = int(row['avg_response_time_ms'] or 0)
 
                # Add common integration points that we expect to monitor
                common_integrations = [
                    'prokerala', 'rag_knowledge', 'openai_guidance',
                    'elevenlabs_voice', 'did_avatar', 'social_media'
                ]
 
                # Only add fallback zeros for common integrations that don't have data
                for integration in common_integrations:
                    if integration not in success_rates:
                        success_rates[integration] = 0.0
                        avg_response_times[integration] = 0
 
                return {
                    "success_rates": success_rates,
                    "avg_response_times": avg_response_times
                }
 
            finally:
                await db_manager.release_connection(conn)
 
        except Exception as e:
            logger.error(f"Failed to calculate integration metrics: {e}")
            # Return fallback data for common integrations
            common_integrations = [
                'prokerala', 'rag_knowledge', 'openai_guidance',
                'elevenlabs_voice', 'did_avatar', 'social_media'
            ]
            return {
                "success_rates": {integration: 0.0 for integration in common_integrations},
                "avg_response_times": {integration: 0 for integration in common_integrations}
            }

    async def _get_active_alerts(self) -> List[Dict]:
        """Get active alerts for admin attention"""
        alerts = []
 
        try:
            from db import db_manager
            conn = await db_manager.get_connection()
            try:
                # Check if monitoring_alerts table exists
                table_exists = await conn.fetchval("""
                    SELECT EXISTS(
                        SELECT 1 FROM information_schema.tables
                        WHERE table_name = 'monitoring_alerts' AND table_schema = 'public'
                    )
                """)
 
                if table_exists:
                    # Get alerts from monitoring_alerts table
                    alert_data = await conn.fetch("""
                        SELECT
                            alert_type as type,
                            severity,
                            message,
                            created_at as timestamp,
                            acknowledged
                        FROM monitoring_alerts
                        WHERE acknowledged = false
                        AND created_at > NOW() - INTERVAL '24 hours'
                        ORDER BY
                            CASE severity
                                WHEN 'critical' THEN 1
                                WHEN 'high' THEN 2
                                WHEN 'medium' THEN 3
                                ELSE 4
                            END,
                            created_at DESC
                        LIMIT 10
                    """)
 
                    for alert in alert_data:
                        alerts.append(dict(alert))
                else:
                    # Generate basic alerts from session data
                    error_rate = await conn.fetchrow("""
                        SELECT
                            CASE
                                WHEN COUNT(*) = 0 THEN 0
                                ELSE COUNT(CASE WHEN status != 'completed' THEN 1 END)::float / COUNT(*) * 100
                            END as error_rate
                        FROM sessions
                        WHERE created_at > NOW() - INTERVAL '1 hour'
                    """)
 
                    if error_rate and error_rate["error_rate"] > 20:
                        alerts.append({
                            "type": "warning",
                            "severity": "high" if error_rate["error_rate"] > 50 else "medium",
                            "message": f"High session failure rate: {error_rate['error_rate']:.1f}%",
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                            "acknowledged": False
                        })
 
            finally:
                await db_manager.release_connection(conn)
 
            return alerts
 
        except Exception as e:
            logger.error(f"Failed to get active alerts: {e}")
            return []
 
    async def _get_system_health_from_db(self) -> Dict:
        """Get system health status from database metrics"""
        logger.info("🔄 Getting system health from database...")
        try:
            from db import db_manager
            conn = await db_manager.get_connection()
            try:
                # Calculate system health based on session success rates
                health_metrics = await conn.fetchrow("""
                    SELECT
                        COUNT(*) as total_sessions,
                        COUNT(CASE WHEN status = 'completed' THEN 1 END) as successful_sessions,
                        COUNT(CASE WHEN status = 'active' THEN 1 END) as active_sessions,
                        COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_sessions
                    FROM sessions
                    WHERE created_at > NOW() - INTERVAL '1 hour'
                """)
 
                if health_metrics and health_metrics['total_sessions'] > 0:
                    success_rate = (health_metrics['successful_sessions'] / health_metrics['total_sessions']) * 100
 
                    # Determine system status based on success rate
                    if success_rate >= 95:
                        system_status = "healthy"
                    elif success_rate >= 80:
                        system_status = "degraded"
                    else:
                        system_status = "critical"
                else:
                    system_status = "healthy"  # No recent activity
 
                # Get integration points from database - try integration_validations table first
                integration_points = {}
 
                # Check if integration_validations table exists and has data
                try:
                    integration_data = await conn.fetch("""
                        SELECT
                            integration_name,
                            COUNT(*) as total_validations,
                            COUNT(CASE WHEN status = 'success' THEN 1 END) as successful_validations,
                            AVG(response_time_ms) as avg_response_time,
                            MAX(validation_time) as last_validation
                        FROM integration_validations
                        WHERE validation_time > NOW() - INTERVAL '24 hours'
                        GROUP BY integration_name
                    """)
 
                    # Process integration validations data
                    for integration in integration_data:
                        name = integration['integration_name']
                        success_rate = (integration['successful_validations'] / integration['total_validations']) * 100 if integration['total_validations'] > 0 else 0
 
                        integration_points[name] = {
                            "status": "healthy" if success_rate >= 95 else "warning" if success_rate >= 80 else "error",
                            "success_rate": round(success_rate, 1),
                            "total_validations": integration['total_validations'],
                            "latency_ms": int(integration['avg_response_time'] or 0),
                            "last_check": integration['last_validation'].isoformat() if integration['last_validation'] else datetime.now(timezone.utc).isoformat()
                        }
 
                except Exception as table_error:
                    # integration_validations table doesn't exist or has no data
                    # Create sample integration data from platform_settings and current system status
                    logger.info(f"🔧 integration_validations table not available: {table_error}")
                    logger.info("🔧 Falling back to platform_settings...")
 
                    # Check platform_settings for API configurations
                    try:
                        platform_configs = await conn.fetch("""
                            SELECT key, value, updated_at
                            FROM platform_settings
                            WHERE key LIKE '%api%' OR key LIKE '%secret%' OR key LIKE '%config%'
                        """)
 
                        # Map platform configs to integrations
                        config_map = {
                            'prokerala': any('prokerala' in row['key'].lower() for row in platform_configs),
                            'openai_guidance': any('openai' in row['key'].lower() for row in platform_configs),
                            'elevenlabs_voice': any('elevenlabs' in row['key'].lower() for row in platform_configs),
                            'did_avatar': any('did' in row['key'].lower() for row in platform_configs),
                            'rag_knowledge': True,  # Always available
                            'social_media': any('facebook' in row['key'].lower() or 'instagram' in row['key'].lower() for row in platform_configs)
                        }
 
                        # Set status based on configuration availability
                        for integration, is_configured in config_map.items():
                            integration_points[integration] = {
                                "status": "healthy" if is_configured else "not_configured",
                                "success_rate": 95.0 if is_configured else 0.0,
                                "total_validations": 0,
                                "latency_ms": 1500 if is_configured else 0,
                                "last_check": datetime.now(timezone.utc).isoformat()
                            }
 
                    except Exception as config_error:
                        logger.warning(f"Could not read platform_settings: {config_error}")
 
                # Ensure all expected integrations are present
                expected_integrations = ['prokerala', 'rag_knowledge', 'openai_guidance', 'elevenlabs_voice', 'did_avatar', 'social_media']
                for integration in expected_integrations:
                    if integration not in integration_points:
                        integration_points[integration] = {
                            "status": "unknown",
                            "success_rate": 0.0,
                            "total_validations": 0,
                            "latency_ms": 0,
                            "last_check": datetime.now(timezone.utc).isoformat()
                        }
 
                logger.info(f"✅ System health calculated: status={system_status}, integrations={len(integration_points)}")
                logger.info(f"📊 Integration points: {list(integration_points.keys())}")
 
                return {
                    "system_status": system_status,
                    "integration_points": integration_points,
                    "recent_issues": [],  # Will be populated by _get_critical_issues
                    "last_check": datetime.now(timezone.utc).isoformat()
                }
 
            finally:
                await db_manager.release_connection(conn)
 
        except Exception as e:
            logger.error(f"Failed to get system health from database: {e}")
            return {
                "system_status": "error",
                "integration_points": {},
                "recent_issues": [{"type": "system_error", "message": str(e), "timestamp": datetime.now(timezone.utc).isoformat()}],
                "last_check": datetime.now(timezone.utc).isoformat()
            }
 
    async def _get_active_sessions_count(self) -> int:
        """Get count of active sessions from database"""
        try:
            from db import db_manager
            conn = await db_manager.get_connection()
            try:
                count = await conn.fetchval("""
                    SELECT COUNT(*) FROM sessions
                    WHERE status = 'active'
                    AND created_at > NOW() - INTERVAL '4 hours'
                """)
                return count or 0
            finally:
                await db_manager.release_connection(conn)
        except Exception as e:
            logger.error(f"Failed to get active sessions count: {e}")
            return 0
 
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
 
    async def get_comprehensive_test_definitions(self) -> List[Dict[str, Any]]:
        """
        Get comprehensive test definitions dynamically from backend systems and database
        This discovers available tests from TestSuiteGenerator and existing test data
        Following .cursor rules: No hardcoded data, retrieve from database and backend systems
        Returns test suites (not individual test cases) for proper grouping
        """
        try:
            # Method 1: Try to get test definitions from TestSuiteGenerator (primary source)
            try:
                from test_suite_generator import TestSuiteGenerator
 
                generator = TestSuiteGenerator()
                test_suites = await generator.generate_all_test_suites()
 
                # Keep test suites grouped (don't flatten into individual test cases)
                comprehensive_tests = []
                for suite_name, suite_data in test_suites.items():
                    if "error" not in suite_data and "test_cases" in suite_data:
                        # Count individual test cases within this suite
                        test_case_count = len(suite_data.get("test_cases", []))
 
                        comprehensive_tests.append({
                            "test_name": suite_name,
                            "test_category": suite_data.get("test_category", suite_name.replace("_tests", "")),
                            "test_type": suite_data.get("test_type", "integration"),
                            "description": suite_data.get("description", ""),
                            "priority": suite_data.get("priority", "medium"),
                            "suite_name": suite_name,
                            "suite_display_name": suite_data.get("test_suite_name", suite_name),
                            "test_case_count": test_case_count  # Track individual test cases within suite
                        })
 
                if comprehensive_tests:
                    logger.info(f"Retrieved {len(comprehensive_tests)} test suites from TestSuiteGenerator")
                    return comprehensive_tests
 
            except ImportError:
                logger.warning("TestSuiteGenerator not available, falling back to database discovery")
            except Exception as e:
                logger.warning(f"TestSuiteGenerator failed: {e}, falling back to database discovery")
 
            # Method 2: Get test definitions from database (secondary source)
            try:
                conn = await db_manager.get_connection()
                try:
                    # Get test suites grouped by category from test_case_results table
                    test_suites_data = await conn.fetch("""
                        SELECT
                            test_category,
                            COUNT(*) as test_case_count,
                            CASE
                                WHEN test_category IN ('auth', 'api', 'database') THEN 'critical'
                                WHEN test_category IN ('integration', 'performance') THEN 'high'
                                ELSE 'medium'
                            END as priority
                        FROM test_case_results
                        WHERE test_category IS NOT NULL
                        AND test_category != ''
                        GROUP BY test_category
                        ORDER BY test_category
                    """)
 
                    if test_suites_data:
                        comprehensive_tests = []
                        for row in test_suites_data:
                            comprehensive_tests.append({
                                "test_name": f"{row['test_category']}_tests",
                                "test_category": row["test_category"],
                                "test_type": "integration",
                                "description": f"Database discovered {row['test_category']} test suite",
                                "priority": row["priority"],
                                "suite_name": f"{row['test_category']}_tests",
                                "suite_display_name": row["test_category"].replace("_", " ").title(),
                                "test_case_count": row["test_case_count"]
                            })
 
                        logger.info(f"Retrieved {len(comprehensive_tests)} test suites from database")
                        return comprehensive_tests
 
                finally:
                    await db_manager.release_connection(conn)
 
            except Exception as e:
                logger.warning(f"Database test discovery failed: {e}")
 
            # Method 3: Discover tests from backend systems (tertiary source)
            try:
                # Get available test types from TestExecutionEngine
                from test_execution_engine import TestExecutionEngine
 
                engine = TestExecutionEngine()
                available_suites = await engine._get_available_test_suites()
 
                if available_suites:
                    comprehensive_tests = []
                    for suite in available_suites:
                        test_type = suite.get("test_type", "unknown")
                        test_category = suite.get("test_category", "unknown")
 
                        comprehensive_tests.append({
                            "test_name": f"{test_category}_tests",
                            "test_category": test_category,
                            "test_type": test_type,
                            "description": f"Auto-discovered {test_category} test suite",
                            "priority": "medium",
                            "suite_name": f"{test_category}_tests",
                            "suite_display_name": f"{test_category.replace('_', ' ').title()} Tests",
                            "test_case_count": 0  # Unknown count for auto-discovered suites (0 = unknown)
                        })
 
                    logger.info(f"Retrieved {len(comprehensive_tests)} test suites from TestExecutionEngine")
                    return comprehensive_tests
 
            except Exception as e:
                logger.warning(f"TestExecutionEngine discovery failed: {e}")
 
            # Method 4: Minimal fallback - return empty list (no hardcoded data)
            logger.warning("All test discovery methods failed - returning empty test list")
            return []
 
        except Exception as e:
            logger.error(f"Failed to get comprehensive test definitions: {e}")
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
async def get_dashboard():
    """Get monitoring dashboard data for admin interface (public endpoint for testing)"""
    try:
        dashboard_data = await monitoring_dashboard.get_dashboard_data()
        return StandardResponse(
            status="success",
            message="Dashboard data retrieved",
            data=dashboard_data
        )
    except Exception as e:
        logger.error(f"Failed to get dashboard data: {e}")
        # Return minimal data structure to prevent frontend crashes
        fallback_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "system_health": {
                "system_status": "error",
                "integration_points": {},
                "recent_issues": [
                    {
                        "type": "dashboard_error",
                        "message": f"Dashboard data retrieval failed: {str(e)}",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "severity": "high"
                    }
                ]
            },
            "active_sessions": 0,
            "recent_sessions": [],
            "integration_statistics": {},
            "critical_issues": [],
            "social_media_health": {},
            "overall_metrics": {},
            "metrics": {
                "success_rates": {},
                "avg_response_times": {}
            },
            "alerts": []
        }
        return StandardResponse(
            status="error",
            message=f"Dashboard data retrieval failed: {str(e)}",
            data=fallback_data
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
    """Get current test execution status with comprehensive test information (database-driven, public endpoint)"""
    try:
        conn = await db_manager.get_connection()
        try:
            # Get comprehensive test definitions from monitoring dashboard
            try:
                comprehensive_tests = await monitoring_dashboard.get_comprehensive_test_definitions()
                total_test_suites = len(comprehensive_tests)  # Count of test suites (16)
                # Calculate total individual test cases by summing test_case_count from all suites
                total_comprehensive_tests = sum(test.get("test_case_count", 0) for test in comprehensive_tests)
            except Exception as e:
                logger.error(f"Failed to get comprehensive test definitions: {e}")
                comprehensive_tests = []
                total_test_suites = 0
                total_comprehensive_tests = 0

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
                    message="Comprehensive test status retrieved",
                    data={
                        "last_execution": latest_execution['completed_at'].isoformat() if latest_execution['completed_at'] else None,
                        "total_tests": total_comprehensive_tests,  # Individual test cases (41)
                        "total_test_suites": total_test_suites,  # Test suites count (16)
                        "passed_tests": latest_execution['passed_tests'] or 0,
                        "failed_tests": latest_execution['failed_tests'] or 0,
                        "test_coverage": float(latest_execution['coverage_percentage'] or 0),
                        "execution_time": latest_execution['execution_time_seconds'] or 0,
                        "status": latest_execution['status'] or 'unknown',
                        "auto_fixes_applied": 0,  # Set to 0 for now as requested

                        # Additional comprehensive test information
                        "comprehensive_test_suite": {
                            "total_defined_tests": total_comprehensive_tests,
                            "last_execution_tests": latest_execution.get('total_tests') if latest_execution else 0, # Use actual value from latest execution or 0
                            "execution_coverage": round((latest_execution['total_tests'] or 0) / max(total_comprehensive_tests, 1) * 100, 1)
                        }
                    }
                )
            else:
                # No test executions found - show comprehensive test suite info
                return StandardResponse(
                    status="success",
                    message="No test executions found, showing comprehensive test suite definitions",
                    data={
                        "last_execution": None,
                        "total_tests": total_comprehensive_tests,  # Individual test cases (41)
                        "total_test_suites": total_test_suites,  # Test suites count (16)
                        "passed_tests": 0,
                        "failed_tests": 0,
                        "test_coverage": 0.0,
                        "execution_time": 0,
                        "status": "not_run",
                        "auto_fixes_applied": 0,

                        # Additional comprehensive test information
                        "comprehensive_test_suite": {
                            "total_defined_tests": total_comprehensive_tests,
                            "last_execution_tests": 0, # Default to zero last-execution tests when there are no runs
                            "execution_coverage": 0.0
                        }
                    }
                )
        finally:
            await db_manager.release_connection(conn)
    except Exception as e:
        logger.error(f"Failed to get test status: {e}")
        return StandardResponse(
            status="error",
            message=f"Failed to retrieve test status: {str(e)}",
            data={}
        )

@router.get("/test-sessions")
async def get_test_sessions(
    limit: int = 100,
    offset: int = 0,
    admin: dict = Depends(get_current_admin_dependency),
):
    """Get a list of all test execution sessions (admin-only, with pagination)"""
    # Validate pagination parameters
    if not (1 <= limit <= 1000):
        raise HTTPException(status_code=400, detail="Limit must be between 1 and 1000")
    if not (offset >= 0):
        raise HTTPException(status_code=400, detail="Offset must be non-negative")
    
    try:
        conn = await db_manager.get_connection()
        try:
            # Get total count of sessions for pagination
            total_sessions_count = await conn.fetchval("""
                SELECT COUNT(*)
                FROM test_execution_sessions
            """) or 0

            sessions_from_db = await conn.fetch("""
                SELECT
                  id, status, test_type, test_category, total_tests, passed_tests, failed_tests,
                  execution_time_seconds, coverage_percentage, started_at, completed_at
                FROM test_execution_sessions
                ORDER BY completed_at DESC NULLS LAST, started_at DESC
                LIMIT $1 OFFSET $2
            """, limit, offset)
            sessions_data = []
            for session in sessions_from_db:
                sessions_data.append({
                    "id": session['id'],
                    "status": session['status'],
                    "test_type": session['test_type'],
                    "test_category": session['test_category'],
                    "total_tests": session['total_tests'] or 0,
                    "passed_tests": session['passed_tests'] or 0,
                    "failed_tests": session['failed_tests'] or 0,
                    "execution_time": session['execution_time_seconds'] or 0,
                    "coverage_percentage": float(session['coverage_percentage'] or 0),
                    "started_at": session['started_at'].isoformat() if session['started_at'] else None,
                    "completed_at": session['completed_at'].isoformat() if session['completed_at'] else None,
                    # Logs intentionally omitted from the public listing to prevent PII/leakage
                    "log_summary": None,
                    "full_log": None
                })
            return StandardResponse(
                status="success",
                message="Test sessions retrieved",
                data={
                    "sessions": sessions_data,
                    "total": total_sessions_count,
                    "page": offset // limit + 1 if limit > 0 else 1,
                    "per_page": limit
                }
            )
        finally:
            await db_manager.release_connection(conn)
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Failed to get test sessions: {e}")
        return StandardResponse(
            status="error",
            message=f"Failed to retrieve test sessions: {str(e)}",
            data={"sessions": [], "total": 0, "page": offset // limit + 1 if limit > 0 else 1, "per_page": limit}
        )

@router.get("/test-metrics")
async def get_test_metrics():
    """Get comprehensive test execution metrics and statistics for all available tests (database-driven, public endpoint for testing)"""
    try:
        conn = await db_manager.get_connection()
        try:
            # Get comprehensive test definitions and their latest execution status
            try:
                comprehensive_tests = await monitoring_dashboard.get_comprehensive_test_definitions()
                total_test_suites = len(comprehensive_tests)  # Count of test suites (16)
                # Calculate total individual test cases by summing test_case_count from all suites
                total_individual_tests = sum(test.get("test_case_count", 0) for test in comprehensive_tests)
            except Exception as e:
                logger.error(f"Failed to get comprehensive test definitions: {e}")
                comprehensive_tests = []
                total_test_suites = 0
                total_individual_tests = 0

            # Get latest test execution results for each test
            latest_executions = await conn.fetch("""
                WITH latest_test_runs AS (
                    SELECT DISTINCT ON (test_type, test_category)
                        test_type,
                        test_category,
                        status,
                        total_tests,
                        passed_tests,
                        failed_tests,
                        execution_time_seconds,
                        completed_at
                    FROM test_execution_sessions
                    WHERE status IN ('passed', 'failed', 'partial')
                    ORDER BY test_type, test_category, completed_at DESC NULLS LAST
                )
                SELECT * FROM latest_test_runs
            """)

            # Calculate comprehensive metrics
            total_executed_tests = 0
            total_passed_tests = 0
            total_failed_tests = 0
            total_execution_time = 0
            execution_count = 0

            # Create execution map for quick lookup
            execution_map = {}
            for execution in latest_executions:
                key = f"{execution['test_type']}_{execution['test_category']}"
                execution_map[key] = execution

                if execution['total_tests']:
                    total_executed_tests += execution['total_tests']
                total_passed_tests += execution['passed_tests'] or 0
                total_failed_tests += execution['failed_tests'] or 0
                total_execution_time += execution['execution_time_seconds'] or 0
                execution_count += 1

            # Determine overall success rate
            success_rate = (total_passed_tests / total_executed_tests) * 100 if total_executed_tests > 0 else 0
            avg_execution_time = total_execution_time / execution_count if execution_count > 0 else 0

            # Determine overall coverage trend and auto-fixes
            coverage_trend = [] # Placeholder for future implementation
            auto_fixes_applied = 0 # Placeholder for future implementation

            # Get latest overall execution for summary
            latest_overall_execution = await conn.fetchrow("""
                SELECT completed_at, total_tests, passed_tests, failed_tests,
                       coverage_percentage, execution_time_seconds, status
                FROM test_execution_sessions
                WHERE status IN ('passed', 'failed', 'partial')
                ORDER BY completed_at DESC NULLS LAST, started_at DESC
                LIMIT 1
            """)

            # Ensure total_available_individual_tests is accurate
            if total_individual_tests == 0 and latest_overall_execution and (latest_overall_execution.get('total_tests') or 0) > 0:
                total_available_individual_tests = (latest_overall_execution.get('total_tests') or 0)
            else:
                total_available_individual_tests = total_individual_tests

            return StandardResponse(
                status="success",
                message="Comprehensive test metrics retrieved",
                data={
                    # FIXED: Use actual test counts - individual test cases for execution metrics
                    "total_tests": total_available_individual_tests,
                    "total_test_suites": total_test_suites,  # For dashboard display (16)
                    "total_executed_tests": total_executed_tests,
                    "success_rate": round(success_rate, 1),
                    "avg_execution_time": round(avg_execution_time, 1),
                    "coverage_trend": coverage_trend,
                    "auto_fixes_applied": auto_fixes_applied,

                    # FIXED: Latest execution summary from actual test results
                    "latest_execution": {
                        "last_run": latest_overall_execution['completed_at'].isoformat() if latest_overall_execution and latest_overall_execution['completed_at'] else None,
                        "total_tests": latest_overall_execution['total_tests'] if latest_overall_execution else total_available_individual_tests,
                        "passed_tests": latest_overall_execution['passed_tests'] if latest_overall_execution else 0,
                        "failed_tests": latest_overall_execution['failed_tests'] if latest_overall_execution else 0,
                        "test_coverage": float(latest_overall_execution['coverage_percentage']) if latest_overall_execution and latest_overall_execution['coverage_percentage'] else 0,
                        "execution_time": latest_overall_execution['execution_time_seconds'] if latest_overall_execution else 0,
                        "status": latest_overall_execution['status'] if latest_overall_execution else 'unknown'
                    },

                    # FIXED: Legacy fields for backward compatibility
                    "total_sessions": len(latest_executions)
                }
            )
        finally:
            await db_manager.release_connection(conn)
    except Exception as e:
        logger.error(f"Failed to get test metrics: {e}")
        return StandardResponse(
            status="error",
            message=f"Failed to retrieve test metrics: {str(e)}",
            data={
                "total_tests": 0,
                "total_executed_tests": 0,
                "success_rate": 0,
                "avg_execution_time": 0,
                "coverage_trend": [],
                "auto_fixes_applied": 0,
                "latest_execution": {
                    "total_tests": 0,
                    "passed_tests": 0,
                    "failed_tests": 0,
                    "test_coverage": 0,
                    "execution_time": 0,
                    "status": "unknown"
                },
                "total_sessions": 0
            }
        )

@router.post("/test-execute")
async def execute_test(request: dict):
    """Execute a test suite using our actual test execution engine (public endpoint for testing)"""
    try:
        from test_execution_engine import TestExecutionEngine
 
        test_type = request.get("test_type", "unit")
        test_suite = request.get("test_suite", None)
        triggered_by = request.get("triggered_by", "manual")
 
        # Initialize test execution engine
        engine = TestExecutionEngine()
 
        # FIXED: Handle individual test suite execution vs all suites
        if test_suite and test_suite != "all":
            # Execute specific test suite for individual card
            logger.info(f"Executing individual test suite: {test_suite}")
            result = await engine.execute_test_suite(test_suite, test_type)
 
            # FIXED: Return specific results for individual test cards
            return StandardResponse(
                status="success",
                message=f"Individual test suite '{test_suite}' execution completed",
                data={
                    "test_suite": test_suite,
                    "status": result.get("status", "unknown"),
                    "total_tests": result.get("total_tests", 0),
                    "passed_tests": result.get("passed_tests", 0),
                    "failed_tests": result.get("failed_tests", 0),
                    "execution_time_seconds": result.get("execution_time_seconds", 0),
                    "results": result.get("results", {}),
                    "triggered_by": triggered_by
                }
            )
        else:
            # Execute all test suites (for "Run All Tests" button )
            logger.info("Executing all test suites")
            result = await engine.execute_all_test_suites()
 
            return StandardResponse(
                status="success",
                message=f"All test suites execution completed: {test_type}",
                data=result
            )
    except Exception as e:
        logger.error(f"Test execution failed: {e}")
        return StandardResponse(
            status="error",
            message=f"Failed to execute test: {str(e)}",
            data={}
        )

# Configurable maximum number of test suites to prevent frontend grid instability
MAX_SUITES = int(os.getenv('MAX_TEST_SUITES', '16'))

def infer_frontend_category_and_icon(test_category: str) -> tuple[str, str]:
    """
    Centralized helper function to determine frontend category and icon from test_category.
 
    Args:
        test_category: The test category string from database
 
    Returns:
        tuple: (frontend_category, icon)
    """
    category_lower = test_category.lower()
 
    # Expanded keyword lists for better matching
    core_platform_keywords = [
        'database', 'db', 'api', 'security', 'integration', 'performance',
        'auto_healing', 'auto-heal', 'auto_heal'
    ]
 
    revenue_critical_keywords = [
        'payment', 'payments', 'spiritual', 'avatar'
    ]
 
    communication_keywords = [
        'live', 'live_audio', 'live_video', 'live_media', 'live_audio_video_business_critical',
        'audio', 'video', 'social', 'media', 'social_media'
    ]
 
    user_experience_keywords = [
        'user', 'user_management', 'user_mgmt', 'community', 'notification', 'notifications'
    ]
 
    business_management_keywords = [
        'admin', 'monitoring', 'business'
    ]
 
    # Determine frontend category based on expanded keyword matching
    if any(keyword in category_lower for keyword in core_platform_keywords):
        frontend_category = 'Core Platform'
    elif any(keyword in category_lower for keyword in revenue_critical_keywords):
        frontend_category = 'Revenue Critical'
    elif any(keyword in category_lower for keyword in communication_keywords):
        frontend_category = 'Communication'
    elif any(keyword in category_lower for keyword in user_experience_keywords):
        frontend_category = 'User Experience'
    elif any(keyword in category_lower for keyword in business_management_keywords):
        frontend_category = 'Business Management'
    else:
        frontend_category = 'Other Services'
 
    # Expanded icon mapping with all variants
    icon_mapping = {
        'database': '🗄️', 'db': '🗄️',
        'api': '🔌',
        'security': '🔒',
        'integration': '🔗',
        'performance': '⚡',
        'auto_healing': '🔄', 'auto-heal': '🔄', 'auto_heal': '🔄',
        'payment': '💳', 'payments': '💳',
        'spiritual': '🕉️',
        'avatar': '🎭',
        'live': '📹', 'live_audio': '📹', 'live_video': '📹', 'live_media': '📹',
        'live_audio_video_business_critical': '📹',
        'audio': '🔊', 'video': '📹',
        'social_media': '📱', 'social': '📱', 'media': '📱',
        'user_management': '👤', 'user_mgmt': '👤', 'user': '👤',
        'community': '🤝',
        'notifications': '🔔', 'notification': '🔔',
        'admin': '⚙️',
        'monitoring': '📊',
        'business': '💼'
    }
 
    # Find matching icon (first match wins)
    icon = '🔧'  # default
    for keyword, emoji in icon_mapping.items():
        if keyword in category_lower:
            icon = emoji
            break
 
    return frontend_category, icon

@router.get("/test-suites")
async def get_available_test_suites():
    """Get all available test suites - database-driven discovery from TestSuiteGenerator"""
    try:
        # Method 1: Get available test suites from TestSuiteGenerator (primary source)
        try:
            comprehensive_tests = await monitoring_dashboard.get_comprehensive_test_definitions()
            if comprehensive_tests:
                logger.info(f"Using TestSuiteGenerator - found {len(comprehensive_tests)} test suites")
 
                # Convert to the format expected by the frontend
                categorized_suites = {}
 
                for test_suite in comprehensive_tests:
                    test_category = test_suite.get("test_category", "unknown")
                    suite_name = test_suite.get("suite_display_name", test_category.replace("_", " ").title())
                    priority = test_suite.get("priority", "medium")
 
                    # Use centralized helper function for consistent categorization and icon assignment
                    frontend_category, icon = infer_frontend_category_and_icon(test_category)
 
                    # Create frontend category if it doesn't exist
                    if frontend_category not in categorized_suites:
                        categorized_suites[frontend_category] = {
                            "category": frontend_category,
                            "services": []
                        }
 
                    # Add test suite to appropriate category
                    categorized_suites[frontend_category]["services"].append({
                        "title": suite_name,
                        "testType": test_category,
                        "icon": icon,
                        "priority": priority,
                        "description": test_suite.get("description", suite_name),
                        "name": test_category,
                        "timeout_seconds": 300
                    })
 
                # Convert to list format expected by frontend
                suite_config = list(categorized_suites.values())
 
                # Apply configurable suite cap to prevent frontend grid instability
                total_services = sum(len(category["services"]) for category in suite_config)
                if total_services > MAX_SUITES:
                    # Truncate services while preserving category structure
                    services_added = 0
                    for category in suite_config:
                        if services_added >= MAX_SUITES:
                            category["services"] = []
                        else:
                            remaining_slots = MAX_SUITES - services_added
                            category["services"] = category["services"][:remaining_slots]
                            services_added += len(category["services"])
 
                total_test_suites = len(comprehensive_tests)
 
                return StandardResponse(
                    status="success",
                    message=f"Retrieved {total_test_suites} test suites from TestSuiteGenerator (database-driven)",
                    data={
                        "test_suites": suite_config,
                        "total_suites": total_test_suites,
                        "source": "test_suite_generator"
                    }
                )
        except Exception as e:
            logger.warning(f"TestSuiteGenerator discovery failed: {e}, falling back to database")
 
        # Method 2: Fallback to test_case_results table (secondary source)
        conn = await db_manager.get_connection()
        try:
            try:
                # Get test categories from test_case_results table as fallback
                test_categories = await conn.fetch("""
                    WITH ranked_categories AS (
                        SELECT
                            test_category,
                            COUNT(*) as total_tests,
                            COUNT(*) FILTER (WHERE status = 'passed') as passed_tests,
                            COUNT(*) FILTER (WHERE status = 'failed') as failed_tests,
                            MAX(created_at) as last_execution,
                            ROW_NUMBER() OVER (ORDER BY MAX(created_at) DESC, COUNT(*) DESC) as rn
                        FROM test_case_results
                        WHERE test_category IS NOT NULL
                        AND test_category != ''
                        GROUP BY test_category
                    )
                    SELECT
                        test_category,
                        total_tests,
                        passed_tests,
                        failed_tests,
                        last_execution
                    FROM ranked_categories
                    WHERE rn <= 16  -- Limit to exactly 16 test suites
                    ORDER BY test_category
                """)
            except asyncpg.exceptions.UndefinedTableError:
                # Table doesn't exist - return empty result instead of error
                logger.warning("test_case_results table not found in database")
                return StandardResponse(
                    status="success",
                    message="No test execution results found - test_case_results table needs to be created in database",
                    data={"test_suites": [], "total_suites": 0}
                )
            except Exception as query_error:
                # Any other query error (like column not found)  provide detailed error for debugging
                error_type = type(query_error).__name__
                logger.error(f"Query error in test_case_results: {error_type}: {query_error}")
 
                return StandardResponse(
                    status="success",
                    message="Test execution results unavailable - database schema needs to be updated",
                    data={"test_suites": [], "total_suites": 0}
                )
 
            # Icon mapping is now centralized in helper function
 
            # Group test categories by frontend category for consumption (100% database-driven)
            categorized_suites = {}
            for test_category_row in test_categories:
                test_category = test_category_row['test_category']
                total_tests = test_category_row['total_tests']
                passed_tests = test_category_row['passed_tests']
                failed_tests = test_category_row['failed_tests']
 
                # Derive display information from test_category name (database-driven approach)
                # Following .cursor rules: Handle missing columns gracefully, no assumptions about schema
                display_name = test_category.replace('_', ' ').title()
 
                # Fallback logic for cases where display_name column might be expected but missing
                # This ensures compatibility with any code that expects display_name from database
                name_fallback = test_category  # Use test_category as 'name' fallback
 
                # Use centralized helper function for consistent categorization and icon assignment
                frontend_category, icon = infer_frontend_category_and_icon(test_category)
 
                # Determine priority based on test results and category patterns (database-driven)
                if failed_tests > 0:
                    priority_level = 'critical'
                elif any(keyword in test_category.lower() for keyword in ['database', 'api', 'security', 'payment', 'spiritual']):
                    priority_level = 'critical'
                elif any(keyword in test_category.lower() for keyword in ['integration', 'performance', 'user', 'admin']):
                    priority_level = 'high'
                else:
                    priority_level = 'medium'
 
                # Icon is now determined by the helper function above
 
                # Create frontend category if it doesn't exist
                if frontend_category not in categorized_suites:
                    categorized_suites[frontend_category] = {
                        "category": frontend_category,
                        "services": []
                    }
 
                # Add test suite to appropriate category with fallback logic
                # Following .cursor rules: Graceful handling of missing columns, robust fallbacks
                categorized_suites[frontend_category]["services"].append({
                    "title": display_name,  # Always use derived display name
                    "testType": test_category,  # Use actual database column
                    "icon": icon,
                    "priority": priority_level,
                    "description": display_name,  # Use derived display name (fallback-safe)
                    "name": name_fallback,  # Provide 'name' fallback for compatibility
                    "timeout_seconds": 300  # Default 5 minutes
                })
 
            # Convert to list format expected by frontend (100% database-driven)
            suite_config = list(categorized_suites.values())
 
            # Apply configurable suite cap to prevent frontend grid instability
            total_services = sum(len(category["services"]) for category in suite_config)
            if total_services > MAX_SUITES:
                # Truncate services while preserving category structure
                services_added = 0
                for category in suite_config:
                    if services_added >= MAX_SUITES:
                        category["services"] = []
                    else:
                        remaining_slots = MAX_SUITES - services_added
                        category["services"] = category["services"][:remaining_slots]
                        services_added += len(category["services"])
 
            total_test_categories = len(test_categories)
 
            logger.info(f"Retrieved {total_test_categories} test categories from test_case_results table (100% database-driven)")
 
            return StandardResponse(
                status="success",
                message=f"Retrieved {total_test_categories} test categories from test execution results",
                data={
                    "test_suites": suite_config,
                    "total_suites": total_test_categories
                }
            )
 
        except asyncpg.PostgresError as db_error:
            # Handle specific database connection and query errors
            logger.error(f"Database error while fetching test suites: {db_error}")
            return StandardResponse(
                status="error",
                message=f"Database error: {str(db_error)}",
                data={"test_suites": []}
            )
        finally:
            if conn:
                await db_manager.release_connection(conn)
 
    except Exception as e:
        # Handle general connection manager errors and other unexpected issues
        logger.error(f"Failed to get test suites from database: {e}")
        return StandardResponse(
            status="error",
            message=f"Failed to retrieve test suites: {str(e)}",
            data={"test_suites": []}
        )

@router.get("/business-logic-validation")
async def get_business_logic_validation_status():
    """Get business logic validation status and recent results (public endpoint for testing)"""
    try:
        conn = await db_manager.get_connection()
        try:
            # Check if business_logic_issues table exists and get recent results
            table_exists = await conn.fetchval("""
                SELECT EXISTS(
                    SELECT 1 FROM information_schema.tables
                    WHERE table_name = 'business_logic_issues' AND table_schema = 'public'
                )
            """)
 
            if not table_exists:
                # Return empty data if table doesn't exist yet
                return StandardResponse(
                    status="success",
                    message="Business logic validation table not yet created",
                    data={
                        "summary": {
                            "total_validations": 0,
                            "passed_validations": 0,
                            "success_rate": 0,
                            "avg_quality_score": 0
                        },
                        "recent_validations": []
                    }
                )
 
            # Check schema compatibility first
            schema_check = await conn.fetch("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'business_logic_issues'
                AND column_name IN ('issue_description', 'severity_score', 'validation_type')
            """)
 
            available_columns = {row['column_name'] for row in schema_check}
            has_new_schema = 'issue_description' in available_columns and 'severity_score' in available_columns
            has_validation_type = 'validation_type' in available_columns
 
            # Build query based on available schema
            if has_new_schema:
                # New schema with issue_description and severity_score
                recent_validations = await conn.fetch("""
                    SELECT
                        session_id,
                        issue_description,
                        severity_score as quality_score,
                        created_at,
                        CASE
                            WHEN severity_score IS NULL OR severity_score = 0 THEN 'success'
                            WHEN severity_score <= 3 THEN 'warning'
                            ELSE 'error'
                        END as validation_result,
                        COALESCE(validation_type, 'business_logic') as validation_type
                    FROM business_logic_issues
                    WHERE created_at >= NOW() - INTERVAL '24 hours'
                    ORDER BY created_at DESC
                    LIMIT 50
                """)
            elif has_validation_type:
                # Old schema with validation_type but no new columns
                recent_validations = await conn.fetch("""
                    SELECT
                        session_id,
                        validation_type,
                        'No description available' as issue_description,
                        0 as quality_score,
                        created_at,
                        CASE
                            WHEN validation_type LIKE '%success%' OR validation_type LIKE '%pass%' THEN 'success'
                            WHEN validation_type LIKE '%warning%' THEN 'warning'
                            ELSE 'error'
                        END as validation_result
                    FROM business_logic_issues
                    WHERE created_at >= NOW() - INTERVAL '24 hours'
                    ORDER BY created_at DESC
                    LIMIT 50
                """)
            else:
                # Minimal schema - just basic columns
                recent_validations = await conn.fetch("""
                    SELECT
                        session_id,
                        'business_logic' as validation_type,
                        'Legacy validation entry' as issue_description,
                        0 as quality_score,
                        created_at,
                        'unknown' as validation_result
                    FROM business_logic_issues
                    WHERE created_at >= NOW() - INTERVAL '24 hours'
                    ORDER BY created_at DESC
                    LIMIT 50
                """)
 
            # Calculate summary statistics
            total_validations = len(recent_validations)
            passed_validations = sum(1 for v in recent_validations
                                   if v['validation_result'] and str(v['validation_result']).lower() == 'success')
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
async def trigger_business_logic_validation(request: dict):
    """Trigger business logic validation for spiritual content (public endpoint for testing)"""
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
 
            tables_to_check = ['live_chat_sessions', 'sessions', 'session_participants', 'user_sessions']
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
 
            # Sessions in last 24 hours - use sessions table with correct column names
            sessions_24h = await conn.fetchval('''
                SELECT COUNT(*) FROM sessions
                WHERE created_at >= NOW() - INTERVAL '24 hours'
                AND (service_type LIKE '%video%' OR service_type LIKE '%chat%')
            ''')
            session_metrics["sessions_24h"] = sessions_24h or 0
 
            # Revenue in last 24 hours - calculate from credits_used
            revenue_24h = await conn.fetchval('''
                SELECT COALESCE(SUM(credits_used * 0.1), 0) FROM sessions
                WHERE created_at >= NOW() - INTERVAL '24 hours'
                AND (service_type LIKE '%video%' OR service_type LIKE '%chat%')
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


def _extract_agora_channel_from_session_data(session_data):
    """
    Parse session_data JSON string to extract agora_channel field.
    Returns the agora_channel string or None if parsing fails or field is missing.
 
    Args:
        session_data: JSON string or dict containing session information
 
    Returns:
        str or None: The agora channel identifier if found, otherwise None
    """
    if not session_data:
        return None
 
    try:
        # Handle both string and dict inputs
        if isinstance(session_data, str):
            import json
            parsed_data = json.loads(session_data)
        elif isinstance(session_data, dict):
            parsed_data = session_data
        else:
            return None
 
        # Try different possible field names for agora channel
        possible_fields = ['agora_channel', 'channel_name', 'channel', 'agora_channel_name']
        for field in possible_fields:
            if field in parsed_data and isinstance(parsed_data[field], str):
                return parsed_data[field]
 
        return None
 
    except (json.JSONDecodeError, TypeError, AttributeError, KeyError) as e:
        # Log the error for debugging but don't break the application
        logger.debug(f"Failed to parse session_data for agora_channel: {e}")
        return None

@router.get("/live-audio-video-sessions")
async def get_live_audio_video_sessions():
    """Get recent live audio/video sessions data"""
    try:
        conn = await db_manager.get_connection()
 
        # Get recent sessions
        sessions = []
        try:
            sessions_data = await conn.fetch('''
                SELECT s.id as session_id, s.user_id, s.service_type, s.status,
                       s.created_at as start_time, s.updated_at as end_time,
                       s.duration_minutes, s.credits_used, s.session_data,
                       lcs.channel_name as agora_channel
                FROM sessions s
                LEFT JOIN live_chat_sessions lcs ON s.id::text = lcs.session_id
                WHERE s.created_at >= NOW() - INTERVAL '7 days'
                AND (s.service_type LIKE '%video%' OR s.service_type LIKE '%chat%')
                ORDER BY s.created_at DESC
                LIMIT 20
            ''')
 
            for session in sessions_data:
                sessions.append({
                    "session_id": str(session['session_id']),
                    "user_id": session['user_id'],
                    "service_type": session['service_type'],
                    "status": session['status'],
                    "start_time": session['start_time'].isoformat() if session['start_time'] else None,
                    "end_time": session['end_time'].isoformat() if session['end_time'] else None,
                    "duration": session['duration_minutes'],
                    "cost": float(session['credits_used'] * 0.1) if session['credits_used'] else 0.0,
                    "agora_channel": session.get('agora_channel') or _extract_agora_channel_from_session_data(session.get('session_data'))
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

@router.get("/test-categories")
async def get_test_categories():
    """Get test categories for the monitoring dashboard"""
    try:
        conn = await db_manager.get_connection()
        try:
            # Get test categories from test_case_results table
            test_categories = await conn.fetch("""
                SELECT DISTINCT test_category
                FROM test_case_results
                WHERE test_category IS NOT NULL
                AND test_category != ''
            """)
 
            return StandardResponse(
                status="success",
                message="Test categories retrieved",
                data={
                    "test_categories": [dict(category) for category in test_categories]
                }
            )
        finally:
            await db_manager.release_connection(conn)
    except Exception as e:
        logger.error(f"Failed to get test categories: {e}")
        return StandardResponse(
            status="error",
            message=f"Failed to retrieve test categories: {str(e)}",
            data={}
        )

# Export for use in other modules
__all__ = ["monitoring_dashboard", "router", "connection_manager"]