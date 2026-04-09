# 🏛️ Karnataka High Court Integration Guide

Real judgment data from **https://judiciary.karnataka.gov.in** now integrated into your court ecosystem dashboard!

## Overview

This integration connects your dashboard to the Karnataka High Court website to pull real, up-to-date judgment data including:

- ✅ **Real Cases**: Actual judgment orders from 2024-2026
- ✅ **Case Classifications**: WP (Writ Petition), CP (Civil Petition), WA (Writ Appeal), FA (First Appeal), RSA (Regular Second Appeal)
- ✅ **PDF Links**: Direct links to judgment PDFs on judiciary.karnataka.gov.in
- ✅ **Parties**: Petitioner and Respondent names
- ✅ **Judges**: Judge names handling each case
- ✅ **Auto-Sync**: Automatically syncs new cases daily

## Architecture

### Data Flow

```
judiciary.karnataka.gov.in
        ↓
   [Playwright Scraper]
        ↓
   [Data Normalizer]
        ↓
   Supabase PostgreSQL
        ↓
  [Your Dashboard]
```

### Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Backend** | FastAPI | REST API for data access |
| **Database** | Supabase (PostgreSQL) | Store cases, documents, sync logs |
| **Scraper** | Playwright | Navigate website JavaScript |
| **Scheduler** | APScheduler | Auto-sync on schedule |
| **Frontend** | React | Display dashboard |

## Setup Instructions

### 1️⃣ Create Supabase Project

