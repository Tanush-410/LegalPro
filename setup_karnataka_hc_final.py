#!/usr/bin/env python3
"""
FINAL SETUP: Load 2026 Karnataka High Court cases into database
- Removes all other courts  
- Adds ONLY Karnataka High Court
- Loads all 23 sample 2026 cases with all case types
- Ready for dashboard display
"""

import sys
import json
from datetime import datetime
sys.path.insert(0, '/Users/tanush.s.vashisht/Desktop/Tanush/work/court-ecosystem/backend')

from app.database import SessionLocal, Base, engine
from app.models import Court, Case, Judgment, CourtEnum
from test_2026_dataset import KARNATAKA_HC_2026_COMPLETE

print("\n" + "="*80)
print("🚀 FINAL SETUP: KARNATAKA HIGH COURT 2026 INTEGRATION")
print("="*80 + "\n")

# Initialize database
Base.metadata.create_all(bind=engine)
db = SessionLocal()

try:
    # Step 1: Remove all existing courts
    print("STEP 1: Removing old courts (Supreme, High Courts, Lower Courts)...")
    existing_courts = db.query(Court).all()
    for court in existing_courts:
        db.delete(court)
    db.commit()
    print(f"   ✓ Removed {len(existing_courts)} courts")
    
    # Step 2: Create Karnataka High Court ONLY
    print("\nSTEP 2: Creating Karnataka High Court...")
    karnataka_hc = Court(
        name="Karnataka High Court",
        level=CourtEnum.HIGH,
        state="Karnataka",
        district=None
    )
    db.add(karnataka_hc)
    db.commit()
    print(f"   ✓ Created: {karnataka_hc.name}")
    
    # Step 3: Load all 23 sample 2026 cases
    print("\nSTEP 3: Loading 23 sample 2026 cases...")
    case_count = 0
    judgment_count = 0
    case_types = {}
    
    for case_data in KARNATAKA_HC_2026_COMPLETE:
        try:
            # Parse judgment date
            judgment_date = None
            if case_data.get("judgment_date"):
                judgment_date = datetime.fromisoformat(case_data["judgment_date"])
            
            # Create case
            case = Case(
                case_number=case_data.get("case_number"),
                case_type=case_data.get("case_type", "Unknown"),
                case_description=case_data.get("description", ""),
                court_id=karnataka_hc.id,
                petitioner=case_data.get("petitioner", "Unknown"),
                respondent=case_data.get("respondent", "Unknown"),
                case_date=judgment_date or datetime.now(),
                is_new=True
            )
            
            db.add(case)
            db.flush()  # Get the case ID
            case_count += 1
            
            # Track case types
            case_type = case_data.get("case_type", "Other")
            case_types[case_type] = case_types.get(case_type, 0) + 1
            
            # Add judgment if judge info available
            if case_data.get("judges"):
                judgment = Judgment(
                    case_id=case.id,
                    judge_name=case_data.get("judges"),
                    judgment_date=judgment_date or datetime.now(),
                    judgment_text=case_data.get("description", ""),
                    verdict="Judgment issued"
                )
                db.add(judgment)
                judgment_count += 1
            
        except Exception as e:
            print(f"   ⚠️  Error loading case {case_data.get('case_number')}: {e}")
            continue
    
    db.commit()
    print(f"   ✓ Loaded {case_count} cases")
    print(f"   ✓ Created {judgment_count} judgments")
    
    # Step 4: Display summary by case type
    print("\nSTEP 4: Cases by Type:")
    for case_type in sorted(case_types.keys()):
        print(f"   {case_type:15} {case_types[case_type]:2} cases")
    
    # Step 5: Verify data
    print("\nSTEP 5: Database Verification...")
    total_cases = db.query(Case).count()
    total_courts = db.query(Court).count()
    
    courts_info = db.query(Court.name, Court.level).all()
    print(f"   ✓ Total Courts: {total_courts}")
    for court_name, court_level in courts_info:
        print(f"      - {court_name} ({court_level})")
    
    print(f"   ✓ Total Cases: {total_cases}")
    
    # Step 6: Show sample cases
    print("\nSTEP 6: Sample Cases from Database:\n")
    sample_cases = db.query(Case).limit(5).all()
    for i, case in enumerate(sample_cases, 1):
        print(f"{i}. {case.case_number} ({case.case_type})")
        if case.court:
            print(f"   Court: {case.court.name}")
        print(f"   Petitioner: {case.petitioner}")
        print(f"   Respondent: {case.respondent}")
        if case.judgments:
            print(f"   Judge: {case.judgments[0].judge_name}")
        print()
    
    # Final status
    print("="*80)
    print("✅ SETUP COMPLETE - READY FOR DASHBOARD!")
    print("="*80)
    print(f"\n📊 Summary:")
    print(f"   ✓ Database: SQLite (court_ecosystem.db)")
    print(f"   ✓ Court: Karnataka High Court ONLY")
    print(f"   ✓ Cases: 23 from 2026")
    print(f"   ✓ Case Types: {len(case_types)} different types")
    print(f"   ✓ Years: 2026 only")
    print(f"\n🚀 Next Step: Start the server")
    print(f"   cd backend && python3 -m uvicorn app.main:app --reload")
    print(f"\n🌐 Dashboard URL: http://localhost:8000/dashboard")
    print("\n" + "="*80 + "\n")

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
