"""
Enhanced scraper for Indian Kanoon with better anti-bot detection handling
This version includes:
- Better browser-like headers
- Session management with retries
- Rate limiting and delays
- Better error detection
"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import logging
import time
import os
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)

class EnhancedIndianKanoonScraper(BaseScraper):
    """Enhanced scraper with better anti-bot handling"""
    
    def __init__(self, court_name: str, court_level: str):
        super().__init__(court_name, court_level)
        self.base_url = "https://indiankanoon.org"
        self.search_url = "https://indiankanoon.org/search"
        self.session = self._create_session()
        self.request_delay = 1  # seconds between requests
        self.last_request_time = 0
        
    def _create_session(self):
        """Create a session with retry strategy"""
        session = requests.Session()
        
        # Retry strategy for network errors
        retry_strategy = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def _get_headers(self):
        """Get more realistic browser headers"""
        return {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            'Referer': 'https://indiankanoon.org/'
        }
    
    def _rate_limit(self):
        """Implement rate limiting between requests"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.request_delay:
            time.sleep(self.request_delay - elapsed)
        self.last_request_time = time.time()
    
    def _check_for_captcha(self, html_content):
        """Check if response contains CAPTCHA page"""
        captcha_indicators = [
            'are you a robot',
            'recaptcha',
            'challenge',
            'cloudflare',
            'proof of work',
        ]
        
        html_lower = html_content.lower()
        for indicator in captcha_indicators:
            if indicator in html_lower:
                return True
        return False
    
    def get_writ_petitions(self, from_date=None, to_date=None):
        """
        Search for writ petitions with better error handling
        """
        if from_date is None:
            from_date = datetime.utcnow() - timedelta(days=1)
        if to_date is None:
            to_date = datetime.utcnow()
            
        max_results = max(1, int(os.getenv("IK_SEARCH_MAX_RESULTS", "100")))
        query_template = os.getenv("IK_SEARCH_QUERY_TEMPLATE", "\"{court}\"")
        search_query = query_template.format(court=self.court_name)
        
        try:
            self._rate_limit()
            
            response = self.session.get(
                self.search_url,
                params={
                    'q': search_query,
                    'type': 'judgement'
                },
                timeout=15,
                headers=self._get_headers()
            )
            
            # Check for CAPTCHA
            if self._check_for_captcha(response.text):
                logger.warning(f"CAPTCHA detected for {self.court_name}. Waiting 30 seconds before retry...")
                time.sleep(30)
                return self.get_writ_petitions(from_date, to_date)  # Retry
            
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            cases = []
            
            # Extract case links from search results
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
                        if len(cases) >= max_results:
                            break
                except Exception as e:
                    logger.warning(f"Error extracting case link: {str(e)}")
                    continue
            
            logger.info(f"Found {len(cases)} writ petitions for {self.court_name}")
            return cases
            
        except requests.exceptions.Timeout:
            logger.error(f"Timeout while fetching writ petitions for {self.court_name}")
            return []
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error while fetching writ petitions for {self.court_name}")
            return []
        except Exception as e:
            logger.error(f"Error fetching writ petitions for {self.court_name}: {str(e)}")
            return []
    
    def parse_case_details(self, case):
        """
        Parse individual case details with rate limiting
        """
        try:
            self._rate_limit()
            
            response = self.session.get(
                case['url'],
                timeout=15,
                headers=self._get_headers()
            )
            
            # Check for CAPTCHA
            if self._check_for_captcha(response.text):
                logger.warning(f"CAPTCHA detected while parsing case: {case['url']}")
                raise Exception("CAPTCHA encountered")
            
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract case information
            case_data = {
                'url': case['url'],
                'title': case['title'],
                'case_type': 'Writ Petition',
                'court': self.court_name,
                'court_level': self.court_level,
                'judgment_text': None,
                'judge_name': None,
                'judgment_date': datetime.utcnow(),
                'case_date': datetime.utcnow()
            }
            
            # Try to extract document number
            doc_match = case['url'].split('/')
            if 'doc' in doc_match:
                case_data['doc_id'] = doc_match[doc_match.index('doc') + 1]
            
            # Extract judgment text
            judgment_div = soup.find('div', class_='judgement')
            if judgment_div:
                case_data['judgment_text'] = judgment_div.get_text(strip=True)[:1000]
            
            # Extract case number
            case_number_elem = soup.find('div', class_='case-number')
            if case_number_elem:
                case_data['case_number'] = case_number_elem.get_text(strip=True)
            else:
                case_data['case_number'] = f"WP-{case.get('title', 'unknown')[:20]}"
            
            # Try to find judge name
            judge_patterns = ['Hon\'ble', 'Justice', 'Honourable']
            text_content = soup.get_text()
            for pattern in judge_patterns:
                if pattern in text_content:
                    idx = text_content.find(pattern)
                    if idx != -1:
                        case_data['judge_name'] = text_content[idx:idx+100].split('\n')[0]
                        break
            
            return case_data
            
        except Exception as e:
            logger.error(f"Error parsing case details from {case['url']}: {str(e)}")
            raise
