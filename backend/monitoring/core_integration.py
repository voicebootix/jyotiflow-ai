"""
🔌 MONITORING CORE INTEGRATION
Integrates the monitoring system with core_foundation_enhanced
"""

import asyncio
import os
from datetime import datetime
from typing import Dict, Any, Optional
from functools import wraps
import time
import json

# Import monitoring components
from .integration_monitor import IntegrationMonitor
from .context_tracker import ContextTracker
from .business_validator import BusinessValidator

# Database manager
try:
    from db_manager import db_manager
except ImportError:
    print("⚠️ db_manager not available, monitoring will run in limited mode")
    db_manager = None

# Logger
import logging
logger = logging.getLogger(__name__)

class MonitoringCoreIntegration:
    """Core integration for monitoring system"""
    
    def __init__(self):
        self.integration_monitor = IntegrationMonitor()
        self.context_tracker = ContextTracker()
        self.business_validator = BusinessValidator()
        self.initialized = False
        
    async def initialize(self):
        """Initialize monitoring system"""
        try:
            logger.info("🚀 Initializing monitoring core integration...")
            
            # Start background monitoring tasks
            asyncio.create_task(self.integration_monitor.start_monitoring())
            
            self.initialized = True
            logger.info("✅ Monitoring core integration initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize monitoring: {e}")
            raise
            
    def create_middleware(self):
        """Create FastAPI middleware for monitoring"""
        from fastapi import Request, Response
        from fastapi.responses import JSONResponse
        import time
        
        async def monitoring_middleware(request: Request, call_next):
            """Middleware to monitor all API calls"""
            start_time = time.time()
            
            # Extract request info
            endpoint = str(request.url.path)
            method = request.method
            
            # Skip monitoring endpoints to avoid recursion
            if endpoint.startswith("/monitoring"):
                return await call_next(request)
            
            try:
                # Process request
                response = await call_next(request)
                
                # Calculate response time
                response_time = int((time.time() - start_time) * 1000)  # ms
                
                # Log API call asynchronously
                asyncio.create_task(self._log_api_call(
                    endpoint=endpoint,
                    method=method,
                    status_code=response.status_code,
                    response_time=response_time,
                    request=request
                ))
                
                return response
                
            except Exception as e:
                # Log error
                response_time = int((time.time() - start_time) * 1000)
                
                asyncio.create_task(self._log_api_call(
                    endpoint=endpoint,
                    method=method,
                    status_code=500,
                    response_time=response_time,
                    request=request,
                    error=str(e)
                ))
                
                # Re-raise the exception
                raise
                
        return monitoring_middleware
        
    async def _log_api_call(self, endpoint: str, method: str, status_code: int, 
                           response_time: int, request: Request, error: Optional[str] = None):
        """Log API call to database"""
        if not db_manager:
            return
            
        try:
            # Extract user info if available
            user_id = None
            if hasattr(request.state, "user"):
                user_id = getattr(request.state.user, "id", None)
            
            # Get request body safely
            request_body = None
            if method in ["POST", "PUT", "PATCH"]:
                try:
                    # Store body for later reading
                    if not hasattr(request.state, "_body"):
                        request.state._body = await request.body()
                    request_body = request.state._body.decode("utf-8") if request.state._body else None
                except:
                    pass
            
            async with db_manager.get_connection() as conn:
                await conn.execute("""
                    INSERT INTO monitoring_api_calls 
                    (endpoint, method, status_code, response_time, user_id, request_body, error, timestamp)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, NOW())
                """, endpoint, method, status_code, response_time, user_id, request_body, error)
                
        except Exception as e:
            logger.error(f"Failed to log API call: {e}")
            
    def monitor_endpoint(self, endpoint_name: str):
        """Decorator to monitor specific endpoints"""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                start_time = time.time()
                
                try:
                    # Execute the endpoint
                    result = await func(*args, **kwargs)
                    
                    # Track successful execution
                    execution_time = time.time() - start_time
                    asyncio.create_task(self._track_endpoint_execution(
                        endpoint_name, True, execution_time
                    ))
                    
                    return result
                    
                except Exception as e:
                    # Track failed execution
                    execution_time = time.time() - start_time
                    asyncio.create_task(self._track_endpoint_execution(
                        endpoint_name, False, execution_time, str(e)
                    ))
                    raise
                    
            return wrapper
        return decorator
        
    async def _track_endpoint_execution(self, endpoint_name: str, success: bool, 
                                      execution_time: float, error: Optional[str] = None):
        """Track endpoint execution metrics"""
        try:
            # Update integration metrics
            await self.integration_monitor.update_metrics(
                integration_name=endpoint_name,
                metric_type="endpoint_execution",
                value=1,
                metadata={
                    "success": success,
                    "execution_time": execution_time,
                    "error": error
                }
            )
        except Exception as e:
            logger.error(f"Failed to track endpoint execution: {e}")

# Global instance
monitoring_integration = MonitoringCoreIntegration()

# Export convenience functions
async def init_monitoring():
    """Initialize monitoring system"""
    await monitoring_integration.initialize()

def get_monitoring_middleware():
    """Get monitoring middleware for FastAPI"""
    return monitoring_integration.create_middleware()

def monitor_endpoint(endpoint_name: str):
    """Decorator to monitor endpoints"""
    return monitoring_integration.monitor_endpoint(endpoint_name)

__all__ = ['monitoring_integration', 'init_monitoring', 'get_monitoring_middleware', 'monitor_endpoint']