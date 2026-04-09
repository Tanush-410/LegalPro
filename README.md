# Court Ecosystem Backend

This is a comprehensive README that should be created:

## README

# Court Ecosystem - Backend Ecosystem for Court Documents

A modern backend system for automatically scraping, indexing, and analyzing court documents/judgments focusing on writ petitions from Indian courts (Supreme Court, High Courts, Lower Courts).

## Features

✅ **Automated Daily Scraping** - Automatically scrapes writ petitions from multiple court websites  
✅ **Multi-Court Support** - Handles Supreme Court, High Courts, and Lower Courts  
✅ **Metadata Extraction** - NLP-based extraction of case information, judges, parties, verdicts  
✅ **RESTful API** - Complete API for querying cases and judgments  
✅ **Dashboard** - Real-time visualization of case statistics and trends  
✅ **Database** - PostgreSQL for reliable data storage  
✅ **Docker Ready** - Easy deployment with Docker & Docker Compose  

## Project Structure

```
court-ecosystem/
├── backend/
│   ├── app/
│   │   ├── scrapers/          # Web scrapers for courts
│   │   ├── models.py          # SQLAlchemy database models
│   │   ├── schemas.py         # Pydantic schemas
│   │   ├── database.py        # Database configuration
│   │   ├── routes/            # API routes
│   │   ├── metadata/          # Metadata extraction logic
│   │   ├── scheduler/         # APScheduler jobs
│   │   └── main.py            # FastAPI application
│   ├── requirements.txt       # Python dependencies
│   └── .env.example           # Environment variables template
├── dashboard/
│   └── index.html             # Dashboard UI
├── documents/                 # Stored documents (optional)
├── Dockerfile                 # Docker image definition
├── docker-compose.yml         # Docker Compose configuration
└── README.md
```

## Tech Stack

- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL
- **Scraping**: BeautifulSoup, Selenium, Requests
- **Scheduling**: APScheduler
- **NLP/Extraction**: Regex, Spacy-ready
- **API Server**: Uvicorn
- **Frontend**: HTML5, Chart.js
- **Containerization**: Docker, Docker Compose

## Installation

### Prerequisites
- Docker & Docker Compose (recommended)
- OR Python 3.11+, PostgreSQL 15+

### Option 1: Using Docker Compose (Recommended)

```bash
# Navigate to project root
cd court-ecosystem

# Start all services
docker-compose up -d

# Check logs
docker-compose logs -f api

# Check status
docker-compose ps
```

Services will be available at:
- **API Documentation**: http://localhost:8000/docs
- **API Health**: http://localhost:8000/health
- **Dashboard**: http://localhost:3000

### Option 2: Manual Setup

```bash
# Create Python environment
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your database URL

# Run migrations (first time)
python -c "from app.database import engine; from app.models import Base; Base.metadata.create_all(bind=engine)"

# Start API server
uvicorn app.main:app --reload --port 8000

# In another terminal, open dashboard
cd ../dashboard
# Serve with any web server or open index.html in browser
```

## Configuration

### Environment Variables (.env)

```env
DATABASE_URL=postgresql://user:password@localhost:5432/court_ecosystem
DEBUG=True
SECRET_KEY=your-secret-key-here
```

### Scheduler Configuration

Edit `backend/app/scheduler/jobs.py` to change scrape timing:
- Default: 2:00 AM daily
- Modify `CronTrigger(hour=2, minute=0)`

## API Endpoints

### Dashboard
- `GET /api/dashboard/stats` - Get dashboard statistics
- `GET /api/dashboard/courts-breakdown` - Cases per court
- `GET /api/dashboard/timeline` - Cases timeline (last N days)

### Cases
- `GET /api/cases` - List all cases (with pagination)
- `GET /api/cases/{case_id}` - Get single case
- `GET /api/cases/{case_id}/documents` - Get case documents

### Judgments
- `GET /api/judgments` - List judgments
- `GET /api/judgments?case_id={id}` - Judgments for a case

### Health
- `GET /health` - Health check
- `GET /` - API info

## API Examples

### Get Dashboard Stats
```bash
curl http://localhost:8000/api/dashboard/stats
```

Response:
```json
{
  "total_cases": 150,
  "total_judgments": 145,
  "supreme_court_count": 45,
  "high_court_count": 65,
  "lower_court_count": 40,
  "today_cases": 5,
  "last_scrape_time": "2024-02-24T02:00:00"
}
```

### Get Cases (with pagination)
```bash
curl "http://localhost:8000/api/cases?skip=0&limit=20&court_id=1"
```

### Get Courts Breakdown
```bash
curl http://localhost:8000/api/dashboard/courts-breakdown
```

Response:
```json
[
  {
    "court_name": "Supreme Court of India",
    "court_level": "Supreme Court",
    "case_count": 45
  },
  {
    "court_name": "Delhi High Court",
    "court_level": "High Court",
    "case_count": 30
  }
]
```

## Database Schema

### Courts Table
```sql
- id: Integer (Primary Key)
- name: String (unique)
- level: Enum (Supreme, High, Lower)
- state: String (nullable)
- district: String (nullable)
```

