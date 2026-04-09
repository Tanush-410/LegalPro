# 👨‍💻 Development Guide - Court Ecosystem

## Contributing & Development

This guide helps developers extend and enhance the Court Ecosystem.

---

## Setting Up Development Environment

### 1. Clone/Navigate to Project
```bash
cd /Users/tanush.s.vashisht/Desktop/Tanush/work/court-ecosystem
```

### 2. Create Development Virtual Environment
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Install Development Tools (Optional)
```bash
pip install pytest pytest-cov black flake8 mypy
```

### 4. Run in Development Mode
```bash
# Terminal 1: Run API
cd backend
uvicorn app.main:app --reload --port 8000

# Terminal 2: View logs in real-time
docker-compose logs -f api
```

---

## Code Structure & Conventions

### 1. Module Organization

Each module follows this structure:
```python
"""
Module description - what this module does
"""

# Standard library imports
import os
import time
from datetime import datetime

# Third-party imports
from sqlalchemy import Column, Integer, String
import requests

# Local imports
from app.database import Base
from app.models import Court

# Implementation
class MyClass:
    pass

def my_function():
    pass
```

### 2. Naming Conventions
- Classes: `PascalCase` → `MyScraperClass`
- Functions: `snake_case` → `my_function_name`
- Constants: `UPPER_CASE` → `MAX_RETRIES = 3`
- Private: `_snake_case` → `_internal_method()`

---

## Adding a New Court Scraper

### Step 1: Create Scraper File
Create `backend/app/scrapers/high_court_mumbai.py`:

```python
"""
Scraper for Bombay High Court
"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import logging
from app.scrapers.base_scraper import BaseScraper

logger = logging.getLogger(__name__)

class BombayHighCourtScraper(BaseScraper):
    """Scraper for Bombay High Court"""
    
    def __init__(self):
        super().__init__(
            court_name="Bombay High Court",
            court_level="High Court"
        )
        self.base_url = "https://bombayHighCourt.gov.in"  # Example
    
    def get_writ_petitions(self, from_date=None, to_date=None):
        """Fetch writ petitions from Bombay High Court"""
        # Implementation here
        cases = []
        # ... scraping logic ...
        return cases
    
    def parse_case_details(self, case):
        """Parse individual case"""
        # Implementation here
        case_data = {}
        # ... parsing logic ...
        return case_data
```

### Step 2: Update Factory Function
Edit `backend/app/scrapers/indian_kanoon.py`:

```python
from app.scrapers.high_court_mumbai import BombayHighCourtScraper

def get_scraper(court_name: str, court_level: str):
    """Factory function to get the appropriate scraper"""
    
    if "Bombay" in court_name or "Mumbai" in court_name:
        return BombayHighCourtScraper()
    
    # Default to Indian Kanoon
    return IndianKanoonScraper(court_name, court_level)
```

### Step 3: Add Court to Database Seeding
Edit `backend/app/scheduler/jobs.py`:

```python
def seed_courts(db: Session):
    """Add default courts if they don't exist"""
    courts = [
        Court(name="Supreme Court of India", level=CourtEnum.SUPREME),
        # ... existing courts ...
        Court(
            name="Bombay High Court",
            level=CourtEnum.HIGH,
            state="Maharashtra"
        ),  # NEW
    ]
    
    for court in courts:
        if not db.query(Court).filter(Court.name == court.name).first():
            db.add(court)
    
    db.commit()
```

---

## Enhancing Metadata Extraction

### Current Extraction (Regex-based)
Located in `backend/app/metadata/extractor.py`

### Adding spaCy NLP

```python
"""
Enhanced metadata extraction with spaCy
"""
import spacy
from app.metadata.extractor import MetadataExtractor

class EnhancedExtractor(MetadataExtractor):
    """Uses spaCy for better extraction"""
    
    def __init__(self):
        self.nlp = spacy.load('en_core_web_sm')
    
    @staticmethod
    def extract_judge_names_nlp(text: str) -> list:
        """Extract names using NLP"""
        doc = nlp(text)
        judges = []
        
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                judges.append(ent.text)
        
        return judges
```

Usage in `jobs.py`:
```python
from app.metadata.enhanced_extractor import EnhancedExtractor

extractor = EnhancedExtractor()
metadata = extractor.extract_all_metadata(judgment_text)
```

---

## Adding New API Endpoints

### Step 1: Create Route File
Create `backend/app/routes/search.py`:

