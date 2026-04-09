# Real-Time Court Case Detection Setup Guide

## Overview

This guide explains how to set up your Court Ecosystem platform for **real-time case detection** from official eCourts Government portals. The system now:

✅ Polls official eCourts portals every 5-15 minutes (configurable)
✅ Ethically scrapes with robots.txt compliance & rate limiting
✅ Supports proxy rotation for large-scale deployments
✅ Broadcasts new cases via WebSocket in real-time
✅ Falls back to legacy scrapers (Indian Kanoon, AIR Online)
✅ Tracks CNR (Case Number Record) for deduplication

---

## Quick Start (5 minutes)

### 1. Update Environment Variables

Copy the new `.env.example` to `.env`:
```bash
cp backend/.env.example backend/.env
```

Key configurations for real-time:
```bash
# Enable official eCourts portals
USE_ECOURTS_PORTAL=true

# Poll every 10 minutes (adjust 5-15)
SCRAPER_POLLING_INTERVAL_MINUTES=10

# Look back 24 hours for new cases
SCRAPER_LOOKBACK_HOURS=24

# Rate limiting: 1 request per minute
SCRAPER_RATE_LIMIT_SECONDS=60
```

### 2. Install New Dependencies

```bash
cd backend
pip install -r requirements.txt
```

New packages added:
- `websockets==12.0` - WebSocket support for real-time updates
- `urllib3==2.1.0` - Proxy management
- `rotatingproxy==0.1.0` - Proxy rotation (optional)

### 3. Run Database Migration

Add new columns to track real-time cases:
```bash
# The system will auto-create tables on startup
# New columns in `cases` table:
# - cnr (Case Number Record) - PRIMARY KEY for eCourts
# - is_new (Boolean) - marks freshly detected cases
# - first_detected_at (DateTime) - when case was first found
```

### 4. Start the Backend

```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Monitor logs for:
```
=== Scheduler started with real-time polling ===
  - Real-time job: runs every 10 minutes
  - Daily job: runs at 2:00 AM
  - eCourts Portal enabled: true
  - Lookback window: 24 hours
```

---

## Architecture

### Scraper Selection Flow

```
for each court:
  if USE_ECOURTS_PORTAL:
    try:
      scraper = ECourtsServicesScraper (hcservices.ecourts.gov.in)
    catch:
      scraper = NJDGScraper (njdg.ecourts.gov.in)
  else:
    scraper = Indian Kanoon / AIR Online (legacy)
  
  scraper.scrape(from_date=now - 24 hours)
```

### Component Details

#### 1. **ECourtsServicesScraper** (`backend/app/scrapers/ecourts_scraper.py`)

**Official portals supported:**
- High Court: `hcservices.ecourts.gov.in`
- District Courts: `{district}.dcourts.gov.in` (e.g., bengaluru.dcourts.gov.in)
- NJDG Portal: `njdg.ecourts.gov.in`

**Key features:**
```python
ECourtsServicesScraper(
    court_name="Delhi High Court",
    court_level="HIGH",
    portal="high_court"  # or "district" with district param
)
```

**Ethical scraping built-in:**
```python
class RobotsChecker:
    - Checks robots.txt before scraping
    - Caches results for 1 hour
    - Returns False if path is blocked
    
class ProxyManager:
    - Loads proxies from PROXY_LIST env
    - Rotates proxies on each request
    - Marks failed proxies for skipping
    - Falls back to direct connection if all fail
```

**Rate limiting:**
```python
_rate_limit(seconds=60)
# Default: 1 request per minute per IP
# Configurable via SCRAPER_RATE_LIMIT_SECONDS
```

#### 2. **Scheduler** (`backend/app/scheduler/jobs.py`)

**Real-time polling job:**
```python
# Runs every N minutes (configurable)
scrape_court_documents()
  ├─ for each court in database
  ├─ get_scraper_for_court(use_ecourts=True)
  ├─ scraper.scrape(from_date=now - 24 hours)
  ├─ deduplicate by CNR
  ├─ save new cases to database
  └─ broadcast via WebSocket (~100-500ms latency)
```

**Configuration:**
```python
SCRAPER_POLLING_INTERVAL_MINUTES=10  # 5-15 recommended
SCRAPER_LOOKBACK_HOURS=24            # Match your polling interval
```

#### 3. **WebSocket Service** (`backend/app/routes/websocket.py`)

**Real-time case updates:**
```javascript
// Client: subscribe to updates
ws = new WebSocket("ws://localhost:8000/api/ws/ws/client-123");

ws.send(JSON.stringify({
    type: "subscribe",
    courts: ["Delhi High Court", "Bombay High Court"],
    case_types: ["Writ Petition", "Civil Appeal"]
}));

// Server: broadcast new cases
{
    type: "new_case",
    case: {
        id: 5678,
        cnr: "DELHC0123456789",
        case_number: "WP-2026-001",
        court: "Delhi High Court",
        case_type: "Writ Petition",
        petitioner: "John Doe",
        respondent: "State of India",
        first_detected_at: "2026-03-10T10:30:00"
    }
}
```

**Client library example (JavaScript):**
```javascript
class CourtWebSocket {
    constructor(clientId) {
        this.ws = new WebSocket(`ws://localhost:8000/api/ws/ws/${clientId}`);
        this.setupHandlers();
    }
    
