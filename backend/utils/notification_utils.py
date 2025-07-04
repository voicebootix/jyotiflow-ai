import os
from aiosmtplib import send as smtp_send
from email.message import EmailMessage
from twilio.rest import Client as TwilioClient
import firebase_admin
from firebase_admin import credentials, messaging

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

# Push Notification (FCM via Firebase Admin)
def send_push_notification(device_token, title, body):
    # Initialize Firebase Admin SDK if not already done
    if not firebase_admin._apps:
        cred = credentials.Certificate(os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY_PATH"))
        firebase_admin.initialize_app(cred)
    
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body
        ),
        token=device_token,
    )
    
    response = messaging.send(message)
    return response 