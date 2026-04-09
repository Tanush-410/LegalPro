"""
Scraper control routes
"""
from fastapi import APIRouter, BackgroundTasks
from datetime import datetime
from ..scheduler.jobs import scrape_court_documents

router = APIRouter(prefix="/api/scrape", tags=["scraper"])

@router.post("/trigger")
async def trigger_scrape(background_tasks: BackgroundTasks):
    """Manually trigger a scrape job"""
    background_tasks.add_task(scrape_court_documents)
    return {
        "status": "ok",
        "message": "Scrape job triggered in background",
        "timestamp": datetime.utcnow().isoformat()
    }
