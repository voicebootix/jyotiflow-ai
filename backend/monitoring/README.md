# 📊 JyotiFlow Integration Monitoring System

## Overview

The JyotiFlow Integration Monitoring System provides real-time validation and monitoring of the entire spiritual guidance flow, from user input through various AI integrations to final response delivery. It also monitors social media automation workflows.

## Features

### 1. **Real-Time Integration Monitoring**
- Tracks every API call in the integration chain
- Validates responses for completeness and accuracy
- Detects silent failures where APIs succeed but return invalid data
- Measures performance metrics for each integration

### 2. **Business Logic Validation**
- **RAG Relevance Validation** (User specifically requested)
  - Keyword matching analysis
  - Domain relevance scoring
  - Semantic similarity calculation
  - Cultural authenticity checking
- **Prokerala Birth Chart Validation**
  - Planetary data completeness
  - Nakshatra accuracy
  - Data sanity checks
- **OpenAI Response Quality**
  - Swami persona consistency
  - Context incorporation validation
  - Harmful content detection

### 3. **Social Media Automation Validation**
- Credential validation for all platforms
- Content quality scoring
- Posting workflow validation
- Rate limit monitoring

### 4. **Context Preservation Tracking**
- Ensures user data flows correctly through all integrations
- Detects data loss between integration points
- Maintains audit trail of context transformations

### 5. **Auto-Fix Mechanisms**
- Automatic retry with exponential backoff
- Query enhancement for better RAG retrieval
- Prompt regeneration for OpenAI
- Token refresh for social media

## Installation

### 1. Run Database Migration

```bash
cd backend
python migrations/add_validation_tracking_tables.py
```

### 2. Register Monitoring in main.py

Add these lines to your `main.py`:

```python
# Import monitoring system
from monitoring.register_monitoring import register_monitoring_system

# After creating the FastAPI app
app = FastAPI(...)

# Register monitoring (add after other routers)
register_monitoring_system(app)
```

## API Endpoints

### Dashboard Endpoints

#### Get Dashboard Overview
```
GET /api/monitoring/dashboard
Authorization: Bearer <admin_token>
```

Returns comprehensive dashboard data including:
- System health status
- Active sessions
- Recent validation failures
- Integration performance metrics
- Social media health

#### Get Session Details
```
GET /api/monitoring/session/{session_id}
Authorization: Bearer <admin_token>
```

Returns detailed validation report for a specific session.

#### Get Integration Health
```
GET /api/monitoring/integration/{integration_point}/health
Authorization: Bearer <admin_token>
```

Integration points: `prokerala`, `rag_knowledge`, `openai_guidance`, `elevenlabs_voice`, `did_avatar`, `social_media`

#### Trigger Validation Test
```
POST /api/monitoring/test/{test_type}
Authorization: Bearer <admin_token>
```

Test types: `full_flow`, `social_media`

### WebSocket Real-Time Updates
```
WS /api/monitoring/ws
```

Connects to real-time monitoring updates (system health every 5 seconds).

## Integration with Existing Code

### Option 1: Using Decorators (Recommended)

```python
from monitoring.integration_hooks import MonitoringHooks, monitor_prokerala_call

# For complete session monitoring
@MonitoringHooks.monitor_session
async def handle_spiritual_guidance(request_data: dict):
    # Your existing code
    pass

# For specific integration monitoring
@MonitoringHooks.monitor_integration_point(IntegrationPoint.PROKERALA)
async def get_birth_chart(birth_details: dict):
    # Your existing Prokerala API call
    pass
```

### Option 2: Manual Integration

```python
import time
from monitoring.integration_hooks import monitor_prokerala_call

async def get_birth_chart(birth_details: dict, session_id: str):
    start_time = time.time()
    
    # Your existing Prokerala API call
    response = await call_prokerala_api(birth_details)
    
    # Add monitoring
    duration_ms = int((time.time() - start_time) * 1000)
    await monitor_prokerala_call(birth_details, response, session_id, duration_ms)
    
    return response
```

## Dashboard UI Integration

The monitoring dashboard is designed to integrate with your existing admin dashboard. Add a new menu item:

```javascript
// In your admin dashboard navigation
{
  label: 'System Monitoring',
  icon: 'ChartBarIcon',
  href: '/admin/monitoring',
  badge: systemHealth.issues_count // Optional badge for alerts
}
```

