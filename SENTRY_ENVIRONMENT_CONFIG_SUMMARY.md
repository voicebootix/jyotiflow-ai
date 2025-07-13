# Sentry Environment Variable Configuration Summary

## Changes Made
Updated the Sentry initialization in `backend/main.py` to use environment variables with production-safe defaults instead of hardcoded values.

## Problem Solved
The previous implementation used hardcoded values that were risky for production:
- `traces_sample_rate=1.0` (100% sampling - high performance impact)
- `send_default_pii=True` (sends personally identifiable information - privacy risk)

## New Implementation

### Before (Hardcoded Values):
```python
sentry_sdk.init(
    dsn=sentry_dsn,
    traces_sample_rate=1.0,
    send_default_pii=True,
)
```

### After (Environment Variables with Error Handling):
```python
# Read Sentry configuration from environment variables with production-safe defaults
# Parse traces_sample_rate with proper error handling
try:
    traces_sample_rate = float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.1"))
    # Validate that the value is within the valid range (0.0 to 1.0)
    if not (0.0 <= traces_sample_rate <= 1.0):
        print(f"⚠️ Invalid SENTRY_TRACES_SAMPLE_RATE value: {traces_sample_rate}. Must be between 0.0 and 1.0. Using default: 0.1")
        traces_sample_rate = 0.1
except (ValueError, TypeError) as e:
    env_value = os.getenv("SENTRY_TRACES_SAMPLE_RATE")
    print(f"⚠️ Invalid SENTRY_TRACES_SAMPLE_RATE value: '{env_value}'. Must be a number between 0.0 and 1.0. Using default: 0.1")
    traces_sample_rate = 0.1

send_default_pii = os.getenv("SENTRY_SEND_DEFAULT_PII", "false").lower() in ("true", "1", "yes", "on")

sentry_sdk.init(
    dsn=sentry_dsn,
    traces_sample_rate=traces_sample_rate,
    send_default_pii=send_default_pii,
)
```

## Environment Variables

### `SENTRY_TRACES_SAMPLE_RATE`
- **Purpose**: Controls the percentage of transactions sent to Sentry for performance monitoring
- **Type**: Float (0.0 to 1.0)
- **Default**: `0.1` (10% sampling)
- **Examples**:
  - `SENTRY_TRACES_SAMPLE_RATE=0.1` - 10% sampling (recommended for production)
  - `SENTRY_TRACES_SAMPLE_RATE=1.0` - 100% sampling (for development/testing)
  - `SENTRY_TRACES_SAMPLE_RATE=0.01` - 1% sampling (for high-traffic production)

### `SENTRY_SEND_DEFAULT_PII`
- **Purpose**: Controls whether personally identifiable information is sent to Sentry
- **Type**: Boolean
- **Default**: `false` (no PII data sent)
- **Accepted Values**: `true`, `1`, `yes`, `on` (case-insensitive) for true; anything else for false
- **Examples**:
  - `SENTRY_SEND_DEFAULT_PII=false` - No PII data (recommended for production)
  - `SENTRY_SEND_DEFAULT_PII=true` - Include PII data (for development/debugging)

## Production-Safe Defaults

### `traces_sample_rate=0.1` (10% sampling)
- **Benefits**:
  - Reduced performance impact on production systems
  - Lower Sentry quota usage
  - Still provides sufficient data for performance monitoring
  - Balances observability with system performance

### `send_default_pii=False` (no PII data)
- **Benefits**:
  - Complies with privacy regulations (GDPR, CCPA, etc.)
  - Reduces risk of accidentally exposing sensitive user data
  - Follows security best practices
  - Can be enabled selectively for debugging when needed

## Configuration Examples

### Development Environment
```bash
export SENTRY_DSN="https://your-dsn@sentry.io/project-id"
export SENTRY_TRACES_SAMPLE_RATE=1.0
export SENTRY_SEND_DEFAULT_PII=true
```

### Production Environment
```bash
export SENTRY_DSN="https://your-dsn@sentry.io/project-id"
export SENTRY_TRACES_SAMPLE_RATE=0.1
export SENTRY_SEND_DEFAULT_PII=false
```

### High-Traffic Production
```bash
export SENTRY_DSN="https://your-dsn@sentry.io/project-id"
export SENTRY_TRACES_SAMPLE_RATE=0.01
export SENTRY_SEND_DEFAULT_PII=false
```

## Deployment Configuration

### Render.com
In your Render dashboard, add these environment variables:
```
SENTRY_TRACES_SAMPLE_RATE=0.1
SENTRY_SEND_DEFAULT_PII=false
```

### Docker/Docker Compose
```yaml
environment:
  - SENTRY_DSN=https://your-dsn@sentry.io/project-id
  - SENTRY_TRACES_SAMPLE_RATE=0.1
  - SENTRY_SEND_DEFAULT_PII=false
```

### Kubernetes
```yaml
env:
  - name: SENTRY_TRACES_SAMPLE_RATE
    value: "0.1"
  - name: SENTRY_SEND_DEFAULT_PII
    value: "false"
```

## Enhanced Logging
The initialization now provides detailed logging showing the actual configuration values used:
```
✅ Sentry initialized successfully (traces_sample_rate=0.1, send_default_pii=False)
```

## Benefits

### 1. **Configuration Flexibility**
- Change settings without code deployments
- Different configurations for different environments
- Easy A/B testing of sampling rates

### 2. **Production Safety**
- Safe defaults that won't impact performance
- Privacy-compliant by default
- Reduced risk of accidental misconfigurations

### 3. **Cost Optimization**
- Lower Sentry quota usage with reduced sampling
- Optimized performance monitoring overhead
- Better resource utilization

### 4. **Security & Compliance**
- No PII data sent by default
- Complies with privacy regulations
- Configurable for specific compliance requirements

## Error Handling

### `SENTRY_TRACES_SAMPLE_RATE` Error Handling
The application now includes robust error handling for invalid `traces_sample_rate` values:

**Handled Error Cases:**
- **Non-numeric values**: `"abc"`, `"invalid"`, `""`
- **Out-of-range values**: `"-0.1"`, `"1.5"`, `"2.0"`
- **Empty or missing values**: Uses default `0.1`

**Example Error Messages:**
```
⚠️ Invalid SENTRY_TRACES_SAMPLE_RATE value: 'abc'. Must be a number between 0.0 and 1.0. Using default: 0.1
⚠️ Invalid SENTRY_TRACES_SAMPLE_RATE value: 1.5. Must be between 0.0 and 1.0. Using default: 0.1
```

**Graceful Fallback:**
- Application continues to start normally
- Falls back to safe default value (0.1)
- Logs warning message for debugging
- No application crashes or startup failures

## Troubleshooting

### Invalid `traces_sample_rate` value
The application now gracefully handles invalid values and will not crash. Check the logs for warning messages about invalid values.

### Boolean parsing for `send_default_pii`
The following values are considered `true` (case-insensitive):
- `true`
- `1`
- `yes`
- `on`

All other values (including empty string) are considered `false`.

### Verification
Check the application logs for the Sentry initialization message to verify the configuration is being applied correctly. Warning messages will appear for invalid values.

This configuration provides a robust, production-ready Sentry setup that balances observability with performance and privacy requirements.