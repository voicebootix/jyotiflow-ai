from fastapi import APIRouter, Depends
from ..db import get_db

router = APIRouter(prefix="/api/admin/integrations", tags=["Admin Integrations"])

@router.get("/status")
async def get_integrations_status(db=Depends(get_db)):
    """Get status of all integrations"""
    try:
        # Get API integrations
        api_integrations = await db.fetch("""
            SELECT 
                integration_name,
                status,
                last_tested,
                test_result
            FROM api_integrations
            ORDER BY integration_name
        """)
        
        # Get platform settings
        platform_settings = await db.fetch("""
            SELECT 
                key,
                value
            FROM platform_settings
            WHERE key LIKE '%credentials%' OR key LIKE '%integration%'
            ORDER BY key
        """)
        
        # Check specific integrations
        integrations_status = {
            "database": "connected",
            "stripe": "unknown",
            "sendgrid": "unknown", 
            "twilio": "unknown",
            "facebook": "unknown",
            "instagram": "unknown",
            "youtube": "unknown",
            "tiktok": "unknown"
        }
        
        # Check if we have any integration data
        for integration in api_integrations:
            integration_name = integration['integration_name'].lower()
            if integration_name in integrations_status:
                integrations_status[integration_name] = integration['status']
        
        # Check platform settings for social media
        for setting in platform_settings:
            key = setting['key'].lower()
            if 'facebook' in key and setting['value']:
                integrations_status['facebook'] = 'configured'
            elif 'instagram' in key and setting['value']:
                integrations_status['instagram'] = 'configured'
            elif 'youtube' in key and setting['value']:
                integrations_status['youtube'] = 'configured'
            elif 'tiktok' in key and setting['value']:
                integrations_status['tiktok'] = 'configured'
        
        return {
            "success": True,
            "data": {
                "integrations": integrations_status,
                "api_integrations": [dict(integration) for integration in api_integrations],
                "platform_settings": [dict(setting) for setting in platform_settings]
            }
        }
        
    except Exception as e:
        print(f"Integrations status error: {e}")
        return {
            "success": False,
            "error": str(e),
            "data": {
                "integrations": {
                    "database": "error",
                    "stripe": "unknown",
                    "sendgrid": "unknown",
                    "twilio": "unknown",
                    "facebook": "unknown",
                    "instagram": "unknown",
                    "youtube": "unknown",
                    "tiktok": "unknown"
                },
                "api_integrations": [],
                "platform_settings": []
            }
        }