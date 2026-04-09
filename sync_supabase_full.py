#!/usr/bin/env python3
"""
Supabase Full Sync Script
Clears old data and syncs all 79 court cases to Supabase
"""

import os
import sys
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Supabase Credentials
SUPABASE_URL = "https://tvcxhspsgxmlzafovcpi.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR2Y3hoc3BzZ3htbHphZm92Y3BpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzE5MjQzMjIsImV4cCI6MjA4NzUwMDMyMn0.OMBB0Kh2rOzts2cwaI9I7nBxKdf4fhLZappIuFdxGSQ"

# Set environment variables
os.environ["SUPABASE_URL"] = SUPABASE_URL
os.environ["SUPABASE_ANON_KEY"] = SUPABASE_ANON_KEY

def main():
    """Main sync function"""
    print("\n" + "="*60)
    print("🔄 SUPABASE FULL SYNC - CLEAR OLD DATA & SYNC NEW")
    print("="*60 + "\n")
    
    try:
        # Import after setting env vars
        from supabase import create_client
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        import sys
        sys.path.insert(0, '/Users/tanush.s.vashisht/Desktop/Tanush/work/court-ecosystem/backend')
        
        from app.models import Base, Case, Court, Judgment
        from app.database import get_db
        
        # Connect to local database
        db_path = '/Users/tanush.s.vashisht/Desktop/Tanush/work/court-ecosystem/backend/court_ecosystem.db'
        local_engine = create_engine(f'sqlite:///{db_path}', connect_args={"check_same_thread": False})
        LocalSession = sessionmaker(bind=local_engine)
        local_db = LocalSession()
        
        # Connect to Supabase
        logger.info("📡 Connecting to Supabase...")
        supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        logger.info("✅ Connected to Supabase project: courtcases")
        
        # ===== STEP 1: CLEAR OLD DATA =====
        logger.info("\n🗑️  STEP 1: Clearing old data from Supabase...")
        
        try:
            # Clear cases
            response = supabase.table("cases").select("id").execute()
            if response.data:
                case_ids = [case['id'] for case in response.data]
                logger.info(f"  Found {len(case_ids)} old cases to delete")
                for case_id in case_ids:
                    supabase.table("cases").delete().eq("id", case_id).execute()
                    logger.info(f"  ✓ Deleted case ID {case_id}")
            else:
                logger.info("  ℹ️ No old cases found")
        except Exception as e:
            logger.warning(f"  ⚠️ Could not clear cases (might not exist yet): {e}")
        
        try:
            # Clear court
            supabase.table("courts").delete().neq("id", -999).execute()  # Delete all
            logger.info("  ✓ Cleared courts table")
        except Exception as e:
            logger.warning(f"  ⚠️ Could not clear courts: {e}")
        
        # ===== STEP 2: SYNC COURTS =====
        logger.info("\n🏛️  STEP 2: Syncing courts...")
        
        courts = local_db.query(Court).all()
        for court in courts:
            court_data = {
                "name": court.name,
                "level": court.level,
                "state": court.state,
                "district": court.district or ""
            }
            try:
                response = supabase.table("courts").insert(court_data).execute()
                logger.info(f"  ✅ Synced court: {court.name}")
            except Exception as e:
                logger.error(f"  ❌ Error syncing court {court.name}: {e}")
        
        # ===== STEP 3: EXTRACT UNIQUE JUDGES FROM JUDGMENTS =====
        logger.info("\n⚖️  STEP 3: Syncing judges from judgments...")
        
        judgments = local_db.query(Judgment).all()
        unique_judges = {}
        for judgment in judgments:
            if judgment.judge_name:
                if judgment.judge_name not in unique_judges:
                    unique_judges[judgment.judge_name] = 1
                else:
                    unique_judges[judgment.judge_name] += 1
        
        synced_judges = 0
        for judge_name, case_count in unique_judges.items():
            judge_data = {
                "name": judge_name,
                "cases_handled": case_count
            }
            try:
                response = supabase.table("judges").insert(judge_data).execute()
                synced_judges += 1
                logger.info(f"  ✓ {judge_name} ({case_count} cases)")
            except Exception as e:
                logger.warning(f"  ⚠️ Error syncing judge {judge_name}: {e}")
        
        logger.info(f"  ✅ Total judges synced: {synced_judges}")
        
        # ===== STEP 4: SYNC CASES =====
        logger.info("\n📋 STEP 4: Syncing 79 cases...")
        
        cases = local_db.query(Case).all()
        synced_cases = 0
        errors = 0
        
        for idx, case in enumerate(cases, 1):
            # Get judge name from latest judgment
            judge_name = None
            if case.judgments:
                latest_judgment = max(case.judgments, key=lambda j: j.judgment_date if j.judgment_date else datetime.min)
                judge_name = latest_judgment.judge_name
            
            case_data = {
                "case_number": case.case_number,
                "case_type": case.case_type,
                "cnr": case.cnr or "",
                "petitioner": case.petitioner or "Unknown",
                "respondent": case.respondent or "Unknown",
                "judge_name": judge_name or "Unassigned",
                "case_date": case.case_date.isoformat() if case.case_date else None,
                "court_id": case.court_id,
                "pdf_url": case.pdf_url or "",
                "case_status": case.case_status or "Active",
                "priority": case.priority or 1,
                "case_description": case.case_description or "",
                "created_at": case.created_at.isoformat() if case.created_at else datetime.now().isoformat()
            }
            
            try:
                response = supabase.table("cases").insert(case_data).execute()
                synced_cases += 1
                progress = (idx / len(cases)) * 100
                logger.info(f"  [{idx:2d}/79] ✓ {case.case_number:<15} | {progress:5.1f}%")
            except Exception as e:
                errors += 1
                logger.error(f"  [{idx:2d}/79] ❌ {case.case_number}: {e}")
        
        # ===== FINAL SUMMARY =====
        logger.info("\n" + "="*60)
        logger.info("📊 SYNC SUMMARY")
        logger.info("="*60)
        logger.info(f"✅ Courts synced: {len(courts)}")
        logger.info(f"✅ Judges synced: {synced_judges}")
        logger.info(f"✅ Cases synced: {synced_cases}/79")
        logger.info(f"❌ Errors: {errors}")
        logger.info("="*60)
        
        # Verify sync
        logger.info("\n✅ Verifying Supabase data...")
        response = supabase.table("cases").select("id").execute()
        case_count = len(response.data) if response.data else 0
        logger.info(f"📊 Total cases in Supabase: {case_count}")
        
        if case_count == 79:
            logger.info("\n🎉 SUCCESS! All 79 cases synced to Supabase!")
        else:
            logger.warning(f"\n⚠️ Expected 79 cases, found {case_count}")
        
        # Close connections
        local_db.close()
        
        print("\n" + "="*60)
        print("✅ SYNC COMPLETE!")
        print("="*60 + "\n")
        
        return 0
        
    except Exception as e:
        logger.error(f"\n❌ SYNC FAILED: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
