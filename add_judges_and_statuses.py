#!/usr/bin/env python3
import sqlite3
import random
from datetime import datetime, timedelta

db_path = '/Volumes/PortableSSD/court-ecosystem/court_cases.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Get all case IDs
cur.execute("SELECT id FROM cases")
case_ids = [row[0] for row in cur.fetchall()]

# Sample judges
judges = [
    "Hon'ble Justice Aravind Kumar",
    "Hon'ble Justice Nageshwara Rao",
    "Hon'ble Justice P.S. Narasimha",
    "Hon'ble Justice Sanjay Karol",
    "Hon'ble Justice Mustafa Aftab",
    "Hon'ble Justice B.V. Nagarathna",
    "Hon'ble Justice Vikram Nath",
    "Hon'ble Justice S. Krishnamurthy"
]

# Verdicts
verdicts = ["ALLOWED", "DISMISSED", "PARTLY ALLOWED", "WITHDRAWN"]

# Add judgments for each case
for case_id in case_ids:
    judge = random.choice(judges)
    verdict = random.choice(verdicts)
    judgment_date = (datetime.utcnow() - timedelta(days=random.randint(1, 80))).isoformat()
    
    cur.execute("""INSERT INTO judgments 
                   (case_id, judge_name, judgment_date, verdict, created_at) 
                   VALUES (?, ?, ?, ?, ?)""",
                (case_id, judge, judgment_date, verdict, datetime.utcnow().isoformat()))

conn.commit()

# Check result
cur.execute("SELECT COUNT(*) FROM judgments")
count = cur.fetchone()[0]
print(f"✅ Added {count} judgments with judges")

# Now add varied case statuses
statuses = ["FILED", "DISPOSED", "APPEALED", "SETTLED", "ONGOING", "ADJOURNED"]
cur.execute("SELECT id FROM cases")
case_ids = [row[0] for row in cur.fetchall()]

for case_id in case_ids:
    status = random.choice(statuses)
    cur.execute("UPDATE cases SET case_status = ? WHERE id = ?", (status, case_id))

conn.commit()

# Verify
cur.execute("SELECT DISTINCT case_status FROM cases")
statuses = cur.fetchall()
print(f"✅ Updated case statuses: {', '.join(row[0] for row in statuses)}")

# Get distinct judges
cur.execute("SELECT COUNT(DISTINCT judge_name) FROM judgments")
judge_count = cur.fetchone()[0]
print(f"✅ Total unique judges: {judge_count}")

conn.close()
