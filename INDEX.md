# 📑 Project Map & Quick Navigation

A complete guide to finding everything in the Court Ecosystem project.

---

## 🎯 Quick Links

| Need Help With? | Go To | File/Link |
|---|---|---|
| 🚀 **Getting Started** | Quick Start Guide | [QUICKSTART.md](QUICKSTART.md) |
| 🏗️ **Architecture** | System Overview | [ARCHITECTURE.md](ARCHITECTURE.md) |
| 📚 **Full Docs** | Complete Guide | [README.md](README.md) |
| 👨‍💻 **Development** | Dev Guide | [DEVELOPMENT.md](DEVELOPMENT.md) |
| 🐳 **Docker Setup** | Compose File | [docker-compose.yml](docker-compose.yml) |
| 🔧 **Configuration** | Environment | [backend/.env.example](backend/.env.example) |

---

## 📂 File Directory Map

```
court-ecosystem/
│
├─ 📖 QUICKSTART.md                 ← START HERE (5 min read)
├─ 📖 README.md                     ← Complete documentation
├─ 📖 ARCHITECTURE.md               ← System architecture
├─ 📖 DEVELOPMENT.md                ← Developer guide
├─ 📖 INDEX.md                      ← This file
│
├─ 🚀 setup.sh                      ← Docker setup (1 command)
├─ 🚀 setup-manual.sh               ← Manual Python setup
│
├─ 🐳 docker-compose.yml            ← Container orchestration
├─ 🐳 Dockerfile                    ← Container image build
│
├─ 📁 backend/                      ← Python backend
│   ├── requirements.txt            ← All dependencies
│   ├── .env.example                ← Configuration template
│   │
│   └── app/                        ← Main application
│       ├── main.py                 ← FastAPI app entry
│       ├── database.py             ← PostgreSQL config
│       ├── models.py               ← Database models
│       ├── schemas.py              ← Data schemas
│       │
│       ├── routes/
│       │   ├── dashboard.py        ← Stats endpoints
│       │   └── cases.py            ← Case endpoints
│       │
│       ├── scrapers/
│       │   ├── base_scraper.py     ← Base class
│       │   └── indian_kanoon.py    ← Main scraper
│       │
│       ├── metadata/
│       │   └── extractor.py        ← Metadata extraction
│       │
│       └── scheduler/
│           └── jobs.py             ← Scheduled tasks
│
├─ 📁 dashboard/
│   ├── index.html                  ← Dashboard UI
│   └── public/                     ← Static assets
│
└─ 📁 documents/                    ← Downloaded documents
```

---

## 🔍 Finding Things

### By Task

#### I want to...

