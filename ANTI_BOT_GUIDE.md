# Anti-Bot Detection & CAPTCHA Handling Guide

## Current Status: ✅ Working

Indian Kanoon works with basic User-Agent spoofing because:
- It's a public legal database designed for research access
- They don't have aggressive rate limiting
- robots.txt allows `/search` and `/doc` endpoints
- No JavaScript-based CAPTCHA on most pages

## If You Encounter "Are You a Robot?" Page

### Option 1: Add Better Headers (Recommended First)
```python
def _get_headers(self):
    """Enhanced headers to look more like a real browser"""
    return {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Referer': 'https://indiankanoon.org/',
        'Cache-Control': 'max-age=0'
    }
```

### Option 2: Add Session Management
```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def create_session():
    session = requests.Session()
    retry = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=(500, 502, 504)
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

# Use it:
session = create_session()
response = session.get(url, headers=headers, timeout=10)
```

### Option 3: Use Selenium for JavaScript Rendering (If Needed)
```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def scrape_with_js():
    driver = webdriver.Chrome()  # Requires chromedriver
    driver.get(search_url)
    
    # Wait for JS to render
    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, "result"))
    )
    
    # Now parse with BeautifulSoup
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    # ... rest of parsing
    driver.quit()
```

### Option 4: Use Rotating Proxies (For Heavy Scraping)
```python
import requests
from itertools import cycle

# Free proxy list (replace with paid proxies for reliability)
proxies = [
    'http://proxy1.com:8080',
    'http://proxy2.com:8080',
    'http://proxy3.com:8080',
]
proxy_pool = cycle(proxies)

for request in requests.get(
    url,
    proxies={'http': next(proxy_pool)},
    headers=headers,
    timeout=10
):
    # Process request
```

### Option 5: Use 2Captcha or Anti-Captcha (Paid Service)
```python
from 2captcha import *

solver = TwoCaptcha('API_KEY')
try:
    result = solver.recaptcha(
        sitekey='6Le-wvkSVVABCPBMRTvw0Q21Chm1MoO5Zh_j7VgV',
        url='https://indiankanoon.org'
    )
except Exception as e:
    print(f"Error: {e}")

captcha_token = result.get('code')
# Then use token in request headers
```

## Current Rate Limiting
- 1 second delay between requests (prevents hammering)
- 15-minute intervals between full scrapes
- Maximum 100 cases per scrape job

## Best Practices for Ethical Scraping
1. ✅ Respect robots.txt
2. ✅ Add delays between requests
3. ✅ Use meaningful User-Agent
4. ✅ Cache results to avoid re-scraping
5. ✅ Check legal/terms of service
6. ✅ Don't overload servers (rate limit)

## Indian Kanoon Terms
- ✅ Non-commercial use: Allowed
- ✅ Academic research: Allowed  
- ⚠️ Commercial scraping: May require permission
- ❌ Republishing without attribution: Not allowed

## Monitoring Scraper Health
Check logs to see if scraper is working:
```bash
# View scraper logs
tail -f /tmp/court-scraper.log

# Check if blocked
grep -i "robot\|captcha\|403\|429" /tmp/court-scraper.log
```

If you see these errors:
- `403 Forbidden` - IP might be temporarily blocked
- `429 Too Many Requests` - Rate limiting triggered
- `"Are you a robot?"` - CAPTCHA bypass needed

## Next Steps
1. Monitor the scraper for first week
2. If CAPTCHA errors appear, implement Option 1 (better headers)
3. If that fails, implement Option 3 (Selenium)
4. For large-scale scraping, use Option 4 (rotating proxies)
