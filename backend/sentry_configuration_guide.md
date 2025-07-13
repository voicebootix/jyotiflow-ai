# Sentry Configuration Guide for JyotiFlow.ai

## Overview
Sentry provides error monitoring and performance tracking for your JyotiFlow.ai application. It's optional but highly recommended for production deployments.

## Configuration

### 1. Get Your Sentry DSN
1. Sign up at [sentry.io](https://sentry.io)
2. Create a new project for your JyotiFlow.ai application
3. Copy the DSN (Data Source Name) from your project settings

### 2. Set Environment Variable
Add the following environment variable to your deployment:

```bash
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
```

### 3. Optional Configuration
You can also set these optional environment variables:

```bash
# Environment name (default: development)
APP_ENV=production

# Sample rate for performance traces (default: 0.1 = 10%)
SENTRY_TRACES_SAMPLE_RATE=0.1
```

## What Sentry Monitors

### Error Tracking
- Unhandled exceptions
- API errors
- Database connection issues
- Authentication failures

### Performance Monitoring
- API response times
- Database query performance
- External API calls (OpenAI, etc.)
- User session tracking

### Integrations
- FastAPI framework
- PostgreSQL database
- AsyncPG connection pool
- OpenAI API calls

## Benefits

1. **Real-time Error Alerts**: Get notified immediately when errors occur
2. **Performance Insights**: Monitor application performance and identify bottlenecks
3. **User Impact Analysis**: Understand how errors affect your users
4. **Release Tracking**: Monitor the health of new deployments
5. **Issue Resolution**: Detailed stack traces and context for faster debugging

## Current Status
- ✅ Sentry integration code is implemented
- ⚠️ DSN not configured (optional)
- ✅ Graceful fallback when not configured
- ✅ Comprehensive error handling

## Testing Sentry
Once configured, you can test Sentry by triggering an error:

```python
# This will be captured by Sentry if configured
raise Exception("Test error for Sentry monitoring")
```

## Security
- Sentry automatically filters sensitive data
- No passwords or API keys are sent to Sentry
- User data is anonymized by default
- You can configure additional data filtering if needed

## Cost
- Sentry offers a generous free tier
- Most small to medium applications stay within free limits
- Paid plans available for high-volume applications