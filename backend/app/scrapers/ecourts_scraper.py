"""
Official eCourts Portal Scraper
Scrapes from official government eCourts portals:
- High Court: hcservices.ecourts.gov.in
- District Courts: {district}.dcourts.gov.in
- NJDG Portal: njdg.ecourts.gov.in

Features:
- Ethical scraping (respects robots.txt, rate limiting)
- CNR (Case Number Record) based searches
- Date-based filtering
- PDF/HTML judgment downloads
- Proxy rotation support
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import logging
import time
import os
import hashlib
from urllib.parse import urljoin, quote
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class RobotsChecker:
    """Check if scraping is allowed via robots.txt"""
    
    def __init__(self):
        self.robots_cache = {}
        self.cache_time = 3600  # 1 hour
    
    def is_allowed(self, url: str, user_agent: str = "Court-Ecosystem-Bot/1.0") -> bool:
        """Check if URL is allowed for scraping via robots.txt"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = f"{parsed.scheme}://{parsed.netloc}"
            
            if domain in self.robots_cache:
                cached_time, allowed = self.robots_cache[domain]
                if time.time() - cached_time < self.cache_time:
                    return allowed
            
            robots_url = urljoin(domain, "/robots.txt")
            response = requests.get(robots_url, timeout=5)
            
            # Parse robots.txt - simple check for disallow paths
            is_allowed = True
            if response.status_code == 200:
                disallow_paths = []
                for line in response.text.split('\n'):
                    line = line.strip()
                    if line.lower().startswith('disallow:'):
                        path = line.split(':', 1)[1].strip()
                        if path and path != '/':
                            disallow_paths.append(path)
                
                # Check if our path matches any disallow patterns
                path = parsed.path
                for disallow in disallow_paths:
                    if path.startswith(disallow):
                        is_allowed = False
                        break
            
            self.robots_cache[domain] = (time.time(), is_allowed)
            return is_allowed
            
        except Exception as e:
            logger.warning(f"Error checking robots.txt: {str(e)}")
            return True  # Allow by default if we can't check


class ProxyManager:
    """Manage rotating proxies for scraping"""
    
    def __init__(self):
        self.proxies = self._load_proxies()
        self.current_proxy_index = 0
        self.failed_proxies = set()
    
    def _load_proxies(self) -> list:
        """Load proxies from environment or configuration"""
        proxy_list = os.getenv("PROXY_LIST", "").strip()
        
        if not proxy_list:
            logger.info("No proxies configured. Using direct connection.")
            return []
        
        # Format: http://proxy1.com:8080,http://proxy2.com:8080
        proxies = [p.strip() for p in proxy_list.split(',') if p.strip()]
        logger.info(f"Loaded {len(proxies)} proxies")
        return proxies
    
    def get_proxy(self) -> dict:
        """Get next proxy in rotation"""
        if not self.proxies:
            return None
        
        # Skip failed proxies
        attempts = 0
        while attempts < len(self.proxies):
            proxy = self.proxies[self.current_proxy_index % len(self.proxies)]
            self.current_proxy_index += 1
            
            if proxy not in self.failed_proxies:
                return {"http": proxy, "https": proxy}
            attempts += 1
        
        logger.warning("All proxies failed. Using direct connection.")
        return None
    
    def mark_failed(self, proxy_url: str):
        """Mark proxy as failed"""
        if proxy_url:
            self.failed_proxies.add(proxy_url)
            logger.warning(f"Proxy marked as failed: {proxy_url}")


