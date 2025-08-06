"""
🔌 INTEGRATION HOOKS - Adds monitoring to existing JyotiFlow endpoints
Integrates monitoring without modifying core files.
"""

import time
import logging
from typing import Dict, Callable
from functools import wraps
from datetime import datetime, timezone

from .integration_monitor import get_integration_monitor, IntegrationPoint

logger = logging.getLogger(__name__)

class MonitoringHooks:
    """
    Hooks to integrate monitoring with existing JyotiFlow endpoints
    """
    
    @staticmethod
    def monitor_session(func: Callable) -> Callable:
        """Decorator to monitor a complete session flow"""
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get monitor instance using the thread-safe getter
            monitor = get_integration_monitor()
            
            session_id = kwargs.get("session_id") or f"session_{datetime.now(timezone.utc).timestamp()}"
            user_id = kwargs.get("user_id", 0)
            
            # Extract request data
            request_data = None
            for arg in args:
                if hasattr(arg, "dict"):  # Pydantic model
                    request_data = arg.dict()
                    break
                elif isinstance(arg, dict):
                    request_data = arg
                    break
            
            if request_data:
                # Start monitoring
                await monitor.start_session_monitoring(
                    session_id=session_id,
                    user_id=user_id,
                    birth_details=request_data.get("birth_details", {}),
                    spiritual_question=request_data.get("question", "") or request_data.get("user_input", ""),
                    service_type=request_data.get("service_type", "comprehensive_reading")
                )
            
            try:
                # Call original function
                result = await func(*args, **kwargs)
                
                # Complete monitoring
                monitor = get_integration_monitor()
                await monitor.complete_session_monitoring(session_id)
                
                return result
                
            except Exception as e:
                # Log error in monitoring
                monitor = get_integration_monitor()
                if session_id in monitor.active_sessions:
                    monitor.active_sessions[session_id]["overall_status"] = "failed"
                    monitor.active_sessions[session_id]["error"] = str(e)
                    await monitor.complete_session_monitoring(session_id)
                raise
                
        return wrapper
    
    @staticmethod
    def monitor_integration_point(integration_point: IntegrationPoint):
        """Decorator to monitor a specific integration point"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(*args, **kwargs):
                session_id = kwargs.get("session_id")
                
                # If no session_id, try to extract from args
                if not session_id:
                    for arg in args:
                        if isinstance(arg, dict) and "session_id" in arg:
                            session_id = arg["session_id"]
                            break
                
                if not session_id:
                    # Generate a temporary session ID
                    session_id = f"temp_{integration_point.value}_{datetime.now(timezone.utc).timestamp()}"
                
                # Capture input data
                input_data = {}
                for arg in args:
                    if hasattr(arg, "dict"):
                        input_data = arg.dict()
                        break
                    elif isinstance(arg, dict):
                        input_data = arg
                        break
                
                # Start timing
                start_time = time.time()
                
                try:
                    # Call original function
                    result = await func(*args, **kwargs)
                    
                    # Calculate duration
                    duration_ms = int((time.time() - start_time) * 1000)
                    
                    # Validate integration point
                    monitor = get_integration_monitor()
                if session_id in monitor.active_sessions:
                        output_data = result if isinstance(result, dict) else {"result": str(result)}
                        
                        try:
                            validation_result = await monitor.validate_integration_point(
                                session_id=session_id,
                                integration_point=integration_point,
                                input_data=input_data,
                                output_data=output_data,
                                duration_ms=duration_ms
                            )
                            
                            # Check if validation failed
                            if validation_result and not validation_result.get("passed", True):
                                logger.warning(
                                    f"Integration validation failed for {integration_point}: "
                                    f"{validation_result.get('errors', [])}"
                                )
                        except Exception as validation_error:
                            logger.error(f"Error during integration validation: {validation_error}")
                            # Continue execution even if monitoring fails
                    
                    return result
                    
                except Exception as e:
                    # Log integration failure
                    duration_ms = int((time.time() - start_time) * 1000)
                    
                    monitor = get_integration_monitor()
                if session_id in monitor.active_sessions:
                        try:
                            await monitor.validate_integration_point(
                                session_id=session_id,
                                integration_point=integration_point,
                                input_data=input_data,
                                output_data={"error": str(e)},
                                duration_ms=duration_ms
                            )
                        except Exception as validation_error:
                            logger.error(f"Error during integration validation: {validation_error}")
                    raise
                    
            return wrapper
        return decorator

# Specific monitoring hooks for each integration

async def monitor_prokerala_call(birth_details: Dict, prokerala_response: Dict, 
                                session_id: str, duration_ms: int):
    """Monitor Prokerala API call"""
    monitor = get_integration_monitor()
    await monitor.validate_integration_point(
        session_id=session_id,
        integration_point=IntegrationPoint.PROKERALA,
        input_data={"birth_details": birth_details},
        output_data=prokerala_response,
        duration_ms=duration_ms
    )

async def monitor_rag_retrieval(question: str, rag_response: Dict, 
                               session_id: str, duration_ms: int):
    """Monitor RAG knowledge retrieval"""
    monitor = get_integration_monitor()
    await monitor.validate_integration_point(
        session_id=session_id,
        integration_point=IntegrationPoint.RAG_KNOWLEDGE,
        input_data={"question": question},
        output_data=rag_response,
        duration_ms=duration_ms
    )

async def monitor_openai_generation(prompt: str, openai_response: Dict,
                                   session_id: str, duration_ms: int):
    """Monitor OpenAI response generation"""
    monitor = get_integration_monitor()
    await monitor.validate_integration_point(
        session_id=session_id,
        integration_point=IntegrationPoint.OPENAI_GUIDANCE,
        input_data={"prompt": prompt[:500]},  # Truncate long prompts
        output_data=openai_response,
        duration_ms=duration_ms
    )

async def monitor_elevenlabs_generation(text: str, voice_response: Dict,
                                       session_id: str, duration_ms: int):
    """Monitor ElevenLabs voice generation"""
    monitor = get_integration_monitor()
    await monitor.validate_integration_point(
        session_id=session_id,
        integration_point=IntegrationPoint.ELEVENLABS_VOICE,
        input_data={"text": text[:200]},  # Truncate long text
        output_data=voice_response,
        duration_ms=duration_ms
    )

async def monitor_did_generation(audio_url: str, avatar_response: Dict,
                                session_id: str, duration_ms: int):
    """Monitor D-ID avatar generation"""
    monitor = get_integration_monitor()
    await monitor.validate_integration_point(
        session_id=session_id,
        integration_point=IntegrationPoint.DID_AVATAR,
        input_data={"audio_url": audio_url},
        output_data=avatar_response,
        duration_ms=duration_ms
    )

async def monitor_social_media_action(platform: str, action_data: Dict,
                                     session_id: str, duration_ms: int):
    """Monitor social media actions"""
    monitor = get_integration_monitor()
    await monitor.validate_integration_point(
        session_id=session_id,
        integration_point=IntegrationPoint.SOCIAL_MEDIA,
        input_data={"platform": platform, **action_data},
        output_data=action_data.get("result", {}),
        duration_ms=duration_ms
    )

# Utility function to wrap existing functions with monitoring
def add_monitoring_to_function(original_func: Callable, 
                             integration_point: IntegrationPoint) -> Callable:
    """Add monitoring to an existing function without modifying it"""
    
    @wraps(original_func)
    async def monitored_func(*args, **kwargs):
        # Get monitor instance using the thread-safe getter
        monitor = get_integration_monitor()
        
        # Extract session_id from kwargs or generate one
        session_id = kwargs.get("session_id", f"auto_{datetime.now(timezone.utc).timestamp()}")
        
        # Start timing
        start_time = time.time()
        
        try:
            # Call original function
            result = await original_func(*args, **kwargs)
            
            # Calculate duration
            duration_ms = int((time.time() - start_time) * 1000)
            
            # Monitor the call
            await monitor.validate_integration_point(
                session_id=session_id,
                integration_point=integration_point,
                input_data={"args": str(args)[:200], "kwargs": str(kwargs)[:200]},
                output_data=result if isinstance(result, dict) else {"result": str(result)[:500]},
                duration_ms=duration_ms
            )
            
            return result
            
        except Exception as e:
            # Monitor the failure
            duration_ms = int((time.time() - start_time) * 1000)
            await monitor.validate_integration_point(
                session_id=session_id,
                integration_point=integration_point,
                input_data={"args": str(args)[:200], "kwargs": str(kwargs)[:200]},
                output_data={"error": str(e)},
                duration_ms=duration_ms
            )
            raise
    
    return monitored_func

# Export singleton instance
monitoring_hooks = MonitoringHooks()