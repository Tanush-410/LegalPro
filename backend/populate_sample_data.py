#!/usr/bin/env python3
"""
Populate database with sample court case data for testing
This demonstrates what real eCourts scraping would produce
"""
from datetime import datetime, timedelta
from app.database import SessionLocal
from app.models import Court, Case, Judgment, Document, CourtEnum
import random

def populate_sample_data():
    db = SessionLocal()
    
    try:
        # Clear existing data
        print("Clearing existing data...")
        db.query(Document).delete()
        db.query(Judgment).delete()
        db.query(Case).delete()
        db.query(Court).delete()
        db.commit()
        
        # Create courts
        print("Creating courts...")
        courts_data = [
            Court(name="Supreme Court of India", level=CourtEnum.SUPREME),
            Court(name="Delhi High Court", level=CourtEnum.HIGH, state="Delhi"),
            Court(name="Bombay High Court", level=CourtEnum.HIGH, state="Maharashtra"),
            Court(name="Calcutta High Court", level=CourtEnum.HIGH, state="West Bengal"),
            Court(name="Bengaluru District Court", level=CourtEnum.LOWER, district="Karnataka"),
            Court(name="Delhi District Court", level=CourtEnum.LOWER, district="Delhi"),
            Court(name="Mumbai District Court", level=CourtEnum.LOWER, district="Maharashtra"),
        ]
        
        for court in courts_data:
            db.add(court)
        db.commit()
        
        # Sample case data
        case_types = ["Writ Petition", "Civil Appeal", "Criminal Appeal", "Arbitration", "Habeas Corpus"]
        petitioners = [
            "Ram Kumar Singh",
            "Priya Sharma",
            "Tech Solutions Ltd.",
            "State of Karnataka",
            "Ministry of Education",
            "National Health Authority"
        ]
        respondents = [
            "State of India",
            "Municipal Corporation",
            "District Magistrate",
            "Reserve Bank of India",
            "Central Board of Direct Taxes",
            "Ministry of Home Affairs"
        ]
        judges = [
            "Hon'ble Justice Sanjay Singh",
            "Hon'ble Justice Priya Patel",
            "Hon'ble Justice Rajesh Kumar",
            "Hon'ble Justice Meera Verma",
            "Hon'ble Justice Arun Sharma",
            "Hon'ble Justice Deepa Bhardwaj"
        ]
        
        # Create sample cases from past 30 days (including today)
        print("Creating sample cases...")
        case_counter = 1
        for court in courts_data:
            num_cases = random.randint(3, 8)
            
            for i in range(num_cases):
                # Random date in past 30 days
                days_ago = random.randint(0, 29)
                case_date = datetime.utcnow() - timedelta(days=days_ago, hours=random.randint(0, 23))
                
                case = Case(
                    cnr=f"{court.level.name[:3].upper()}{case_counter:010d}",
                    case_number=f"WP-{case_counter:05d}/{datetime.utcnow().year}",
                    case_type=random.choice(case_types),
                    court_id=court.id,
                    petitioner=random.choice(petitioners),
                    respondent=random.choice(respondents),
                    case_date=case_date,
                    is_new=(days_ago < 2),  # Mark recent ones as new
                    first_detected_at=case_date + timedelta(hours=random.randint(1, 4))
                )
                db.add(case)
                db.flush()
                
                # Add judgment
                judgment_date = case_date + timedelta(days=random.randint(10, 60))
                judgment = Judgment(
                    case_id=case.id,
                    judge_name=random.choice(judges),
                    judgment_date=judgment_date,
                    judgment_text=f"This case was decided on {judgment_date.date()}. "
                                   f"The petitioner {case.petitioner} appealed against {case.respondent}. "
                                   f"After hearing arguments from both sides, the court decided in favor of "
                                   f"{'petitioner' if random.random() > 0.5 else 'respondent'}.",
                    verdict=random.choice(["Allowed", "Dismissed", "Partially Allowed"])
                )
                db.add(judgment)
                db.flush()
                
                # Add document
                pdf_url = f"https://hcservices.ecourts.gov.in/ecourtindiaHC/document/{case.cnr}.pdf"
                document = Document(
                    case_id=case.id,
                    judgment_id=judgment.id,
                    file_name=f"judgment_{case.case_number.replace('/', '-')}.pdf",
                    file_path=pdf_url,
                    file_type="pdf",
                    file_size=random.randint(100000, 500000),
                    source_url=pdf_url
                )
                db.add(document)
                
                case_counter += 1
        
        db.commit()
        
        # Verify
        total_courts = db.query(Court).count()
        total_cases = db.query(Case).count()
        total_judgments = db.query(Judgment).count()
        total_docs = db.query(Document).count()
        
        print(f"\n✅ Successfully populated database:")
        print(f"   - {total_courts} Courts")
        print(f"   - {total_cases} Cases")
        print(f"   - {total_judgments} Judgments")
        print(f"   - {total_docs} Documents")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    populate_sample_data()
