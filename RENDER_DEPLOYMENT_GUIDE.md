# Render Deployment Guide - Real Usage Data AI Recommendations
# தமிழ் - Render பயன்படுத்த வழிகாட்டி - உண்மையான பயன்பாட்டு தரவு AI பரிந்துரைகள்

## 🚀 Quick Deploy to Render / Render-ல் விரைவு பயன்படுத்த

### 1. Repository Setup / களஞ்சிய அமைப்பு

1. **GitHub Repository** - Ensure your code is in a GitHub repository
2. **Branch** - Use `main` or `master` branch for deployment
3. **Requirements** - All dependencies are in `backend/requirements.txt`

### 2. Render Dashboard Setup / Render டாஷ்போர்டு அமைப்பு

1. **Login to Render** - https://dashboard.render.com
2. **New Web Service** - Click "New +" → "Web Service"
3. **Connect Repository** - Connect your GitHub repository
4. **Configure Service** - Use the settings below

### 3. Backend Service Configuration / பின்புற சேவை கட்டமைப்பு

```yaml
Name: jyotiflow-backend
Environment: Python 3.11
Build Command: cd backend && pip install -r requirements.txt
Start Command: cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
```

### 4. Environment Variables / சுற்றுப்புற மாறிகள்

#### Required Variables / தேவையான மாறிகள்:

```bash
# Database
DATABASE_URL=postgresql://username:password@host:port/database

# AI Configuration
OPENAI_API_KEY=your-openai-api-key
ENABLE_AI_SCHEDULER=true
AI_SCHEDULER_TIMEZONE=Asia/Kolkata
AI_ANALYSIS_INTERVAL_HOURS=24

# JWT Secret
JWT_SECRET=your-jwt-secret-key

# Stripe (if using payments)
STRIPE_SECRET_KEY=your-stripe-secret-key
STRIPE_PUBLISHABLE_KEY=your-stripe-publishable-key
```

#### Optional Variables / விருப்ப மாறிகள்:

```bash
# Notification System
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password

# Twilio (SMS/WhatsApp)
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_SMS_NUMBER=+1234567890
TWILIO_WHATSAPP_NUMBER=whatsapp:+1234567890

# Firebase (Push Notifications)
FIREBASE_SERVICE_ACCOUNT_KEY_PATH=path/to/firebase-key.json
```

### 5. Frontend Service Configuration / முன்புற சேவை கட்டமைப்பு

```yaml
Name: jyotiflow-frontend
Environment: Static Site
Build Command: cd frontend && npm install --legacy-peer-deps && npm run build
Publish Directory: frontend/dist
```

#### Frontend Environment Variables / முன்புற சுற்றுப்புற மாறிகள்:

```bash
VITE_API_URL=https://your-backend-service.onrender.com
```

## 🔧 Database Setup / தரவுத்தள அமைப்பு

### 1. PostgreSQL Database / PostgreSQL தரவுத்தளம்

1. **Create Database** - In Render dashboard, create a new PostgreSQL database
2. **Get Connection String** - Copy the internal database URL
3. **Set Environment Variable** - Add `DATABASE_URL` to your backend service

### 2. Database Migrations / தரவுத்தள மாற்றங்கள்

The system will automatically create tables on first run. If you need manual migrations:

```bash
# Connect to your database and run:
\i backend/migrations/followup_system.sql
\i backend/migrations/add_followup_tracking_columns.sql
```

## 🤖 AI Scheduler Configuration / AI அட்டவணை கட்டமைப்பு

### 1. Enable AI Scheduler / AI அட்டவணையை இயக்கு

```bash
ENABLE_AI_SCHEDULER=true
AI_SCHEDULER_TIMEZONE=Asia/Kolkata
AI_ANALYSIS_INTERVAL_HOURS=24
```

### 2. Scheduler Features / அட்டவணை அம்சங்கள்

- **Daily Analysis** - Runs at 2 AM IST every day
- **Real Usage Data** - Analyzes 90 days of session data
- **Top 3 Recommendations** - Stores best recommendations
- **Automatic Updates** - Updates admin dashboard

### 3. Manual Trigger / கைமுறை தூண்டல்

You can manually trigger AI analysis via API:

```bash
POST https://your-backend.onrender.com/admin/trigger-daily-analysis
```

## 📊 Real Usage Data Features / உண்மையான பயன்பாட்டு தரவு அம்சங்கள்

### 1. Admin Dashboard / நிர்வாக டாஷ்போர்டு

Access: `https://your-frontend.onrender.com/admin`

Features:
- **Real Usage Analytics Table** - Shows actual session data
- **AI Pricing Recommendations** - Based on real usage patterns
- **Data Quality Indicators** - Shows confidence levels
- **Tamil Language Support** - Full Tamil interface

### 2. Data Sources / தரவு ஆதாரங்கள்

- **Session Analytics** - 90 days of session data
- **User Satisfaction** - Rating scores and feedback
- **Revenue Metrics** - Actual revenue per session
- **Completion Rates** - Session completion statistics

### 3. AI Recommendations / AI பரிந்துரைகள்

