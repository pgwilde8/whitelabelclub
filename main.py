from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from app.db.database import init_db
import uvicorn

# Create FastAPI app
app = FastAPI(
    title="ClubLaunch - White Label Club Platform",
    description="Launch your own branded community platform",
    version="1.0.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="templates")

# Include routes
from app.routes import web, api, ai, admin, users
# NEW: Stripe routes
from app.routes import stripe_connect, stripe_payments, stripe_webhooks

# Include web routes
app.include_router(web.router)

# Include API routes
app.include_router(api.router)

# Include AI routes
app.include_router(ai.router)

# Include Admin routes
app.include_router(admin.router)

# Include User routes
app.include_router(users.router)

# NEW: Include Stripe routers
app.include_router(stripe_connect.router)
app.include_router(stripe_payments.router)
app.include_router(stripe_webhooks.router)

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    await init_db()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "ClubLaunch API is running"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
