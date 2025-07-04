from fastapi import APIRouter, Body, HTTPException
from utils.notification_utils import send_email, send_sms, send_whatsapp, send_push_notification
import asyncio

router = APIRouter(prefix="/api/notify", tags=["Notification"])

@router.post("/followup")
async def send_followup(
    channel: str = Body(...),  # "email", "sms", "whatsapp", "push"
    to: str = Body(...),
    subject: str = Body("JyotiFlow.ai Notification"),
    message: str = Body(...),
    device_token: str = Body(None)
):
    try:
        if channel == "email":
            await send_email(to, subject, message)
        elif channel == "sms":
            # Run sync function in thread pool
            await asyncio.get_event_loop().run_in_executor(None, send_sms, to, message)
        elif channel == "whatsapp":
            # Run sync function in thread pool
            await asyncio.get_event_loop().run_in_executor(None, send_whatsapp, to, message)
        elif channel == "push" and device_token:
            # Run sync function in thread pool
            await asyncio.get_event_loop().run_in_executor(None, send_push_notification, device_token, subject, message)
        else:
            raise HTTPException(status_code=400, detail="Invalid channel or missing device_token for push")
        
        return {"success": True, "message": f"{channel} notification sent successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send {channel} notification: {str(e)}") 