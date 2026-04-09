#!/usr/bin/env python3
from app.database import SessionLocal
from app.models import Case, Court, Judgment, Document, CourtEnum, ScrapeLog
from sqlalchemy import func
from datetime import datetime

db = SessionLocal()

verified_only = False

# Total counts - use simpler approach to avoid subquery issues
total_cases = db.query(func.count(Case.id)).scalar() or 0

if verified_only:
    # Count only cases with both judgment and document
    total_cases = (
        db.query(func.count(Case.id))
        .filter(Case.judgments.any())
        .filter(Case.documents.any())
        .scalar() or 0
    )

print(f"Total cases: {total_cases}")

# Total judgments
total_judgments = db.query(func.count(Judgment.id)).scalar() or 0
print(f"Total judgments: {total_judgments}")

# Count by court level - use direct filter instead of complex joins
supreme_cases = db.query(Case).join(Court).filter(Court.level == CourtEnum.SUPREME).all()
supreme_count = len([c for c in supreme_cases if not verified_only or (c.judgments and c.documents)])
print(f"Supreme: {len(supreme_cases)} found, {supreme_count} after filter")

high_cases = db.query(Case).join(Court).filter(Court.level == CourtEnum.HIGH).all()
high_count = len([c for c in high_cases if not verified_only or (c.judgments and c.documents)])
print(f"High: {len(high_cases)} found, {high_count} after filter")

lower_cases = db.query(Case).join(Court).filter(Court.level == CourtEnum.LOWER).all()
lower_count = len([c for c in lower_cases if not verified_only or (c.judgments and c.documents)])
print(f"Lower: {len(lower_cases)} found, {lower_count} after filter")

db.close()
