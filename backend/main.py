from core_foundation_enhanced import app
from routers.admin_subscriptions import router as admin_subscription_router
from routers.spiritual import router as spiritual_router
from routers.sessions import router as sessions_router
from routers.credits import router as credits_router

# Register admin subscription router
app.include_router(admin_subscription_router, prefix="/api/admin")
app.include_router(spiritual_router)
app.include_router(sessions_router)
app.include_router(credits_router)





