#!/usr/bin/env python3
import os
import sys

# Set database URL
os.environ["DATABASE_URL"] = "sqlite:////Volumes/PortableSSD/court-ecosystem/data/court_ecosystem.db"
sys.path.insert(0, "/Volumes/PortableSSD/court-ecosystem/backend")

from datetime import datetime, timedelta
from app.database import SessionLocal
from app.models import Case, Court, CourtEnum
import random

db = SessionLocal()

# First, ensure Karnataka High Court exists
existing = db.query(Court).filter(Court.name == "Karnataka High Court").first()
if not existing:
    court = Court(name="Karnataka High Court", level=CourtEnum.HIGH, state="Karnataka")
    db.add(court)
    db.commit()
    print("✅ Created Karnataka High Court")
else:
    print("✅ Karnataka High Court already exists")

courts = db.query(Court).all()
print(f"Found {len(courts)} courts")

petitioners = ["Ram Kumar", "Priya Singh", "Sanjay Patel", "Deepa Sharma", "Vikas Verma", "Ananya Roy", "Arjun Gupta", "Neha Kapoor"]
respondents = ["Union of India", "State of Karnataka", "CBI", "Delhi Police", "Ministry of Justice", "High Court of Delhi"]
case_types = ["Writ Petition", "Civil Appeal", "Review Petition", "Special Leave Petition"]

count = 0
for court in courts:
    for i in range(15):
        case_date = datetime.utcnow() - timedelta(days=random.randint(0, 100))
        case_num = f"{court.name.split()[0][:3].upper()}-{random.randint(10000, 99999)}"
        
        # Check if case already exists
        existing_case = db.query(Case).filter(Case.case_number == case_num).first()
        if not existing_case:
            case = Case(
                case_number=case_num,
                court_id=court.id,
                petitioner=random.choice(petitioners),
                respondent=random.choice(respondents),
                case_type=random.choice(case_types),
                case_date=case_date
            )
            db.add(case)
            count += 1

db.commit()
db.close()
print(f"✅ Inserted {count} sample cases into database")
