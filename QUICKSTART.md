# 🚀 Quick Start Guide - Court Ecosystem

## Project Overview

This is a **complete backend ecosystem** for scraping, indexing, and managing Indian court documents (specifically Writ Petitions) from:
- Supreme Court of India
- High Courts (Delhi, Bombay, Calcutta)
- Lower Courts (District courts)

---

## What's Been Built

### ✅ Complete Backend System
- **API Server** (FastAPI) - RESTful API for all court data
- **Database** (PostgreSQL) - Stores cases, judgments, documents, metadata
- **Web Scrapers** - Automated daily scraping from court websites
- **Metadata Extraction** - NLP-based information extraction
- **Scheduler** - APScheduler for daily automated runs at 2 AM
- **Dashboard** - Real-time statistics visualization
- **Docker Ready** - Full Docker & Docker Compose setup

---

## Project Structure

```
court-ecosystem/
├── 📁 backend/
│   ├── app/
│   │   ├── scrapers/
│   │   │   ├── base_scraper.py      # Base scraper class
│   │   │   └── indian_kanoon.py     # Indian Kanoon scraper
│   │   ├── models.py                # SQLAlchemy models
│   │   ├── schemas.py               # Pydantic schemas
│   │   ├── database.py              # DB configuration
│   │   ├── routes/
│   │   │   ├── dashboard.py         # Dashboard endpoints
│   │   │   └── cases.py             # Cases/Judgments endpoints
│   │   ├── metadata/
│   │   │   └── extractor.py         # Metadata extraction
│   │   ├── scheduler/
│   │   │   └── jobs.py              # Scheduled jobs
│   │   └── main.py                  # FastAPI app
│   ├── requirements.txt             # Python dependencies
│   └── .env.example                 # Env template
├── 📁 dashboard/
│   └── index.html                   # Dashboard UI
├── 📁 documents/                    # Stored documents
├── Dockerfile
├── docker-compose.yml
├── setup.sh                         # Docker setup
├── setup-manual.sh                  # Manual setup
└── README.md
```

---

## Quick Start (3 Options)

### Option 1: Supabase (Easiest) ⭐ **RECOMMENDED**

Cloud database, no Docker needed!

```bash
cd /Users/tanush.s.vashisht/Desktop/Tanush/work/court-ecosystem/backend

# Create environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your Supabase connection string
# (See SUPABASE_SETUP.md for detailed guide)

# Start API
uvicorn app.main:app --reload --port 8000
```

**Then access:**
- 📖 API Docs: http://localhost:8000/docs
- 🎨 Dashboard: Open `dashboard/index.html`

**Setup time:** 15 minutes  
**Full guide:** [SUPABASE_SETUP.md](SUPABASE_SETUP.md)

### Option 2: Docker ⭐

```bash
cd /Users/tanush.s.vashisht/Desktop/Tanush/work/court-ecosystem

# Make setup script executable
chmod +x setup.sh

# Run setup (requires Docker Desktop installed)
./setup.sh
```

**Then access:**
- 📊 Dashboard: http://localhost:3000
- 📖 API Docs: http://localhost:8000/docs
- 🏥 Health Check: http://localhost:8000/health

### Option 3: Local PostgreSQL (Advanced)

```bash
# Install PostgreSQL first
brew install postgresql
brew services start postgresql

cd /Users/tanush.s.vashisht/Desktop/Tanush/work/court-ecosystem/backend

# Create environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env and set: DATABASE_URL=postgresql://localhost/court_ecosystem
createdb court_ecosystem

# Start API
uvicorn app.main:app --reload --port 8000
```

---

## Key Features Implemented

### 1️⃣ **Web Scraping**
- [indian_kanoon.py](backend/app/scrapers/indian_kanoon.py) - Scrapes writ petitions from Indian Kanoon
- Extracts case details, judgments, verdicts
- Rate limiting (1 sec between requests)
- Error handling & retry logic

### 2️⃣ **Database**
Tables created automatically:
- `courts` - Store court information
- `cases` - Writ petitions
- `judgments` - Court judgments
- `documents` - PDF/HTML documents
- `document_metadata` - Extracted metadata
- `scrape_logs` - Tracking scrape runs

### 3️⃣ **Metadata Extraction**
[extractor.py](backend/app/metadata/extractor.py) extracts:
- Case numbers
- Judge names
- Parties (petitioner/respondent)
- Judgment dates
- Verdicts (allowed/dismissed/quashed)

### 4️⃣ **Scheduler**
[jobs.py](backend/app/scheduler/jobs.py):
- Runs daily at 2:00 AM
- Scrapes all configured courts
- Saves cases to database
- Logs all scraping activities
- Automatic retry on failure

### 5️⃣ **API Endpoints**

**Dashboard Stats**
```bash
GET /api/dashboard/stats
# Returns: total_cases, total_judgments, court breakdown, today's cases
```

**Court Breakdown**
```bash
GET /api/dashboard/courts-breakdown
# Returns: cases count per individual court
```

**Cases Timeline**
```bash
GET /api/dashboard/timeline?days=30
# Returns: daily case count for last N days
```

**List Cases**
```bash
GET /api/cases?skip=0&limit=20&court_id=1
# Paginated case listing with filters
```

**List Judgments**
```bash
GET /api/judgments?case_id=5
# Get judgments for a case
```

