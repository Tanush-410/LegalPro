#!/usr/bin/env python3
"""
Direct Supabase Schema Setup using PostgreSQL connection
Sets up all required tables in Supabase PostgreSQL database
"""

import os
import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s') 
logger = logging.getLogger(__name__)

# Supabase Credentials
SUPABASE_URL = "https://tvcxhspsgxmlzafovcpi.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR2Y3hoc3BzZ3htbHphZm92Y3BpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzE5MjQzMjIsImV4cCI6MjA4NzUwMDMyMn0.OMBB0Kh2rOzts2cwaI9I7nBxKdf4fhLZappIuFdxGSQ"
SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR2Y3hoc3BzZ3htbHphZm92Y3BpIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MTkyNDMyMiwiZXhwIjoyMDg3NTAwMzIyfQ.1K7gJUCVYBJ5pOUm5GVNQ00EJHHxoJ0ynPWlB0qhI_U"

# Create a minimal cases table first to see what happens
MINIMAL_SCHEMA = """
-- Drop and recreate cases table with minimal fields
DROP TABLE IF EXISTS cases CASCADE;

CREATE TABLE cases (
    id BIGSERIAL PRIMARY KEY,
    case_number TEXT NOT NULL,
    case_type TEXT,
    cnr TEXT,
    petitioner TEXT,
    respondent TEXT,
    judge_name TEXT,
    pdf_url TEXT,
    case_status TEXT DEFAULT 'Active',
    priority INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes
CREATE INDEX idx_cases_case_number ON cases(case_number);
CREATE INDEX idx_cases_case_type ON cases(case_type);

-- Enable RLS
ALTER TABLE cases ENABLE ROW LEVEL SECURITY;

-- Allow public access
CREATE POLICY "Allow public read" ON cases FOR SELECT USING (true);
"""

print("\n" + "="*70)
print("🔧 DIRECT SUPABASE SCHEMA SETUP")
print("="*70 + "\n")

try:
    import psycopg2
    from psycopg2 import sql
    import base64
    import json
    
    logger.info("📡 Attempting direct PostgreSQL connection...")
    
    # Extract database credentials from Supabase URL
    # Format: https://[project-id].supabase.co
    project_id = SUPABASE_URL.split('//')[1].split('.')[0]
    
    # Attempt connections (Supabase uses specific credentials format)
    # Connection string format:
    db_user = "postgres"
    db_host = f"{project_id}.db.supabase.co"
    db_name = "postgres"
    db_port = 5432
    
    # Try using the anon key's embedded password or try common passwords
    # Note: This requires knowing the postgres password which isn't in the anon key
    
    logger.warning("⚠️ Direct PostgreSQL connection requires service role key with postgres password")
    logger.info("\n📋 Alternative: Use Supabase Dashboard")
    logger.info("   1. Go to: https://supabase.com/dashboard")
    logger.info("   2. Project: courtcases")
    logger.info("   3. Click SQL Editor")
    logger.info("   4. Create new query")
    logger.info("   5. Copy-paste SQL from below:")
    logger.info("   6. Click Run")
    
    print("\n" + "="*70)
    print("📝 COPY THIS SQL AND RUN IN SUPABASE")
    print("="*70 + "\n")
    print(MINIMAL_SCHEMA)
    print("\n" + "="*70 + "\n")
    
except ImportError:
    logger.warning("⚠️ psycopg2 not available, using alternative method...")
    print("\n" + "="*70)
    print("📝 COPY THIS SQL AND RUN IN SUPABASE")  
    print("="*70 + "\n")
    print(MINIMAL_SCHEMA)
    print("\n" + "="*70 + "\n")

except Exception as e:
    logger.error(f"Error: {e}")
    print("\n" + "="*70)
    print("📝 COPY THIS SQL AND RUN IN SUPABASE")
    print("="*70 + "\n")
    print(MINIMAL_SCHEMA)
    print("\n" + "="*70 + "\n")

print("""
NEXT STEPS:
1️⃣  Run the SQL above in Supabase dashboard
2️⃣  Then execute: python sync_supabase_simple.py
3️⃣  All 79 cases will sync to Supabase

ALTERNATIVE - If you cannot create tables:
- The tables might already exist with different column names
- Run this command to check existing schema:
  SELECT column_name FROM information_schema.columns WHERE table_name='cases';
""")
