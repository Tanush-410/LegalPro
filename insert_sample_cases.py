#!/usr/bin/env python3
import sqlite3
import random
from datetime import datetime, timedelta

db_path = '/Volumes/PortableSSD/court-ecosystem/court_cases.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Create court
cur.execute("INSERT OR IGNORE INTO courts (name, level, state, created_at) VALUES (?, ?, ?, ?)",
            ("Karnataka High Court", "HIGH", "Karnataka", datetime.utcnow().isoformat()))
conn.commit()

# Get court ID
cur.execute("SELECT id FROM courts WHERE name = 'Karnataka High Court'")
court_id = cur.fetchone()[0]

# Create sample cases
petitioners = ["Ram Kumar", "Priya Singh", "Sanjay Patel", "Deepa Sharma", "Vikas Verma"]
respondents = ["Union of India", "State of Karnataka", "CBI", "Delhi Police"]
case_types = ["Writ Petition", "Civil Appeal", "Review Petition", "Special Leave Petition"]

for i in range(20):
    case_number = f"WP-{random.randint(10000, 99999)}"
    case_date = (datetime.utcnow() - timedelta(days=random.randint(0, 100))).isoformat()
    
    cur.execute("""INSERT INTO cases 
                   (case_number, court_id, petitioner, respondent, case_type, case_date, case_status, created_at) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (case_number, court_id, random.choice(petitioners), random.choice(respondents),
                 random.choice(case_types), case_date, "PENDING", datetime.utcnow().isoformat()))

conn.commit()
cur.execute("SELECT COUNT(*) FROM cases")
count = cur.fetchone()[0]
print(f"✅ Inserted {count} total cases")
conn.close()
