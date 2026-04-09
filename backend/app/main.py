"""
Main FastAPI application
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import logging
import os
from app.routes import dashboard, cases, scraper, websocket, karnataka_hc, supabase_sync, auth
from app.scheduler.jobs import start_scheduler, initialize_db, seed_courts
from app.scheduler import karnataka_hc_jobs
from app.database import SessionLocal, engine, Base
from app.models import User

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
    logger.info("Starting up application...")
    
    # Create user table
    try:
        User.metadata.create_all(bind=engine)
        logger.info("✅ User table initialized")
    except Exception as e:
        logger.error(f"⚠️ User table initialization failed: {e}")
    
    # Initialize database tables
    try:
        initialize_db()
    except Exception as e:
        logger.error(f"⚠️ Database initialization failed: {e}")
        logger.info("Continuing without database initialization...")
    
    # Seed default courts
    try:
        db = SessionLocal()
        try:
            seed_courts(db)
        finally:
            db.close()
    except Exception as e:
        logger.error(f"⚠️ Court seeding failed: {e}")
    
    # Start scheduler
    try:
        start_scheduler()
    except Exception as e:
        logger.error(f"⚠️ Scheduler failed to start: {e}")
    
    # Start daily sync scheduler
    try:
        karnataka_hc_jobs.start_scheduler()
    except Exception as e:
        logger.error(f"⚠️ Karnataka HC scheduler failed: {e}")
    
    # Auto-sync to Supabase if configured
    if os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_ANON_KEY"):
        logger.info("📡 Starting auto-sync to Supabase...")
        from app.routes.supabase_sync import sync_to_supabase_internal
        result = sync_to_supabase_internal()
        logger.info(f"Supabase sync result: {result}")
    else:
        logger.info("⚠️ Supabase not configured - skipping auto-sync")
    
    logger.info("Application startup complete")

# Include routers
app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(cases.router)
app.include_router(scraper.router)
app.include_router(websocket.router)
app.include_router(karnataka_hc.router)
app.include_router(supabase_sync.router)

# Scheduler management endpoints
@app.get("/api/scheduler/status")
async def get_scheduler_status():
    """Get current scheduler status and jobs"""
    return karnataka_hc_jobs.get_scheduler_status()

@app.post("/api/scheduler/sync-now")
async def trigger_sync_now():
    """Manually trigger Karnataka HC sync"""
    result = karnataka_hc_jobs.sync_from_karnataka_hc()
    return {
        "status": "completed",
        "result": result,
        "message": f"Synced {result.get('synced', 0)} cases from Karnataka HC"
    }

@app.post("/api/scheduler/supabase-sync-now")
async def trigger_supabase_sync_now():
    """Manually trigger Supabase sync"""
    result = karnataka_hc_jobs.sync_supabase_daily()
    return {
        "status": "completed",
        "result": result,
        "message": "Supabase sync completed"
    }

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