    setupHandlers() {
        this.ws.onmessage = (event) => {
            const message = JSON.parse(event.data);
            if (message.type === "new_case") {
                console.log("🚨 New case detected:", message.case.case_number);
                // Update UI, send notification, etc.
            }
        };
    }
    
    subscribe(courts, caseTypes) {
        this.ws.send(JSON.stringify({
            type: "subscribe",
            courts,
            case_types: caseTypes
        }));
    }
}
```

---

## Configuration Examples

### Example 1: Moderate Load (Default)
```bash
USE_ECOURTS_PORTAL=true
SCRAPER_POLLING_INTERVAL_MINUTES=10
SCRAPER_LOOKBACK_HOURS=24
SCRAPER_RATE_LIMIT_SECONDS=60
PROXY_LIST=                           # No proxies
```
- Polls every 10 minutes
- 1 request per minute per IP
- Covers ~100-200 cases per poll across all courts
- Best for: Small-medium deployments

### Example 2: High Freshness (Development/Testing)
```bash
USE_ECOURTS_PORTAL=true
SCRAPER_POLLING_INTERVAL_MINUTES=5
SCRAPER_LOOKBACK_HOURS=12
SCRAPER_RATE_LIMIT_SECONDS=45
PROXY_LIST=                           # No proxies
```
- Polls every 5 minutes
- 1 request per 45 seconds per IP
- Nearly real-time (5-minute latency)
- Best for: Testing, demo, high-traffic courts

### Example 3: Large Scale with Proxies
```bash
USE_ECOURTS_PORTAL=true
SCRAPER_POLLING_INTERVAL_MINUTES=5
SCRAPER_LOOKBACK_HOURS=24
SCRAPER_RATE_LIMIT_SECONDS=30
PROXY_LIST=http://proxy1:8080,http://proxy2:8080,socks5://proxy3:1080
```
- 5-minute polling across multiple IP addresses
- Higher load capacity
- Best for: Production with 50+ courts

### Example 4: Legacy + Official Hybrid
```bash
USE_ECOURTS_PORTAL=true
SCRAPER_SOURCES=air,ik                # Fallback sources
SCRAPER_POLLING_INTERVAL_MINUTES=15
SCRAPER_LOOKBACK_HOURS=48
IK_MAX_CASES_PER_COURT=50
AIR_MAX_CASES_PER_COURT=25
```
- Primary: Official eCourts
- Fallback: Indian Kanoon + AIR Online for historical backfill
- Best for: Comprehensive coverage

---

## Database Schema Changes

### New columns in `cases` table:

```sql
ALTER TABLE cases ADD COLUMN cnr VARCHAR(255) UNIQUE INDEX;
ALTER TABLE cases ADD COLUMN is_new BOOLEAN DEFAULT TRUE INDEX;
ALTER TABLE cases ADD COLUMN first_detected_at DATETIME DEFAULT NOW() INDEX;
```

Example query to find freshly detected cases:
```sql
SELECT * FROM cases 
WHERE is_new = true 
  AND first_detected_at > NOW() - INTERVAL '1 hour'
ORDER BY first_detected_at DESC;
```

---

## API Endpoints

### REST API

```bash
# Manually trigger a scrape job
POST /api/scrape/trigger

# Get WebSocket status
GET /api/ws/status

# Response:
{
    "status": "ok",
    "active_connections": 42,
    "subscriptions": 42,
    "timestamp": "2026-03-10T10:30:45.123456"
}
```

### WebSocket API

```
ws://localhost:8000/api/ws/ws/{client_id}
```

**Client → Server messages:**
```javascript
// Subscribe to updates
{
    type: "subscribe",
    courts: ["Delhi High Court"],
    case_types: ["Writ Petition"]
}

// Keep-alive ping
{ type: "ping" }

// Get connection status
{ type: "get_status" }
```

**Server → Client messages:**
```javascript
// Subscription confirmation
{
    type: "subscribed",
    courts: [...],
    case_types: [...]
}

// New case detected
{
    type: "new_case",
    case: { ... },
    timestamp: "2026-03-10T10:30:45.123456"
}

// Case status update
{
    type: "case_update",
    case_id: 123,
    update: { status: "judgment_released", judgment_date: "2026-03-10" }
}

// Scraping job status
{
    type: "scrape_status",
    status: { action: "started", court: "Delhi High Court", ... },
    timestamp: "2026-03-10T10:30:45.123456"
}

// Keep-alive pong
{ type: "pong", timestamp: "2026-03-10T10:30:45.123456" }

// Connection status
{
    type: "status",
    connected: true,
    active_clients: 42,
    subscription: { courts: [...], case_types: [...] }
}
```

---

## Troubleshooting

### Issue: No cases detected
**Diagnosis:**
```bash
# Check logs
docker logs court-backend | grep "scrape_court_documents"