**Start the system**
- → [QUICKSTART.md - Quick Start](QUICKSTART.md#quick-start-2-options)
- → Run: `./setup.sh`

**Understand the architecture**
- → [ARCHITECTURE.md](ARCHITECTURE.md)
- → Section: "System Components"

**View the API documentation**
- → Run: `docker-compose up -d`
- → Open: http://localhost:8000/docs

**See the dashboard**
- → Run: `docker-compose up -d`
- → Open: http://localhost:3000

**Add a new court**
- → [DEVELOPMENT.md - Adding a New Court Scraper](DEVELOPMENT.md#adding-a-new-court-scraper)
- → Edit: `backend/app/scrapers/`

**Add new API endpoint**
- → [DEVELOPMENT.md - Adding New API Endpoints](DEVELOPMENT.md#adding-new-api-endpoints)
- → Edit: `backend/app/routes/`

**Improve metadata extraction**
- → [DEVELOPMENT.md - Enhancing Metadata Extraction](DEVELOPMENT.md#enhancing-metadata-extraction)
- → Edit: `backend/app/metadata/extractor.py`

**Debug an issue**
- → [README.md - Troubleshooting](README.md#troubleshooting)
- → Run: `docker-compose logs -f api`

**Configure settings**
- → Copy: `backend/.env.example` → `backend/.env`
- → Edit: `backend/.env`
- → See: [README.md - Configuration](README.md#configuration)

**Deploy to production**
- → [DEVELOPMENT.md - Deployment Checklist](DEVELOPMENT.md#deployment-checklist)

**Write tests**
- → [DEVELOPMENT.md - Testing](DEVELOPMENT.md#testing)

---

### By Component

#### Backend Application

**Main Application File**
- Location: `backend/app/main.py`
- Purpose: FastAPI application setup
- Key: Entry point for API server

**Database Configuration**
- Location: `backend/app/database.py`
- Purpose: PostgreSQL connection setup
- Key: Manages database sessions

**Data Models**
- Location: `backend/app/models.py`
- Purpose: SQLAlchemy ORM models
- Tables: courts, cases, judgments, documents, metadata, scrape_logs

**API Schemas**
- Location: `backend/app/schemas.py`
- Purpose: Pydantic validation schemas
- Usage: Request/response validation

#### API Endpoints

**Dashboard Routes**
- Location: `backend/app/routes/dashboard.py`
- Endpoints:
  - `GET /api/dashboard/stats` - Statistics
  - `GET /api/dashboard/courts-breakdown` - Court breakdown
  - `GET /api/dashboard/timeline` - Timeline data

**Case Routes**
- Location: `backend/app/routes/cases.py`
- Endpoints:
  - `GET /api/cases` - List cases
  - `GET /api/cases/{id}` - Get case
  - `GET /api/judgments` - List judgments
  - `GET /api/cases/{id}/documents` - Get documents

#### Data Processing

**Web Scrapers**
- Location: `backend/app/scrapers/`
- Base: `base_scraper.py` - Abstract base class
- Main: `indian_kanoon.py` - Indian Kanoon implementation
- Purpose: Fetch court documents

**Metadata Extraction**
- Location: `backend/app/metadata/extractor.py`
- Purpose: Extract structured info from text
- Extracts: Case numbers, judges, parties, verdicts

**Scheduler**
- Location: `backend/app/scheduler/jobs.py`
- Purpose: Daily scraping automation
- Trigger: 2:00 AM daily

#### Frontend

**Dashboard**
- Location: `dashboard/index.html`
- Type: Single-page HTML application
- Charts: Chart.js library
- Features: Stats, charts, breakdown table

---

## 📊 Data Flow

```
Court Websites ↓
         ↓
   [Scrapers] ↓
         ↓
[Metadata Extraction] ↓
         ↓
[PostgreSQL Database] ↓
         ↓
[FastAPI Routes] ↓
         ↓
[Dashboard] + [API Clients]
```

**Details in**: [ARCHITECTURE.md - Data Flow](ARCHITECTURE.md#data-flow)

---

## 🔧 Configuration Files

**Environment Variables**
- File: `backend/.env.example` → copy to `backend/.env`
- Variables: DATABASE_URL, DEBUG, SECRET_KEY
- Purpose: Application configuration

**Docker Compose**
- File: `docker-compose.yml`
- Services: PostgreSQL, FastAPI, Nginx
- Usage: `docker-compose up -d`

**Dockerfile**
- File: `Dockerfile`
- Base: Python 3.11
- Purpose: Build API server image

**Requirements**
- File: `backend/requirements.txt`
- Contains: All Python dependencies
- Update: `pip install -r requirements.txt`

---

## 🗄️ Database Schema

```
courts
├─ id (PK)
├─ name
├─ level (ENUM)
├─ state
└─ district

cases
├─ id (PK)
├─ case_number (unique)
├─ case_type
├─ court_id (FK)
├─ petitioner
├─ respondent
├─ case_date
└─ created_at

judgments
├─ id (PK)
├─ case_id (FK)
├─ judge_name
├─ judgment_date
├─ judgment_text
├─ verdict
└─ created_at

documents
├─ id (PK)
├─ case_id (FK)
├─ judgment_id (FK)
├─ file_name
├─ file_path
├─ file_type
├─ source_url
└─ created_at

document_metadata
├─ id (PK)
├─ document_id (FK)
├─ key
├─ value
└─ extracted_at

scrape_logs
├─ id (PK)
├─ court_id (FK)
├─ scrape_date
├─ status
├─ cases_found
├─ cases_saved
├─ error_message
├─ execution_time
└─ created_at
```

**Details in**: [README.md - Database Schema](README.md#database-schema)

---

## 🚀 Getting Started Steps

### Step 1: Quick Setup
```bash
cd /Users/tanush.s.vashisht/Desktop/Tanush/work/court-ecosystem
chmod +x setup.sh
./setup.sh
```
**Time**: ~2 minutes  
**Result**: All services running

### Step 2: Access Services
- Dashboard: http://localhost:3000
- API Docs: http://localhost:8000/docs
- API Health: http://localhost:8000/health

**Time**: ~30 seconds  
**Result**: Services accessible

### Step 3: Check Data
```bash
curl http://localhost:8000/api/dashboard/stats
```
**Time**: ~30 seconds  
**Result**: Can see API responses

### Step 4: View Logs
```bash
docker-compose logs -f api
```
**Time**: Continuous  
**Result**: Monitor system activity

---

## 📈 API Endpoints Reference

### Dashboard Statistics
```
GET /api/dashboard/stats
├─ total_cases
├─ total_judgments
├─ supreme_court_count
├─ high_court_count
├─ lower_court_count
├─ today_cases
└─ last_scrape_time
```

### Courts Breakdown
```
GET /api/dashboard/courts-breakdown
├─ court_name
├─ court_level
└─ case_count
```

### Cases Timeline
```
GET /api/dashboard/timeline?days=30
├─ date
└─ count
```

### List Cases
```
GET /api/cases?skip=0&limit=20&court_id=1&case_type=Writ%20Petition
├─ case_number
├─ case_type
├─ court_id
├─ petitioner
├─ respondent
└─ case_date
```

### Single Case
```
GET /api/cases/{case_id}
└─ Case details
```

### Case Documents
```
GET /api/cases/{case_id}/documents
└─ List of documents for case
```

### List Judgments
```
GET /api/judgments?case_id=5
├─ judge_name
├─ judgment_date
├─ judgment_text
└─ verdict
```

---

## 🛠️ Common Commands

### Docker Operations
```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f api

# Rebuild
docker-compose up -d --build

# Check status
docker-compose ps
```

### Database Access
```bash
# Connect to database
docker-compose exec db psql -U court_user -d court_ecosystem

# View courts
SELECT * FROM courts;

# View cases
SELECT * FROM cases LIMIT 10;

# View recent scrapes
SELECT * FROM scrape_logs ORDER BY created_at DESC;
```

### API Testing
```bash
# Health check
curl http://localhost:8000/health

# Get stats
curl http://localhost:8000/api/dashboard/stats

# List cases
curl http://localhost:8000/api/cases?limit=5

# View API docs
open http://localhost:8000/docs
```

---

## 📚 Documentation Map

| Document | Purpose | Length | Audience |
|----------|---------|--------|----------|
| [QUICKSTART.md](QUICKSTART.md) | Get started fast | 5 min | Everyone |
| [README.md](README.md) | Full documentation | 20 min | Operators |
| [ARCHITECTURE.md](ARCHITECTURE.md) | System design | 15 min | Architects |
| [DEVELOPMENT.md](DEVELOPMENT.md) | Development guide | 30 min | Developers |
| [INDEX.md](INDEX.md) | This file | 10 min | Navigators |

---

## 🎓 Learning Path

### For Non-Technical Users
1. Read: [QUICKSTART.md](QUICKSTART.md)
2. Run: `./setup.sh`
3. Open: http://localhost:3000
4. Explore: Dashboard UI

### For System Operators
1. Read: [README.md](README.md)
2. Read: [ARCHITECTURE.md](ARCHITECTURE.md)
3. Learn: Common commands section
4. Setup: Production deployment

### For Developers
1. Read: [DEVELOPMENT.md](DEVELOPMENT.md)
2. Setup: Dev environment
3. Learn: Code structure
4. Try: Adding new scraper
5. Implement: New features

### For DevOps
1. Read: [docker-compose.yml](docker-compose.yml)
2. Read: [Dockerfile](Dockerfile)
3. Check: [README.md - Deployment](README.md#deployment-architecture)
4. Setup: Production cluster

---

## 🆘 Troubleshooting Quick Links

| Problem | Solution | Link |
|---------|----------|------|
| Services won't start | Check Docker | [README.md - Docker Issues](README.md#troubleshooting) |
| API not responding | Check health endpoint | `curl http://localhost:8000/health` |
| Database connection error | Check DATABASE_URL | [README.md - Database Connection Error](README.md#troubleshooting) |
| Scraper not finding cases | Check logs | `docker-compose logs api` |
| Dashboard not loading | Check API | [README.md - Dashboard Not Loading Data](README.md#troubleshooting) |
| Port already in use | Kill process | `lsof -i :8000` |

---

## 📋 Checklist: First Time Setup

- [ ] Navigate to project: `cd /Users/tanush.s.vashisht/Desktop/Tanush/work/court-ecosystem`
- [ ] Read [QUICKSTART.md](QUICKSTART.md) (5 min)
- [ ] Run `chmod +x setup.sh` (1 sec)
- [ ] Run `./setup.sh` (2 min)
- [ ] Wait for services to start (1 min)
- [ ] Open http://localhost:3000 in browser
- [ ] Open http://localhost:8000/docs for API
- [ ] Test API: `curl http://localhost:8000/api/dashboard/stats`
- [ ] View logs: `docker-compose logs -f api`
- [ ] Read full [README.md](README.md) for details

**Total Time**: ~15 minutes

---

## 🚀 Next Steps After Setup

1. **Review Data**: Check dashboard at http://localhost:3000
2. **Test API**: Explore endpoints at http://localhost:8000/docs
3. **Check Logs**: Monitor activity `docker-compose logs -f`
4. **Read Docs**: Study [ARCHITECTURE.md](ARCHITECTURE.md)
5. **Extend System**: Follow [DEVELOPMENT.md](DEVELOPMENT.md)

---

## 📞 Support Resources

- **Quick Questions**: Check [QUICKSTART.md](QUICKSTART.md)
- **How-to Guides**: Check [DEVELOPMENT.md](DEVELOPMENT.md)
- **System Details**: Check [ARCHITECTURE.md](ARCHITECTURE.md)
- **Troubleshooting**: Check [README.md](README.md#troubleshooting)
- **API Help**: Open http://localhost:8000/docs
- **Logs**: `docker-compose logs -f`

---

## 🎯 Key Files at a Glance

```
Started yet?              → ./setup.sh
Need basic info?          → QUICKSTART.md
Want system overview?     → ARCHITECTURE.md
Full documentation?       → README.md
Need dev help?            → DEVELOPMENT.md
Getting lost?             → This file (INDEX.md)
```

---

**Version**: 1.0.0  
**Last Updated**: February 24, 2026  
**Status**: Production Ready ✅

---

## 🎉 Welcome to Court Ecosystem!

You now have a complete, production-ready backend system for managing court documents. Everything is documented, containerized, and ready to use.

**Next Action**: Run `./setup.sh` and visit http://localhost:3000 🚀

