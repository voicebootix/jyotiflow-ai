# AI Scheduler Deployment Guide
# தமிழ் - AI அட்டவணைப்படுத்தி பயன்படுத்த வழிகாட்டி

## 🎯 Overview / கண்ணோட்டம்

The AI Scheduler automatically runs daily analysis at 2 AM IST and stores the top 3 AI pricing recommendations. This guide explains how to deploy and configure the scheduler.

AI அட்டவணைப்படுத்தி தினசரி காலை 2 மணிக்கு தானாக பகுப்பாய்வு செய்து சிறந்த 3 AI விலை பரிந்துரைகளை சேமிக்கும். இந்த வழிகாட்டி அட்டவணைப்படுத்தியை எவ்வாறு பயன்படுத்துவது மற்றும் கட்டமைப்பது என்பதை விளக்குகிறது.

## 🚀 Deployment Options / பயன்படுத்த விருப்பங்கள்

### Option 1: Render Background Service (Recommended)
### விருப்பம் 1: Render பின்புற சேவை (பரிந்துரைக்கப்படுகிறது)

#### 1. Environment Variables / சுற்றுப்புற மாறிகள்

Add to your Render environment variables:

```bash
ENABLE_AI_SCHEDULER=true
```

#### 2. Background Service Configuration / பின்புற சேவை கட்டமைப்பு

Create a new background service in Render:

```yaml
# render.yaml
services:
  - type: web
    name: jyotiflow-api
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python main.py
    envVars:
      - key: ENABLE_AI_SCHEDULER
        value: true

  - type: background
    name: jyotiflow-scheduler
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python ai_scheduler.py --daemon
    envVars:
      - key: ENABLE_AI_SCHEDULER
        value: true
```

### Option 2: Cron Job (Alternative)
### விருப்பம் 2: Cron Job (மாற்று)

#### 1. Manual Trigger Endpoint / கைமுறை தொடக்க முனையம்

Use the manual trigger endpoint for testing:

```bash
curl -X POST https://your-app.onrender.com/api/admin/trigger-daily-analysis
```

#### 2. Cron Job Setup / Cron Job அமைப்பு

Add to your server's crontab:

```bash
# Run daily at 2 AM IST (8:30 PM UTC)
30 20 * * * curl -X POST https://your-app.onrender.com/api/admin/trigger-daily-analysis
```

## ⚙️ Configuration / கட்டமைப்பு

### Environment Variables / சுற்றுப்புற மாறிகள்

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `ENABLE_AI_SCHEDULER` | Enable/disable scheduler | `false` | Yes |
| `AI_SCHEDULER_TIME` | Analysis time (24h format) | `02:00` | No |
| `AI_SCHEDULER_TIMEZONE` | Timezone for scheduling | `IST` | No |

### Time Configuration / நேர கட்டமைப்பு

The scheduler runs at 2 AM IST by default. To change:

```python
# In ai_scheduler.py
target_hour = 2  # Change this to your preferred hour
```

## 📊 Monitoring / கண்காணிப்பு

### 1. Logs / பதிவுகள்

Scheduler logs are written to `ai_scheduler.log`:

```bash
tail -f ai_scheduler.log
```

### 2. Admin Dashboard / நிர்வாக டாஷ்போர்டு

Check the admin dashboard for:
- Daily analysis summary
- Top 3 recommendations
- Expected revenue impact
- Analysis timestamps

### 3. Database Monitoring / தரவுத்தள கண்காணிப்பு

Check the database for stored recommendations:

```sql
-- Check daily analysis recommendations
SELECT * FROM ai_pricing_recommendations 
WHERE metadata->>'daily_analysis' = 'true'
ORDER BY created_at DESC;

-- Check analysis summary
SELECT * FROM ai_insights_cache 
WHERE insight_type = 'daily_analysis_summary'
ORDER BY created_at DESC;
```

## 🧪 Testing / சோதனை

### 1. Manual Testing / கைமுறை சோதனை

Test the scheduler manually:

```bash
# Run manual analysis
python ai_scheduler.py --manual

# Test scheduler functionality
python test_ai_scheduler.py
```

### 2. API Testing / API சோதனை

Test via API endpoint:

```bash
curl -X POST https://your-app.onrender.com/api/admin/trigger-daily-analysis
```

Expected response:
```json
{
  "success": true,
  "message": "Daily analysis triggered successfully"
}
```

