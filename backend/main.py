from core_foundation_enhanced import app
from routers.admin_subscriptions import router as admin_subscription_router

# Register admin subscription router
app.include_router(admin_subscription_router, prefix="/api/admin")





