# JyotiFlow.ai Internal Follow-up System

## Overview

The Internal Follow-up System is a comprehensive solution for managing automated follow-up communications with users after spiritual sessions. It includes credit charging, multi-channel delivery, analytics, and admin management capabilities.

## Features

### ✅ Implemented Features

1. **Database Schema**
   - `follow_up_templates` - Template management with Tamil support
   - `follow_up_schedules` - Scheduled follow-ups with status tracking
   - `follow_up_analytics` - Performance tracking and metrics
   - `follow_up_settings` - System configuration
   - Updated `sessions` table with `follow_up_sent` and `follow_up_count` columns

2. **Backend Services**
   - **FollowUpService** - Core service for scheduling, sending, and managing follow-ups
   - **Credit Integration** - Automatic credit deduction for follow-ups
   - **Multi-channel Support** - Email, SMS, WhatsApp, Push notifications
   - **Template System** - Dynamic content with variable substitution
   - **Analytics Tracking** - Delivery rates, read rates, revenue tracking

3. **API Endpoints**
   - User endpoints: Schedule, view, cancel follow-ups
   - Admin endpoints: Template management, analytics, settings
   - Automatic scheduling after session completion

4. **Frontend Components**
   - **AdminDashboard** - Complete follow-up management interface
   - **FollowUpCenter** - User-facing follow-up management
   - Template creation and management
   - Analytics dashboard
   - Settings configuration

5. **Integration Points**
   - Automatic follow-up scheduling after spiritual sessions
   - Credit system integration
   - Notification system integration
   - Session tracking

## Database Schema

### Tables Created

```sql
-- Follow-up templates
CREATE TABLE follow_up_templates (
    id UUID PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    tamil_name VARCHAR(100),
    description TEXT,
    template_type VARCHAR(50) NOT NULL,
    channel VARCHAR(20) NOT NULL,
    subject VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    tamil_content TEXT,
    variables JSONB DEFAULT '[]',
    credits_cost INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Follow-up schedules
CREATE TABLE follow_up_schedules (
    id UUID PRIMARY KEY,
    user_email VARCHAR(255) NOT NULL,
    session_id VARCHAR(255) REFERENCES sessions(id),
    template_id UUID REFERENCES follow_up_templates(id),
    channel VARCHAR(20) NOT NULL,
    scheduled_at TIMESTAMP NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    credits_charged INTEGER DEFAULT 0,
    sent_at TIMESTAMP,
    delivered_at TIMESTAMP,
    read_at TIMESTAMP,
    failure_reason TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Follow-up analytics
CREATE TABLE follow_up_analytics (
    id UUID PRIMARY KEY,
    date DATE NOT NULL,
    template_id UUID REFERENCES follow_up_templates(id),
    channel VARCHAR(20) NOT NULL,
    total_sent INTEGER DEFAULT 0,
    total_delivered INTEGER DEFAULT 0,
    total_read INTEGER DEFAULT 0,
    total_failed INTEGER DEFAULT 0,
    credits_charged INTEGER DEFAULT 0,
    revenue_generated DECIMAL(10,2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(date, template_id, channel)
);

-- Follow-up settings
CREATE TABLE follow_up_settings (
    id UUID PRIMARY KEY,
    setting_key VARCHAR(100) UNIQUE NOT NULL,
    setting_value TEXT NOT NULL,
    setting_type VARCHAR(20) DEFAULT 'string',
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Updated Sessions Table

```sql
-- Added to existing sessions table
ALTER TABLE sessions ADD COLUMN follow_up_sent BOOLEAN DEFAULT FALSE;
ALTER TABLE sessions ADD COLUMN follow_up_count INTEGER DEFAULT 0;
```

## API Endpoints

### User Endpoints

- `POST /api/followup/schedule` - Schedule a follow-up
- `GET /api/followup/my-followups` - Get user's follow-ups
- `POST /api/followup/cancel/{followup_id}` - Cancel a follow-up

### Admin Endpoints

- `GET /api/followup/admin/templates` - Get all templates
- `POST /api/followup/admin/templates` - Create template
- `PUT /api/followup/admin/templates/{id}` - Update template
- `DELETE /api/followup/admin/templates/{id}` - Delete template
- `GET /api/followup/admin/schedules` - Get all schedules
- `GET /api/followup/admin/analytics` - Get analytics
- `GET /api/followup/admin/settings` - Get settings
- `PUT /api/followup/admin/settings` - Update settings

### Automatic Endpoints

- `POST /api/followup/auto/session-complete` - Auto-schedule after session

## Usage Examples

### 1. Automatic Follow-up After Session

When a user completes a spiritual session, the system automatically:

1. Checks for available follow-up templates
2. Schedules a follow-up for the user
3. Deducts credits from user account
4. Sends the follow-up at the scheduled time

```python
# In sessions.py - automatically triggered
asyncio.create_task(schedule_session_followup(session_id, user["email"], service_type, db))
```

### 2. Manual Follow-up Scheduling

```python
# Schedule a custom follow-up
request = FollowUpRequest(
    user_email="user@example.com",
    session_id="session-123",
    template_id="template-456",
    channel=FollowUpChannel.EMAIL,
    scheduled_at=datetime.now() + timedelta(days=1)
)

