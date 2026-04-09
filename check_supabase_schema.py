#!/usr/bin/env python3
"""
Check current Supabase schema and show what needs to be fixed
"""

import os
import sys

# Supabase Credentials
SUPABASE_URL = "https://tvcxhspsgxmlzafovcpi.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR2Y3hoc3BzZ3htbHphZm92Y3BpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzE5MjQzMjIsImV4cCI6MjA4NzUwMDMyMn0.OMBB0Kh2rOzts2cwaI9I7nBxKdf4fhLZappIuFdxGSQ"

# Set environment variables
os.environ["SUPABASE_URL"] = SUPABASE_URL
os.environ["SUPABASE_ANON_KEY"] = SUPABASE_ANON_KEY

print("\n" + "="*70)
print("🔍 CHECKING SUPABASE SCHEMA")
print("="*70 + "\n")

try:
    from supabase import create_client
    
    # Connect to Supabase
    print("📡 Connecting to Supabase...")
    supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    print("✅ Connected!\n")
    
    # Try to get existing cases data to see what columns we have
    print("📋 Checking existing tables:\n")
    
    tables_to_check = ["cases", "courts", "judges", "judgments"]
    
    for table_name in tables_to_check:
        try:
            print(f"  Checking '{table_name}' table...")
            response = supabase.table(table_name).select("*", count="exact").limit(1).execute()
            
            if response.data and len(response.data) > 0:
                columns = list(response.data[0].keys())
                print(f"    ✅ Table EXISTS")
                print(f"    📊 Columns: {', '.join(columns)}")
            else:
                print(f"    ⚠️ Table EXISTS but is EMPTY")
                print(f"    📝 Unable to see columns (table empty)")
                
        except Exception as e:
            error_msg = str(e)
            if "not found" in error_msg.lower() or "does not exist" in error_msg.lower():
                print(f"    ❌ Table DOES NOT EXIST")
            else:
                print(f"    ⚠️ Connection error: {error_msg[:50]}")
        
        print()
    
    print("="*70)
    print("📊 ANALYSIS")
    print("="*70)
    print("""
If you see:
  ❌ Table DOES NOT EXIST - Need to CREATE the table
  ⚠️ Table EXISTS but EMPTY - Columns might not be set up correctly
  
SOLUTION: Run the SQL in Supabase SQL Editor
See: SUPABASE_SETUP_GUIDE.md for full instructions
    """)
    print("="*70 + "\n")
    
except ImportError:
    print("❌ Supabase library not installed")
    print("   Run: pip install supabase")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nTroubleshooting:")
    print("1. Check your internet connection")
    print("2. Verify Supabase credentials are correct")
    print("3. Check Supabase project status on dashboard")
    sys.exit(1)
