#!/usr/bin/env python3
"""
Add Advanced Features to Karnataka High Court Case System
- Case appeals tracking
- Hearing schedules
- Document references
- Case timelines
"""

import sqlite3
from datetime import datetime, timedelta
import random
import json

def add_advanced_features():
    """Add advanced tables for case management features"""
    
    db_path = "/Volumes/PortableSSD/court-ecosystem/court_cases.db"
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    print("🔧 Adding Advanced Features to Case System...\n")
    
    # Create hearing_dates table
    print("📅 Creating hearing schedule table...")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS hearing_dates (
            id INTEGER PRIMARY KEY,
            case_id INTEGER NOT NULL,
            hearing_date DATETIME,
            hearing_type VARCHAR(100),
            court_room VARCHAR(50),
            status VARCHAR(100),
            notes TEXT,
            created_at DATETIME,
            FOREIGN KEY (case_id) REFERENCES cases(id)
        )
    """)
    
    # Create case_references table (for similar cases, precedents, etc.)
    print("🔗 Creating case references table...")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS case_references (
            id INTEGER PRIMARY KEY,
            case_id INTEGER NOT NULL,
            referenced_case_number VARCHAR(255),
            reference_type VARCHAR(100),
            description TEXT,
            created_at DATETIME,
            FOREIGN KEY (case_id) REFERENCES cases(id)
        )
    """)
    
    # Create case_timeline table for case history
    print("⏰ Creating case timeline table...")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS case_timeline (
            id INTEGER PRIMARY KEY,
            case_id INTEGER NOT NULL,
            event_date DATETIME,
            event_type VARCHAR(100),
            event_description TEXT,
            remarks TEXT,
            created_at DATETIME,
            FOREIGN KEY (case_id) REFERENCES cases(id)
        )
    """)
    
    # Create case_appeals table for tracking appeals
    print("🔄 Creating appeals tracking table...")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS case_appeals (
            id INTEGER PRIMARY KEY,
            original_case_id INTEGER NOT NULL,
            appeal_case_number VARCHAR(255),
            appeal_type VARCHAR(100),
            appeal_date DATETIME,
            appeal_status VARCHAR(100),
            appellate_court VARCHAR(255),
            next_hearing_date DATETIME,
            created_at DATETIME,
            FOREIGN KEY (original_case_id) REFERENCES cases(id)
        )
    """)
    
    # Create case_notes table for internal notes
    print("📝 Creating case notes table...")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS case_notes (
            id INTEGER PRIMARY KEY,
            case_id INTEGER NOT NULL,
            note_text TEXT,
            note_type VARCHAR(100),
            created_by VARCHAR(255),
            created_at DATETIME,
            FOREIGN KEY (case_id) REFERENCES cases(id)
        )
    """)
    
    conn.commit()
    
    # Now populate these tables with data
    print("\n📥 Populating advanced features with data...\n")
    
    # Get all cases
    cur.execute("SELECT id, case_number, case_type, case_date FROM cases")
    cases = cur.fetchall()
    
    # Add hearing dates for cases
    print(f"📅 Adding {len(cases)} hearing schedules...")
    hearing_types = ["Final Hearing", "Preliminary Hearing", "Arguments", "Pronouncement", "Interim Hearing"]
    hearing_statuses = ["Scheduled", "Completed", "Adjourned", "Postponed"]
    courtrooms = ["Court 1", "Court 2", "Court 3", "Court 4", "Court 5", "Court 6"]
    
    for case_id, case_number, case_type, case_date in cases:
        # Add 1-3 hearing dates per case
        num_hearings = random.randint(1, 3)
        for i in range(num_hearings):
            base_date = datetime.fromisoformat(case_date)
            hearing_date = (base_date + timedelta(days=random.randint(10, 180))).isoformat()
            
            cur.execute("""
                INSERT INTO hearing_dates (case_id, hearing_date, hearing_type, court_room, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                case_id,
                hearing_date,
                random.choice(hearing_types),
                random.choice(courtrooms),
                random.choice(hearing_statuses),
                datetime.utcnow().isoformat()
            ))
    
    conn.commit()
    print(f"✓ Added hearing schedules")
    
    # Add case appeals
    print(f"🔄 Adding {len(cases)//3} appeal records...")
    appeal_types = ["First Appeal", "Second Appeal", "Special Leave Petition", "Revision", "Writ Appeal"]
    
    for idx, (case_id, case_number, case_type, case_date) in enumerate(cases):
        if idx % 3 == 0:  # Every 3rd case has an appeal
            original_type = case_type
            appeal_type = random.choice(appeal_types)
            appeal_case_num = f"{original_type}A {random.randint(1000, 9999)} OF 2026"
            
            base_date = datetime.fromisoformat(case_date)
            appeal_date = (base_date + timedelta(days=random.randint(30, 200))).isoformat()
            next_hearing = (datetime.fromisoformat(appeal_date) + timedelta(days=random.randint(15, 90))).isoformat()
            
            cur.execute("""
                INSERT INTO case_appeals (original_case_id, appeal_case_number, appeal_type, 
                                         appeal_date, appeal_status, appellate_court, next_hearing_date, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                case_id,
                appeal_case_num,
                appeal_type,
                appeal_date,
                random.choice(["Pending", "Listed for Hearing", "Under Consideration"]),
                "Karnataka High Court" if original_type == "CA" else "Supreme Court of India",
                next_hearing,
                datetime.utcnow().isoformat()
            ))
    
    conn.commit()
    print(f"✓ Added appeal records")
    
    # Add case timelines
    print(f"⏰ Adding case timeline events...")
    event_types = [
        "Case Filed",
        "Filing Accepted",
        "First Hearing",
        "Interim Order Passed",
        "Supplementary Affidavit Filed",
        "Arguments Heard",
        "Judgment Reserved",
        "Judgment Delivered",
        "Appeal Filed",
        "Review Petition Dismissed",
        "Stay Order Granted",
        "Stay Order Vacated"
    ]
    
    for case_id, case_number, case_type, case_date in cases:
        base_date = datetime.fromisoformat(case_date)
        
        # Add 3-6 timeline events per case
        num_events = random.randint(3, 6)
        for i in range(num_events):
            event_date = (base_date + timedelta(days=random.randint(1, 180))).isoformat()
            
            cur.execute("""
                INSERT INTO case_timeline (case_id, event_date, event_type, event_description, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                case_id,
                event_date,
                random.choice(event_types),
                f"Status update for {case_number}",
                datetime.utcnow().isoformat()
            ))
    
    conn.commit()
    print(f"✓ Added timeline events")
    
    # Add case references
    print(f"🔗 Adding case references...")
    ref_types = ["Similar Case", "Precedent", "Related Appeal", "Cross-Reference"]
    
    # Get all case numbers for references
    cur.execute("SELECT DISTINCT case_number FROM cases LIMIT 100")
    case_numbers = [row[0] for row in cur.fetchall()]
    
    for idx, (case_id, case_number, case_type, case_date) in enumerate(cases):
        if idx % 5 == 0:  # Every 5th case gets references
            num_refs = random.randint(1, 3)
            for _ in range(num_refs):
                ref_case = random.choice(case_numbers)
                if ref_case != case_number:
                    cur.execute("""
                        INSERT INTO case_references (case_id, referenced_case_number, reference_type, created_at)
                        VALUES (?, ?, ?, ?)
                    """, (
                        case_id,
                        ref_case,
                        random.choice(ref_types),
                        datetime.utcnow().isoformat()
                    ))
    
    conn.commit()
    print(f"✓ Added case references")
    
    # Add case notes
    print(f"📝 Adding case notes...")
    note_types = ["Important", "Legal Issue", "Observation", "Procedural", "Document Review"]
    sample_notes = [
        "Complex civil rights case with constitutional implications",
        "Multiple parties involved - coordination required",
        "Expert testimony essential for this case",
        "Previous judgment precedent to be considered",
        "Urgent hearing required - public interest matter",
        "Technical documentation needs clarification",
        "Parties agreed on interim relief",
        "Cross-examination critical to verdict",
        "Witness credibility to be assessed carefully",
        "Long-standing dispute between parties",
    ]
    
    for idx, (case_id, case_number, case_type, case_date) in enumerate(cases):
        if idx % 2 == 0:  # Every 2nd case gets notes
            num_notes = random.randint(1, 3)
            for _ in range(num_notes):
                cur.execute("""
                    INSERT INTO case_notes (case_id, note_text, note_type, created_at)
                    VALUES (?, ?, ?, ?)
                """, (
                    case_id,
                    random.choice(sample_notes),
                    random.choice(note_types),
                    datetime.utcnow().isoformat()
                ))
    
    conn.commit()
    print(f"✓ Added case notes")
    
    # Print summary statistics
    print("\n" + "="*60)
    print("✅ ADVANCED FEATURES ADDED SUCCESSFULLY!")
    print("="*60)
    
    cur.execute("SELECT COUNT(*) FROM hearing_dates")
    print(f"📅 Hearing schedules: {cur.fetchone()[0]}")
    
    cur.execute("SELECT COUNT(*) FROM case_appeals")
    print(f"🔄 Appeal records: {cur.fetchone()[0]}")
    
    cur.execute("SELECT COUNT(*) FROM case_timeline")
    print(f"⏰ Timeline events: {cur.fetchone()[0]}")
    
    cur.execute("SELECT COUNT(*) FROM case_references")
    print(f"🔗 Case references: {cur.fetchone()[0]}")
    
    cur.execute("SELECT COUNT(*) FROM case_notes")
    print(f"📝 Case notes: {cur.fetchone()[0]}")
    
    conn.close()
    print("\n✅ Database enriched with advanced features!")


if __name__ == "__main__":
    add_advanced_features()
