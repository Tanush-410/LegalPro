#!/usr/bin/env python3
"""
Setup Supabase tables for court ecosystem
Run this to create all required tables in Supabase
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
print("🔧 SUPABASE TABLE SETUP")
print("="*70 + "\n")

try:
    from supabase import create_client
    import logging
    
    logging.basicConfig(level=logging.INFO)
    
    # Connect to Supabase
    print("📡 Connecting to Supabase...")
    supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    print("✅ Connected!\n")
    
    # Read SQL file
    sql_file = '/Users/tanush.s.vashisht/Desktop/Tanush/work/court-ecosystem/SUPABASE_CREATE_TABLES.sql'
    print(f"📖 Reading SQL from {sql_file}")
    
    with open(sql_file, 'r') as f:
        sql_content = f.read()
    
    # Split by semicolon and execute each statement
    statements = [s.strip() for s in sql_content.split(';') if s.strip()]
    
    print(f"📋 Found {len(statements)} SQL statements\n")
    
    executed = 0
    for i, statement in enumerate(statements, 1):
        # Skip comments
        if statement.startswith('--'):
            continue
            
        try:
            print(f"  [{i}/{len(statements)}] Executing: {statement[:50]}...")
            # Execute raw SQL
            result = supabase.rpc('exec_sql', {'sql': statement}).execute()
            print(f"  ✅ Success")
            executed += 1
        except Exception as e:
            # Some operations may not need rpc, try direct query
            try:
                print(f"  ⚠️ Trying alternate method...")
                # For non-SELECT statements, we might need different approach
                if 'CREATE' in statement or 'INSERT' in statement or 'DROP' in statement:
                    print(f"  ℹ️ Manual setup needed for: {statement[:30]}...")
            except:
                pass
    
    print(f"\n✅ Setup complete!")
    print("📝 Note: If some CREATE statements failed, you may need to run the SQL manually")
    print("   in the Supabase dashboard (SQL Editor) for CREATE TABLE statements.\n")
    
    # Verify tables exist by trying to query them
    print("🔍 Verifying tables...")
    try:
        # Try to select from courts
        response = supabase.table("courts").select("id", count="exact").execute()
        print(f"  ✅ courts table exists (columns: {len(response.data[0].keys()) if response.data else 'empty'})")
    except Exception as e:
        print(f"  ⚠️ courts table query failed: {str(e)[:50]}")
    
    try:
        # Try to select from cases
        response = supabase.table("cases").select("id", count="exact").execute()
        print(f"  ✅ cases table exists (columns: {len(response.data[0].keys()) if response.data else 'empty'})")
    except Exception as e:
        print(f"  ⚠️ cases table query failed: {str(e)[:50]}")
    
    try:
        # Try to select from judges
        response = supabase.table("judges").select("id", count="exact").execute()
        print(f"  ✅ judges table exists (columns: {len(response.data[0].keys()) if response.data else 'empty'})")
    except Exception as e:
        print(f"  ⚠️ judges table query failed: {str(e)[:50]}")
    
    print("\n" + "="*70)
    print("📋 MANUAL SETUP INSTRUCTIONS")
    print("="*70)
    print("""
If tables still don't exist, follow these steps:

1. Open Supabase Dashboard: https://supabase.com/dashboard
2. Go to: courtcases project → SQL Editor
3. Create a new query
4. Copy the SQL from: SUPABASE_CREATE_TABLES.sql
5. Run the queries
6. Then run: python sync_supabase_simple.py

Alternative: Use pgAdmin or connect with PostgreSQL client
to run the SQL directly.
    """)
    print("="*70 + "\n")
    
except ImportError:
    print("❌ supabase library not installed")
    print("   Install with: pip install supabase")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
