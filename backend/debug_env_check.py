"""
Debug endpoint to check environment variable loading
"""
from fastapi import APIRouter
import os

router = APIRouter(prefix="/api/debug", tags=["Debug"])

@router.get("/env-check")
async def check_environment_variables():
    """Check if environment variables are properly loaded"""
    
    # Check key environment variables
    env_status = {
        "PROKERALA_CLIENT_ID": {
            "available": bool(os.getenv("PROKERALA_CLIENT_ID")),
            "value_preview": os.getenv("PROKERALA_CLIENT_ID", "NOT_SET")[:10] + "..." if os.getenv("PROKERALA_CLIENT_ID") else "NOT_SET",
            "is_placeholder": os.getenv("PROKERALA_CLIENT_ID", "") == "your-client-id"
        },
        "PROKERALA_CLIENT_SECRET": {
            "available": bool(os.getenv("PROKERALA_CLIENT_SECRET")),
            "value_preview": os.getenv("PROKERALA_CLIENT_SECRET", "NOT_SET")[:10] + "..." if os.getenv("PROKERALA_CLIENT_SECRET") else "NOT_SET",
            "is_placeholder": os.getenv("PROKERALA_CLIENT_SECRET", "") == "your-client-secret"
        },
        "OPENAI_API_KEY": {
            "available": bool(os.getenv("OPENAI_API_KEY")),
            "value_preview": os.getenv("OPENAI_API_KEY", "NOT_SET")[:10] + "..." if os.getenv("OPENAI_API_KEY") else "NOT_SET",
            "is_placeholder": os.getenv("OPENAI_API_KEY", "") == "your-openai-api-key"
        },
        "DATABASE_URL": {
            "available": bool(os.getenv("DATABASE_URL")),
            "value_preview": os.getenv("DATABASE_URL", "NOT_SET")[:30] + "..." if os.getenv("DATABASE_URL") else "NOT_SET",
            "is_placeholder": False
        },
        "AGORA_APP_ID": {
            "available": bool(os.getenv("AGORA_APP_ID")),
            "value_preview": os.getenv("AGORA_APP_ID", "NOT_SET")[:10] + "..." if os.getenv("AGORA_APP_ID") else "NOT_SET",
            "is_placeholder": False
        }
    }
    
    # Count available vs placeholder
    total_checked = len(env_status)
    available_count = sum(1 for env in env_status.values() if env["available"])
    placeholder_count = sum(1 for env in env_status.values() if env["is_placeholder"])
    
    return {
        "status": "success",
        "summary": {
            "total_checked": total_checked,
            "available": available_count,
            "using_placeholders": placeholder_count,
            "missing": total_checked - available_count
        },
        "environment_variables": env_status,
        "diagnosis": {
            "prokerala_ready": env_status["PROKERALA_CLIENT_ID"]["available"] and not env_status["PROKERALA_CLIENT_ID"]["is_placeholder"],
            "openai_ready": env_status["OPENAI_API_KEY"]["available"] and not env_status["OPENAI_API_KEY"]["is_placeholder"],
            "database_ready": env_status["DATABASE_URL"]["available"],
            "overall_status": "ready" if available_count >= 3 and placeholder_count == 0 else "configuration_issues"
        }
    }

