#!/usr/bin/env python3
"""
Sync local SQLite database to Supabase PostgreSQL
Run this script to push all cases to Supabase
"""

import os
import sys
import json
from datetime import datetime

sys.path.insert(0, '/Users/tanush.s.vashisht/Desktop/Tanush/work/court-ecosystem/backend')

from app.database import SessionLocal
from app.models import Case, Court, Judgment
from app.supabase_manager import SupabaseManager

print("\n" + "="*80)
print("🔄 SYNCING LOCAL DATABASE TO SUPABASE")
print("="*80 + "\n")

# Check if Supabase credentials are set
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_ANON_KEY")

if not supabase_url or not supabase_key:
    print("❌ ERROR: Supabase credentials not configured!")
    print("\n📝 SETUP INSTRUCTIONS:")
    print("1. Create a Supabase project at https://supabase.com")
    print("2. Get your SUPABASE_URL and SUPABASE_ANON_KEY")
    print("3. Set environment variables:")
    print("   export SUPABASE_URL='your_url'")
    print("   export SUPABASE_ANON_KEY='your_key'")
    print("4. Run this script again")
    print("\n💾 Alternative: Use local SQLite database (already synced)")
    sys.exit(1)

try:
    # Initialize Supabase
    print("📡 Connecting to Supabase...")
    sm = SupabaseManager()
    
    # Get all cases from local database
    db = SessionLocal()
    local_cases = db.query(Case).all()
    local_court = db.query(Court).first()
    
    print(f"📦 Found {len(local_cases)} cases in local database")
    
    # Sync to Supabase
    print("📤 Uploading cases to Supabase...")
    
    synced = 0
    errors = 0
    
    for case in local_cases:
        try:
            # Prepare case data
            case_data = {
                "case_number": case.case_number,
                "cnr": case.cnr,
                "case_type": case.case_type,
                "case_description": case.case_description,
                "petitioner": case.petitioner,
                "respondent": case.respondent,
                "case_date": case.case_date.isoformat() if case.case_date else None,
                "pdf_url": case.pdf_url,
                "case_status": case.case_status,
                "priority": case.priority,
                "court_name": case.court.name if case.court else "Karnataka High Court",
                "judge_name": case.judgments[0].judge_name if case.judgments else None,
            }
            
            # Attempt to create in Supabase (will skip if already exists)
            result = sm.create_case(case_data)
            if result:
                synced += 1
            
        except Exception as e:
            errors += 1
            print(f"   ⚠️  Error syncing {case.case_number}: {str(e)[:50]}")
    
    # Sync court information
    if local_court:
        try:
            court_data = {
                "name": local_court.name,
                "level": local_court.level,
                "state": local_court.state,
                "district": local_court.district
            }
            sm.create_court(court_data)
            print(f"✅ Court synced: {local_court.name}")
        except Exception as e:
            print(f"⚠️  Could not sync court: {e}")
    
    # Summary
    print("\n" + "="*80)
    print("✅ SYNC COMPLETE")
    print("="*80)
    print(f"\n📊 Results:")
    print(f"   • Cases Synced: {synced}")
    print(f"   • Errors: {errors}")
    print(f"   • Total Cases: {len(local_cases)}")
    
    if errors == 0:
        print(f"\n🎉 All cases successfully synced to Supabase!")
        print(f"   Database: Karnataka High Court")
        print(f"   Records: {synced} cases, {len(local_cases)} total")
    else:
        print(f"\n⚠️  Some cases had errors during sync")
    
    print("\n💡 Next Steps:")
    print("   • Visit your Supabase dashboard to view the data")
    print("   • Set up Supabase auto-sync for real-time updates")
    print("   • Configure additional security policies")
    
    print("\n" + "="*80)

except Exception as e:
    print(f"\n❌ Sync failed: {e}")
    print("\nTroubleshooting:")
    print("1. Verify SUPABASE_URL and SUPABASE_ANON_KEY are correct")
    print("2. Ensure Supabase project has 'cases' and 'courts' tables")
    print("3. Check that RLS policies allow inserts")
    sys.exit(1)