Each recommendation includes:
- **Real Data Indicators** - Completion rate, satisfaction, sessions
- **Confidence Scoring** - Based on data quality
- **Expected Impact** - Revenue projections
- **Tamil Reasoning** - Detailed explanations in Tamil

## 🔍 Monitoring and Logs / கண்காணிப்பு மற்றும் பதிவுகள்

### 1. Render Logs / Render பதிவுகள்

- **Build Logs** - Check build process
- **Runtime Logs** - Monitor application performance
- **Error Logs** - Debug issues

### 2. Health Checks / ஆரோக்கிய சோதனைகள்

```bash
GET https://your-backend.onrender.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z",
  "ai_scheduler": "running",
  "database": "connected"
}
```

### 3. AI Scheduler Monitoring / AI அட்டவணை கண்காணிப்பு

Check scheduler status:
```bash
GET https://your-backend.onrender.com/admin/ai-scheduler-status
```

## 🚨 Troubleshooting / சிக்கல் தீர்ப்பு

### 1. Common Issues / பொதுவான சிக்கல்கள்

#### Build Failures / கட்டுமான தோல்விகள்
```bash
# Check requirements.txt
# Ensure all dependencies are listed
# Verify Python version compatibility
```

#### Database Connection Issues / தரவுத்தள இணைப்பு சிக்கல்கள்
```bash
# Verify DATABASE_URL format
# Check database credentials
# Ensure database is accessible
```

#### AI Scheduler Not Running / AI அட்டவணை இயங்கவில்லை
```bash
# Check ENABLE_AI_SCHEDULER=true
# Verify timezone settings
# Check logs for errors
```

### 2. Performance Optimization / செயல்திறன் உகந்தமயமாக்கல்

#### Database Optimization / தரவுத்தள உகந்தமயமாக்கல்
```sql
-- Add indexes for better performance
CREATE INDEX idx_sessions_created_at ON sessions(created_at);
CREATE INDEX idx_sessions_service_type ON sessions(service_type);
CREATE INDEX idx_sessions_user_id ON sessions(user_id);
```

#### Caching / கேசிங்
- AI insights are cached for 24 hours
- Recommendations refresh every 30 seconds
- Real usage data updates daily

## 📈 Scaling Considerations / அளவிடல் கருத்துகள்

### 1. Auto Scaling / தானியங்கி அளவிடல்

Render automatically scales based on:
- **Traffic** - Number of requests
- **Resource Usage** - CPU and memory
- **Response Times** - Performance metrics

### 2. Database Scaling / தரவுத்தள அளவிடல்

- **Upgrade Plan** - As your data grows
- **Connection Pooling** - Optimize database connections
- **Read Replicas** - For high read workloads

### 3. AI Processing / AI செயலாக்கம்

- **Background Tasks** - AI analysis runs in background
- **Async Processing** - Non-blocking operations
- **Resource Management** - Efficient memory usage

## 🔐 Security Considerations / பாதுகாப்பு கருத்துகள்

### 1. Environment Variables / சுற்றுப்புற மாறிகள்

- **Never commit secrets** - Use Render environment variables
- **Rotate keys regularly** - Update API keys periodically
- **Limit access** - Use least privilege principle

### 2. API Security / API பாதுகாப்பு

- **JWT Authentication** - Secure user sessions
- **Rate Limiting** - Prevent abuse
- **Input Validation** - Sanitize all inputs

### 3. Database Security / தரவுத்தள பாதுகாப்பு

- **Connection Encryption** - Use SSL/TLS
- **Access Control** - Limit database access
- **Regular Backups** - Automated backup system

## 📞 Support / ஆதரவு

### 1. Render Support / Render ஆதரவு

- **Documentation** - https://render.com/docs
- **Community** - https://community.render.com
- **Status Page** - https://status.render.com

### 2. Application Support / பயன்பாட்டு ஆதரவு

- **Logs** - Check Render logs first
- **Health Checks** - Monitor application health
- **AI Scheduler** - Verify scheduler status

## 🎉 Success Checklist / வெற்றி சரிபார்ப்பு பட்டியல்

### ✅ Deployment Checklist / பயன்படுத்த சரிபார்ப்பு பட்டியல்

- [ ] Backend service deployed successfully
- [ ] Frontend service deployed successfully
- [ ] Database connected and accessible
- [ ] Environment variables configured
- [ ] Health check endpoint responding
- [ ] AI scheduler enabled and running
- [ ] Admin dashboard accessible
- [ ] Real usage data displaying
- [ ] AI recommendations generating
- [ ] Tamil language support working

### ✅ Testing Checklist / சோதனை சரிபார்ப்பு பட்டியல்

- [ ] User registration and login
- [ ] Spiritual guidance services
- [ ] Credit system functionality
- [ ] Admin dashboard features
- [ ] AI insights and recommendations
- [ ] Real usage analytics
- [ ] Tamil language interface
- [ ] Mobile responsiveness

---

**Status**: ✅ Ready for Render Deployment
**தமிழ் நிலை**: ✅ Render பயன்படுத்த தயாராக உள்ளது

**Last Updated**: January 2024
**கடைசி புதுப்பிப்பு**: ஜனவரி 2024 