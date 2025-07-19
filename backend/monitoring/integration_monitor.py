"""
🔍 INTEGRATION MONITOR - Core monitoring engine for JyotiFlow
Tracks the entire integration chain from user input to final response
with real-time validation and silent failure detection.
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import aiohttp
import traceback

from db import db_manager

logger = logging.getLogger(__name__)

# Import validators
from validators.prokerala_validator import ProkeralaValidator
from validators.rag_validator import RAGValidator
from validators.openai_validator import OpenAIValidator
from validators.elevenlabs_validator import ElevenLabsValidator
from validators.did_validator import DIDValidator
from validators.social_media_validator import SocialMediaValidator

# Import context tracker
from .context_tracker import ContextTracker
from .business_validator import BusinessLogicValidator

class IntegrationStatus(Enum):
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"
    DEGRADED = "degraded"
    VALIDATION_ERROR = "validation_error"

class IntegrationPoint(Enum):
    USER_INPUT = "user_input"
    PROKERALA = "prokerala"
    RAG_KNOWLEDGE = "rag_knowledge"
    OPENAI_GUIDANCE = "openai_guidance"
    ELEVENLABS_VOICE = "elevenlabs_voice"
    DID_AVATAR = "did_avatar"
    FINAL_RESPONSE = "final_response"
    SOCIAL_MEDIA = "social_media"

class IntegrationMonitor:
    """
    Production-ready integration monitoring system that tracks
    and validates the entire spiritual guidance flow.
    """
    
    def __init__(self):
        self.validators = {
            IntegrationPoint.PROKERALA: ProkeralaValidator(),
            IntegrationPoint.RAG_KNOWLEDGE: RAGValidator(),
            IntegrationPoint.OPENAI_GUIDANCE: OpenAIValidator(),
            IntegrationPoint.ELEVENLABS_VOICE: ElevenLabsValidator(),
            IntegrationPoint.DID_AVATAR: DIDValidator(),
            IntegrationPoint.SOCIAL_MEDIA: SocialMediaValidator()
        }
        self.context_tracker = ContextTracker()
        self.business_validator = BusinessLogicValidator()
        self.active_sessions = {}
        self.metrics = {}  # Store metrics for each integration
        
    async def start_monitoring(self):
        """Start background monitoring tasks"""
        logger.info("🚀 Starting integration monitoring background tasks...")
        # Start periodic health checks
        asyncio.create_task(self._periodic_health_check())
        
    async def update_metrics(self, integration_name: str, metric_type: str, 
                           value: float, metadata: Optional[Dict] = None):
        """Update metrics for an integration point"""
        if integration_name not in self.metrics:
            self.metrics[integration_name] = {}
        
        if metric_type not in self.metrics[integration_name]:
            self.metrics[integration_name][metric_type] = []
        
        self.metrics[integration_name][metric_type].append({
            "value": value,
            "timestamp": datetime.now(timezone.utc),
            "metadata": metadata or {}
        })
        
        # Keep only last 1000 metrics per type
        if len(self.metrics[integration_name][metric_type]) > 1000:
            self.metrics[integration_name][metric_type] = \
                self.metrics[integration_name][metric_type][-1000:]
    
    async def _periodic_health_check(self):
        """Periodically check integration health"""
        while True:
            try:
                await asyncio.sleep(300)  # Check every 5 minutes
                health_status = await self.get_system_health()
                logger.info(f"📊 System health check: {health_status['overall_status']}")
            except Exception as e:
                logger.error(f"Error in periodic health check: {e}")
        
    async def start_session_monitoring(self, session_id: str, user_id: int, 
                                     birth_details: Dict, spiritual_question: str,
                                     service_type: str) -> Dict:
        """Start monitoring a new user session"""
        try:
            # Create session context
            session_context = {
                "session_id": session_id,
                "user_id": user_id,
                "birth_details": birth_details,
                "spiritual_question": spiritual_question,
                "service_type": service_type,
                "started_at": datetime.now(timezone.utc),
                "integration_results": {},
                "validation_results": {},
                "issues_found": [],
                "auto_fixes_applied": [],
                "overall_status": IntegrationStatus.SUCCESS.value
            }
            
            # Store in active sessions
            self.active_sessions[session_id] = session_context
            
            # Initialize context tracking
            await self.context_tracker.initialize_session(session_id, session_context)
            
            # Store in database
            conn = await db_manager.get_connection()
            try:
                await conn.execute("""
                    INSERT INTO validation_sessions 
                    (session_id, user_id, started_at, user_context, overall_status)
                    VALUES ($1, $2, $3, $4, $5)
                    ON CONFLICT (session_id) DO UPDATE 
                    SET started_at = $3, user_context = $4
                """, session_id, user_id, session_context["started_at"], 
                    json.dumps(session_context), IntegrationStatus.SUCCESS.value)
            finally:
                await db_manager.release_connection(conn)
            
            logger.info(f"✅ Started monitoring session {session_id}")
            return {"success": True, "session_id": session_id}
            
        except Exception as e:
            logger.error(f"❌ Failed to start session monitoring: {e}")
            return {"success": False, "error": str(e)}
    
    async def validate_integration_point(self, session_id: str, 
                                       integration_point: IntegrationPoint,
                                       input_data: Dict, output_data: Dict,
                                       duration_ms: int) -> Dict:
        """Validate a specific integration point in the flow"""
        validation_start = time.time()
        
        try:
            if session_id not in self.active_sessions:
                logger.warning(f"Session {session_id} not found in active monitoring")
                return {"validated": False, "error": "Session not found"}
            
            session_context = self.active_sessions[session_id]
            
            # Get validator for this integration point
            validator = self.validators.get(integration_point)
            if not validator:
                logger.warning(f"No validator for integration point: {integration_point.value}")
                validation_result = {
                    "validated": True,
                    "passed": True,
                    "warnings": ["No validator available"]
                }
            else:
                # Run validation
                validation_result = await validator.validate(
                    input_data, output_data, session_context
                )
            
            # Add performance metrics
            validation_result["duration_ms"] = duration_ms
            validation_result["validation_time_ms"] = int((time.time() - validation_start) * 1000)
            
            # Update context
            await self.context_tracker.update_context(
                session_id, integration_point.value, input_data, output_data
            )
            
            # Store validation result
            session_context["integration_results"][integration_point.value] = validation_result
            
            # Check for issues
            if not validation_result.get("passed", True):
                issue = {
                    "integration_point": integration_point.value,
                    "issue_type": validation_result.get("issue_type", "validation_failed"),
                    "severity": validation_result.get("severity", "error"),
                    "description": validation_result.get("error", "Validation failed"),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
                session_context["issues_found"].append(issue)
                
                # Attempt auto-fix if possible
                if validation_result.get("auto_fixable", False):
                    fix_result = await self._attempt_auto_fix(
                        session_id, integration_point, validation_result
                    )
                    if fix_result.get("fixed", False):
                        session_context["auto_fixes_applied"].append({
                            "integration_point": integration_point.value,
                            "fix_type": fix_result.get("fix_type"),
                            "timestamp": datetime.now(timezone.utc).isoformat()
                        })
            
            # Store in database
            await self._store_validation_result(
                session_id, integration_point.value, validation_result
            )
            
            # Update overall status
            await self._update_session_status(session_id)
            
            return validation_result
            
        except Exception as e:
            logger.error(f"❌ Validation error at {integration_point.value}: {e}")
            logger.error(traceback.format_exc())
            return {
                "validated": False,
                "error": str(e),
                "integration_point": integration_point.value
            }
    
    async def validate_business_logic(self, session_id: str) -> Dict:
        """Run comprehensive business logic validation for the session"""
        try:
            if session_id not in self.active_sessions:
                return {"validated": False, "error": "Session not found"}
            
            session_context = self.active_sessions[session_id]
            
            # Run business logic validation
            business_validation = await self.business_validator.validate_session(
                session_context
            )
            
            # Store results
            session_context["validation_results"]["business_logic"] = business_validation
            
            # Check for critical issues
            if business_validation.get("critical_issues", []):
                session_context["overall_status"] = IntegrationStatus.FAILED.value
                
                # Alert admin for critical issues
                await self._alert_admin_critical_issue(session_id, business_validation)
            
            return business_validation
            
        except Exception as e:
            logger.error(f"❌ Business logic validation error: {e}")
            return {"validated": False, "error": str(e)}
    
    async def complete_session_monitoring(self, session_id: str) -> Dict:
        """Complete monitoring for a session and generate final report"""
        try:
            if session_id not in self.active_sessions:
                return {"success": False, "error": "Session not found"}
            
            session_context = self.active_sessions[session_id]
            session_context["completed_at"] = datetime.now(timezone.utc)
            
            # Run final business logic validation
            final_validation = await self.validate_business_logic(session_id)
            
            # Calculate session metrics
            session_metrics = await self._calculate_session_metrics(session_context)
            session_context["metrics"] = session_metrics
            
            # Store final results in database
            conn = await db_manager.get_connection()
            try:
                await conn.execute("""
                    UPDATE validation_sessions
                    SET completed_at = $1, overall_status = $2, 
                        validation_results = $3, user_context = $4
                    WHERE session_id = $5
                """, session_context["completed_at"], 
                    session_context["overall_status"],
                    json.dumps(session_context["validation_results"]),
                    json.dumps(session_context),
                    session_id)
            finally:
                await db_manager.release_connection(conn)
            
            # Generate session report
            session_report = {
                "session_id": session_id,
                "overall_status": session_context["overall_status"],
                "duration_seconds": (
                    session_context["completed_at"] - session_context["started_at"]
                ).total_seconds(),
                "integration_points_validated": len(session_context["integration_results"]),
                "issues_found": len(session_context["issues_found"]),
                "auto_fixes_applied": len(session_context["auto_fixes_applied"]),
                "metrics": session_metrics,
                "critical_issues": final_validation.get("critical_issues", []),
                "recommendations": await self._generate_recommendations(session_context)
            }
            
            # Clean up active session
            del self.active_sessions[session_id]
            
            logger.info(f"✅ Completed monitoring for session {session_id}")
            return session_report
            
        except Exception as e:
            logger.error(f"❌ Failed to complete session monitoring: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_system_health(self) -> Dict:
        """Get overall system health status"""
        try:
            health_status = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "active_sessions": len(self.active_sessions),
                "integration_points": {},
                "recent_issues": [],
                "system_status": "healthy"
            }
            
            # Check each integration point health
            for point in IntegrationPoint:
                if point == IntegrationPoint.USER_INPUT or point == IntegrationPoint.FINAL_RESPONSE:
                    continue
                    
                point_health = await self._check_integration_point_health(point)
                health_status["integration_points"][point.value] = point_health
            
            # Get recent issues from database
            conn = await db_manager.get_connection()
            try:
                recent_issues = await conn.fetch("""
                    SELECT issue_type, severity, description, created_at
                    FROM business_logic_issues
                    WHERE created_at > NOW() - INTERVAL '1 hour'
                    ORDER BY created_at DESC
                    LIMIT 10
                """)
                
                health_status["recent_issues"] = [
                    dict(issue) for issue in recent_issues
                ]
            finally:
                await db_manager.release_connection(conn)
            
            # Determine overall system status
            critical_count = sum(
                1 for p in health_status["integration_points"].values()
                if p.get("status") == "error"
            )
            
            if critical_count >= 2:
                health_status["system_status"] = "critical"
            elif critical_count == 1:
                health_status["system_status"] = "degraded"
            elif any(p.get("status") == "warning" for p in health_status["integration_points"].values()):
                health_status["system_status"] = "warning"
            
            return health_status
            
        except Exception as e:
            logger.error(f"❌ Failed to get system health: {e}")
            return {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "system_status": "error",
                "error": str(e)
            }
    
    # Private helper methods
    async def _attempt_auto_fix(self, session_id: str, 
                               integration_point: IntegrationPoint,
                               validation_result: Dict) -> Dict:
        """Attempt to auto-fix validation issues"""
        try:
            validator = self.validators.get(integration_point)
            if not validator or not hasattr(validator, 'auto_fix'):
                return {"fixed": False, "reason": "No auto-fix available"}
            
            fix_result = await validator.auto_fix(
                validation_result, self.active_sessions[session_id]
            )
            
            return fix_result
            
        except Exception as e:
            logger.error(f"❌ Auto-fix failed: {e}")
            return {"fixed": False, "error": str(e)}
    
    async def _store_validation_result(self, session_id: str, 
                                     integration_name: str,
                                     validation_result: Dict):
        """Store validation result in database"""
        try:
            conn = await db_manager.get_connection()
            try:
                await conn.execute("""
                    INSERT INTO integration_validations
                    (session_id, integration_name, validation_type, status,
                     expected_value, actual_value, error_message, auto_fixed)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                """, session_id, integration_name, 
                    validation_result.get("validation_type", "standard"),
                    "success" if validation_result.get("passed", True) else "failed",
                    json.dumps(validation_result.get("expected", {})),
                    json.dumps(validation_result.get("actual", {})),
                    validation_result.get("error", ""),
                    validation_result.get("auto_fixed", False))
            finally:
                await db_manager.release_connection(conn)
        except Exception as e:
            logger.error(f"Failed to store validation result: {e}")
    
    async def _update_session_status(self, session_id: str):
        """Update overall session status based on validations"""
        if session_id not in self.active_sessions:
            return
            
        session_context = self.active_sessions[session_id]
        results = session_context["integration_results"]
        
        failed_count = sum(1 for r in results.values() if not r.get("passed", True))
        critical_count = sum(1 for r in results.values() 
                           if r.get("severity") == "critical" and not r.get("passed", True))
        
        if critical_count > 0:
            session_context["overall_status"] = IntegrationStatus.FAILED.value
        elif failed_count > 2:
            session_context["overall_status"] = IntegrationStatus.PARTIAL.value
        elif failed_count > 0:
            session_context["overall_status"] = IntegrationStatus.DEGRADED.value
        else:
            session_context["overall_status"] = IntegrationStatus.SUCCESS.value
    
    async def _alert_admin_critical_issue(self, session_id: str, validation_result: Dict):
        """Send alert to admin for critical issues"""
        try:
            # This would integrate with existing WebSocket connections
            # For now, log critical issues
            logger.critical(f"🚨 CRITICAL ISSUE in session {session_id}: {validation_result}")
            
            # Store in database for admin dashboard
            conn = await db_manager.get_connection()
            try:
                for issue in validation_result.get("critical_issues", []):
                    await conn.execute("""
                        INSERT INTO business_logic_issues
                        (session_id, issue_type, severity, description, 
                         auto_fixable, user_impact)
                        VALUES ($1, $2, $3, $4, $5, $6)
                    """, session_id, issue.get("type"), "critical",
                        issue.get("description"), False, 
                        issue.get("user_impact", "User may receive incorrect guidance"))
            finally:
                await db_manager.release_connection(conn)
                        
        except Exception as e:
            logger.error(f"Failed to alert admin: {e}")
    
    async def _calculate_session_metrics(self, session_context: Dict) -> Dict:
        """Calculate comprehensive session metrics"""
        metrics = {
            "total_duration_ms": 0,
            "integration_durations": {},
            "validation_scores": {},
            "performance_score": 0,
            "quality_score": 0
        }
        
        # Calculate durations
        for point, result in session_context["integration_results"].items():
            duration = result.get("duration_ms", 0)
            metrics["integration_durations"][point] = duration
            metrics["total_duration_ms"] += duration
        
        # Calculate validation scores
        total_validations = len(session_context["integration_results"])
        passed_validations = sum(1 for r in session_context["integration_results"].values() 
                               if r.get("passed", True))
        
        if total_validations > 0:
            metrics["quality_score"] = (passed_validations / total_validations) * 100
        
        # Performance score based on duration
        if metrics["total_duration_ms"] < 5000:  # Under 5 seconds
            metrics["performance_score"] = 100
        elif metrics["total_duration_ms"] < 10000:  # Under 10 seconds
            metrics["performance_score"] = 80
        elif metrics["total_duration_ms"] < 15000:  # Under 15 seconds
            metrics["performance_score"] = 60
        else:
            metrics["performance_score"] = 40
        
        return metrics
    
    async def _generate_recommendations(self, session_context: Dict) -> List[str]:
        """Generate recommendations based on session analysis"""
        recommendations = []
        
        # Check for slow integrations
        for point, result in session_context["integration_results"].items():
            if result.get("duration_ms", 0) > 3000:
                recommendations.append(f"Optimize {point} integration - taking {result['duration_ms']}ms")
        
        # Check for validation failures
        for issue in session_context["issues_found"]:
            if issue["severity"] == "error":
                recommendations.append(f"Fix {issue['integration_point']}: {issue['description']}")
        
        # Check business logic issues
        business_validation = session_context.get("validation_results", {}).get("business_logic", {})
        if business_validation.get("rag_relevance_score", 100) < 65:
            recommendations.append("Improve RAG knowledge retrieval relevance")
        
        return recommendations
    
    async def _check_integration_point_health(self, integration_point: IntegrationPoint) -> Dict:
        """Check health of a specific integration point"""
        try:
            # Get recent validation results for this integration
            conn = await db_manager.get_connection()
            try:
                recent_validations = await conn.fetch("""
                    SELECT status, COUNT(*) as count
                    FROM integration_validations
                    WHERE integration_name = $1
                    AND validation_time > NOW() - INTERVAL '1 hour'
                    GROUP BY status
                """, integration_point.value)
                
                total = sum(row['count'] for row in recent_validations)
                success = sum(row['count'] for row in recent_validations if row['status'] == 'success')
                
                if total == 0:
                    return {"status": "unknown", "message": "No recent validations"}
                
                success_rate = (success / total) * 100
                
                # Get average duration
                avg_duration = await conn.fetchval("""
                    SELECT AVG(CAST(actual_value->>'duration_ms' AS INTEGER))
                    FROM integration_validations
                    WHERE integration_name = $1
                    AND validation_time > NOW() - INTERVAL '1 hour'
                    AND actual_value->>'duration_ms' IS NOT NULL
                """, integration_point.value) or 0
                
                # Determine status
                if success_rate >= 95:
                    status = "healthy"
                elif success_rate >= 80:
                    status = "warning"
                else:
                    status = "error"
                
                return {
                    "status": status,
                    "success_rate": round(success_rate, 1),
                    "avg_duration_ms": int(avg_duration),
                    "total_validations": total
                }
            finally:
                await db_manager.release_connection(conn)
                
        except Exception as e:
            logger.error(f"Failed to check integration health: {e}")
            return {"status": "error", "error": str(e)}

# Singleton instance
integration_monitor = IntegrationMonitor()