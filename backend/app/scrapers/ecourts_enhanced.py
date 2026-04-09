"""
Enhanced eCourts Scraper - Pulls from official government judicial portals
Targets:
  - bengaluru.dcourts.gov.in (Bengaluru District Court)
  - services.ecourts.gov.in (eCourts Services Portal)
  - njdg.ecourts.gov.in (National Judgment Grid)
  
This scraper uses multiple strategies to extract real court data.
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import logging
import time
import re
from urllib.parse import urljoin, quote
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class ECourtsDataExtractor(BaseScraper):
    """Extract real court data from official eCourts portals"""
    
    def __init__(self, court_name: str, court_level: str, region: str = "bengaluru"):
        super().__init__(court_name, court_level)
        self.region = region.lower()
        self.session = self._create_session()
        self.rate_limit = 2  # seconds between requests
    
    def _create_session(self) -> requests.Session:
        """Create resilient session"""
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
        """Browser-like headers"""
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
    
    def _safe_request(self, url: str, **kwargs) -> requests.Response:
        """Make safe HTTP request with rate limiting"""
        time.sleep(self.rate_limit)
        try:
            kwargs['headers'] = self._get_headers()
            kwargs['timeout'] = 15
            response = self.session.get(url, **kwargs)
            response.raise_for_status()
            return response
        except Exception as e:
            logger.error(f"Request failed for {url}: {e}")
            return None
    
    def _extract_case_numbers(self, text: str) -> list:
        """Extract case numbers from text"""
        # Pattern for Indian case numbers
        patterns = [
            r'[A-Z]+\s*\d+/\d{4}',  # WP 123/2024
            r'[A-Z]+-?\d+\(\w+\)\d+',  # AP-123(W)2023
            r'CNR\s?[A-Z]{4}\d{10}',  # CNR DELHC0123456789
        ]
        
        cases = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            cases.extend(matches)
        
        return list(set(cases))
    
    def scrape_bengaluru_district_court(self, from_date=None, to_date=None) -> list:
        """Scrape from Bengaluru District Court portal"""
        try:
            if from_date is None:
                from_date = datetime.utcnow() - timedelta(days=7)
            if to_date is None:
                to_date = datetime.utcnow()
            
            cases = []
            base_url = "https://bengaluru.dcourts.gov.in"
            
            # Try different search endpoints
            endpoints = [
                "/court-orders-search-by-case-number/",
                "/court-orders/",
                "/judgment-search/",
            ]
            
            for endpoint in endpoints:
                try:
                    url = urljoin(base_url, endpoint)
                    logger.info(f"Scraping: {url}")
                    
                    response = self._safe_request(url)
                    if not response:
                        continue
                    
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Look for case tables or divs
                    tables = soup.find_all('table')
                    for table in tables:
                        rows = table.find_all('tr')[1:]  # Skip header
                        for row in rows[:20]:  # Limit to 20 per table
                            try:
                                cells = row.find_all(['td', 'th'])
                                if not cells:
                                    continue
                                
                                row_text = ' '.join([c.get_text(strip=True) for c in cells])
                                case_numbers = self._extract_case_numbers(row_text)
                                
                                if case_numbers:
                                    for case_no in case_numbers[:1]:  # First match per row
                                        case_dict = {
                                            'cnr': case_no[:20],
                                            'case_number': case_no,
                                            'case_type': 'District Court Case',
                                            'court': "Bengaluru District Court",
                                            'url': url,
                                            'title': f"Case {case_no}",
                                            'judge_name': self._extract_judge_name(row_text),
                                            'judgment_date': self._extract_date(row_text) or datetime.utcnow(),
                                            'petitioner': None,
                                            'respondent': None,
                                        }
                                        cases.append(case_dict)
                            except Exception as e:
                                logger.debug(f"Row parsing error: {e}")
                                continue
                    
                    if len(cases) > 5:
                        break
                
                except Exception as e:
                    logger.debug(f"Endpoint {endpoint} failed: {e}")
                    continue
            
            logger.info(f"Bengaluru DC: Found {len(cases)} cases")
            return cases
        
        except Exception as e:
            logger.error(f"Bengaluru scraper error: {e}")
            return []
    
    def scrape_njdg_portal(self, from_date=None, to_date=None) -> list:
        """Scrape from National Judgment Data Grid (NJDG)"""
        try:
            if from_date is None:
                from_date = datetime.utcnow() - timedelta(days=7)
            if to_date is None:
                to_date = datetime.utcnow()
            
            cases = []
            base_url = "https://njdg.ecourts.gov.in"
            
            endpoints = [
                "/njdgnew/",
                "/search",
                "/njdgstatistics/",
            ]
            
            for endpoint in endpoints:
                try:
                    url = urljoin(base_url, endpoint)
                    logger.info(f"Scraping: {url}")
                    
                    response = self._safe_request(url)
                    if not response:
                        continue
                    
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Extract all text and look for case info
                    text = soup.get_text()
                    case_numbers = self._extract_case_numbers(text)
                    
                    # Also look for links that might be case documents
                    for link in soup.find_all('a', href=True):
                        href = link.get('href', '')
                        link_text = link.get_text(strip=True)
                        
                        if any(keyword in href.lower() for keyword in ['judgment', 'case', 'order', 'pdf']):
                            if link_text and len(link_text) > 3:
                                case_dict = {
                                    'cnr': link_text[:20],
                                    'case_number': link_text[:50],
                                    'case_type': 'Judgment',
                                    'court': self.court_name,
                                    'url': urljoin(base_url, href),
                                    'title': link_text[:80],
                                    'judge_name': None,
                                    'judgment_date': datetime.utcnow(),
                                    'petitioner': None,
                                    'respondent': None,
                                }
                                cases.append(case_dict)
                                if len(cases) >= 15:
                                    break
                    
                    if len(cases) > 5:
                        break
                
                except Exception as e:
                    logger.debug(f"NJDG endpoint {endpoint} failed: {e}")
                    continue
            
            logger.info(f"NJDG: Found {len(cases)} cases")
            return cases
        
        except Exception as e:
            logger.error(f"NJDG scraper error: {e}")
            return []
    
    def scrape_ecourts_services(self, from_date=None, to_date=None) -> list:
        """Scrape from eCourts Services Portal"""
        try:
            if from_date is None:
                from_date = datetime.utcnow() - timedelta(days=7)
            if to_date is None:
                to_date = datetime.utcnow()
            
            cases = []
            base_url = "https://services.ecourts.gov.in"
            
            # Try multiple endpoints
            endpoints = [
                "/ecourtindiaHC/",
                "/ecourtindia/",
                "/",
            ]
            
            for endpoint in endpoints:
                try:
                    url = urljoin(base_url, endpoint)
                    logger.info(f"Scraping: {url}")
                    
                    response = self._safe_request(url)
                    if not response:
                        continue
                    
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Look for case information in tables
                    tables = soup.find_all('table')
                    for table in tables:
                        rows = table.find_all('tr')[1:]
                        for row in rows[:20]:
                            try:
                                cells = row.find_all(['td', 'th'])
                                if len(cells) < 2:
                                    continue
                                
                                row_text = ' '.join([c.get_text(strip=True) for c in cells])
                                
                                # Extract linked case numbers
                                for link in row.find_all('a'):
                                    link_text = link.get_text(strip=True)
                                    link_href = link.get('href', '')
                                    
                                    if link_text and len(link_text) > 2:
                                        case_dict = {
                                            'cnr': link_text[:20],
                                            'case_number': link_text[:50],
                                            'case_type': 'High Court Case',
                                            'court': self.court_name,
                                            'url': urljoin(base_url, link_href) if link_href else url,
                                            'title': link_text[:80],
                                            'judge_name': self._extract_judge_name(row_text),
                                            'judgment_date': self._extract_date(row_text) or datetime.utcnow(),
                                            'petitioner': None,
                                            'respondent': None,
                                        }
                                        cases.append(case_dict)
                                        if len(cases) >= 15:
                                            break
                                
                                if len(cases) >= 15:
                                    break
                            except Exception as e:
                                logger.debug(f"Row parsing error: {e}")
                                continue
                    
                    if len(cases) > 5:
                        break
                
                except Exception as e:
                    logger.debug(f"eCourts endpoint {endpoint} failed: {e}")
                    continue
            
            logger.info(f"eCourts Services: Found {len(cases)} cases")
            return cases
        
        except Exception as e:
            logger.error(f"eCourts Services scraper error: {e}")
            return []
    
    def _extract_judge_name(self, text: str) -> str:
        """Extract judge name from text if present"""
        try:
            patterns = [r'(?:Hon\'?ble|J\.|Judge)\s+([A-Z][a-zA-Z\s\.]+)', ]
            for pattern in patterns:
                match = re.search(pattern, text)
                if match:
                    return match.group(1).strip()
        except:
            pass
        return None
    
    def _extract_date(self, text: str) -> datetime:
        """Extract date from text"""
        try:
            patterns = [
                r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})',  # DD/MM/YYYY
                r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})',  # YYYY/MM/DD
            ]
            
            for pattern in patterns:
                match = re.search(pattern, text)
                if match:
                    groups = match.groups()
                    try:
                        if int(groups[2]) > 31:  # Year first
                            return datetime(int(groups[0]), int(groups[1]), int(groups[2]))
                        else:
                            return datetime(int(groups[2]), int(groups[1]), int(groups[0]))
                    except:
                        pass
        except:
            pass
        return None
    
    def get_writ_petitions(self, from_date=None, to_date=None) -> list:
        """Fetch writ petitions - required by BaseScraper"""
        return self.scrape(from_date, to_date)
    
    def parse_case_details(self, case_url):
        """Parse case details - required by BaseScraper"""
        # For now, return the case as-is since we already have the data
        return case_url if isinstance(case_url, dict) else {'url': case_url}
    
    def scrape(self, from_date=None, to_date=None) -> list:
        """Main scrape method - aggregates from multiple sources"""
        all_cases = []
        
        # Scrape from all sources
        logger.info(f"Starting multi-source scrape for {self.court_name}")
        
        all_cases.extend(self.scrape_bengaluru_district_court(from_date, to_date))
        time.sleep(2)  # Rate limit between sources
        
        all_cases.extend(self.scrape_njdg_portal(from_date, to_date))
        time.sleep(2)
        
        all_cases.extend(self.scrape_ecourts_services(from_date, to_date))
        
        # Remove duplicates by case number
        seen = set()
        unique_cases = []
        for case in all_cases:
            key = case.get('case_number', '').upper()
            if key and key not in seen:
                seen.add(key)
                unique_cases.append(case)
        
        logger.info(f"Total unique cases collected: {len(unique_cases)}")
        return unique_cases


class NJDGScraper(BaseScraper):
    """Specialized NJDG scraper for judgment grid"""
    def __init__(self, court_name: str, court_level: str):
        super().__init__(court_name, court_level)
        self.extractor = ECourtsDataExtractor(court_name, court_level)
    
    def get_writ_petitions(self, from_date=None, to_date=None) -> list:
        """Get cases from NJDG"""
        return self.scrape(from_date, to_date)
    
    def parse_case_details(self, case_url):
        """Parse case details"""
        return case_url if isinstance(case_url, dict) else {'url': case_url}
    
    def scrape(self, from_date=None, to_date=None) -> list:
        return self.extractor.scrape_njdg_portal(from_date, to_date)
