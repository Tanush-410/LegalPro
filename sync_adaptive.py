#!/usr/bin/env python3
"""
Supabase Sync - Adaptive Schema Detection
Detects existing columns and syncs accordingly
"""

import os
import sys
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# Supabase Credentials
SUPABASE_URL = "https://tvcxhspsgxmlzafovcpi.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR2Y3hoc3BzZ3htbHphZm92Y3BpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzE5MjQzMjIsImV4cCI6MjA4NzUwMDMyMn0.OMBB0Kh2rOzts2cwaI9I7nBxKdf4fhLZappIuFdxGSQ"

os.environ["SUPABASE_URL"] = SUPABASE_URL
os.environ["SUPABASE_ANON_KEY"] = SUPABASE_ANON_KEY

def main():
    print("\n" + "="*70)
    print("🔄 ADAPTIVE SUPABASE SYNC")
    print("="*70 + "\n")
    
    try:
        from supabase import create_client
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        import sys
        sys.path.insert(0, '/Users/tanush.s.vashisht/Desktop/Tanush/work/court-ecosystem/backend')
        
        from app.models import Case
        
        # Connect databases
        logger.info("📡 Connecting to Supabase...")
        supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        logger.info("✅ Connected!\n")
        
        logger.info("📡 Connecting to local database...")
        db_path = '/Users/tanush.s.vashisht/Desktop/Tanush/work/court-ecosystem/backend/court_ecosystem.db'
        local_engine = create_engine(f'sqlite:///{db_path}', connect_args={"check_same_thread": False})
        LocalSession = sessionmaker(bind=local_engine)
        local_db = LocalSession()
        
        cases_local = local_db.query(Case).all()
        logger.info(f"✅ Loaded {len(cases_local)} local cases\n")
        
        # === DETECT SCHEMA ===
        logger.info("🔍 Detecting Supabase 'cases' table schema...")
        
        # Try a test insert to see what columns are accepted
        test_data = {
            "case_number": "SCHEMA_TEST",
            "case_type": "Test",
        }
        
        accepted_columns = set()
        rejected_columns = set()
        
        test_insert = test_data.copy()
        for col in ["cnr", "petitioner", "respondent", "judge_name", "pdf_url", "case_status", "priority"]:
            test_insert[col] = "test_value" if col != "priority" else 1
        
        try:
            logger.info("  Testing column acceptance...\n")
            response = supabase.table("cases").insert(test_insert).execute()
            inserted_id = response.data[0]['id'] if response.data else None
            
            # If we got here, all columns were accepted
            accepted_columns = set(test_insert.keys())
            
            # Clean up test record
            if inserted_id:
                supabase.table("cases").delete().eq("id", inserted_id).execute()
                logger.info(f"  ✅ Test record created and cleaned up")
            
            logger.info(f"\n  ✅ Accepted columns: {', '.join(sorted(accepted_columns))}\n")
            
        except Exception as e:
            error_msg = str(e)
            logger.warning(f"  ⚠️ Full insert test failed: {error_msg[:80]}\n")
            
            # Try with minimal columns
            minimal = {"case_number": "SCHEMA_TEST_MINIMAL", "case_type": "Test"}
            try:
                response = supabase.table("cases").insert(minimal).execute()
                inserted_id = response.data[0]['id'] if response.data else None
                accepted_columns = set(minimal.keys())
                
                if inserted_id:
                    supabase.table("cases").delete().eq("id", inserted_id).execute()
                
                logger.info(f"  ✅ Minimal schema works with: {', '.join(sorted(accepted_columns))}\n")
            except Exception as e2:
                logger.error(f"  ❌ Even minimal insert failed: {str(e2)[:80]}\n")
                return 1
        
        # === SYNC WITH DETECTED SCHEMA ===
        logger.info("="*70)
        logger.info("🚀 SYNCING 79 CASES WITH DETECTED SCHEMA")
        logger.info("="*70 + "\n")
        
        synced = 0
        errors = 0
        
        for idx, case in enumerate(cases_local, 1):
            # Build data with only detected columns
            case_data = {"case_number": case.case_number}
            
            # Add columns we know work
            if "case_type" in accepted_columns:
                case_data["case_type"] = case.case_type
            if "cnr" in accepted_columns:
                case_data["cnr"] = case.cnr or ""
            if "petitioner" in accepted_columns:
                case_data["petitioner"] = case.petitioner or "Unknown"
            if "respondent" in accepted_columns:
                case_data["respondent"] = case.respondent or "Unknown"
            if "pdf_url" in accepted_columns:
                case_data["pdf_url"] = case.pdf_url or ""
            if "judge_name" in accepted_columns:
                judge_name = "Unassigned"
                if case.judgments:
                    latest_judgment = max(case.judgments, key=lambda j: j.judgment_date if j.judgment_date else datetime.min)
                    if latest_judgment.judge_name:
                        judge_name = latest_judgment.judge_name
                case_data["judge_name"] = judge_name
            if "case_status" in accepted_columns:
                case_data["case_status"] = case.case_status or "Active"
            if "priority" in accepted_columns:
                case_data["priority"] = case.priority or 1
            
            try:
                response = supabase.table("cases").insert(case_data).execute()
                synced += 1
                pct = (idx / len(cases_local)) * 100
                logger.info(f"  [{idx:2d}/79] ✅ {case.case_number:<15} | {pct:5.1f}%")
            except Exception as e:
                errors += 1
                logger.error(f"  [{idx:2d}/79] ❌ {case.case_number:<15} | {str(e)[:50]}")
        
        logger.info("\n" + "="*70)
        logger.info("📊 FINAL RESULTS")
        logger.info("="*70)
        logger.info(f"✅ Cases synced: {synced}/79")
        logger.info(f"❌ Errors: {errors}")
        
        # Verify
        response = supabase.table("cases").select("id", count="exact").execute()
        final_count = response.count if hasattr(response, 'count') else len(response.data)
        logger.info(f"📊 Total in Supabase: {final_count}")
        logger.info("="*70 + "\n")
        
        if synced >= 79:
            logger.info("🎉 SUCCESS! All cases synced!")
            return 0
        else:
            logger.warning(f"⚠️ Only {synced} cases synced (expected 79)")
            return 1
            
    except Exception as e:
        logger.error(f"\n❌ Error: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())