response = await followup_service.schedule_followup(request)
```

### 3. Template Management

```python
# Create a new template
template = FollowUpTemplate(
    name="Session Follow-up 1",
    tamil_name="அமர்வு பின்தொடர்தல் 1",
    description="First follow-up after spiritual session",
    template_type=FollowUpType.SESSION_FOLLOWUP,
    channel=FollowUpChannel.EMAIL,
    subject="How is your spiritual journey progressing? 🕉️",
    content="Dear {{user_name}}, Thank you for your recent spiritual consultation...",
    tamil_content="அன்புள்ள {{user_name}}, உங்கள் சமீபத்திய ஆன்மீக ஆலோசனைக்கு நன்றி...",
    credits_cost=5
)
```

## Configuration

### Default Settings

```python
settings = {
    'auto_followup_enabled': True,
    'default_credits_cost': 5,
    'max_followups_per_session': 3,
    'min_interval_hours': 24,
    'max_interval_days': 30,
    'enable_credit_charging': True,
    'enable_analytics': True
}
```

### Template Variables

Available variables for template substitution:
- `{{user_name}}` - User's display name
- `{{user_email}}` - User's email
- `{{session_date}}` - Session completion date
- `{{service_type}}` - Type of service used
- `{{guidance_summary}}` - Brief summary of guidance

## Frontend Integration

### Admin Dashboard

Access the follow-up management through:
1. Admin Dashboard → Follow-ups tab
2. Manage templates, schedules, analytics, and settings
3. Create custom templates with Tamil support
4. Monitor delivery rates and revenue

### User Interface

Users can access their follow-ups through:
1. FollowUpCenter component
2. View scheduled follow-ups
3. Cancel pending follow-ups
4. Track delivery status

## Credit System Integration

### Credit Charging Logic

1. **Automatic Deduction**: Credits are deducted when follow-up is scheduled
2. **Credit Validation**: System checks user has sufficient credits before scheduling
3. **Refund Policy**: Cancelled follow-ups can be configured for credit refunds
4. **Cost Configuration**: Different templates can have different credit costs

### Credit Flow

```
User completes session → System checks credits → Deducts credits → Schedules follow-up → Sends message → Tracks analytics
```

## Analytics & Reporting

### Metrics Tracked

- **Delivery Rates**: Percentage of successfully delivered messages
- **Read Rates**: Percentage of messages read by users
- **Revenue Generation**: Total revenue from follow-up credits
- **Channel Performance**: Performance by delivery channel
- **Template Performance**: Most effective templates

### Analytics Dashboard

Admin can view:
- Real-time delivery statistics
- Revenue generated from follow-ups
- Top-performing templates
- Channel performance comparison
- User engagement metrics

## Security & Permissions

### User Permissions

- Users can only manage their own follow-ups
- Users can only cancel pending follow-ups
- Users cannot access admin functions

### Admin Permissions

- Full access to template management
- Access to all user follow-ups
- Analytics and reporting access
- System settings configuration

## Error Handling

### Common Error Scenarios

1. **Insufficient Credits**: User doesn't have enough credits for follow-up
2. **Template Not Found**: Referenced template doesn't exist
3. **Delivery Failure**: Message delivery fails (network, invalid contact, etc.)
4. **Scheduling Conflicts**: Too many follow-ups scheduled for same user

### Error Recovery

- Failed deliveries are logged with reasons
- System retries for transient failures
- Credit refunds for failed deliveries (configurable)
- Automatic cleanup of expired follow-ups

## Deployment Notes

### Environment Variables

```bash
# Email Configuration
SMTP_HOST=your-smtp-host
SMTP_PORT=587
SMTP_USER=your-smtp-user
SMTP_PASS=your-smtp-password

# SMS Configuration (Twilio)
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_SMS_NUMBER=your-twilio-number
TWILIO_WHATSAPP_NUMBER=your-whatsapp-number

# Push Notifications (Firebase)
FIREBASE_SERVICE_ACCOUNT_KEY_PATH=path/to/firebase-key.json
```

### Database Migration

Run the migration script to set up the database:

```bash
# Apply the migration
psql -d your_database -f backend/migrations/followup_system.sql
```

### Service Dependencies

- **Email Service**: SMTP or SendGrid
- **SMS Service**: Twilio
- **WhatsApp Service**: Twilio WhatsApp API
- **Push Notifications**: Firebase Cloud Messaging

## Future Enhancements

### Planned Features

1. **AI-Powered Personalization**: Dynamic content based on user behavior
2. **Advanced Scheduling**: Smart scheduling based on user activity patterns
3. **A/B Testing**: Test different templates for effectiveness
4. **Integration APIs**: Webhook support for external systems
5. **Bulk Operations**: Mass follow-up scheduling for campaigns

### Scalability Considerations

- **Queue System**: Implement message queuing for high-volume scenarios
- **Rate Limiting**: Prevent spam and respect service provider limits
- **Caching**: Cache templates and user preferences
- **Monitoring**: Comprehensive logging and alerting

## Support & Maintenance

### Monitoring

- Track delivery success rates
- Monitor credit system integration
- Alert on system failures
- Performance metrics tracking

### Troubleshooting

1. **Check logs** for delivery failures
2. **Verify credits** are being deducted correctly
3. **Test templates** for variable substitution
4. **Monitor external services** (SMTP, SMS providers)

### Maintenance Tasks

- Clean up old analytics data
- Archive completed follow-ups
- Update templates for seasonal content
- Review and optimize credit costs

---

## Summary

The Internal Follow-up System provides a complete solution for automated user engagement after spiritual sessions. It includes:

✅ **Complete Implementation**: Database, backend, frontend, and API
✅ **Credit Integration**: Automatic charging and validation
✅ **Multi-channel Support**: Email, SMS, WhatsApp, Push
✅ **Tamil Language Support**: Bilingual templates and content
✅ **Admin Management**: Full control panel for administrators
✅ **Analytics**: Comprehensive tracking and reporting
✅ **User Interface**: Easy-to-use follow-up management for users

The system is production-ready and can be deployed immediately to enhance user engagement and spiritual guidance continuity. 