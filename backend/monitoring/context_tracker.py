"""
🔗 CONTEXT TRACKER - Preserves user context through the entire integration chain
Ensures no data loss between integration points and tracks context transformations.
"""

import asyncio
import json
import logging
import hashlib
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from enum import Enum

from db import db_manager
import logging
logger = logging.getLogger(__name__)
from database_timezone_fixer import safe_utc_now

logger = logging.getLogger(__name__)

class ContextTracker:
    """
    Tracks and validates context preservation through the entire
    spiritual guidance integration chain.
    """
    
    def __init__(self):
        self.session_contexts = {}
        self.context_snapshots = {}
        
    async def initialize_session(self, session_id: str, initial_context: Dict) -> bool:
        """Initialize context tracking for a new session"""
        try:
            # Create initial context snapshot
            self.session_contexts[session_id] = {
                "initial": initial_context.copy(),
                "current": initial_context.copy(),
                "transformations": [],
                "data_loss_detected": False,
                "context_chain": []
            }
            
            # Store initial snapshot
            await self._store_context_snapshot(
                session_id, "initial", initial_context
            )
            
            logger.info(f"✅ Initialized context tracking for session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize context tracking: {e}")
            return False
    
    async def update_context(self, session_id: str, integration_point: str,
                           input_data: Dict, output_data: Dict) -> Dict:
        """Update context after an integration point and check for data loss"""
        try:
            if session_id not in self.session_contexts:
                logger.warning(f"Session {session_id} not found in context tracker")
                return {"success": False, "error": "Session not found"}
            
            session_context = self.session_contexts[session_id]
            current_context = session_context["current"]
            
            # Create context snapshot before update
            before_snapshot = self._create_snapshot(current_context)
            
            # Track transformation
            transformation = {
                "integration_point": integration_point,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "input_keys": list(input_data.keys()),
                "output_keys": list(output_data.keys()),
                "data_preserved": True,
                "data_loss": []
            }
            
            # Check for critical context preservation
            critical_fields = self._get_critical_fields(integration_point)
            data_loss = []
            
            for field in critical_fields:
                if field in current_context and field not in output_data:
                    # Check if field is preserved in nested structure
                    if not self._field_exists_in_data(field, output_data):
                        data_loss.append({
                            "field": field,
                            "value": current_context[field],
                            "lost_at": integration_point
                        })
            
            if data_loss:
                transformation["data_preserved"] = False
                transformation["data_loss"] = data_loss
                session_context["data_loss_detected"] = True
                logger.warning(f"⚠️ Data loss detected at {integration_point}: {data_loss}")
            
            # Update current context with output data
            self._merge_context(current_context, output_data, integration_point)
            
            # Store transformation
            session_context["transformations"].append(transformation)
            
            # Add to context chain
            session_context["context_chain"].append({
                "integration_point": integration_point,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "context_snapshot": self._create_snapshot(current_context)
            })
            
            # Store context snapshot
            await self._store_context_snapshot(
                session_id, integration_point, current_context
            )
            
            return {
                "success": True,
                "data_preserved": transformation["data_preserved"],
                "data_loss": data_loss,
                "context_size": len(json.dumps(current_context))
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to update context: {e}")
            return {"success": False, "error": str(e)}
    
    async def validate_context_integrity(self, session_id: str) -> Dict:
        """Validate that critical context has been preserved throughout the chain"""
        try:
            if session_id not in self.session_contexts:
                return {"valid": False, "error": "Session not found"}
            
            session_context = self.session_contexts[session_id]
            initial_context = session_context["initial"]
            current_context = session_context["current"]
            
            validation_result = {
                "valid": True,
                "integrity_score": 100.0,
                "missing_critical_data": [],
                "context_transformations": len(session_context["transformations"]),
                "data_loss_events": []
            }
            
            # Check critical fields preservation
            critical_fields = {
                "session_id": "Session identifier",
                "user_id": "User identifier",
                "birth_details": "Birth chart information",
                "spiritual_question": "User's original question",
                "service_type": "Selected service type"
            }
            
            for field, description in critical_fields.items():
                if field in initial_context:
                    if field not in current_context:
                        validation_result["missing_critical_data"].append({
                            "field": field,
                            "description": description,
                            "initial_value": initial_context[field]
                        })
                        validation_result["valid"] = False
            
            # Check for data loss events
            for transformation in session_context["transformations"]:
                if not transformation["data_preserved"]:
                    validation_result["data_loss_events"].append({
                        "integration_point": transformation["integration_point"],
                        "timestamp": transformation["timestamp"],
                        "lost_data": transformation["data_loss"]
                    })
            
            # Calculate integrity score
            total_fields = len(critical_fields)
            preserved_fields = total_fields - len(validation_result["missing_critical_data"])
            validation_result["integrity_score"] = (preserved_fields / total_fields) * 100
            
            # Check context enrichment
            validation_result["context_enriched"] = len(current_context) > len(initial_context)
            validation_result["new_fields_added"] = list(
                set(current_context.keys()) - set(initial_context.keys())
            )
            
            return validation_result
            
        except Exception as e:
            logger.error(f"❌ Failed to validate context integrity: {e}")
            return {"valid": False, "error": str(e)}
    
    async def get_context_flow_report(self, session_id: str) -> Dict:
        """Generate a detailed report of context flow through integration chain"""
        try:
            if session_id not in self.session_contexts:
                return {"success": False, "error": "Session not found"}
            
            session_context = self.session_contexts[session_id]
            
            report = {
                "session_id": session_id,
                "context_flow": [],
                "data_loss_detected": session_context["data_loss_detected"],
                "total_transformations": len(session_context["transformations"]),
                "context_size_growth": self._calculate_context_growth(session_context)
            }
            
            # Build context flow visualization
            for i, chain_item in enumerate(session_context["context_chain"]):
                flow_item = {
                    "step": i + 1,
                    "integration_point": chain_item["integration_point"],
                    "timestamp": chain_item["timestamp"],
                    "context_keys": list(chain_item["context_snapshot"].keys()),
                    "context_size": len(json.dumps(chain_item["context_snapshot"]))
                }
                
                # Check what changed from previous step
                if i > 0:
                    prev_snapshot = session_context["context_chain"][i-1]["context_snapshot"]
                    curr_snapshot = chain_item["context_snapshot"]
                    
                    flow_item["fields_added"] = list(
                        set(curr_snapshot.keys()) - set(prev_snapshot.keys())
                    )
                    flow_item["fields_removed"] = list(
                        set(prev_snapshot.keys()) - set(curr_snapshot.keys())
                    )
                    flow_item["fields_modified"] = self._find_modified_fields(
                        prev_snapshot, curr_snapshot
                    )
                
                report["context_flow"].append(flow_item)
            
            return report
            
        except Exception as e:
            logger.error(f"❌ Failed to generate context flow report: {e}")
            return {"success": False, "error": str(e)}
    
    # Private helper methods
    def _get_critical_fields(self, integration_point: str) -> List[str]:
        """Get critical fields that must be preserved at each integration point"""
        base_fields = ["session_id", "user_id", "spiritual_question", "service_type"]
        
        critical_fields_map = {
            "prokerala": base_fields + ["birth_details"],
            "rag_knowledge": base_fields + ["birth_details", "prokerala_data"],
            "openai_guidance": base_fields + ["birth_details", "prokerala_data", "rag_knowledge"],
            "elevenlabs_voice": base_fields + ["openai_response"],
            "did_avatar": base_fields + ["openai_response", "elevenlabs_audio_url"],
            "social_media": base_fields + ["content_text", "platform"]
        }
        
        return critical_fields_map.get(integration_point, base_fields)
    
    def _field_exists_in_data(self, field: str, data: Dict) -> bool:
        """Check if a field exists anywhere in nested data structure"""
        if field in data:
            return True
            
        for value in data.values():
            if isinstance(value, dict):
                if self._field_exists_in_data(field, value):
                    return True
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict) and self._field_exists_in_data(field, item):
                        return True
        
        return False
    
    def _merge_context(self, current_context: Dict, new_data: Dict, integration_point: str):
        """Merge new data into current context intelligently"""
        # Map integration points to their output field names
        output_field_map = {
            "prokerala": "prokerala_data",
            "rag_knowledge": "rag_knowledge",
            "openai_guidance": "openai_response",
            "elevenlabs_voice": "elevenlabs_audio_url",
            "did_avatar": "did_video_url",
            "social_media": "social_media_result"
        }
        
        # Store the output in the appropriate field
        if integration_point in output_field_map:
            current_context[output_field_map[integration_point]] = new_data
        
        # Also merge any top-level fields that don't conflict
        for key, value in new_data.items():
            if key not in current_context:
                current_context[key] = value
    
    def _create_snapshot(self, context: Dict) -> Dict:
        """Create a snapshot of context for comparison"""
        # Create a deep copy but exclude large binary data
        snapshot = {}
        for key, value in context.items():
            if isinstance(value, (str, int, float, bool, list, dict)):
                if key not in ["audio_data", "video_data", "image_data"]:  # Exclude binary
                    if isinstance(value, (dict, list)):
                        snapshot[key] = json.loads(json.dumps(value))  # Deep copy
                    else:
                        snapshot[key] = value
        return snapshot
    
    async def _store_context_snapshot(self, session_id: str, integration_point: str, context: Dict):
        """Store context snapshot in database for debugging"""
        try:
            snapshot = self._create_snapshot(context)
            context_hash = hashlib.md5(json.dumps(snapshot, sort_keys=True).encode()).hexdigest()
            
            conn = await db_manager.get_connection()
            try:
                await conn.execute("""
                    INSERT INTO context_snapshots 
                    (session_id, integration_point, context_data, context_hash, created_at)
                    VALUES ($1, $2, $3, $4, $5)
                """, session_id, integration_point, json.dumps(snapshot), 
                    context_hash, safe_utc_now())
            finally:
                await db_manager.release_connection(conn)
                    
        except Exception as e:
            logger.error(f"Failed to store context snapshot: {e}")
    
    def _calculate_context_growth(self, session_context: Dict) -> Dict:
        """Calculate how context size grew through the chain"""
        initial_size = len(json.dumps(session_context["initial"]))
        current_size = len(json.dumps(session_context["current"]))
        
        return {
            "initial_size_bytes": initial_size,
            "final_size_bytes": current_size,
            "growth_percentage": ((current_size - initial_size) / initial_size) * 100 if initial_size > 0 else 0,
            "size_healthy": current_size < 1_000_000  # Warn if context exceeds 1MB
        }
    
    def _find_modified_fields(self, prev_snapshot: Dict, curr_snapshot: Dict) -> List[str]:
        """Find fields that were modified between snapshots"""
        modified = []
        
        for key in set(prev_snapshot.keys()) & set(curr_snapshot.keys()):
            if json.dumps(prev_snapshot[key]) != json.dumps(curr_snapshot[key]):
                modified.append(key)
        
        return modified