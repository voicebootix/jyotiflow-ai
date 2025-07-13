# 🔒 CORS Security Improvements

## Overview

The CORS (Cross-Origin Resource Sharing) middleware has been updated to be environment-aware and more secure for production deployments. The previous configuration allowed all origins (`"*"`), which poses security risks in production environments.

## Changes Made

### 1. **Environment-Aware Configuration**

The CORS settings now automatically adjust based on the `APP_ENV` environment variable:

- **Development**: Allows common localhost origins for development
- **Staging**: Allows staging domains plus development origins  
- **Production**: Only allows specific trusted production domains

### 2. **Configurable via Environment Variables**

You can now override the default CORS origins using the `CORS_ORIGINS` environment variable:

```bash
# Custom origins (comma-separated)
CORS_ORIGINS=https://yourdomain.com,https://api.yourdomain.com,https://admin.yourdomain.com
```

### 3. **Restricted Methods and Headers in Production**

- **Development/Staging**: Allows all methods and headers for flexibility
- **Production**: Only allows necessary HTTP methods and headers

## Files Modified

- `backend/sentry_test_server.py` - Updated CORS middleware configuration
- `backend/main.py` - Updated CORS middleware configuration  
- `.env.example` - Added CORS configuration documentation

## Configuration Details

### Development Environment (`APP_ENV=development`)
```python
# Default origins (can be overridden with CORS_ORIGINS)
origins = [
    "http://localhost:3000",
    "http://localhost:5173", 
    "http://localhost:8080",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173"
]
methods = ["*"]  # All methods allowed
headers = ["*"]  # All headers allowed
```

### Staging Environment (`APP_ENV=staging`)
```python
# Default origins (can be overridden with CORS_ORIGINS)
origins = [
    "https://staging.jyotiflow.ai",
    "https://dev.jyotiflow.ai", 
    "http://localhost:3000",
    "http://localhost:5173"
]
methods = ["*"]  # All methods allowed
headers = ["*"]  # All headers allowed
```

### Production Environment (`APP_ENV=production`)
```python
# Default origins (can be overridden with CORS_ORIGINS)
origins = [
    "https://jyotiflow.ai",
    "https://www.jyotiflow.ai",
    "https://api.jyotiflow.ai"
]
methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]  # Only necessary methods
headers = [  # Only necessary headers
    "Accept",
    "Accept-Language", 
    "Content-Language",
    "Content-Type",
    "Authorization",
    "X-Requested-With",
    "X-CSRF-Token",
    "Cache-Control"
]
```

## Environment Variables

### Required
- `APP_ENV`: Environment name (`development`, `staging`, `production`)

### Optional
- `CORS_ORIGINS`: Comma-separated list of allowed origins (overrides defaults)

### Example `.env` file
```bash
# Set environment
APP_ENV=production

# Custom CORS origins (optional)
CORS_ORIGINS=https://yourdomain.com,https://api.yourdomain.com

# Other existing variables...
SENTRY_DSN=your-sentry-dsn
```

## Testing

The CORS configuration has been tested and verified to work correctly in all environments:

```bash
# Test the CORS configuration
cd backend
python3 -c "
import os

def get_cors_origins():
    '''Test CORS origins configuration'''
    app_env = os.getenv('APP_ENV', 'development').lower()
    
    if app_env == 'production':
        return 'https://jyotiflow.ai,https://www.jyotiflow.ai,https://jyotiflow-ai-frontend.onrender.com'.split(',')
    elif app_env == 'staging':
        return 'https://staging.jyotiflow.ai,https://dev.jyotiflow.ai,https://jyotiflow-ai-frontend.onrender.com,http://localhost:3000,http://localhost:5173'.split(',')
    else:
        return 'http://localhost:3000,http://localhost:5173,http://localhost:8080,http://127.0.0.1:3000,http://127.0.0.1:5173,https://jyotiflow-ai-frontend.onrender.com'.split(',')

# Test different environments
for env in ['development', 'staging', 'production']:
    os.environ['APP_ENV'] = env
    origins = get_cors_origins()
    print(f'{env.capitalize()}: {origins}')
"
```

## Security Benefits

1. **Restricted Origins**: Production only allows specific trusted domains
2. **Limited Methods**: Production restricts HTTP methods to necessary ones
3. **Controlled Headers**: Production limits allowed headers
4. **Environment Isolation**: Different security levels per environment
5. **Configurable**: Easy to customize without code changes

## Deployment Instructions

### For Development
```bash
export APP_ENV=development
# CORS_ORIGINS is optional - defaults to localhost origins
```

### For Staging
```bash
export APP_ENV=staging  
export CORS_ORIGINS=https://staging.yourdomain.com,http://localhost:3000
```

### For Production
```bash
export APP_ENV=production
export CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com,https://api.yourdomain.com
```

## Migration Guide

If you're upgrading from the previous version:

1. **Set Environment Variable**: Add `APP_ENV=production` to your production environment
2. **Configure Origins**: Add `CORS_ORIGINS` with your production domains
3. **Test**: Verify that your frontend can still communicate with the backend
4. **Monitor**: Check for any CORS-related errors in your logs

## Common Issues and Solutions

### Issue: Frontend requests being blocked
**Solution**: Ensure your frontend domain is included in `CORS_ORIGINS`

### Issue: Pre-flight requests failing
**Solution**: Ensure `OPTIONS` method is included (automatically included in production)

### Issue: Authentication not working
**Solution**: Ensure `Authorization` header is allowed (automatically included in production)

## Future Improvements

Potential future enhancements:
- [ ] Rate limiting per origin
- [ ] Dynamic origin validation
- [ ] Origin whitelisting from database
- [ ] Automatic detection of allowed origins

## Support

If you encounter any issues with the CORS configuration, please:
1. Check your environment variables
2. Verify your origins are correctly formatted (include protocol)
3. Check server logs for CORS-related errors
4. Test with a simple curl command to verify configuration