"""
Data seeding endpoint - Populates database with sample court cases
Only available in demo/test environments for development
"""

from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..models import Case, Court, Judgment, CourtEnum
from datetime import datetime, timedelta
import random

router = APIRouter(prefix="/api/seed", tags=["seed"])

# Real Karnataka High Court Data
REAL_JUDGES = [
    "Hon'ble Justice P. Sree Sudha",
    "Hon'ble Justice Aravind Kumar",
    "Hon'ble Justice Nageshwara Rao",
    "Hon'ble Justice P.S. Narasimha",
    "Hon'ble Justice Sanjay Karol",
    "Hon'ble Justice Mustafa Aftab",
    "Hon'ble Justice B.V. Nagarathna",
    "Hon'ble Justice Vikram Nath",
    "Hon'ble Justice S. Krishnamurthy",
    "Hon'ble Justice Hemavati",
]

REAL_PETITIONERS = [
    "Kirloskar Corporation Ltd.", "Infosys Technologies Limited",
    "Biocon Limited", "TVS Motor Company Ltd.", "JSW Steel Ltd.",
    "Asian Paints India Ltd.", "Dr. Reddy's Laboratories Ltd.",
    "Bosch Limited", "Titan Company Limited", "Voltas Limited",
    "HDFC Bank Limited", "ICICI Bank Limited", "ITC Limited",
    "Wipro Limited", "TCS (Tata Consultancy Services)",
    "Mahindra & Mahindra Ltd.", "Bajaj Auto Ltd.",
    "Hero MotoCorp Limited", "Maruti Suzuki India Limited",
    "Larsen & Toubro Limited", "State Bank of India"
]

REAL_RESPONDENTS = [
    "State of Karnataka", "Union of India",
    "Central Bureau of Investigation", "Income Tax Department",
    "Ministry of Labour", "Bangalore Development Authority",
    "Karnataka State Electricity Board", "BMTC",
    "University of Bangalore", "Indian Railways"
]

CASE_TYPES = [
    ("WP", "Writ Petition"),
    ("CP", "Civil Petition"),
    ("CA", "Civil Appeal"),
    ("CRA", "Criminal Appeal"),
    ("FA", "First Appeal"),
]

CASE_STATUSES = [
    "DISPOSED", "ALLOWED", "DISMISSED", "PARTLY ALLOWED",
    "WITHDRAWN", "ADJOURNED", "PENDING HEARING"
]


def generate_case_number(case_type_code: str, counter: int) -> str:
    """Generate realistic case number"""
    return f"{case_type_code} {counter} OF 2026"


@router.post("/populate-demo-data")
async def populate_demo_data():
    """
    Populate database with 100 sample court cases
    WARNING: This will clear existing cases
    """
    db = SessionLocal()
    try:
        # Check if data already exists
        existing_count = db.query(Case).count()
        if existing_count > 50:  # Already has significant data
            return {
                "status": "skipped",
                "message": f"Database already has {existing_count} cases",
                "cases_count": existing_count
            }

        # Get or create Karnataka High Court
        court = db.query(Court).filter(Court.name == "Karnataka High Court").first()
        if not court:
            court = Court(
                name="Karnataka High Court",
                level=CourtEnum.HIGH,
                state="Karnataka"
            )
            db.add(court)
            db.commit()

        print(f"✅ Using court: {court.name} (ID: {court.id})")

        # Clear existing cases if any
        if existing_count > 0:
            db.query(Judgment).delete()
            db.query(Case).delete()
            db.commit()
            print(f"🗑️  Cleared {existing_count} existing cases")

        # Generate 100 cases
        added_count = 0
        case_counter = {ct[0]: 1 for ct in CASE_TYPES}

        total_goal = 100
        cases_per_type = total_goal // len(CASE_TYPES)
        remainder = total_goal % len(CASE_TYPES)

        for idx, (case_type_code, case_type_name) in enumerate(CASE_TYPES):
            num_cases = cases_per_type + (1 if idx < remainder else 0)

            for i in range(num_cases):
                try:
                    case_number = generate_case_number(case_type_code, case_counter[case_type_code])
                    case_counter[case_type_code] += 1

                    # Generate dates
                    days_back = random.randint(1, 90)
                    case_date = (datetime.utcnow() - timedelta(days=days_back)).isoformat()
                    judgment_date = (datetime.utcnow() - timedelta(days=random.randint(1, days_back))).isoformat()

                    # Create case
                    case = Case(
                        case_number=case_number,
                        case_type=case_type_code,
                        case_description=f"{case_type_name} case relating to jurisdiction matters",
                        court_id=court.id,
                        petitioner=random.choice(REAL_PETITIONERS),
                        respondent=random.choice(REAL_RESPONDENTS),
                        case_date=case_date,
                        case_status=random.choice(CASE_STATUSES),
                        pdf_url=f"https://judiciary.karnataka.gov.in/judgments/{case_number.replace(' ', '_')}.pdf"
                    )
                    db.add(case)
                    db.flush()  # Get case ID

                    # Create judgment
                    judgment = Judgment(
                        case_id=case.id,
                        judge_name=random.choice(REAL_JUDGES),
                        judgment_date=judgment_date,
                        judgment_text=f"The {case_type_name} is disposed. The {random.choice(['petitioner', 'respondent'])} has {random.choice(['succeeded', 'failed', 'partially succeeded'])} in their claims.",
                        verdict=random.choice(["ALLOWED", "DISMISSED", "PARTLY ALLOWED", "WITHDRAWN"])
                    )
                    db.add(judgment)

                    added_count += 1

                    if added_count % 10 == 0:
                        db.commit()
                        print(f"  ✓ Added {added_count}/100 cases")

                except Exception as e:
                    print(f"  ❌ Error adding case: {e}")
                    db.rollback()

        # Final commit
        db.commit()

        return {
            "status": "success",
            "message": "Successfully populated database with demo data",
            "cases_added": added_count,
            "total_cases": db.query(Case).count()
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error seeding data: {str(e)}")
    finally:
        db.close()


@router.get("/check-data")
async def check_data_status():
    """Check current database status"""
    db = SessionLocal()
    try:
        cases_count = db.query(Case).count()
        courts_count = db.query(Court).count()
        judgments_count = db.query(Judgment).count()

        return {
            "status": "ok",
            "cases": cases_count,
            "courts": courts_count,
            "judgments": judgments_count,
            "needs_seeding": cases_count < 50
        }
    finally:
        db.close()