# Manual test
curl -X POST http://localhost:8000/api/scrape/trigger
```

**Solutions:**
1. Verify `USE_ECOURTS_PORTAL=true`
2. Check `SCRAPER_LOOKBACK_HOURS` and `SCRAPER_POLLING_INTERVAL_MINUTES`
3. Verify portal URLs are accessible:
   ```bash
   curl https://hcservices.ecourts.gov.in
   curl https://njdg.ecourts.gov.in
   ```
4. Check `SCRAPER_RATE_LIMIT_SECONDS` - may be too high

### Issue: "CAPTCHA detected"
**Solution:**
- eCourts portals have built-in CAPTCHA checks
- System automatically pauses 30 seconds and retries
- If persistent, reduce `SCRAPER_RATE_LIMIT_SECONDS` to 120+
- Consider adding proxies via `PROXY_LIST`

### Issue: WebSocket not receiving updates
**Diagnosis:**
```bash
# Check WebSocket service
curl http://localhost:8000/api/ws/status

# Check scheduler running
docker logs court-backend | grep "Real-time job"
```

**Solutions:**
1. Verify WebSocket connection: `ws.readyState === 1`
2. Send subscription message after connect
3. Verify courts exist in database
4. Check firewall allows WebSocket (port 8000)

### Issue: High database growth
**Solutions:**
```sql
-- Archive old cases (older than 1 year)
DELETE FROM cases 
WHERE created_at < NOW() - INTERVAL '1 year'
  AND is_new = false;

-- Optimize with indexes
CREATE INDEX idx_cases_first_detected ON cases(first_detected_at);
```

---

## Performance Tuning

### Database Connection Pool
```python
# backend/app/database.py
engine = create_engine(
    DATABASE_URL,
    pool_size=20,              # Max concurrent connections
    max_overflow=40,           # Extra connections allowed
    pool_pre_ping=True         # Verify connection before use
)
```

### Memory Usage
```bash
# Monitor scraper memory
docker stats court-backend

# If high: reduce IK_MAX_CASES_PER_COURT or AIR_MAX_CASES_PER_COURT
```

### Network Optimization
```bash
# Reduce lookback for faster scrapes
SCRAPER_LOOKBACK_HOURS=12

# Increase polling interval to reduce load
SCRAPER_POLLING_INTERVAL_MINUTES=15

# Disable legacy scrapers if not needed
SCRAPER_SOURCES=
```

---

## Security Considerations

### Rate Limiting
✅ Built-in: 1 request/minute per IP
✅ Respects robots.txt from portals
✅ Automatic CAPTCHA detection & retry
⚠️ Shared proxies may have lower limits

### Proxy Usage
- ✅ Use for non-gov sites (Indian Kanoon)
- ❌ Do NOT use for official gov portals (auto-rejects)
- Use proxies from trusted providers only
- Rotate regularly to avoid blacklisting

### API Security
- WebSocket endpoints are open (add authentication for production)
- Add API key validation to scraper endpoint
- Rate limit dashboard API with reverse proxy (Nginx, Cloudflare)

```nginx
# Example nginx rate limit for WebSocket
limit_req_zone $binary_remote_addr zone=ws_limit:10m rate=10r/s;
location /api/ws/ {
    limit_req zone=ws_limit burst=20 nodelay;
    proxy_pass http://backend:8000;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
}
```

---

## Production Deployment Checklist

- [ ] Set `ENVIRONMENT=production`
- [ ] Set `DEBUG=false`
- [ ] Use strong `SECRET_KEY`
- [ ] Configure `ALLOWED_ORIGINS` for CORS
- [ ] Set `SCRAPER_RATE_LIMIT_SECONDS>=60`
- [ ] Disable `VERBOSE_SCRAPING`
- [ ] Configure monitoring/alerts (SLACK_WEBHOOK_URL)
- [ ] Set up database backups
- [ ] Configure reverse proxy (Nginx) with rate limiting
- [ ] Use CloudFlare or similar CDN for DDoS protection
- [ ] Monitor WebSocket connection count
- [ ] Archive old cases regularly

---

## Next Steps

1. **Frontend Integration:**
   - Connect frontend to WebSocket endpoint
   - Display new cases with badge/notification
   - Filter by court/case type

2. **Advanced Features:**
   - Push notifications (Firebase Cloud Messaging)
   - Email alerts for specific case criteria
   - PDF parsing & metadata extraction
   - Machine learning for verdict classification

3. **Scaling:**
   - Horizontal scaling with multiple workers
   - Redis for caching & session management
   - Separate scraper instances per court
   - Message queue (RabbitMQ) for large-scale

---

## References

- [eCourts Services Portal](https://hcservices.ecourts.gov.in/)
- [NJDG Portal](https://njdg.ecourts.gov.in/)
- [District Courts](https://district.dcourts.gov.in/)
- [robots.txt Specification](https://en.wikipedia.org/wiki/Robots.txt)
- [WebSocket Protocol](https://datatracker.ietf.org/doc/html/rfc6455)

---

**Last Updated:** March 10, 2026
