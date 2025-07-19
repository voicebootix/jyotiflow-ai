# 🔍 JyotiFlow.ai Integrated Monitoring System

## Overview

The Integrated Monitoring System provides real-time observability for the JyotiFlow.ai platform, tracking API performance, integration health, user sessions, and business metrics.

## Architecture

### Core Components

1. **Integration Monitor** (`integration_monitor.py`)
   - Monitors external service integrations (Prokerala, OpenAI, ElevenLabs, etc.)
   - Tracks API response times and error rates
   - Provides health status for each integration

2. **Context Tracker** (`context_tracker.py`)
   - Tracks user session context
   - Monitors feature usage patterns
   - Provides insights into user behavior

3. **Business Validator** (`business_validator.py`)
   - Validates business rules and constraints
   - Tracks revenue metrics
   - Monitors credit usage and conversions

4. **Dashboard** (`dashboard.py`)
   - Real-time web dashboard
   - WebSocket support for live updates
   - API endpoints for metrics retrieval

5. **Core Integration** (`core_integration.py`)
   - Middleware for automatic API monitoring
   - Decorator support for custom monitoring
   - Integration with core_foundation_enhanced

## Database Schema

The monitoring system uses the following tables:

- `monitoring_api_calls` - Tracks all API requests
- `monitoring_sessions` - User session tracking
- `monitoring_integration_health` - Integration status
- `monitoring_integration_metrics` - Performance metrics
- `monitoring_alerts` - System alerts
- `monitoring_context` - Session context data
- `monitoring_business_metrics` - Business KPIs

## Setup

### 1. Database Setup

```bash
# Create monitoring tables
cd backend
python3 create_monitoring_tables.py
```

### 2. Environment Variables

```bash
export DATABASE_URL="postgresql://user:password@localhost:5432/yourdb"
```

### 3. Integration with FastAPI

The monitoring system is automatically integrated when the application starts:

```python
# In main.py
from monitoring.register_monitoring import register_monitoring_system, init_monitoring
from monitoring.core_integration import get_monitoring_middleware

# In lifespan context
await init_monitoring()

# Register monitoring
register_monitoring_system(app)
app.middleware("http")(get_monitoring_middleware())
```

## Usage

### Automatic Monitoring

All API endpoints are automatically monitored via middleware:
- Request/response times
- Status codes
- Error tracking
- User identification

### Custom Monitoring

Use decorators for specific monitoring:

```python
from monitoring.core_integration import monitor_endpoint

@router.post("/api/spiritual/guidance")
@monitor_endpoint("spiritual_guidance")
async def spiritual_guidance(request: Request):
    # Your endpoint logic
    pass
```

### Monitoring Hooks (Legacy)

The system also supports the legacy `@MonitoringHooks.monitor_session` decorator:

```python
from monitoring.hooks import MonitoringHooks

@router.post("/api/sessions/start")
@MonitoringHooks.monitor_session
async def start_session(request: Request):
    # Your endpoint logic
    pass
```

## Dashboard Access

Access the monitoring dashboard at:
- URL: `http://localhost:10000/monitoring/dashboard`
- Real-time metrics updates via WebSocket
- Integration health status
- Session analytics
- Alert management

## API Endpoints

- `GET /monitoring/api/metrics` - System metrics
- `GET /monitoring/api/health` - Health status
- `GET /monitoring/api/sessions` - Active sessions
- `GET /monitoring/api/alerts` - System alerts
- `GET /monitoring/api/integration/{name}` - Specific integration status

## Status Check

Run the status check script to verify the system:

```bash
cd backend
python3 check_monitoring_status.py
```

## Troubleshooting

### Database Connection Issues
- Ensure DATABASE_URL is set correctly
- Check PostgreSQL is running
- Verify database permissions

### Monitoring Not Capturing Data
- Check middleware is registered in main.py
- Verify monitoring tables exist
- Check application logs for errors

### Dashboard Not Loading
- Ensure monitoring router is registered
- Check port 10000 is accessible
- Verify static files are served

## Integration with Core Foundation Enhanced

The monitoring system integrates seamlessly with `core_foundation_enhanced.py`:
- Uses the same database connection pool
- Shares authentication context
- Provides health metrics to the enhanced health monitor

## Best Practices

1. **Don't Over-Monitor**: Focus on critical endpoints
2. **Use Async Operations**: All monitoring is non-blocking
3. **Set Appropriate Alerts**: Configure thresholds wisely
4. **Regular Cleanup**: Archive old monitoring data periodically
5. **Security**: Don't log sensitive data (passwords, tokens)

## Future Enhancements

- [ ] Grafana integration for advanced visualization
- [ ] Machine learning for anomaly detection
- [ ] Automated alert resolution
- [ ] Performance optimization recommendations
- [ ] Integration with external monitoring services

## Support

For issues or questions:
1. Check the status with `check_monitoring_status.py`
2. Review application logs
3. Check database connectivity
4. Verify all dependencies are installed