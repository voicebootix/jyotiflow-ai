import sys
from pathlib import Path
from fastapi import FastAPI
from routers import (
    admin_products, admin_subscriptions, admin_credits,
    admin_analytics, admin_content, admin_settings
)

sys.path.append(str(Path(__file__).parent))

from core_foundation_enhanced import app

app = FastAPI()
app.include_router(admin_products.router)
app.include_router(admin_subscriptions.router)
app.include_router(admin_credits.router)
app.include_router(admin_analytics.router)
app.include_router(admin_content.router)
app.include_router(admin_settings.router)





