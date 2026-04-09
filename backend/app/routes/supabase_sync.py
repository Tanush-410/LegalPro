"""
Supabase Sync Routes
Auto-sync local database to Supabase
"""
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
import os
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["sync"])

def sync_to_supabase_internal():
    """Internal function to sync database to Supabase"""
    try:
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_ANON_KEY")
        
        if not supabase_url or not supabase_key:
            logger.warning("⚠️ Supabase credentials not configured")
            return {"status": "skipped", "message": "Supabase credentials not configured"}
        
        from app.database import SessionLocal
        from app.models import Case, Court
        from app.supabase_manager import SupabaseManager
        
        logger.info("📡 Starting Supabase sync...")
        sm = SupabaseManager()
        db = SessionLocal()
        
        # Get all cases
        cases = db.query(Case).all()
        court = db.query(Court).first()
        
        synced = 0
        errors = 0
        
        # Sync court
        if court:
            try:
                court_data = {
                    "name": court.name,
                    "level": court.level,
                    "state": court.state,
                    "district": court.district
                }
                sm.create_court(court_data)
                logger.info(f"✅ Court synced: {court.name}")
            except Exception as e:
                logger.warning(f"⚠️ Could not sync court: {e}")
        
        # Sync cases
        for case in cases:
            try:
                case_data = {
                    "case_number": case.case_number,
                    "cnr": case.cnr,
                    "case_type": case.case_type,
                    "case_description": case.case_description,
                    "petitioner": case.petitioner,
                    "respondent": case.respondent,
                    "case_date": case.case_date.isoformat() if case.case_date else None,
                    "pdf_url": case.pdf_url,
                    "case_status": case.case_status,
                    "priority": case.priority,
                    "court_name": case.court.name if case.court else "Karnataka High Court",
                    "judge_name": case.judgments[0].judge_name if case.judgments else None,
                }
                result = sm.create_case(case_data)
                if result:
                    synced += 1
            except Exception as e:
                errors += 1
                logger.warning(f"⚠️ Error syncing {case.case_number}: {str(e)[:50]}")
        
        logger.info(f"✅ Sync complete: {synced} cases synced, {errors} errors")
        db.close()
        
        return {
            "status": "success",
            "cases_synced": synced,
            "errors": errors,
            "total_cases": synced + errors
        }
    
    except Exception as e:
        logger.error(f"❌ Sync failed: {e}")
        return {"status": "failed", "message": str(e)}

@router.post("/sync-to-supabase")
async def sync_to_supabase(background_tasks: BackgroundTasks):
    """
    Trigger sync to Supabase
    Returns immediately, syncing happens in background
    """
    background_tasks.add_task(sync_to_supabase_internal)
    return {
        "status": "queued",
        "message": "Sync started in background. Check back in a few seconds."
    }

@router.get("/sync-status")
async def check_supabase_connection():
    """Check if Supabase is configured and accessible"""
    try:
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_ANON_KEY")
        
        if not supabase_url or not supabase_key:
            return {
                "status": "not_configured",
                "message": "Set SUPABASE_URL and SUPABASE_ANON_KEY environment variables"
            }
        
        from app.supabase_manager import SupabaseManager
        sm = SupabaseManager()
        
        return {
            "status": "connected",
            "message": f"Connected to {supabase_url}",
            "url": supabase_url
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
