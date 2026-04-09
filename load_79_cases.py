#!/usr/bin/env python3
"""Load 79 cases from JSON into local database"""
import os
import sys
import json

os.environ["DATABASE_URL"] = "sqlite:////Volumes/PortableSSD/court-ecosystem/data/court_ecosystem.db"
sys.path.insert(0, "/Volumes/PortableSSD/court-ecosystem/backend")

from app.database import SessionLocal
from app.models import Case, Court, CourtEnum, Judgment, Document
from datetime import datetime

# Load JSON data
json_file = "/tmp/karnataka_hc_2026_complete.json"
with open(json_file, 'r') as f:
    cases_data = json.load(f)

print(f"📂 Loaded {len(cases_data)} cases from JSON")

db = SessionLocal()

try:
    # Ensure Karnataka High Court exists
    court = db.query(Court).filter(Court.name == "Karnataka High Court").first()
    if not court:
        court = Court(name="Karnataka High Court", level=CourtEnum.HIGH, state="Karnataka")
        db.add(court)
        db.commit()
        print("✅ Created Karnataka High Court")
    
    # Clear existing cases to avoid duplicates
    existing_count = db.query(Case).count()
    if existing_count > 0:
        print(f"🗑️  Clearing {existing_count} existing cases...")
        db.query(Document).delete()
        db.query(Judgment).delete()
        db.query(Case).delete()
        db.commit()
    
    # Load all 79 cases
    loaded = 0
    for case_data in cases_data:
        try:
            # Check if case already exists
            existing = db.query(Case).filter(Case.case_number == case_data['case_number']).first()
            if existing:
                continue
            
            # Create case
            case = Case(
                case_number=case_data['case_number'],
                court_id=court.id,
                cnr=case_data.get('cnr'),
                case_type=case_data.get('case_type', 'Unknown'),
                case_description=case_data.get('category_description', ''),
                petitioner=case_data.get('petitioner'),
                respondent=case_data.get('respondent'),
                case_date=datetime.strptime(case_data['judgment_date'], '%Y-%m-%d'),
                pdf_url=case_data.get('pdf_url'),
                case_status=case_data.get('case_status', 'Pending'),
                priority=case_data.get('priority', 0),
            )
            db.add(case)
            db.flush()
            
            # Add judgment if we have judge info
            if case_data.get('judge_name'):
                judgment = Judgment(
                    case_id=case.id,
                    judge_name=case_data['judge_name'],
                    judgment_date=datetime.strptime(case_data['judgment_date'], '%Y-%m-%d'),
                    judgment_text=f"Case: {case_data['case_number']}",
                    verdict="Pending",
                )
                db.add(judgment)
                db.flush()
            
            loaded += 1
            if loaded % 10 == 0:
                print(f"  Loading... {loaded}/79")
        
        except Exception as e:
            print(f"⚠️ Error loading {case_data.get('case_number')}: {e}")
            db.rollback()
            continue
    
    db.commit()
    print(f"\n✅ Successfully loaded {loaded} cases into database!")
    
    # Verify
    total = db.query(Case).count()
    print(f"📊 Total cases in database: {total}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
