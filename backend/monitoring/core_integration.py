"""
🔌 MONITORING CORE INTEGRATION
Integrates the monitoring system with core_foundation_enhanced
"""

import asyncio
from typing import Optional
from functools import wraps
import time
from fastapi import Request

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
        from starlette.middleware.base import BaseHTTPMiddleware
        import time
        
        # Store reference to self for the middleware class
        monitoring_integration = self
        
        class MonitoringMiddleware(BaseHTTPMiddleware):
            def __init__(self, app):
                super().__init__(app)
                self.monitoring_integration = monitoring_integration
                
            async def dispatch(self, request: Request, call_next):
                """Middleware to monitor all API calls"""
                start_time = time.time()
                
                # Extract request info
                endpoint = str(request.url.path)
                method = request.method
                
                # Skip monitoring endpoints to avoid recursion
                # All monitoring endpoints are under /api/monitoring prefix
                if endpoint.startswith("/api/monitoring") or endpoint.startswith("/monitoring/ws"):
                    return await call_next(request)
                
                # Store request info for later use
                request.state.monitoring_start_time = start_time
                
                try:
                    # Process request
                    response = await call_next(request)
                    
                    # Calculate response time
                    response_time = int((time.time() - start_time) * 1000)  # ms
                    
                    # Log API call asynchronously
                    asyncio.create_task(self.monitoring_integration._log_api_call(
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
                    
                    asyncio.create_task(self.monitoring_integration._log_api_call(
                        endpoint=endpoint,
                        method=method,
                        status_code=500,
                        response_time=response_time,
                        request=request,
                        error=str(e)
                    ))
                    
                    # Re-raise the exception
                    raise
        
        return MonitoringMiddleware
        
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
            
            # Get request body safely without consuming it
            request_body = None
            if method in ["POST", "PUT", "PATCH"]:
                try:
                    # Try to get body from request state if already read
                    if hasattr(request.state, "_json"):
                        request_body = str(request.state._json)
                    elif hasattr(request.state, "_body"):
                        request_body = request.state._body.decode("utf-8") if request.state._body else None
                    # Note: We cannot read request.body() here as it would consume the stream
                    # The body should be captured by endpoint handlers and stored in request.state
                except (AttributeError, UnicodeDecodeError):
                    pass
            
            conn = await db_manager.get_connection()
            try:
                await conn.execute("""
                    INSERT INTO monitoring_api_calls 
                    (endpoint, method, status_code, response_time, user_id, request_body, error, timestamp)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, NOW())
                """, endpoint, method, status_code, response_time, user_id, request_body, error)
            finally:
                await db_manager.release_connection(conn)
                
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