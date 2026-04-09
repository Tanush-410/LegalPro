#!/usr/bin/env python3
"""
API Endpoints for Manual Sync Control
Add these routes to backend/app/routes/
"""

from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime
import json
import os

router = APIRouter(prefix="/api", tags=["sync"])

@router.post("/sync-cases-now")
async def trigger_manual_sync(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Manually trigger a sync from the website"""
    
    def run_sync():
        try:
            # Import the sync module
            import sys
            sys.path.insert(0, "/Volumes/PortableSSD/court-ecosystem")
            from daily_sync_scheduler import KarnatakaHCDailySync
            
            syncer = KarnatakaHCDailySync()
            syncer.run_daily_sync()
            
        except Exception as e:
            logger.error(f"Sync error: {e}")
    
    background_tasks.add_task(run_sync)
    
    return {
        "status": "SYNC_STARTED",
        "message": "Case sync from website initiated in background",
        "started_at": datetime.utcnow().isoformat()
    }


@router.get("/sync-status")
async def get_sync_status():
    """Get status of last sync"""
    
    sync_log_file = "/Volumes/PortableSSD/court-ecosystem/sync_log.json"
    
    try:
        if os.path.exists(sync_log_file):
            with open(sync_log_file, 'r') as f:
                logs = json.load(f)
            
            if logs:
                last_sync = logs[-1]
                return {
                    "last_sync_time": last_sync.get('timestamp'),
                    "cases_added_last_sync": last_sync.get('new_added', 0),
                    "total_syncs": len(logs),
                    "status": "ACTIVE"
                }
        
        return {
            "status": "NO_SYNC_YET",
            "message": "No sync has been performed yet"
        }
        
    except Exception as e:
        return {
            "status": "ERROR",
            "error": str(e)
        }


@router.get("/sync-history")
async def get_sync_history(limit: int = 10):
    """Get sync history"""
    
    sync_log_file = "/Volumes/PortableSSD/court-ecosystem/sync_log.json"
    
    try:
        if os.path.exists(sync_log_file):
            with open(sync_log_file, 'r') as f:
                logs = json.load(f)
            
            return {
                "total_syncs": len(logs),
                "recent_syncs": logs[-limit:] if logs else []
            }
        
        return {
            "total_syncs": 0,
            "recent_syncs": []
        }
        
    except Exception as e:
        return {
            "error": str(e)
        }
