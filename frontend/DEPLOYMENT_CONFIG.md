# Frontend Deployment Configuration

## Environment Variables

The frontend requires the following environment variable to be set in production:

### Required
- `VITE_API_URL` - The URL of your backend API service (e.g., `https://jyotiflow-ai.onrender.com`)

### Optional
- `VITE_WS_URL` - WebSocket URL (if not set, will be derived from VITE_API_URL)
- `VITE_ENV` - Environment name (development, staging, production)
- `VITE_SENTRY_DSN` - Sentry DSN for error tracking
- `VITE_GA_ID` - Google Analytics ID

## Render.com Configuration

If deploying to Render, add these environment variables in your service settings:

1. Go to your Render dashboard
2. Select your frontend service
3. Go to "Environment" tab
4. Add the following:
   ```
   VITE_API_URL=https://jyotiflow-ai.onrender.com
   ```

## Local Development

For local development, create a `.env.local` file:

```bash
cp .env.example .env.local
```

Then update the values:
```
VITE_API_URL=http://localhost:8000
VITE_ENV=development
```

## Build Configuration

The frontend uses Vite for building. The build command will automatically use the environment variables:

```bash
npm run build
```

## Troubleshooting

### API Calls Going to Wrong Domain

If API calls are going to the frontend domain instead of the backend:
1. Check that `VITE_API_URL` is properly set
2. Verify all fetch calls use the API base URL
3. Clear browser cache and rebuild

### WebSocket Connection Failures

If WebSocket connections fail:
1. Ensure your backend supports WebSocket connections
2. Check that the WebSocket URL is correctly constructed from the API URL
3. Verify CORS settings allow WebSocket connections

### CORS Issues

If you see CORS errors:
1. Verify the backend includes your frontend URL in allowed origins
2. Check that credentials are properly included in requests
3. Ensure the backend is properly configured for your frontend domain