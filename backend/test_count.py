#!/usr/bin/env python3
from app.database import SessionLocal
from app.models import Case, Court
from sqlalchemy import func

db = SessionLocal()
count = db.query(func.count(Case.id)).scalar() or 0
courts = db.query(func.count(Court.id)).scalar() or 0
print(f"Cases: {count}, Courts: {courts}")
db.close()