### Cases Table
```sql
- id: Integer (Primary Key)
- case_number: String (unique)
- case_type: String (e.g., "Writ Petition")
- court_id: Integer (FK)
- petitioner: String
- respondent: String
- case_date: DateTime
```

### Judgments Table
```sql
- id: Integer (Primary Key)
- case_id: Integer (FK)
- judge_name: String
- judgment_date: DateTime
- judgment_text: Text
- verdict: Text
```

### Documents Table
```sql
- id: Integer (Primary Key)
- case_id: Integer (FK)
- judgment_id: Integer (FK)
- file_name: String
- file_path: String
- file_type: String (pdf, html, txt)
- source_url: String
```

### Document Metadata Table
```sql
- id: Integer (Primary Key)
- document_id: Integer (FK)
- key: String (metadata key)
- value: Text (metadata value)
```

## Scraping Details

### Currently Supported Courts
1. **Supreme Court of India**
2. **Delhi High Court**
3. **Bombay High Court**
4. **Calcutta High Court**
5. **Delhi District Court** (Lower Court)

### Scraping Source
- Primary: **Indian Kanoon** (indiankanoon.org)
- Fetches: `Booltype = "Writ Petition"`
- Frequency: Daily at 2:00 AM

### What Gets Extracted
- Case number and type
- Judge names
- Parties (petitioner, respondent)
- Judgment date
- Verdict/Order
- Full judgment text
- Document URL

## Metadata Extraction

Uses NLP regex patterns to extract:
- **Case Numbers**: `Case No.: WP/12345/2024`
- **Judges**: `Justice John Doe, Justice Jane Smith`
- **Parties**: Petitioner vs Respondent names
- **Dates**: Judgment date parsing
- **Verdict**: Order passed (allowed/dismissed/quashed)

Located in `backend/app/metadata/extractor.py`

## Dashboard Features

- **Real-time Stats**: Total cases, judgments, breakdown by court type
- **Court Distribution**: Doughnut chart showing cases by court level
- **Timeline**: Line chart of cases filed over last 30 days
- **Court Breakdown**: Detailed table of cases per individual court
- **Auto-refresh**: Updates every 30 seconds

## Monitoring & Logs

### View API Logs
```bash
docker-compose logs -f api
```

### View Database Connection
```bash
docker-compose exec db psql -U court_user -d court_ecosystem
```

### Query Scrape Results
```bash
psql -U court_user -d court_ecosystem
SELECT * FROM scrape_logs ORDER BY created_at DESC LIMIT 10;
```

## Development

### Adding a New Court Scraper

1. Create new scraper in `backend/app/scrapers/` (e.g., `high_court_mumbai.py`)
2. Extend `BaseScraper` class
3. Implement `get_writ_petitions()` and `parse_case_details()`
4. Update factory function in `indian_kanoon.py`
5. Add court to `seed_courts()` in `backend/app/scheduler/jobs.py`

### Running Tests

```bash
pytest backend/
```

## Troubleshooting

### Database Connection Error
```
Check DATABASE_URL in .env
Ensure PostgreSQL is running
docker-compose ps
```

### Scraper Not Finding Cases
- Check internet connectivity
- Verify court website structure hasn't changed
- Review scraper logs: `docker-compose logs api`

### Dashboard Not Loading Data
- Ensure API is running: http://localhost:8000/health
- Check browser console for CORS errors
- Verify database has data: `SELECT COUNT(*) FROM cases;`

### Docker Issues
```bash
# Restart all services
docker-compose restart

# Rebuild containers
docker-compose down
docker-compose up -d --build

# Check logs
docker-compose logs -f
```

## Performance Tuning

### Database Optimization
- Add indexes on frequently queried columns
- Archive old records monthly
- Use connection pooling (already configured)

### Scraper Optimization
- Increase timeout for slow networks
- Add rate limiting (currently 1 sec between requests)
- Use headless browser for JavaScript-heavy sites

## Future Enhancements

- [ ] Support for State-level courts
- [ ] PDF text extraction with OCR
- [ ] Advanced NLP for better metadata extraction
- [ ] Case similarity and clustering
- [ ] Full-text search capability
- [ ] Email alerts for specific case types
- [ ] GraphQL API
- [ ] React-based dashboard
- [ ] Mobile app

## Contributing

1. Fork repository
2. Create feature branch: `git checkout -b feature/new-court`
3. Commit changes: `git commit -am 'Add new court'`
4. Push to branch: `git push origin feature/new-court`
5. Submit pull request

## License

MIT License - see LICENSE file

## Support

For issues or questions:
- Check [Issues](https://github.com/your-repo/issues)
- Review [Documentation](#)
- Contact development team

## Changelog

### v1.0.0 (Current)
- Initial release
- 3 court support (Supreme, High, Lower)
- Dashboard with real-time stats
- Full metadata extraction
- Daily automated scraping

---

**Last Updated**: February 24, 2026  
**Status**: Production Ready
