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