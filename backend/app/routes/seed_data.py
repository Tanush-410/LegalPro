"""
Data seeding endpoint - Populates database with sample court cases
"""

from fastapi import APIRouter
from ..database import SessionLocal
from ..models import Case, Court, Judgment, CourtEnum
from datetime import datetime
import random
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/seed", tags=["seed"])

JUDGES = ["Justice Kumar", "Justice Singh", "Justice Sharma", "Justice Patel", "Justice Reddy"]
PETITIONERS = ["ABC Corp", "XYZ Industries", "State of Karnataka", "Union of India", "Tech Ltd"]
RESPONDENTS = ["State of Karnataka", "Union of India", "Ministry of Labour", "BMTC", "Tax Department"]


@router.post("/populate-demo-data")  
async def populate_demo_data():
    """Populate database with 100 demo court cases"""
    db = SessionLocal()
    try:
        # Check existing data
        existing_cases = db.query(Case).count()
        if existing_cases > 50:
            return {"status": "skipped", "reason": "Database already populated", "cases": existing_cases}

        # Get or create court
        court = db.query(Court).filter_by(name="Karnataka High Court").first()
        if not court:
            court = Court(name="Karnataka High Court", level=CourtEnum.HIGH, state="Karnataka")
            db.add(court)
            db.flush()
        
        # Create 100 cases
        added = 0
        for i in range(100):
            try:
                case = Case(
                    case_number=f"WP-{2000 + i}/2026",
                    case_type="WP",
                    case_description=f"Court case {i+1}",
                    court_id=court.id,
                    petitioner=random.choice(PETITIONERS),
                    respondent=random.choice(RESPONDENTS),
                    case_date=datetime.utcnow().isoformat(),
                    case_status="PENDING",
                    pdf_url=f"https://example.com/{i}.pdf"
                )
                db.add(case)
                db.flush()
                
                judgment = Judgment(
                    case_id=case.id,
                    judge_name=random.choice(JUDGES),
                    judgment_date=datetime.utcnow().isoformat(),
                    judgment_text="Judgment text",
                    verdict="PENDING"
                )
                db.add(judgment)
                added += 1
                
                if added % 20 == 0:
                    db.commit()
            except Exception as e:
                logger.error(f"Error: {e}")
                db.rollback()
        
        db.commit()
        final = db.query(Case).count()
        return {"status": "success", "cases_added": added, "total": final}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        db.close()


@router.get("/check-data")
async def check_data_status():
    """Check database status"""
    db = SessionLocal()
    try:
        cases = db.query(Case).count()
        return {"cases": cases, "needs_seeding": cases == 0}
    finally:
        db.close()