1. Go to [supabase.com/dashboard](https://supabase.com/dashboard)
2. Click **New project**
3. Choose organization and enter project name
4. Create a strong password
5. Click **Create new project** (wait 1-2 min)

### 2️⃣ Get Supabase Credentials

1. Go to **Settings** → **API**
2. Copy **Project URL** from "Project API" section
3. Copy the **anon public** key
4. Copy the **service_role** key (for admin operations)

### 3️⃣ Create Database Schema

The schema creates tables for cases, documents, and sync tracking:

**Tables:**
- `cases`: Judgment records with case numbers, dates, parties, judges, links
- `documents`: PDF references for each judgment
- `sync_logs`: Track when data was last synchronized
- Views: `v_case_statistics`, `v_case_documents`

**To create schema:**

1. In Supabase Dashboard → **SQL Editor**
2. Click **New Query**
3. Copy entire contents of `SUPABASE_SCHEMA.sql`
4. Click **Run**

### 4️⃣ Configure Environment

Create `backend/.env`:

```env
# Supabase
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your-anon-public-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# Data Source
COURT_SOURCE=karnataka_hc
COURT_LEVEL=High Court

# Scheduler
ENABLE_SCHEDULER=true
SYNC_INTERVAL_HOURS=24

# Logging
DEBUG=false
LOG_LEVEL=INFO
```

### 5️⃣ Install Dependencies

```bash
cd backend

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

**Key packages added:**
- `supabase==2.1.5` - Supabase client
- `playwright==1.40.0` - Web scraping (already in requirements)

### 6️⃣ Start Backend & Sync

```bash
cd backend

# Start server
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# In another terminal, trigger initial sync
curl -X POST http://localhost:8000/api/karnataka-hc/sync
```

### 7️⃣ Access Dashboard

Open browser: **http://localhost:8000/dashboard**

Should now show:
- ✅ Total Karnataka HC cases
- ✅ Breakdown by case type (WP, CP, WA, etc.)
- ✅ Cases by year (2024, 2025, 2026)
- ✅ Recent judgments
- ✅ PDF links

## API Endpoints

### Statistics & Dashboard

```
GET /api/karnataka-hc/statistics
  → Returns case counts by type and year

GET /api/karnataka-hc/stats
  → Returns dashboard statistics (total_cases, by_type, etc.)

GET /api/karnataka-hc/dashboard
  → Returns complete dashboard data with recent cases
```

### Cases

```
GET /api/karnataka-hc/cases
  → List all cases (paginated)
  → Query params: case_type, year, limit, offset

GET /api/karnataka-hc/cases/{case_number}
  → Get specific case details with documents

GET /api/karnataka-hc/cases-by-type/{case_type}
  → Get all cases of a type (WP, CP, WA, etc.)
```

### Documents & PDFs

```
GET /api/karnataka-hc/documents
  → List all judgment PDFs

GET /api/karnataka-hc/documents/{case_number}
  → Get PDFs for specific case

GET /api/karnataka-hc/pdf/{case_number}
  → Get PDF download link
```

### Search

```
GET /api/karnataka-hc/search?q=term
  → Search cases by:
    - Case number (WP 1983, CP 312, etc.)
    - Petitioner name
    - Respondent name
    - Judge name
```

### Sync Management

```
POST /api/karnataka-hc/sync
  → Manually trigger data sync from judiciary.karnataka.gov.in
  → Scrapes website and updates Supabase

GET /api/karnataka-hc/health
  → Check if Supabase connection is working
```

## Example Requests

### Get all Civil Petitions from 2025

```bash
curl "http://localhost:8000/api/karnataka-hc/cases?case_type=CP&year=2025"
```

### Get specific case details

```bash
curl "http://localhost:8000/api/karnataka-hc/cases/WP%201983%20OF%202025"
```

### Search for a petitioner

```bash
curl "http://localhost:8000/api/karnataka-hc/search?q=SHUPTHA"
```

### Get PDF for case

```bash
curl "http://localhost:8000/api/karnataka-hc/pdf/WP%201983%20OF%202025"
```

### Manual sync

```bash
curl -X POST http://localhost:8000/api/karnataka-hc/sync
```

## Case Types Scraped

| Code | Meaning | Examples |
|------|---------|----------|
| **WP** | Writ Petition | Habeas corpus, mandamus, prohibition, certiorari |
| **CP** | Civil Petition | Regular civil disputes |
| **WA** | Writ Appeal | Appeals against writ decisions |
| **FA** | First Appeal | Appeals from lower courts |
| **RSA** | Regular Second Appeal | Second appeals from courts |
| **CAS** | Civil Appeal | Civil appeals |

## Data Included

Each judgment record includes:

```json
{
  "case_number": "WP 1983 OF 2025",
  "case_type": "WP",
  "judgment_date": "2026-01-06",
  "court_level": "High Court",
  "petitioner": "SHUPTHA APPANNA",
  "respondent": "SRI MILTON MUTHANNA",
  "judges": "P SREE SUDHA",
  "status": "Decided",
  "pdf_url": "https://judiciary.karnataka.gov.in/documents/wp_1983_2025.pdf",
  "source": "judiciary.karnataka.gov.in"
}
```

## Auto-Sync Schedule

By default, data syncs automatically:
- **Frequency**: Every 24 hours
- **Time**: Server startup + every 24 hours after
- **Source**: judiciary.karnataka.gov.in
- **Updates**: Clears old data and pulls fresh cases

To change sync frequency, edit `backend/.env`:
```env
SYNC_INTERVAL_HOURS=6  # Sync every 6 hours
```

## Troubleshooting

### Supabase Connection Failed

**Error**: `Supabase not available - check .env file`

**Solution**:
1. Verify `.env` has `SUPABASE_URL` and `SUPABASE_ANON_KEY`
2. Check credentials are correct from Supabase dashboard
3. Ensure project is selected

### No Cases Showing

**Problem**: Dashboard shows 0 cases

**Solution**:
1. Check database schema was created (run SUPABASE_SCHEMA.sql)
2. Manually trigger sync: `curl -X POST http://localhost:8000/api/karnataka-hc/sync`
3. Check server logs for errors

### Sync Takes Too Long

**Note**: First sync may take 5-10 minutes depending on data volume

**Optimize**:
- Edit `karnataka_hc_jobs.py` to reduce years/types scraped
- Start with sample data instead of live scraping

### PDF Links Not Working

**Reason**: Links go to judiciary.karnataka.gov.in which may block automated requests

**Workaround**:
- PDF links work for direct browser access
- Users can click links to download judgment PDFs directly

## Advanced Configuration

### Using Sample Data Only

To skip web scraping and use sample data (faster for testing):

In `karnataka_hc_jobs.py`, modify `sync_karnataka_hc_judgments_with_playwright()`:

```python
# Use only sample data (no scraping)
raw_judgments = SAMPLE_KARNATAKA_HC_JUDGMENTS
```

### Custom Scraping Logic

To modify what gets scraped, edit `karnataka_hc_scraper.py`:

1. Change `JUDGMENT_TYPES` list
2. Modify `_scrape_page()` logic
3. Update `extract_judgment_data()` to parse different fields

### Database Backups

Supabase automatically backs up your data. To export:

1. Supabase Dashboard → **Database** → **Tables**
2. Select `cases` table
3. Click **...** → **Export as CSV/JSON**

## Frontend Integration

The dashboard should automatically display:

1. **Overview Tab**: Total cases, breakdown by type, sync status
2. **High Court Tab**: All Karnataka HC cases with filters
3. **Case Details**: Click case to see full info + PDFs
4. **Documents Tab**: Browse all judgment PDFs

To update frontend, modify React components to use endpoints from this API.

## Important Notes

⚠️ **Web Scraping Considerations**:
- Scraper uses Chrome/Chromium via Playwright
- May take 5-10 minutes for first sync
- Website may occasionally block requests - consider staggering syncs
- Always respect the website's robots.txt and Terms of Service

✅ **Best Practices**:
- Sync during off-peak hours if possible
- Keep backup of downloaded data
- Monitor sync status in logs
- Update Supabase regularly for security

## Support & Debugging

### Check Server Status

```bash
curl http://localhost:8000/api/karnataka-hc/health
```

### View Sync Logs

In Supabase Dashboard → **Table Editor** → `sync_logs`

### Debug Scraper

```bash
python3 backend/scrapers/karnataka_hc_scraper.py
```

### Check Database

```bash
# Query all cases
psql postgresql://postgres:password@host/db -c "SELECT COUNT(*) FROM cases;"

# Query by case type
psql "..." -c "SELECT case_type, COUNT(*) FROM cases GROUP BY case_type;"
```

## Next Steps

1. ✅ Set up Supabase project
2. ✅ Create database schema
3. ✅ Configure environment
4. ✅ Start backend
5. ✅ Trigger initial sync
6. ✅ Access dashboard
7. 📱 (Optional) Add mobile app support
8. 📊 (Optional) Add analytics/trending

---

**Questions?** Check the [Supabase docs](https://supabase.com/docs) or [Playwright docs](https://playwright.dev)
