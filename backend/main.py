from core_foundation_enhanced import app
from routers.admin_subscriptions import router as admin_subscription_router
from routers.spiritual import router as spiritual_router
from routers.sessions import router as sessions_router
from routers.credits import router as credits_router
from dotenv import load_dotenv

# --- CORS Middleware (English & Tamil) ---
from fastapi.middleware.cors import CORSMiddleware

# Allow all origins for development/testing. For production, restrict to your frontend domain.
# அனைத்து frontend-களுக்கும் அனுமதி (டெவலப்மெண்ட்/test மட்டும்). Production-ல் frontend URL மட்டும் அனுமதி செய்யவும்.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or ["https://jyotiflow-ai-frontend.onrender.com"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register admin subscription router
app.include_router(admin_subscription_router, prefix="/api/admin")
app.include_router(spiritual_router)
app.include_router(sessions_router)
app.include_router(credits_router)

load_dotenv()





