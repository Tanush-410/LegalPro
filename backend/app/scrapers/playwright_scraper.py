"""
Advanced scraper using Playwright for JavaScript rendering and CAPTCHA bypass
This handles JavaScript-heavy websites and CAPTCHA challenges
"""
import asyncio
from playwright.async_api import async_playwright, Page
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import logging
import time
from app.scrapers.base_scraper import BaseScraper

logger = logging.getLogger(__name__)

class PlaywrightScraper(BaseScraper):
    """Advanced scraper using Playwright to handle JavaScript and CAPTCHA"""
    
    def __init__(self, court_name: str, court_level: str):
        super().__init__(court_name, court_level)
        self.base_url = "https://indiankanoon.org"
        self.search_url = "https://indiankanoon.org/search"
        self.request_delay = 2  # seconds between requests
        self.last_request_time = 0
        
    async def _get_browser(self):
        """Create browser instance with anti-detection measures"""
        playwright = await async_playwright().start()
        
        # Launch chromium with anti-detection
        browser = await playwright.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
            ]
        )
        
        return playwright, browser
    
    async def _navigate_page(self, page: Page, url: str, wait_for_selector: str = None):
        """Navigate to page with anti-bot measures"""
        # Set user agent and headers
        await page.set_extra_http_headers({
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://indiankanoon.org/',
        })
        
        # Stealth mode
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => false,
            });
        """)
        
        # Navigate with timeout
        try:
            await page.goto(url, timeout=30000, wait_until='networkidle')
            
            # Wait for content if selector provided
            if wait_for_selector:
                await page.wait_for_selector(wait_for_selector, timeout=10000)
            else:
                await asyncio.sleep(2)  # Wait for JS to render
                
            return True
        except Exception as e:
            logger.error(f"Error navigating to {url}: {str(e)}")
            return False
    
    async def _check_and_bypass_captcha(self, page: Page) -> bool:
        """Check for and attempt to bypass CAPTCHA"""
        try:
            # Check if CAPTCHA is present
            captcha_elements = await page.query_selector_all(
                'iframe[src*="recaptcha"], [id*="recaptcha"], .g-recaptcha'
            )
            
            if captcha_elements:
                logger.warning(f"CAPTCHA detected on {page.url}")
                
                # Try to wait for auto-solve (some sites have JS-based solvers)
                try:
                    await page.wait_for_timeout(3000)  # Wait 3 seconds
                    
                    # Try clicking on checkbox if exists
                    try:
                        await page.click('input[type="checkbox"]', timeout=2000)
                    except:
                        pass
                    
                    return False  # Still has CAPTCHA, can't solve
                except:
                    return False
            
            return True  # No CAPTCHA
        except Exception as e:
            logger.error(f"Error checking CAPTCHA: {str(e)}")
            return True
    
    def get_writ_petitions(self, from_date=None, to_date=None):
        """Search for writ petitions using Playwright"""
        if from_date is None:
            from_date = datetime.utcnow() - timedelta(days=1)
        if to_date is None:
            to_date = datetime.utcnow()
        
        try:
            # Run async function in sync context
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(
            self._async_get_writ_petitions(from_date, to_date)
        )
    
    async def _async_get_writ_petitions(self, from_date, to_date):
        """Async implementation of writ petitions search"""
        playwright, browser = await self._get_browser()
        cases = []
        
        try:
            page = await browser.new_page()
            
            # Navigate to search with query
            search_params = {
                'q': f'"{self.court_name}" "Writ Petition"',
                'type': 'judgement'
            }
            search_url = f"{self.search_url}?q={search_params['q']}&type={search_params['type']}"
            
            logger.info(f"Searching: {search_url}")
            
            if not await self._navigate_page(page, search_url, wait_for_selector='.result'):
                logger.error("Failed to navigate search page")
                await page.close()
                await browser.close()
                return cases
            
            # Check for CAPTCHA
            has_captcha = not await self._check_and_bypass_captcha(page)
            if has_captcha:
                logger.warning(f"CAPTCHA present, using fallback requests library")
                await page.close()
                await browser.close()
                # Fall back to requests-based scraper
                return self._fallback_get_writ_petitions()
            
            # Get page content
            content = await page.content()
            soup = BeautifulSoup(content, 'html.parser')
            
            # Extract cases
            for result in soup.find_all('li', class_='result'):
                try:
                    link = result.find('a', href=True)
                    if link:
                        case_url = link['href']
                        if not case_url.startswith('http'):
                            case_url = self.base_url + case_url
                        case_title = link.get_text(strip=True)
                        
                        cases.append({
                            'url': case_url,
                            'title': case_title
                        })
                except Exception as e:
                    logger.warning(f"Error extracting case: {str(e)}")
                    continue
            
            logger.info(f"Found {len(cases)} writ petitions for {self.court_name}")
            
            await page.close()
            
        except Exception as e:
            logger.error(f"Error in async get_writ_petitions: {str(e)}")
        finally:
            await browser.close()
            await playwright.stop()
        
        return cases
    
    def _fallback_get_writ_petitions(self):
        """Fallback to requests library if Playwright fails"""
        import requests
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        
        try:
            session = requests.Session()
            retry = Retry(total=3, backoff_factor=0.5, status_forcelist=[429, 500, 502, 503, 504])
            adapter = HTTPAdapter(max_retries=retry)
            session.mount('http://', adapter)
            session.mount('https://', adapter)
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Referer': 'https://indiankanoon.org/',
            }
            
            response = session.get(
                self.search_url,
                params={'q': f'"{self.court_name}" "Writ Petition"', 'type': 'judgement'},
                headers=headers,
                timeout=15
            )
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            cases = []
            
            for result in soup.find_all('li', class_='result'):
                try:
                    link = result.find('a', href=True)
                    if link:
                        case_url = link['href']
                        if not case_url.startswith('http'):
                            case_url = self.base_url + case_url
                        cases.append({'url': case_url, 'title': link.get_text(strip=True)})
                except:
                    continue
            
            logger.info(f"Fallback: Found {len(cases)} writ petitions for {self.court_name}")
            return cases
        except Exception as e:
            logger.error(f"Fallback scraper failed: {str(e)}")
            return []
    
    def parse_case_details(self, case):
        """Parse case details using requests (Playwright can be slow for individual cases)"""
        import requests
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        
        try:
            time.sleep(self.request_delay)
            
            session = requests.Session()
            retry = Retry(total=3, backoff_factor=0.5, status_forcelist=[429, 500, 502, 503, 504])
            adapter = HTTPAdapter(max_retries=retry)
            session.mount('http://', adapter)
            session.mount('https://', adapter)
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'https://indiankanoon.org/',
            }
            
            response = session.get(case['url'], headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            case_data = {
                'url': case['url'],
                'title': case['title'],
                'case_type': 'Writ Petition',
                'court': self.court_name,
                'court_level': self.court_level,
                'judgment_text': None,
                'case_number': f"WP-{case.get('title', 'unknown')[:20]}",
                'case_date': datetime.utcnow(),
                'judgment_date': datetime.utcnow(),
            }
            
            # Extract judgment text
            judgment_div = soup.find('div', class_='judgement')
            if judgment_div:
                case_data['judgment_text'] = judgment_div.get_text(strip=True)[:2000]
            
            # Extract case number
            case_number_elem = soup.find('div', class_='case-number')
            if case_number_elem:
                case_data['case_number'] = case_number_elem.get_text(strip=True)
            
            return case_data
        except Exception as e:
            logger.error(f"Error parsing case: {str(e)}")
            raise