### Dashboard Components

1. **System Health Widget**
```javascript
// Shows overall system status
<SystemHealthWidget />
```

2. **Integration Status Grid**
```javascript
// Shows each integration point health
<IntegrationStatusGrid />
```

3. **Recent Sessions Table**
```javascript
// Lists recent sessions with validation status
<RecentSessionsTable />
```

4. **Real-Time Alerts**
```javascript
// WebSocket connection for live alerts
<RealTimeAlerts wsUrl="/api/monitoring/ws" />
```

## Validation Rules

### RAG Relevance Validation (Comprehensive)

The system uses multiple methods to validate RAG knowledge relevance:

1. **Keyword Match Score (25%)**: Analyzes overlap between question and retrieved knowledge keywords
2. **Domain Match Score (30%)**: Ensures knowledge domain matches question type
3. **Astrological Relevance (20%)**: Validates astrological references are appropriate
4. **Semantic Similarity (15%)**: Uses OpenAI embeddings for semantic comparison
5. **Cultural Authenticity (10%)**: Checks Tamil/Vedic cultural relevance

**Threshold**: Overall relevance must be > 0.65 (65%)

### Social Media Content Validation

Content is validated for:
- Platform-specific character limits
- Hashtag optimization
- Spiritual authenticity (minimum 2 spiritual keywords)
- Engagement potential (questions, CTAs, or emojis)
- Brand consistency

**Threshold**: Quality score must be > 0.6 (60%)

## Monitoring Best Practices

### 1. Session ID Management
Always use consistent session IDs across your integration chain:

```python
session_id = f"session_{user_id}_{timestamp}"
# Pass this session_id to all integration calls
```

### 2. Error Handling
The monitoring system won't interfere with your application flow:

```python
try:
    result = await your_integration_call()
    # Monitoring happens automatically
except Exception as e:
    # Monitoring will capture the error
    # Your error handling continues normally
    raise
```

### 3. Performance Considerations
- Monitoring adds < 50ms overhead per integration
- Validation runs asynchronously
- Database writes are batched for performance

### 4. Alert Management
Configure alert thresholds in your environment:

```bash
MONITORING_ERROR_THRESHOLD=20  # Alert if error rate > 20%
MONITORING_PERFORMANCE_THRESHOLD=5000  # Alert if response > 5 seconds
```

## Troubleshooting

### Common Issues

1. **"Session not found" errors**
   - Ensure you're starting monitoring before making integration calls
   - Check session_id is being passed correctly

2. **Missing validations**
   - Verify the integration point is wrapped with monitoring
   - Check logs for validation errors

3. **Database connection issues**
   - Ensure validation tables are created
   - Check database connection pool settings

### Debug Mode

Enable debug logging:

```python
import logging
logging.getLogger("monitoring").setLevel(logging.DEBUG)
```

## Production Deployment

### 1. Environment Variables
```bash
# Required
DATABASE_URL=postgresql://...
OPENAI_API_KEY=sk-...

# Optional monitoring config
MONITORING_ENABLED=true
MONITORING_SAMPLE_RATE=1.0  # Monitor 100% of sessions
MONITORING_ALERT_WEBHOOK=https://your-webhook.com/alerts
```

### 2. Database Indexes
The migration creates necessary indexes, but for high-volume production:

```sql
-- Additional indexes for performance
CREATE INDEX idx_validation_sessions_user_date 
ON validation_sessions(user_id, started_at DESC);

CREATE INDEX idx_integration_validations_status 
ON integration_validations(integration_name, status);
```

### 3. Retention Policy
Set up a job to clean old monitoring data:

```python
# Run daily
async def cleanup_old_monitoring_data():
    await db.execute("""
        DELETE FROM validation_sessions 
        WHERE created_at < NOW() - INTERVAL '30 days'
    """)
```

## Support

For issues or questions about the monitoring system:
1. Check the logs in `jyotiflow_enhanced.log`
2. Review validation results in the dashboard
3. Enable debug mode for detailed troubleshooting

## Future Enhancements

- Machine learning for anomaly detection
- Predictive failure alerts
- Custom validation rule builder
- Integration with external monitoring tools (Datadog, New Relic)
- Mobile app for monitoring on-the-go