```python
"""
Search endpoints for advanced queries
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.database import get_db
from app.models import Case, Court

router = APIRouter(prefix="/api/search", tags=["search"])

@router.get("/cases-by-judge")
async def search_by_judge(
    judge_name: str = Query(..., min_length=3),
    db: Session = Depends(get_db)
):
    """Search cases by judge name"""
    from app.models import Judgment
    
    results = db.query(Case).join(Judgment).filter(
        Judgment.judge_name.ilike(f"%{judge_name}%")
    ).all()
    
    return results

@router.get("/cases-by-parties")
async def search_by_parties(
    party_name: str = Query(..., min_length=3),
    db: Session = Depends(get_db)
):
    """Search cases by petitioner or respondent"""
    
    results = db.query(Case).filter(
        or_(
            Case.petitioner.ilike(f"%{party_name}%"),
            Case.respondent.ilike(f"%{party_name}%")
        )
    ).all()
    
    return results
```

### Step 2: Register Route in Main App
Edit `backend/app/main.py`:

```python
from app.routes import dashboard, cases, search

# Add to startup
app.include_router(search.router)
```

### Test New Endpoint
```bash
curl "http://localhost:8000/api/search/cases-by-judge?judge_name=john"
```

---

## Modifying the Database Schema

### Example: Add Case Status Field

### Step 1: Create Model Migration
Edit `backend/app/models.py`:

```python
class Case(Base):
    __tablename__ = "cases"
    
    id = Column(Integer, primary_key=True, index=True)
    case_number = Column(String(255), unique=True, index=True)
    case_type = Column(String(100), index=True)
    # ... existing fields ...
    
    # NEW FIELD
    status = Column(String(50), default="PENDING")  # PENDING, RESOLVED, DISMISSED
    created_at = Column(DateTime, default=datetime.utcnow)
```

### Step 2: Update Schema
Edit `backend/app/schemas.py`:

```python
class CaseBase(BaseModel):
    case_number: str
    case_type: str
    court_id: int
    # ... existing fields ...
    status: str = "PENDING"  # NEW
```

### Step 3: Migration (Alembic in future)
```bash
# Manual for now - run this in database
ALTER TABLE cases ADD COLUMN status VARCHAR(50) DEFAULT 'PENDING';
```

---

## Adding Dashboard Features

### Add New Chart
Edit `dashboard/index.html`:

```javascript
// Add new canvas element
<div class="chart-container">
    <h2>Cases by Status (Pie Chart)</h2>
    <div class="chart-wrapper">
        <canvas id="statusChart"></canvas>
    </div>
</div>

// Add function
async function loadStatusDistribution() {
    try {
        const response = await fetch(`${API_BASE}/api/dashboard/status-distribution`);
        const data = await response.json();
        
        updateStatusChart(data);
    } catch (error) {
        console.error('Error loading status:', error);
    }
}

// Update chart
function updateStatusChart(data) {
    const ctx = document.getElementById('statusChart');
    
    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: Object.keys(data),
            datasets: [{
                data: Object.values(data),
                backgroundColor: ['#667eea', '#764ba2', '#f093fb', '#feca57']
            }]
        },
        // ... chart options ...
    });
}

// Call in init()
loadStatusDistribution();
```

### Add Backend Endpoint
Edit `backend/app/routes/dashboard.py`:

```python
@router.get("/status-distribution")
async def get_status_distribution(db: Session = Depends(get_db)):
    """Get case distribution by status"""
    
    result = db.query(
        Case.status,
        func.count(Case.id).label("count")
    ).group_by(Case.status).all()
    
    return {status: count for status, count in result}
```

---

## Testing

### Unit Tests
Create `backend/tests/test_metadata_extractor.py`:

```python
import pytest
from app.metadata.extractor import MetadataExtractor

class TestMetadataExtractor:
    
    def test_extract_case_number(self):
        text = "Case No.: WP/12345/2024"
        result = MetadataExtractor.extract_case_number(text)
        assert result == "WP/12345/2024"
    
    def test_extract_judge_names(self):
        text = "Hon'ble Justice John Doe and Justice Jane Smith delivered the judgment"
        result = MetadataExtractor.extract_judge_names(text)
        assert "John Doe" in result
        assert "Jane Smith" in result
    
    def test_extract_verdict(self):
        text = "This petition is hereby allowed"
        result = MetadataExtractor.extract_verdict(text)
        assert "allowed" in result.lower()
```

### Run Tests
```bash
pytest backend/tests/ -v
```

---

## Database Optimization

