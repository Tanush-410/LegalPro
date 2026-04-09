from datetime import datetime, timedelta
from app.database import SessionLocal
from app.models import Case, Court
import random

db = SessionLocal()
courts = db.query(Court).all()
petitioners = ["Ram Kumar", "Priya Singh", "Sanjay Patel", "Deepa Sharma", "Vikas Verma", "Ananya Roy", "Arjun Gupta", "Neha Kapoor"]
respondents = ["Union of India", "State of Karnataka", "CBI", "Delhi Police", "Ministry of Justice", "High Court of Delhi"]
case_types = ["Writ Petition", "Civil Appeal", "Review Petition", "Special Leave Petition"]
for i in range(30):
    for court in courts:
        case_date = datetime.utcnow() - timedelta(days=random.randint(0, 30))
        case = Case(
            case_number=f"{court.name.split()[0][:3].upper()}-{random.randint(10000, 99999)}",
            court_id=court.id,
            petitioner=random.choice(petitioners),
            respondent=random.choice(respondents),
            case_type=random.choice(case_types),
            case_date=case_date
        )
        db.add(case)
db.commit()
db.close()
print("✅ Sample cases inserted.")