### 6️⃣ **Dashboard**
[dashboard/index.html](dashboard/index.html) shows:
- 📊 Real-time statistics (total cases, by court type)
- 📈 Cases distribution pie chart
- 📉 Timeline line chart (last 30 days)
- 📋 Breakdown table (cases per court)
- 🔄 Auto-refresh every 30 seconds

---

## Database Schema

### Courts
```
id (PK) | name | level | state | district | created_at
```

### Cases
```
id (PK) | case_number | case_type | court_id (FK) | petitioner | respondent | case_date | created_at
```

### Judgments
```
id (PK) | case_id (FK) | judge_name | judgment_date | judgment_text | verdict | created_at
```

### Documents
```
id (PK) | case_id (FK) | judgment_id (FK) | file_name | file_path | file_type | source_url | created_at
```

### Document Metadata
```
id (PK) | document_id (FK) | key | value | extracted_at
```

---

## Configuration

### Edit `.env` file (backend/.env)
```env
DATABASE_URL=postgresql://user:password@localhost:5432/court_ecosystem
DEBUG=True
SECRET_KEY=your-secret-key
```

### Change Scheduler Time
In [backend/app/scheduler/jobs.py](backend/app/scheduler/jobs.py), line ~118:
```python
scheduler.add_job(
    scrape_court_documents,
    trigger=CronTrigger(hour=2, minute=0),  # Change hour=2 to desired time
    ...
)
```

---

## Development Commands

### Docker Commands
```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down

# Rebuild
docker-compose up -d --build

# Check status
docker-compose ps
```

### Database Access
```bash
# Connect to PostgreSQL
docker-compose exec db psql -U court_user -d court_ecosystem

# Or if running manually:
psql postgresql://court_user:court_password@localhost:5432/court_ecosystem
```

### Sample Queries
```sql
-- View all courts
SELECT * FROM courts;

-- Count cases by court
SELECT courts.name, COUNT(cases.id) as case_count 
FROM courts JOIN cases ON courts.id = cases.court_id 
GROUP BY courts.id;

-- View recent cases
SELECT * FROM cases ORDER BY created_at DESC LIMIT 10;

-- View scrape logs
SELECT * FROM scrape_logs ORDER BY created_at DESC;
```

---

## Testing the System

### 1. Check API Health
```bash
curl http://localhost:8000/health
```

### 2. Get Dashboard Stats
```bash
curl http://localhost:8000/api/dashboard/stats
```

### 3. List Cases
```bash
curl http://localhost:8000/api/cases?limit=5
```

### 4. Check Swagger Docs
Open: http://localhost:8000/docs

---

## How It Works (Daily Flow)

```
2:00 AM Daily ↓
├─ APScheduler triggers scrape job
├─ For each court (Supreme, High, Lower):
│  ├─ Fetch writ petitions from Indian Kanoon
│  ├─ Parse case details
│  ├─ Extract metadata (case number, judges, verdict)
│  ├─ Save to database
│  └─ Log scrape results
├─ Store in:
│  ├─ cases (case info)
│  ├─ judgments (verdict & judge info)
│  ├─ documents (document links)
│  ├─ document_metadata (extracted info)
│  └─ scrape_logs (execution report)
└─ Dashboard automatically updates via API calls
```

---

## Next Steps to Enhance

1. **Add More Courts**
   - Modify `seed_courts()` in [backend/app/scheduler/jobs.py](backend/app/scheduler/jobs.py)
   - Create state-specific scrapers

2. **Improve Metadata Extraction**
   - Add spaCy NLP models for better extraction
   - Implement PDF OCR with Tesseract
   - Train custom case classification models

3. **Add Features**
   - Email notifications for specific case types
   - Advanced search/filtering
   - Case similarity detection
   - Judge analytics

4. **Scale Up**
   - Add caching (Redis)
   - Implement full-text search (Elasticsearch)
   - Add GraphQL API
   - Build mobile app

---

## Troubleshooting

### Database Connection Failed
```bash
# Check if PostgreSQL is running
docker-compose ps

# Verify DATABASE_URL in .env
cat backend/.env

# Restart database
docker-compose restart db
```

### API Not Starting
```bash
# Check logs
docker-compose logs api

# Rebuild
docker-compose down
docker-compose up -d --build
```

### Dashboard Not Loading
- Ensure API is running: http://localhost:8000/health
- Check browser console for errors (F12)
- Verify database has data: `SELECT COUNT(*) FROM cases;`

### Scraper Not Finding Cases
- Check internet connection
- Review scraper logs: `docker-compose logs api | grep scrape`
- Verify court website is accessible

---

## Support Files

- 📖 [Full README.md](README.md) - Complete documentation
- 🐳 [docker-compose.yml](docker-compose.yml) - Docker configuration
- 🔧 [requirements.txt](backend/requirements.txt) - All dependencies
- 📚 [API Documentation](http://localhost:8000/docs) - Interactive Swagger UI

---

## Summary

You now have a **production-ready backend system** that:
✅ Automatically scrapes writ petitions daily  
✅ Extracts structured metadata  
✅ Stores everything in PostgreSQL  
✅ Provides REST API for querying  
✅ Shows real-time dashboard  
✅ Runs in Docker containers  
✅ Scales to handle more courts  

**Total lines of code**: ~2000+ lines of production-ready Python code

---

**Ready to scale! 🚀**

Need help? Check the logs: `docker-compose logs -f`