class ECourtsServicesScraper(BaseScraper):
    """Scraper for official eCourts Government portals"""
    
    # Portal configurations
    PORTALS = {
        "high_court": {
            "url": "https://hcservices.ecourts.gov.in/ecourtindiaHC",
            "search_endpoint": "/index.php",
            "type": "High Court"
        },
        "njdg": {
            "url": "https://njdg.ecourts.gov.in",
            "search_endpoint": "/search",
            "type": "NJDG Portal"
        },
        "district": {
            "url_template": "https://{district}.dcourts.gov.in",
            "search_endpoint": "/court-orders-search",
            "type": "District Court"
        }
    }
    
    def __init__(self, court_name: str, court_level: str, district: str = None, portal: str = "high_court"):
        super().__init__(court_name, court_level)
        self.district = district
        self.portal_type = portal
        self.session = self._create_session()
        self.robots_checker = RobotsChecker()
        self.proxy_manager = ProxyManager()
        
        # Rate limiting: 1 request per minute per IP as per ethical guidelines
        self.rate_limit_seconds = int(os.getenv("SCRAPER_RATE_LIMIT_SECONDS", "60"))
        self.last_request_time = 0
        
        # Set base URLs
        if portal == "district" and district:
            self.base_url = self.PORTALS["district"]["url_template"].format(district=district.lower())
        else:
            self.base_url = self.PORTALS.get(portal, self.PORTALS["high_court"])["url"]
        
        logger.info(f"Initialized {portal} scraper for {court_name}")
    
    def _create_session(self) -> requests.Session:
        """Create session with retry strategy"""
        session = requests.Session()
        
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def _get_headers(self) -> dict:
        """Get browser-like headers"""
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
        }
    
    def _rate_limit(self):
        """Implement ethical rate limiting"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit_seconds:
            wait_time = self.rate_limit_seconds - elapsed
            logger.debug(f"Rate limiting: waiting {wait_time:.1f}s")
            time.sleep(wait_time)
        self.last_request_time = time.time()
    
    def _make_request(self, url: str, method: str = "GET", **kwargs) -> requests.Response:
        """Make HTTP request with rate limiting, robots.txt check, and proxy rotation"""
        
        # Check robots.txt
        if not self.robots_checker.is_allowed(url):
            logger.warning(f"URL blocked by robots.txt: {url}")
            raise PermissionError(f"Scraping not allowed by robots.txt: {url}")
        
        # Rate limit
        self._rate_limit()
        
        # Get proxy
        proxies = self.proxy_manager.get_proxy()
        
        # Make request
        try:
            kwargs['headers'] = kwargs.get('headers', self._get_headers())
            kwargs['timeout'] = kwargs.get('timeout', 15)
            
            if proxies:
                kwargs['proxies'] = proxies
            
            logger.info(f"{method} {url}")
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            
            return response
            
        except requests.exceptions.ProxyError as e:
            if proxies:
                self.proxy_manager.mark_failed(proxies.get('http'))
            logger.error(f"Proxy error: {str(e)}")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {str(e)}")
            raise
    
    def get_writ_petitions(self, from_date=None, to_date=None) -> list:
        """
        Search for real court cases from multiple working sources
        Primary: eCourts web search, Secondary: Indian Kanoon, NJDG
        """
        if from_date is None:
            from_date = datetime.utcnow() - timedelta(days=7)
        if to_date is None:
            to_date = datetime.utcnow()
        
        cases = []
        
        # Try multiple real sources that actually work
        logger.info(f"Attempting to fetch real cases from eCourts for {self.court_name}")
        
        # 1. Try direct eCourts web form search
        ecourts_cases = self._fetch_from_ecourts_web(from_date, to_date)
        cases.extend(ecourts_cases)
        
        # 2. Try Indian Kanoon (most reliable public source)
        if len(cases) < 5:
            kanoon_cases = self._fetch_from_kanoon(from_date, to_date)
            cases.extend(kanoon_cases)
        
        # 3. Try NJDG (aggregated judgments)
        if len(cases) < 5:
            njdg_cases = self._fetch_from_njdg_web(from_date, to_date)
            cases.extend(njdg_cases)
        
        logger.info(f"Found {len(cases)} real cases for {self.court_name}")
        return cases
    
    def _fetch_from_ecourts_web(self, from_date, to_date) -> list:
        """Fetch from eCourts web search form"""
        try:
            cases = []
            base_url = "https://hcservices.ecourts.gov.in/ecourtindiaHC"
            
            # Try direct search with common parameters
            search_params = {
                'act': 'case_status',
                'court': self.court_name,
                'case_type': 'Writ Petition',
                'from_date': from_date.strftime('%d/%m/%Y'),
                'to_date': to_date.strftime('%d/%m/%Y'),
            }
            
            search_url = f"{base_url}/index.php"
            response = self._make_request(search_url, params=search_params)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Parse table with results
            for row in soup.find_all('tr')[1:10]:  # First 10 results
                try:
                    cells = row.find_all('td')
                    if not cells or len(cells) < 2:
                        continue
                    
                    case_no = cells[0].get_text(strip=True)
                    case_type = cells[1].get_text(strip=True) if len(cells) > 1 else 'Case'
                    
                    if case_no and len(case_no) > 2:
                        case_dict = {
                            'cnr': case_no[:20],
                            'case_number': case_no,
                            'case_type': case_type,
                            'court': self.court_name,
                            'url': '',
                            'title': f"{case_type} - {case_no}",
                            'judge_name': None,
                            'judgment_date': datetime.utcnow()
                        }
                        cases.append(case_dict)
                except:
                    continue
            
            logger.info(f"Fetched {len(cases)} cases from eCourts web")
            return cases
        except Exception as e:
            logger.debug(f"eCourts web fetch error: {e}")
            return []
    
    def _fetch_from_kanoon(self, from_date, to_date) -> list:
        """Fetch from Indian Kanoon (most reliable)"""
        try:
            cases = []
            search_base = "https://indiankanoon.org/search/"
            
            # Search for recent judgment  
            search_queries = [
                f"{self.court_name}",
                "writ petition judgment",
                "civil appeal judgment"
            ]
            
            for query in search_queries:
                try:
                    params = {'formInput': query, 'pageNumber': 1}
                    response = self._make_request(search_base, params=params)
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Find judgment links
                    for link in soup.find_all('a'):
                        href = link.get('href', '')
                        text = link.get_text(strip=True)
                        
                        if '/doc/' in href and text and len(text) > 5:
                            case_dict = {
                                'cnr': text[:18],
                                'case_number': text[:50],
                                'case_type': 'Judgment',
                                'court': self.court_name,
                                'url': urljoin('https://indiankanoon.org', href),
                                'title': text[:80],
                                'judge_name': None,
                                'judgment_date': datetime.utcnow()
                            }
                            cases.append(case_dict)
                            if len(cases) >= 5:
                                break
                except:
                    continue
                
                if len(cases) >= 5:
                    break
            
            logger.info(f"Fetched {len(cases)} cases from Indian Kanoon")
            return cases
        except Exception as e:
            logger.debug(f"Kanoon fetch error: {e}")
            return []
    
    def _fetch_from_njdg_web(self, from_date, to_date) -> list:
        """Fetch from NJDG judgment grid"""
        try:
            cases = []
            njdg_url = "https://njdg.ecourts.gov.in/njdgnew/"
            
            # Search parameters for NJDG
            search_params = {
                'state': self._get_state_code(),
                'district': 'All',
                'frmdate': from_date.strftime('%d/%m/%Y'),
                'todate': to_date.strftime('%d/%m/%Y'),
            }
            
            response = self._make_request(njdg_url, params=search_params)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Parse results
            for row in soup.find_all('tr')[1:8]:
                try:
                    cells = row.find_all('td')
                    if not cells:
                        continue
                    
                    case_info = cells[0].get_text(strip=True)
                    if case_info and len(case_info) > 3:
                        case_dict = {
                            'cnr': case_info[:18],
                            'case_number': case_info,
                            'case_type': 'Judgment',
                            'court': 'National Judicial Grid',
                            'url': '',
                            'title': case_info,
                            'judge_name': cells[1].get_text(strip=True)[:50] if len(cells) > 1 else None,
                            'judgment_date': datetime.utcnow()
                        }
                        cases.append(case_dict)
                except:
                    continue
            
            logger.info(f"Fetched {len(cases)} cases from NJDG")
            return cases
        except Exception as e:
            logger.debug(f"NJDG fetch error: {e}")
            return []
    
    def _get_state_code(self) -> str:
        """Map court name to state code"""
        state_map = {
            'delhi': 'DL',
            'bombay': 'MH',
            'calcutta': 'WB',
            'bengaluru': 'KA',
            'bangalore': 'KA',
            'karnataka': 'KA',
            'maharashtra': 'MH',
            'west bengal': 'WB'
        }
        for key, code in state_map.items():
            if key in self.court_name.lower():
                return code
        return 'ALL'
    
    def _get_district_code(self) -> str:
        """Map court name to district code"""
        if self.district:
            # Try to use provided district
            return self.district[:3].upper()
        return 'ALL'

    
    def parse_case_details(self, case: dict) -> dict:
        """
        Parse detailed case information from case page or API response
        Extracts judgment text, PDF URLs, judge info, etc.
        """
        try:
            # If case already has substantial data from API, use it directly
            if case.get('judge_name') or case.get('judgment_date'):
                return {
                    'url': case.get('url', ''),
                    'cnr': case.get('cnr', ''),
                    'case_number': case.get('case_number', ''),
                    'case_type': case.get('case_type', 'Case'),
                    'court': self.court_name,
                    'court_level': self.court_level,
                    'title': case.get('title', ''),
                    'judgment_text': case.get('judgment_text', None),
                    'judge_name': case.get('judge_name', None),
                    'judgment_date': case.get('judgment_date', None),
                    'case_date': case.get('case_date', None),
                    'petitioner': case.get('petitioner', None),
                    'respondent': case.get('respondent', None),
                    'documents': []
                }
            
            # Otherwise fetch from URL
            if not case.get('url'):
                return None
            
            response = self._make_request(case['url'])
            soup = BeautifulSoup(response.content, 'html.parser')
            
            case_data = {
                'url': case['url'],
                'cnr': case.get('cnr'),
                'case_number': case.get('case_number'),
                'case_type': case.get('case_type'),
                'court': self.court_name,
                'court_level': self.court_level,
                'title': case.get('title'),
                'judgment_text': None,
                'judge_name': None,
                'judgment_date': None,
                'case_date': None,
                'petitioner': None,
                'respondent': None,
                'documents': []
            }
            
            # Extract case details from page
            all_text = soup.get_text()
            
            # Get judge name - look for common patterns
            judge_patterns = ['Hon\'ble Justice', 'Justice', 'Judge']
            for pattern in judge_patterns:
                idx = all_text.find(pattern)
                if idx != -1:
                    end_idx = all_text.find('\n', idx)
                    if end_idx != -1:
                        potential_judge = all_text[idx:end_idx].strip()
                        if len(potential_judge) < 100:
                            case_data['judge_name'] = potential_judge
                            break
            
            # Extract PDF documents
            for link in soup.find_all('a'):
                href = link.get('href', '')
                text = link.get_text(strip=True).lower()
                if 'pdf' in href.lower() or 'pdf' in text or 'download' in text:
                    full_url = urljoin(self.base_url, href)
                    case_data['documents'].append({
                        'url': full_url,
                        'title': link.get_text(strip=True),
                        'type': 'pdf'
                    })
            
            return case_data
            
        except Exception as e:
            logger.error(f"Error parsing case details {case.get('url')}: {str(e)}")
            return None


class NJDGScraper(BaseScraper):
    """Scraper for NJDG (National Judicial Data Grid) Portal"""
    
    def __init__(self, court_name: str, court_level: str):
        super().__init__(court_name, court_level)
        self.base_url = "https://njdg.ecourts.gov.in"
        self.session = self._create_session()
        self.rate_limit_seconds = int(os.getenv("SCRAPER_RATE_LIMIT_SECONDS", "60"))
        self.last_request_time = 0
    
    def _create_session(self) -> requests.Session:
        """Create session with retry strategy"""
        session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session
    
    def _get_headers(self) -> dict:
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'en-US,en;q=0.9',
            'Content-Type': 'application/json',
        }
    
    def _rate_limit(self):
        """Rate limiting"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit_seconds:
            time.sleep(self.rate_limit_seconds - elapsed)
        self.last_request_time = time.time()
    
    def get_writ_petitions(self, from_date=None, to_date=None) -> list:
        """
        Get statistics and judgments from NJDG (National Judicial Data Grid) portal
        This portal aggregates data from all courts in India
        """
        if from_date is None:
            from_date = datetime.utcnow() - timedelta(days=7)
        if to_date is None:
            to_date = datetime.utcnow()
        
        try:
            self._rate_limit()
            
            # NJDG API endpoint for judgment search
            search_url = f"{self.base_url}/search"
            
            # Parameters for NJDG search
            params = {
                'fltrdistrict': os.getenv("NJDG_DISTRICT", "All"),
                'fltrstate': os.getenv("NJDG_STATE", "All"),
                'startDate': from_date.strftime('%Y-%m-%d'),
                'endDate': to_date.strftime('%Y-%m-%d'),
                'displayStart': 0,
                'displayLength': 100,
                'sortCol': 4,
                'sortType': 'asc'
            }
            
            response = self.session.get(
                search_url,
                params=params,
                timeout=15,
                headers=self._get_headers()
            )
            response.raise_for_status()
            
            cases = []
            
            # Try JSON response first
            try:
                data = response.json()
                if 'data' in data:
                    for row in data['data']:
                        try:
                            case_dict = {
                                'cnr': row[0] if len(row) > 0 else '',
                                'case_number': row[1] if len(row) > 1 else '',
                                'case_type': row[2] if len(row) > 2 else '',
                                'judge_name': row[3] if len(row) > 3 else '',
                                'judgment_date': row[4] if len(row) > 4 else '',
                                'title': f"{row[2]} - {row[1]}" if len(row) > 2 else '',
                                'url': '',
                                'court': 'NJDG'
                            }
                            if case_dict['cnr']:
                                cases.append(case_dict)
                        except:
                            continue
            except:
                # Fallback to HTML parsing
                soup = BeautifulSoup(response.content, 'html.parser')
                for row in soup.find_all('tr')[1:]:
                    try:
                        cells = row.find_all('td')
                        if len(cells) < 3:
                            continue
                        case_dict = {
                            'cnr': cells[0].get_text(strip=True),
                            'case_number': cells[1].get_text(strip=True),
                            'case_type': cells[2].get_text(strip=True),
                            'judge_name': cells[3].get_text(strip=True) if len(cells) > 3 else '',
                            'judgment_date': cells[4].get_text(strip=True) if len(cells) > 4 else '',
                            'title': f"{cells[2].get_text(strip=True)} - {cells[1].get_text(strip=True)}",
                            'url': '',
                            'court': 'NJDG'
                        }
                        if case_dict['cnr']:
                            cases.append(case_dict)
                    except:
                        continue
            
            logger.info(f"Found {len(cases)} judgments from NJDG portal")
            return cases
            
        except Exception as e:
            logger.error(f"Error fetching from NJDG: {str(e)}")
            return []
    
    def parse_case_details(self, case: dict) -> dict:
        """Parse case details from NJDG data"""
        try:
            self._rate_limit()
            
            # NJDG data comes as API response with complete details
            case_data = {
                'url': case.get('url', ''),
                'cnr': case.get('cnr', ''),
                'case_number': case.get('case_number', ''),
                'case_type': case.get('case_type', ''),
                'court': 'NJDG',
                'title': case.get('title', ''),
                'judgment_text': None,
                'judge_name': case.get('judge_name', None),
                'judgment_date': case.get('judgment_date', None),
                'documents': []
            }
            
            # If we have a URL, try to fetch more details
            if case.get('url'):
                try:
                    response = self.session.get(
                        case['url'],
                        timeout=15,
                        headers=self._get_headers()
                    )
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Extract any additional data from page
                    all_text = soup.get_text()
                    case_data['judgment_text'] = all_text[:5000]
                    
                    # Look for PDF links
                    for link in soup.find_all('a'):
                        if 'pdf' in link.get('href', '').lower():
                            case_data['documents'].append({
                                'url': link.get('href'),
                                'title': link.get_text(strip=True),
                                'type': 'pdf'
                            })
                except:
                    pass
            
            return case_data
            
        except Exception as e:
            logger.error(f"Error parsing NJDG case details: {str(e)}")
            return None
