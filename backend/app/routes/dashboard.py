"""
Dashboard and Statistics Routes
"""
from fastapi import APIRouter, Depends, BackgroundTasks, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from app.database import get_db
from app.models import Case, Judgment, Court, ScrapeLog, CourtEnum
from app.schemas import DashboardStats
from app.scheduler.jobs import scrape_court_documents

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    verified_only: bool = Query(False, description="Count only cases that have both judgment and document rows"),
    db: Session = Depends(get_db),
):
    """Get dashboard statistics"""
    
    # Total counts - use simpler approach to avoid subquery issues
    total_cases = db.query(func.count(Case.id)).scalar() or 0
    
    if verified_only:
        # Count only cases with both judgment and document
        total_cases = (
            db.query(func.count(Case.id))
            .filter(Case.judgments.any())
            .filter(Case.documents.any())
            .scalar() or 0
        )
    
    # Total judgments
    total_judgments = db.query(func.count(Judgment.id)).scalar() or 0
    
    # Count by court level - use direct filter instead of complex joins
    supreme_cases = db.query(Case).join(Court).filter(Court.level == CourtEnum.SUPREME).all()
    supreme_count = len([c for c in supreme_cases if not verified_only or (c.judgments and c.documents)])
    
    high_cases = db.query(Case).join(Court).filter(Court.level == CourtEnum.HIGH).all()
    high_count = len([c for c in high_cases if not verified_only or (c.judgments and c.documents)])
    
    lower_cases = db.query(Case).join(Court).filter(Court.level == CourtEnum.LOWER).all()
    lower_count = len([c for c in lower_cases if not verified_only or (c.judgments and c.documents)])
    
    # Today's cases
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_cases = db.query(func.count(Case.id)).filter(Case.created_at >= today_start).scalar() or 0
    
    if verified_only and today_cases > 0:
        today_cases = (
            db.query(func.count(Case.id))
            .filter(Case.created_at >= today_start)
            .filter(Case.judgments.any())
            .filter(Case.documents.any())
            .scalar() or 0
        )
    
    # Last scrape time
    last_scrape = db.query(ScrapeLog).order_by(ScrapeLog.created_at.desc()).first()
    last_scrape_time = last_scrape.created_at if last_scrape else None
    
    return DashboardStats(
        total_cases=total_cases,
        total_judgments=total_judgments,
        supreme_court_count=supreme_count,
        high_court_count=high_count,
        lower_court_count=lower_count,
        today_cases=today_cases,
        last_scrape_time=last_scrape_time
    )

@router.get("/courts-breakdown")
async def get_courts_breakdown(db: Session = Depends(get_db)):
    """Get case counts breakdown by individual courts"""
    
    breakdown = db.query(
        Court.name,
        Court.level,
        func.count(Case.id).label("case_count")
    ).join(Case, Court.id == Case.court_id, isouter=True).group_by(
        Court.id, Court.name, Court.level
    ).all()
    
    return [
        {
            "court_name": name,
            "court_level": level.value if level else "Unknown",
            "case_count": count
        }
        for name, level, count in breakdown
    ]

@router.get("/timeline")
async def get_cases_timeline(
    days: int = 30,
    verified_only: bool = Query(True, description="Include only cases that have both judgment and document rows"),
    db: Session = Depends(get_db),
):
    """Get case count timeline for the last N days"""
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    timeline_query = db.query(
        func.date(Case.created_at).label("date"),
        func.count(Case.id).label("count")
    ).filter(Case.created_at >= start_date)

    if verified_only:
        timeline_query = timeline_query.filter(Case.judgments.any(), Case.documents.any())

    timeline = timeline_query.group_by(
        func.date(Case.created_at)
    ).order_by(func.date(Case.created_at)).all()
    
    return [
        {
            "date": str(date),
            "count": count
        }
        for date, count in timeline
    ]

@router.post("/trigger-scrape")
async def trigger_scrape_manual(background_tasks: BackgroundTasks):
    """Manually trigger a scrape job"""
    background_tasks.add_task(scrape_court_documents)
    return {
        "status": "ok",
        "message": "Scrape job triggered in background",
        "timestamp": datetime.utcnow().isoformat()
    }
