from core_foundation_enhanced import app
from routers.admin_subscriptions import router as admin_subscription_router
from routers.spiritual import router as spiritual_router
from routers.sessions import router as sessions_router
from routers.credits import router as credits_router
from routers.notification import router as notification_router
from routers.admin_products import router as admin_products_router
from routers.followup import router as followup_router
from dotenv import load_dotenv

# --- CORS Middleware (English & Tamil) ---
# (REMOVED: CORS middleware should only be set in core_foundation_enhanced.py)

# Register admin subscription router
app.include_router(admin_subscription_router, prefix="/api/admin")
app.include_router(spiritual_router)
app.include_router(sessions_router)
app.include_router(credits_router)
app.include_router(notification_router)
app.include_router(admin_products_router)  # Revert: No prefix, endpoints at root as before
app.include_router(followup_router)

load_dotenv()





