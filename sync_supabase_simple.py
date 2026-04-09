#!/usr/bin/env python3
"""
Simple Supabase Sync Script  
Syncs all 79 court cases to Supabase with minimum required fields
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
    print("\n" + "="*70)
    print("🔄 SUPABASE FULL SYNC - 79 COURT CASES")
    print("="*70 + "\n")
    
    try:
        # Import after setting env vars
        from supabase import create_client
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        import sys
        sys.path.insert(0, '/Users/tanush.s.vashisht/Desktop/Tanush/work/court-ecosystem/backend')
        
        from app.models import Case, Court, Judgment
        
        # Connect to local database
        db_path = '/Users/tanush.s.vashisht/Desktop/Tanush/work/court-ecosystem/backend/court_ecosystem.db'
        local_engine = create_engine(f'sqlite:///{db_path}', connect_args={"check_same_thread": False})
        LocalSession = sessionmaker(bind=local_engine)
        local_db = LocalSession()
        
        # Connect to Supabase
        logger.info("📡 Connecting to Supabase...")
        supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        logger.info("✅ Connected to Supabase project: courtcases\n")
        
        # ===== STEP 1: CHECK EXISTING CASES =====
        logger.info("📊 Checking existing data in Supabase...")
        try:
            response = supabase.table("cases").select("id", count="exact").execute()
            existing_count = response.count if hasattr(response, 'count') else len(response.data)
            logger.info(f"  Found {existing_count} existing cases\n")
        except Exception as e:
            logger.info(f"  No existing cases found\n")
        
        # ===== STEP 2: GET LOCAL CASES =====
        logger.info("📋 Loading 79 cases from local database...")
        cases = local_db.query(Case).all()
        logger.info(f"✅ Loaded {len(cases)} cases\n")
        
        # ===== STEP 3: SYNC CASES =====
        logger.info("🚀 Syncing cases to Supabase (syncing only core fields)...\n")
        
        synced_cases = 0
        errors = 0
        
        for idx, case in enumerate(cases, 1):
            # Get judge name from latest judgment
            judge_name = "Unassigned"
            if case.judgments:
                latest_judgment = max(case.judgments, key=lambda j: j.judgment_date if j.judgment_date else datetime.min)
                if latest_judgment.judge_name:
                    judge_name = latest_judgment.judge_name
            
            # Build case data with only essential fields
            case_data = {
                "case_number": case.case_number,
                "case_type": case.case_type,
                "cnr": case.cnr or "",
                "petitioner": case.petitioner or "Unknown",
                "respondent": case.respondent or "Unknown",
                "judge_name": judge_name,
                "pdf_url": case.pdf_url or "",
                "case_status": case.case_status or "Active",
                "priority": case.priority or 1
            }
            
            try:
                response = supabase.table("cases").insert(case_data).execute()
                synced_cases += 1
                progress = (idx / len(cases)) * 100
                logger.info(f"  [{idx:2d}/79] ✅ {case.case_number:<15} | {progress:5.1f}%")
            except Exception as e:
                errors += 1
                error_msg = str(e)[:60]
                logger.error(f"  [{idx:2d}/79] ❌ {case.case_number:<15} | {error_msg}")
        
        # ===== FINAL SUMMARY =====
        logger.info("\n" + "="*70)
        logger.info("📊 SYNC SUMMARY")
        logger.info("="*70)
        logger.info(f"✅ Cases synced: {synced_cases}/79")
        logger.info(f"❌ Errors: {errors}")
        logger.info("="*70)
        
        # Verify sync
        logger.info("\n✅ Verifying Supabase data...")
        response = supabase.table("cases").select("id", count="exact").execute()
        case_count = response.count if hasattr(response, 'count') else len(response.data)
        logger.info(f"📊 Total cases now in Supabase: {case_count}")
        
        if case_count >= 79:
            logger.info("\n🎉 SUCCESS! All 79 cases synced to Supabase!")
        else:
            logger.warning(f"\n⚠️ Expected 79+ cases, found {case_count}")
        
        # Close connections
        local_db.close()
        
        print("\n" + "="*70)
        print("✅ SYNC COMPLETE!")
        print("="*70 + "\n")
        
        return 0
        
    except Exception as e:
        logger.error(f"\n❌ SYNC FAILED: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
