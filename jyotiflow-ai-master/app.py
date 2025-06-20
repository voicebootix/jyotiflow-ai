import os
from fastapi import FastAPI
from fastapi.responses import JSONResponse

# Simple working app
app = FastAPI(title="JyotiFlow.ai", description="Swami Jyotirananthan's Digital Ashram")

@app.get("/")
async def home():
    return {"message": "🙏🏼 Welcome to JyotiFlow.ai", "status": "operational"}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "JyotiFlow.ai"}


@app.get("/api/status")
async def api_status():
    return {"api": "active", "version": "1.0", "features": "coming_soon"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
