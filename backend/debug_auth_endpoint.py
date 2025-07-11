"""
Debug endpoint to test AI Marketing Director without authentication
This will help us isolate the authentication issue from the AI agent issue
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import asyncio

# Import the AI Marketing Director
try:
    from simple_ai_marketing_director import ai_marketing_director
    AI_DIRECTOR_AVAILABLE = True
    print("✅ Simple AI Marketing Director imported successfully")
except Exception as e:
    AI_DIRECTOR_AVAILABLE = False
    print(f"❌ AI Marketing Director import failed: {e}")

debug_router = APIRouter(prefix="/debug", tags=["Debug"])

class DebugChatRequest(BaseModel):
    message: str

@debug_router.post("/test-ai-director")
async def test_ai_director_no_auth(request: DebugChatRequest):
    """Test AI Marketing Director without authentication"""
    try:
        if not AI_DIRECTOR_AVAILABLE:
            return {
                "success": False,
                "error": "AI Marketing Director not available",
                "message": "Import failed"
            }
        
        # Test the AI Marketing Director directly
        result = await ai_marketing_director.handle_instruction(request.message)
        
        return {
            "success": True,
            "data": {
                "message": result.get("reply", str(result)) if isinstance(result, dict) else str(result),
                "raw_result": result
            },
            "debug_info": {
                "ai_director_type": str(type(ai_marketing_director)),
                "has_handle_instruction": hasattr(ai_marketing_director, "handle_instruction"),
                "request_message": request.message
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"AI Marketing Director error: {str(e)}",
            "debug_info": {
                "exception_type": str(type(e)),
                "ai_director_available": AI_DIRECTOR_AVAILABLE
            }
        }

@debug_router.get("/auth-test")
async def test_auth_requirements():
    """Test what authentication requirements exist"""
    return {
        "message": "This endpoint works without authentication",
        "ai_director_available": AI_DIRECTOR_AVAILABLE,
        "debug_info": {
            "endpoint": "/debug/auth-test",
            "requires_auth": False
        }
    }