## 🔧 Troubleshooting / சிக்கல் தீர்ப்பு

### Common Issues / பொதுவான சிக்கல்கள்

#### 1. Scheduler Not Starting / அட்டவணைப்படுத்தி தொடங்கவில்லை

**Symptoms**: No logs in `ai_scheduler.log`

**Solution**:
```bash
# Check environment variable
echo $ENABLE_AI_SCHEDULER

# Check database connection
python -c "from db import EnhancedJyotiFlowDatabase; print('DB OK')"
```

#### 2. No Recommendations Generated / பரிந்துரைகள் உருவாக்கப்படவில்லை

**Symptoms**: Empty recommendations list

**Solution**:
```bash
# Check if data exists
python -c "from enhanced_business_logic import MonetizationOptimizer; print('Optimizer OK')"

# Run manual analysis
python ai_scheduler.py --manual
```

#### 3. Time Zone Issues / நேர மண்டல சிக்கல்கள்

**Symptoms**: Scheduler runs at wrong time

**Solution**:
```python
# Update target_hour in ai_scheduler.py
# 2 AM IST = 8:30 PM UTC
target_hour = 2  # Adjust as needed
```

## 📈 Performance Optimization / செயல்திறன் உகந்தமயமாக்கல்

### 1. Database Indexing / தரவுத்தள குறியீட்டு

Add indexes for better performance:

```sql
-- Index for daily analysis queries
CREATE INDEX IF NOT EXISTS idx_ai_pricing_daily_analysis 
ON ai_pricing_recommendations ((metadata->>'daily_analysis'), created_at);

-- Index for insights cache
CREATE INDEX IF NOT EXISTS idx_ai_insights_daily_summary 
ON ai_insights_cache (insight_type, expires_at);
```

### 2. Memory Optimization / நினைவக உகந்தமயமாக்கல்

The scheduler uses minimal memory:
- Single database connection
- Automatic cleanup after analysis
- No persistent data storage in memory

### 3. Error Handling / பிழை கையாளுதல்

The scheduler includes comprehensive error handling:
- Database connection failures
- Analysis failures
- Network timeouts
- Automatic retry logic

## 🔒 Security / பாதுகாப்பு

### 1. API Security / API பாதுகாப்பு

The trigger endpoint is protected:
- Requires admin authentication
- Rate limiting applied
- Input validation

### 2. Database Security / தரவுத்தள பாதுகாப்பு

Recommendations are stored securely:
- SQL injection protection
- Data validation
- Access control

## 📋 Maintenance / பராமரிப்பு

### 1. Log Rotation / பதிவு சுழற்சி

Rotate logs regularly:

```bash
# Add to crontab
0 0 * * 0 mv ai_scheduler.log ai_scheduler.log.old && gzip ai_scheduler.log.old
```

### 2. Data Cleanup / தரவு சுத்தம்

Clean old data periodically:

```sql
-- Clean old recommendations (older than 30 days)
DELETE FROM ai_pricing_recommendations 
WHERE created_at < NOW() - INTERVAL '30 days'
AND status IN ('rejected', 'implemented');

-- Clean expired cache
DELETE FROM ai_insights_cache 
WHERE expires_at < NOW();
```

### 3. Health Checks / ஆரோக்கிய சோதனைகள்

Monitor scheduler health:

```bash
# Check if scheduler is running
ps aux | grep ai_scheduler

# Check recent logs
tail -n 50 ai_scheduler.log | grep "Daily AI analysis"
```

## 🎉 Success Metrics / வெற்றி அளவீடுகள்

Monitor these metrics for success:

- ✅ Daily analysis runs at 2 AM IST
- ✅ Top 3 recommendations stored
- ✅ Expected revenue impact calculated
- ✅ Admin dashboard shows summary
- ✅ Manual trigger works
- ✅ Logs show successful completion

## 📞 Support / ஆதரவு

For issues or questions:

1. Check logs: `tail -f ai_scheduler.log`
2. Test manually: `python ai_scheduler.py --manual`
3. Verify database: Check `ai_pricing_recommendations` table
4. Check admin dashboard: Look for daily analysis summary

---

**Status**: ✅ Ready for Production Deployment
**தமிழ் நிலை**: ✅ உற்பத்தி பயன்படுத்தத்திற்கு தயாராக உள்ளது 