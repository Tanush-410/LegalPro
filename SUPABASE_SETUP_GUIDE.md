# Supabase Setup Guide - Complete Instructions

## Problem
The sync script fails because the Supabase `cases` table doesn't have the required columns.

**Error:** `Could not find the 'case_status' column of 'cases'`

## Solution

Follow these exact steps to set up your Supabase database:

---

## ✅ Step 1: Open Supabase Dashboard

1. Go to: **https://supabase.com/dashboard**
2. Sign in with your account
3. Select project: **courtcases**

---

## ✅ Step 2: Open SQL Editor

1. In the left sidebar, click **SQL Editor**
2. Click **New Query** button (top-right)
3. A blank SQL editor will open

---

## ✅ Step 3: Copy & Run the Setup SQL

**Copy the entire SQL below:**

```sql
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
```

**Steps to paste and run:**
1. Paste the SQL into the SQL Editor
2. Click the **RUN** button (play icon, top-right)
3. Wait for success message (should take ~2-3 seconds)
4. Look for: ✅ **Success**

---

## ✅ Step 4: Verify Table Creation

After running the SQL, verify the table was created:

1. In left sidebar, click **Table Editor**
2. You should see `cases` table in the list
3. Click on `cases` to view its columns
4. Verify these columns exist:
   - `id` (BIGINT PRIMARY KEY)
   - `case_number` (TEXT)
   - `case_type` (TEXT)
   - `cnr` (TEXT)
   - `petitioner` (TEXT)
   - `respondent` (TEXT)
   - `judge_name` (TEXT)
   - `pdf_url` (TEXT)
   - `case_status` (TEXT)
   - `priority` (INTEGER)
   - `created_at` (TIMESTAMP)
   - `updated_at` (TIMESTAMP)

---

## ✅ Step 5: Sync Your 79 Cases

After the table is created, go back to your terminal and run:

```bash
cd /Users/tanush.s.vashisht/Desktop/Tanush/work/court-ecosystem

# Run the sync script
python sync_supabase_simple.py
```

**What you should see:**
```
🔄 SUPABASE FULL SYNC - 79 COURT CASES
...
  [1/79] ✅ WP 1 OF 2026
  [2/79] ✅ WP 2 OF 2026
  ...
  [79/79] ✅ CRIM PET OFF 10 OF 2026

🎉 SUCCESS! All 79 cases synced to Supabase!
```

---

## ✅ Verify in Supabase

After sync completes, verify in Supabase dashboard:

1. Go to **Table Editor**
2. Click on `cases` table
3. Scroll through rows - you should see all 79 cases
4. Click on a case to see full details

---

## 🆘 Troubleshooting

### Issue: "Permission Denied" or "Invalid API Key"
- ✅ Make sure you're signed into Supabase with correct account
- ✅ Check project is named "courtcases"
- ✅ Credentials are already configured in scripts

### Issue: "Table already exists"
- This is OK! The script will drop it first and recreate
- Click RUN again - it will work

### Issue: Sync script still has errors after table creation
1. Run verify query in SQL Editor:
   ```sql
   SELECT column_name FROM information_schema.columns 
   WHERE table_name='cases' 
   ORDER BY ordinal_position;
   ```
2. This shows all columns - confirm they match the list above
3. Then run sync script again

### Issue: Some cases didn't sync
- The sync script shows progress per case
- If some failed, check the error messages
- Run sync again - successful cases won't be duplicated (using upsert logic)

---

## 📊 After Sync Completes

Once all 79 cases are synced to Supabase:

### Update Backend (Optional but Recommended)
Configure backend to use Supabase as primary database:

```bash
# Set these environment variables in your .env file:
SUPABASE_URL=https://tvcxhspsgxmlzafovcpi.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR2Y3hoc3BzZ3htbHphZm92Y3BpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzE5MjQzMjIsImV4cCI6MjA4NzUwMDMyMn0.OMBB0Kh2rOzts2cwaI9I7nBxKdf4fhLZappIuFdxGSQ
```

---

## 📝 Files Created

- `sync_supabase_simple.py` - Main sync script (syncs 79 cases)
- `SUPABASE_CREATE_TABLES.sql` - Full schema file  
- `setup_tables_direct.py` - Setup helper script
- `SUPABASE_SETUP_GUIDE.md` - This file

---

## ⏱️ Time Estimates

| Task | Time |
|------|------|
| Create Supabase table | ~10 seconds |
| Sync 79 cases | ~2-3 minutes |
| Verify in dashboard | ~30 seconds |
| **Total** | **~3-4 minutes** |

---

## ✅ Success Checklist

- [ ] Opened Supabase dashboard
- [ ] Located SQL Editor
- [ ] Copied and ran the SQL schema
- [ ] Verified `cases` table created
- [ ] Ran sync script: `python sync_supabase_simple.py`
- [ ] Saw "All 79 cases synced to Supabase!" message
- [ ] Checked cases in Supabase Table Editor (saw all 79 rows)

**Once complete, your dashboard will have:**
- ✅ All 79 court cases in Supabase
- ✅ Cases accessible via API
- ✅ Cloud-based database (always available)
- ✅ Ready for production deployment

---

**Need help?** Check the troubleshooting section or review error messages from sync script.
