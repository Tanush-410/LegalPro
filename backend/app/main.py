"""
Main FastAPI application
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import logging
import os
from .routes import auth
from .database import engine, Base

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Court Ecosystem API",
    description="Backend API for scraping and managing court documents",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def disable_dashboard_cache(request: Request, call_next):
    """
    Force fresh dashboard assets to avoid stale browser JS after rapid fixes.
    """
    response = await call_next(request)
    if request.url.path.startswith("/dashboard"):
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

# Initialize database
@app.on_event("startup")
async def startup_event():
    """Initialize database and start scheduler"""
    logger.info("🚀 Starting up application...")
    
    try:
        # Create tables
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables initialized")
    except Exception as e:
        logger.warning(f"⚠️ Database initialization warning: {e}")
    
    logger.info("✅ Application startup complete")

# Include routers
app.include_router(auth.router)

# Try to include optional routers
try:
    from .routes import dashboard
    app.include_router(dashboard.router)
except ImportError as e:
    logger.warning(f"Dashboard router not available: {e}")

try:
    from .routes import cases
    app.include_router(cases.router)
except ImportError as e:
    logger.warning(f"Cases router not available: {e}")

try:
    from .routes import scraper
    app.include_router(scraper.router)
except ImportError as e:
    logger.warning(f"Scraper router not available: {e}")

try:
    from .routes import websocket
    app.include_router(websocket.router)
except ImportError as e:
    logger.warning(f"Websocket router not available: {e}")

try:
    from .routes import karnataka_hc
    app.include_router(karnataka_hc.router)
except ImportError as e:
    logger.warning(f"Karnataka HC router not available: {e}")

try:
    from .routes import supabase_sync
    app.include_router(supabase_sync.router)
except ImportError as e:
    logger.warning(f"Supabase sync router not available: {e}")

try:
    from .routes import seed_data
    app.include_router(seed_data.router)
except ImportError as e:
    logger.warning(f"Seed data router not available: {e}")


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "message": "Court Ecosystem API is running"}

# Mount static files (dashboard) - MUST BE LAST so API routes take precedence
dashboard_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "dashboard")
if os.path.exists(dashboard_path):
    # Mount dashboard at root with fallback to index.html for all unmatched routes
    app.mount("/", StaticFiles(directory=dashboard_path, html=True), name="dashboard")
else:
    logger.warning(f"⚠️ Dashboard path not found: {dashboard_path}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
