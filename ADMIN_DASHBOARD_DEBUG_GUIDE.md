# JyotiFlow Admin Dashboard Debug Guide

## Problem Summary
- ✅ Login works (no more 404)
- ❌ Dashboard shows white screen after login
- 🔧 Root cause: Missing admin API endpoints

## What Was Fixed

### 1. Backend Route Registration
- **Before**: Routes from `core_foundation_enhanced.py` weren't being mounted to `enhanced_app`
- **After**: Used APIRouter pattern to properly include routes

### 2. Missing Admin Endpoints
- **Before**: Frontend called `/api/admin/stats`, `/api/admin/monetization`, `/api/admin/optimization` (404)
- **After**: Added all missing admin endpoints with proper data structure

### 3. Frontend Error Handling
- **Before**: Silent failures causing white screen
- **After**: Added console logging and error boundaries

## Testing Steps

### Step 1: Verify Backend is Running
```bash
# In PowerShell (no && operator)
cd backend
python -c "import uvicorn; uvicorn.run('main:app', host='0.0.0.0', port=8000, reload=True)"
```

### Step 2: Test Admin Endpoints
```bash
# Test login
curl -X POST http://localhost:8000/api/auth/login -H "Content-Type: application/json" -d "{\"email\":\"admin@jyotiflow.ai\",\"password\":\"admin123\"}"

# Test admin stats (with token from login)
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/api/admin/stats

# Test admin monetization
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/api/admin/monetization

# Test admin optimization
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/api/admin/optimization
```

### Step 3: Check Frontend Console
1. Open browser developer tools (F12)
2. Go to Console tab
3. Try logging in as admin
4. Look for console messages like:
   - "Checking admin privileges..."
   - "Admin stats response: ..."
   - "Admin authentication successful"

### Step 4: Verify Dashboard Loads
After successful login, you should see:
- Loading spinner: "Loading divine administration..."
- Dashboard with metrics cards
- Navigation tabs (Overview, Users, Revenue, etc.)

## Expected API Responses

### Login Response
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user_email": "admin@jyotiflow.ai",
    "role": "admin"
  }
}
```

### Admin Stats Response
```json
{
  "success": true,
  "message": "Admin stats retrieved successfully",
  "data": {
    "total_users": 0,
    "active_users": 0,
    "total_revenue": 1250.50,
    "daily_revenue": 125.75,
    "total_sessions": 0,
    "satsangs_completed": 12,
    "avatar_generations": 45,
    "live_chat_sessions": 8
  }
}
```

## Troubleshooting

### If Dashboard Still Shows White Screen

1. **Check Console Errors**
   - Open browser dev tools (F12)
   - Look for red error messages
   - Check Network tab for failed requests

2. **Verify API Endpoints**
   - Test each endpoint individually with curl
   - Ensure all return 200 OK with proper JSON

3. **Check Authentication**
   - Verify token is stored in localStorage
   - Check if token is being sent in Authorization header

4. **Database Issues**
   - If database queries fail, endpoints will return error responses
   - Check server logs for database connection errors

### Common Issues

1. **CORS Errors**
   - Frontend can't reach backend
   - Check if backend is running on correct port
   - Verify API_BASE_URL in frontend

2. **Token Issues**
   - Token not being stored properly
   - Token expired or invalid
   - Authorization header not being sent

3. **Component Errors**
   - React component throwing error during render
   - Check for undefined variables or missing props

## Debug Commands

### Test All Admin Endpoints
```bash
python test_admin_endpoints.py
```

### Check Available Routes
```bash
curl http://localhost:8000/api/debug/routes
```

### Test Health Check
```bash
curl http://localhost:8000/health
```

## Next Steps

1. **Test the fix** using the steps above
2. **Check browser console** for any remaining errors
3. **Verify dashboard loads** with proper data
4. **Test all admin features** (Overview, Insights tabs)

If issues persist, check:
- Server logs for backend errors
- Browser console for frontend errors
- Network tab for failed API calls
- Database connectivity and schema 

---

## 1️⃣ **Backend: notification_utils.py** (utils/notification_utils.py)

```python
import os
from aiosmtplib import send as smtp_send
from email.message import EmailMessage
from twilio.rest import Client as TwilioClient
import httpx

