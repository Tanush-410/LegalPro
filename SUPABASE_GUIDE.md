# 📦 Supabase Integration Guide

## Quick Setup

### Step 1: Create Supabase Account & Project
1. Go to https://supabase.com
2. Click "Start your project"
3. Create new project
4. Get your credentials from Settings → API

### Step 2: Set Environment Variables

```bash
# In your terminal or .env file
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_ANON_KEY="your-anon-key-here"
```

### Step 3: Create Tables in Supabase

Go to Supabase Dashboard → SQL Editor and run:

```sql
-- Create courts table
CREATE TABLE courts (
  id BIGSERIAL PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  level TEXT,
  state TEXT,
  district TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Create cases table
CREATE TABLE cases (
  id BIGSERIAL PRIMARY KEY,
  case_number TEXT NOT NULL UNIQUE,
  cnr TEXT UNIQUE,
  case_type TEXT,
  case_description TEXT,
  court_id BIGINT REFERENCES courts(id),
  petitioner TEXT,
  respondent TEXT,
  case_date TIMESTAMP,
  pdf_url TEXT,
  case_status TEXT DEFAULT 'Active',
  priority INTEGER DEFAULT 0,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Create judgments table
CREATE TABLE judgments (
  id BIGSERIAL PRIMARY KEY,
  case_id BIGINT REFERENCES cases(id),
  judge_name TEXT,
  judgment_date TIMESTAMP,
  judgment_text TEXT,
  verdict TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Create documents table
CREATE TABLE documents (
  id BIGSERIAL PRIMARY KEY,
  case_id BIGINT REFERENCES cases(id),
  judgment_id BIGINT REFERENCES judgments(id),
  file_name TEXT,
  file_path TEXT,
  file_type TEXT,
  source_url TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### Step 4: Run Sync Script

```bash
python3 sync_to_supabase.py
```

You'll see:
```
================================================================================
🔄 SYNCING LOCAL DATABASE TO SUPABASE
================================================================================

📡 Connecting to Supabase...
📦 Found 79 cases in local database
📤 Uploading cases to Supabase...
✅ Court synced: Karnataka High Court

================================================================================
✅ SYNC COMPLETE
================================================================================

📊 Results:
   • Cases Synced: 79
   • Errors: 0
   • Total Cases: 79

🎉 All cases successfully synced to Supabase!
```

### Step 5: Verify in Supabase Dashboard

1. Go to Supabase Dashboard
2. Click "Table Editor" 
3. Check `courts` table - should show "Karnataka High Court"
4. Check `cases` table - should show 79 records

---

## 🔐 Security Setup (Important!)

### Enable Row Level Security (RLS)

In Supabase Dashboard → Authentication → Policies:

```sql
-- Allow anyone to SELECT cases (read-only)
CREATE POLICY "Allow public read" ON cases
  FOR SELECT USING (TRUE);

-- Allow authenticated users to INSERT
CREATE POLICY "Allow authenticated insert" ON cases
  FOR INSERT WITH CHECK (auth.role() = 'authenticated');
```

---

## 📊 Verify Your Data

In Supabase SQL Editor:

```sql
-- Check total cases
SELECT COUNT(*) as total_cases FROM cases;

-- Check case status distribution
SELECT case_status, COUNT(*) as count 
FROM cases 
GROUP BY case_status;

-- Check judges
SELECT DISTINCT judge_name FROM judgments ORDER BY judge_name;

-- Check case types
SELECT case_type, COUNT(*) as count 
FROM cases 
GROUP BY case_type 
ORDER BY count DESC;
```

---

## 🔄 Auto-Sync Setup (Advanced)

### Option 1: Manual Sync Daily
```bash
# Run daily via cron
0 2 * * * cd /path/to/project && python3 sync_to_supabase.py
```

### Option 2: Python Scheduler
```python
# In app/scheduler/jobs.py
from apscheduler.schedulers.background import BackgroundScheduler
from sync_to_supabase import sync_database

scheduler = BackgroundScheduler()

@scheduler.scheduled_job('cron', hour=2, minute=0)
def scheduled_sync():
    sync_database()

scheduler.start()
```

---

## 🌐 Use Supabase Data in Frontend

### JavaScript Example:
```javascript
// Fetch from Supabase
const { data, error } = await supabase
  .from('cases')
  .select('*')
  .eq('case_status', 'Active');

// Display in your app
data.forEach(case => {
  console.log(`${case.case_number}: ${case.petitioner} vs ${case.respondent}`);
});
```

### React Example:
```jsx
import { useEffect, useState } from 'react';
import { supabase } from './supabaseClient';

function CasesList() {
  const [cases, setCases] = useState([]);

  useEffect(() => {
    const fetchCases = async () => {
      const { data } = await supabase
        .from('cases')
        .select('*')
        .order('case_date', { ascending: false });
      setCases(data);
    };
    
    fetchCases();
  }, []);

  return (
    <div>
      {cases.map(c => (
        <div key={c.id}>
          <h3>{c.case_number}</h3>
          <p>{c.case_status}</p>
        </div>
      ))}
    </div>
  );
}
```

---

## 🐛 Troubleshooting

### Error: "SUPABASE_URL and SUPABASE_ANON_KEY env vars required"
**Solution:** Set environment variables before running sync script
```bash
export SUPABASE_URL="your_url"
export SUPABASE_ANON_KEY="your_key"
python3 sync_to_supabase.py
```

### Error: "relation cases does not exist"
**Solution:** Create tables using SQL editor (see Step 3 above)

### Cases not appearing in Supabase
**Solution:** 
1. Check RLS policies are correct
2. Verify sync script ran without errors
3. Check Supabase logs for insert errors

### Some cases failed to sync
**Solution:**
- May be due to duplicate case_numbers
- Check Supabase logs for details
- Delete existing data and re-run sync

---

## 📈 Monitor Syncs

Track successful syncs:

```sql
-- Create sync_logs table
CREATE TABLE sync_logs (
  id BIGSERIAL PRIMARY KEY,
  sync_date TIMESTAMP DEFAULT NOW(),
  cases_synced INTEGER,
  errors INTEGER,
  status TEXT,
  notes TEXT
);

-- Log each sync
INSERT INTO sync_logs (cases_synced, errors, status)
VALUES (79, 0, 'success');
```

---

## 🎯 Next Steps

1. ✅ Set up environment variables
2. ✅ Create Supabase tables
3. ✅ Run sync_to_supabase.py
4. ✅ Verify data in dashboard
5. ✅ Set up RLS policies
6. ✅ Configure auto-sync if needed
7. ✅ Integrate with frontend

---

## 💡 Tips & Tricks

### Backup Local Data Before Syncing
```bash
cp /path/to/knowledgebase.db knowledgebase.db.backup
```

### Check Sync Progress
```bash
tail -f sync_to_supabase.py.log
```

### Delete & Re-sync
```sql
-- DELETE FROM cases; -- Clear existing
-- Then re-run sync script
```

---

## 📞 Support

- **Supabase Docs:** https://supabase.com/docs
- **API Reference:** https://supabase.com/docs/reference
- **Community:** https://github.com/supabase/supabase/discussions

---

**Last Updated:** March 16, 2026
**Status:** Ready for Production ✅