### Add Indexes for Performance
```sql
-- Already indexed for common queries
CREATE INDEX idx_cases_created_at ON cases(created_at);
CREATE INDEX idx_cases_case_type ON cases(case_type);
CREATE INDEX idx_judgments_date ON judgments(judgment_date);

-- Add for new queries
CREATE INDEX idx_cases_status ON cases(status);  -- If status field added
CREATE INDEX idx_judgments_judge ON judgments(judge_name);
```

### Query Optimization Example
```python
# BEFORE - N+1 query problem
cases = db.query(Case).all()
for case in cases:
    judgments = db.query(Judgment).filter(Judgment.case_id == case.id).all()

# AFTER - Using joined query
from sqlalchemy.orm import joinedload

cases = db.query(Case).options(joinedload(Case.judgments)).all()
```

---

## Deployment Checklist

### Before Production
- [ ] Set `DEBUG=False` in .env
- [ ] Configure real `SECRET_KEY`
- [ ] Use strong database password
- [ ] Enable HTTPS
- [ ] Set up monitoring/alerts
- [ ] Configure backups
- [ ] Test scraper on target courts
- [ ] Review and clean logs
- [ ] Document any custom scrapers

### Docker Build
```bash
docker-compose build
docker-compose up -d --remove-orphans
```

### Health Check
```bash
curl http://localhost:8000/health
curl http://localhost:8000/api/dashboard/stats
```

---

## Common Tasks

### Adding a New Environment Variable
1. Add to `.env` file
2. Read in code: `os.getenv("VAR_NAME", default)`
3. Update `.env.example`

### Debugging Database Issues
```bash
# Connect to DB
docker-compose exec db psql -U court_user -d court_ecosystem

# View table structure
\d cases

# View data
SELECT * FROM cases LIMIT 5;
```

### Viewing Logs
```bash
# API logs
docker-compose logs api

# Database logs
docker-compose logs db

# All services
docker-compose logs -f
```

### Restarting Services
```bash
# Soft restart (keep data)
docker-compose restart

# Hard restart (recreate containers)
docker-compose down
docker-compose up -d

# Rebuild after code changes
docker-compose up -d --build
```

---

## Git Workflow

### Clone Repository
```bash
git clone <repo-url> court-ecosystem
cd court-ecosystem
```

### Create Feature Branch
```bash
git checkout -b feature/add-new-court
# Make changes
git add .
git commit -m "Add scraper for High Court of Delhi"
```

### Push and Create PR
```bash
git push origin feature/add-new-court
# Create Pull Request on GitHub
```

---

## Code Quality Standards

### Style Guide (PEP 8)
```bash
black backend/app/  # Auto-format code
```

### Type Checking
```bash
mypy backend/app/main.py
```

### Linting
```bash
flake8 backend/app/ --max-line-length=100
```

---

## Troubleshooting Development Issues

### Port Already in Use
```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>
```

### Database Connection Issues
```bash
# Check PostgreSQL service
docker-compose ps

# Reset database (WARNING: Deletes data!)
docker-compose down -v
docker-compose up -d
```

### Scraper Not Working
```bash
# Check internet connection
ping indiankanoon.org

# Check scraper logs
docker-compose logs api | grep scrape
```

---

## Performance Profiling

### Analyze Slow Queries
```python
# In models.py
from sqlalchemy import event
from sqlalchemy.engine import Engine
import time

@event.listens_for(Engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, params, context, executemany):
    conn.info.setdefault('query_start_time', []).append(time.time())

@event.listens_for(Engine, "after_cursor_execute")
def receive_after_cursor_execute(conn, cursor, statement, params, context, executemany):
    total_time = time.time() - conn.info['query_start_time'].pop(-1)
    if total_time > 1.0:  # Log if > 1 second
        print(f"Query executed in {total_time:.4f} seconds")
```

---

## Next Steps for Development

1. **Unit Tests** - Write comprehensive test suite
2. **Integration Tests** - Test end-to-end flows
3. **Load Testing** - Test with high volume
4. **Documentation** - API documentation generation
5. **CI/CD** - GitHub Actions for automated testing
6. **Monitoring** - Add APM (Application Performance Monitoring)

---

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/)
- [APScheduler](https://apscheduler.readthedocs.io/)

---

## Support

For development issues:
1. Check existing issues
2. Review logs: `docker-compose logs -f`
3. Debug database: `docker-compose exec db psql ...`
4. Test API: `curl http://localhost:8000/docs`

---

Happy Development! 🚀