# Email (SMTP/SendGrid)
async def send_email(to, subject, body):
    msg = EmailMessage()
    msg['From'] = os.getenv("SMTP_USER", "noreply@jyotiflow.ai")
    msg['To'] = to
    msg['Subject'] = subject
    msg.set_content(body)
    await smtp_send(
        msg,
        hostname=os.getenv("SMTP_HOST"),
        port=int(os.getenv("SMTP_PORT", 587)),
        username=os.getenv("SMTP_USER"),
        password=os.getenv("SMTP_PASS"),
        start_tls=True
    )

# SMS (Twilio)
def send_sms(to, message):
    client = TwilioClient(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
    from_ = os.getenv("TWILIO_SMS_NUMBER")
    client.messages.create(body=message, from_=from_, to=to)

# WhatsApp (Twilio)
def send_whatsapp(to, message):
    client = TwilioClient(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
    from_ = os.getenv("TWILIO_WHATSAPP_NUMBER")
    client.messages.create(body=message, from_=from_, to=f"whatsapp:{to}")

# Push Notification (FCM)
async def send_push_notification(device_token, title, body):
    server_key = os.getenv("FCM_SERVER_KEY")
    headers = {"Authorization": f"key={server_key}", "Content-Type": "application/json"}
    payload = {
        "to": device_token,
        "notification": {"title": title, "body": body}
    }
    async with httpx.AsyncClient() as client:
        await client.post("https://fcm.googleapis.com/fcm/send", json=payload, headers=headers)
```

---

## 2️⃣ **Backend: notification_router.py** (routers/notification.py)

```python
from fastapi import APIRouter, Body
from utils.notification_utils import send_email, send_sms, send_whatsapp, send_push_notification

router = APIRouter(prefix="/api/notify", tags=["Notification"])

@router.post("/followup")
async def send_followup(
    channel: str = Body(...),  # "email", "sms", "whatsapp", "push"
    to: str = Body(...),
    subject: str = Body("JyotiFlow.ai Notification"),
    message: str = Body(...),
    device_token: str = Body(None)
):
    if channel == "email":
        await send_email(to, subject, message)
    elif channel == "sms":
        send_sms(to, message)
    elif channel == "whatsapp":
        send_whatsapp(to, message)
    elif channel == "push" and device_token:
        await send_push_notification(device_token, subject, message)
    else:
        return {"success": False, "message": "Invalid channel"}
    return {"success": True, "message": f"{channel} sent"}
```

---

## 3️⃣ **Frontend: api.js** (Add methods)

```js
async sendFollowup({ channel, to, subject, message, device_token }) {
  return this.post('/api/notify/followup', { channel, to, subject, message, device_token });
},
```

---

## 4️⃣ **Frontend: Profile.jsx or AdminDashboard.jsx** (Trigger UI)

- Notification Preferences UI (checkboxes for Email, SMS, WhatsApp, Push)
- Button: "Send Test Notification" (calls `spiritualAPI.sendFollowup` with selected channel)

---

## 5️⃣ **.env Example (local or deployment):**

```
SMTP_HOST=smtp.yourprovider.com
SMTP_PORT=587
SMTP_USER=your_email@domain.com
SMTP_PASS=your_email_password

TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_SMS_NUMBER=+1234567890
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886

FCM_SERVER_KEY=your_firebase_server_key
```

---

## **சுருக்கமாக:**
- Email, SMS, WhatsApp, Push Notification follow-up/send/reminder-க்கு backend+frontend code skeleton தயார்.
- நீங்கள் API keys சேர்த்தவுடன், இது production-ready ஆகும்.
- UI-யில் "Send Notification" button, notification preferences, etc. சேர்க்கலாம்.

**API keys/testing credentials சேர்த்ததும், இந்த code-ஐ உங்கள் project-ல் பயன்படுத்தலாம்.  
இன்னும் UI/logic-ல் customization/automation (reminder, schedule, etc.) வேண்டும் என்றால், சொல்லுங்கள்!** 