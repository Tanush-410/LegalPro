# 🚀 Supabase Setup Guide - Court Ecosystem Backend

This guide shows how to run the backend with **Supabase** (cloud database) instead of Docker.

---

## **What is Supabase?**

Supabase is a **free cloud PostgreSQL database**. You don't need to install anything locally!

- ✅ Free tier (up to 500MB)
- ✅ Automatic backups
- ✅ Cloud-hosted
- ✅ Simple connection string

---

## **Step 1: Create Supabase Account**

1. Go to: https://app.supabase.com
2. Sign up (free)
3. Create new project:
   - Project name: `court-ecosystem`
   - Password: Create strong password (save it!)
   - Region: Choose closest to you
   - Click "Create new project"

**Wait 2-3 minutes** for project to be ready.

---

## **Step 2: Get Connection String**

1. Go to your Supabase project dashboard
2. Click **"Settings"** (bottom left)
3. Click **"Database"**
4. Look for **"Connection pooling"** section
5. Switch to **"psycopg2"** mode (dropdown)
6. Copy the entire connection string

**It looks like:**
```
postgresql://postgres:[PASSWORD]@[PROJECT-ID].supabase.co:5432/postgres
```

---

## **Step 3: Setup Backend Locally**

### **3.1 Navigate to Project**
```bash
cd /Users/tanush.s.vashisht/Desktop/Tanush/work/court-ecosystem/backend
```

### **3.2 Create Python Environment**
```bash
python3 -m venv venv
source venv/bin/activate
```

### **3.3 Install Dependencies**
```bash
pip install -r requirements.txt
```

### **3.4 Configure Environment**
```bash
cp .env.example .env
```

### **3.5 Edit .env File**

Open `backend/.env` and update:

```env
# Replace with your Supabase connection string
DATABASE_URL=postgresql://postgres:[PASSWORD]@[PROJECT-ID].supabase.co:5432/postgres
DEBUG=True
SECRET_KEY=your-secret-key-here
```

**Example** (replace with YOUR values):
```env
DATABASE_URL=postgresql://postgres:mypassword123@abcdefgh.supabase.co:5432/postgres
DEBUG=True
SECRET_KEY=test-secret-key
```

---

## **Step 4: Start the Backend**

In the `backend` directory with venv activated:

```bash
uvicorn app.main:app --reload --port 8000
```

**You should see:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

---

## **Step 5: Access Your System**

### **API Documentation:**
Open in browser:
```
http://localhost:8000/docs
```

You'll see all endpoints. Try "GET /api/dashboard/stats" to test.

### **Dashboard:**
Open the HTML file:
```bash
open /Users/tanush.s.vashisht/Desktop/Tanush/work/court-ecosystem/dashboard/index.html
```

Or from terminal:
```
http://localhost:8000
```

### **Health Check:**
```bash
curl http://localhost:8000/health
```

Response:
```json
{"status":"ok","message":"Court Ecosystem API is running"}
```

---

## **Step 6: Verify Database Tables**

The backend automatically creates tables on first run. Check in Supabase:

1. Go to Supabase dashboard
2. Click **"SQL Editor"** (left sidebar)
3. Click **"New Query"**
4. Paste:
```sql
SELECT table_name FROM information_schema.tables 
WHERE table_schema='public';
```
5. Click "Run"

Should show:
- courts
- cases
- judgments
- documents
- document_metadata
- scrape_logs

---

## **Step 7: Test Scraper**

The scraper runs daily at 2 AM. To test manually:

**Create** `test_scrape.py` in project root:
```python
#!/usr/bin/env python3
import sys
sys.path.insert(0, '/Users/tanush.s.vashisht/Desktop/Tanush/work/court-ecosystem/backend')

from app.scheduler.jobs import scrape_court_documents

print("Starting manual scrape test...")
scrape_court_documents()
print("Scrape completed!")
```

**Run:**
```bash
cd /Users/tanush.s.vashisht/Desktop/Tanush/work/court-ecosystem
python3 test_scrape.py
```

Check logs and Supabase database for data.

---

## **Step 8: Setup Daily Automation**

To run scraper daily at 2 AM, use **cron** (Mac's scheduler):

### **Create Update Script**
Create `backend/run_scraper.sh`:
```bash
#!/bin/bash
cd /Users/tanush.s.vashisht/Desktop/Tanush/work/court-ecosystem/backend
source venv/bin/activate
python3 << 'EOF'
from app.scheduler.jobs import scrape_court_documents
scrape_court_documents()
EOF
```

Make executable:
```bash
chmod +x backend/run_scraper.sh
```

### **Add to Cron**
```bash
crontab -e
```

Add this line (runs daily at 2 AM):
```
0 2 * * * /Users/tanush.s.vashisht/Desktop/Tanush/work/court-ecosystem/backend/run_scraper.sh
```

Save and exit.

---

## **API Endpoints (All Working)**

```
✅ GET /api/dashboard/stats
✅ GET /api/dashboard/courts-breakdown
✅ GET /api/dashboard/timeline
✅ GET /api/cases
✅ GET /api/cases/{id}
✅ GET /api/cases/{id}/documents
✅ GET /api/judgments
✅ GET /health
✅ GET /
```

Test any endpoint:
```bash
curl http://localhost:8000/api/dashboard/stats | json_pp
```

---

## **Troubleshooting**

### **"Connection refused"**
- Check DATABASE_URL in .env
- Verify Supabase project is running
- Check password is correct

### **"Permission denied"**
- In Supabase, go to Settings → Database → SSL
- Download certificate if needed

### **Module not found**
- Ensure venv is activated: `source venv/bin/activate`
- Run: `pip install -r requirements.txt`

### **Tables not created**
- Kill and restart backend
- Tables auto-create on startup

---

## **Supabase Dashboard**

Monitor your data in Supabase:

1. **View Data:**
   - SQL Editor → Write queries
   - Table Editor → Browse tables

2. **Monitor Usage:**
   - Settings → Usage

3. **Manage Access:**
   - Settings → Database → Users

4. **Backups:**
   - Automatic daily backups included (free tier)

---

## **Next Steps**

1. ✅ Setup Supabase account
2. ✅ Get connection string
3. ✅ Run local backend
4. ✅ Access API & dashboard
5. ✅ Test with manual scrape
6. ✅ Setup daily automation (optional)

---

## **Comparison: Supabase vs Docker**

| Feature | Supabase | Docker |
|---------|----------|--------|
| Setup Time | 5 min | 5 min |
| Database Hosting | Cloud | Local |
| Cost | Free | Free |
| Backups | Auto | Manual |
| Scalability | Easy | Limited |
| Internet Needed | Yes | No |
| Complexity | Simple | Medium |

---

## **Timeline**

- **5 min:** Create Supabase account
- **2 min:** Get connection string
- **5 min:** Install dependencies
- **2 min:** Configure .env
- **1 min:** Start backend
- **Total: 15 minutes** ⏱️

---

## **You're All Set! 🎉**

Your backend is now running with Supabase!

- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Data: Supabase cloud
- Dashboard: `dashboard/index.html`

---

**Questions?** Check the error messages in terminal or review this guide.

**Next:** Start your backend and explore the API! 🚀
