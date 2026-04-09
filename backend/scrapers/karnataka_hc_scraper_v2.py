"""
Karnataka High Court Judgment Scraper - COMPREHENSIVE V2
Dynamically extracts ALL 73+ case types from the website
Scrapes only 2026 cases for complete coverage

From: https://judiciary.karnataka.gov.in/hckn/index.php/browsejudgments
"""

import logging
import json
from typing import List, Dict, Optional, Set, Tuple
from datetime import datetime
from urllib.parse import urljoin
import time
import asyncio

logger = logging.getLogger(__name__)

# Base URLs
BASE_URL = "https://judiciary.karnataka.gov.in"
JUDGMENTS_BASE = f"{BASE_URL}/hckn/"
BROWSE_JUDGMENTS_URL = f"{JUDGMENTS_BASE}index.php/browsejudgments"

# Configuration
TARGET_YEAR = 2026
MAX_PAGES_PER_TYPE = 200  # High limit to capture all cases
TIMEOUT_PER_PAGE = 20000  # 20 seconds per page


class KarnatakaHCComprehensiveScraper:
    """
    Comprehensive scraper for all 73+ case types from Karnataka HC
    Only 2026 cases
    """
    
    def __init__(self):
        self.session = self._create_session()
        self.all_judgments = []
        self.case_types_found = set()
        
    def _create_session(self):
        """Create requests session with proper headers"""
        import requests
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        return session
    
    async def scrape_all_2026_cases(self) -> List[Dict]:
        """
        Main scraping method:
        1. Dynamically discover all available case types
        2. Scrape each type for 2026 cases
        3. Return comprehensive list
        """
        logger.info("\n" + "="*80)
        logger.info("🔍 KARNATAKA HC COMPREHENSIVE SCRAPER - 2026 CASES ONLY")
        logger.info("="*80)
        
        start_time = datetime.now()
        
        try:
            from playwright.async_api import async_playwright
            
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                try:
                    # Step 1: Get all available case types
                    logger.info("\n📋 STEP 1: Discovering all available case types...")
                    case_types = await self._get_all_case_types(page)
                    logger.info(f"✅ Found {len(case_types)} case types:")
                    for ct in sorted(case_types)[:10]:
                        logger.info(f"   • {ct}")
                    if len(case_types) > 10:
                        logger.info(f"   ... and {len(case_types) - 10} more types")
                    
                    # Step 2: Scrape each type for 2026
                    logger.info(f"\n📋 STEP 2: Scraping all {len(case_types)} types for 2026 cases...")
                    
                    cases_by_type = {}
                    for i, case_type in enumerate(sorted(case_types), 1):
                        logger.info(f"\n   [{i}/{len(case_types)}] Scraping {case_type.upper()}...")
                        
                        cases = await self._scrape_case_type_2026(page, case_type)
                        if cases:
                            cases_by_type[case_type] = cases
                            logger.info(f"      ✅ Found {len(cases)} {case_type.upper()} cases")
                            self.all_judgments.extend(cases)
                        else:
                            logger.info(f"      ⚠️  No 2026 cases found")
                        
                        # Be nice to the server
                        await asyncio.sleep(0.5)
                    
                    logger.info(f"\n✅ Scanning complete!")
                    logger.info(f"   Total cases collected: {len(self.all_judgments)}")
                    logger.info(f"   Case types with 2026 data: {len(cases_by_type)}")
                    
                    # Summary
                    logger.info(f"\n📊 Summary by Type:")
                    for case_type in sorted(cases_by_type.keys()):
                        count = len(cases_by_type[case_type])
                        logger.info(f"   {case_type.upper()}: {count} cases")
                    
                finally:
                    await browser.close()
            
            duration = (datetime.now() - start_time).total_seconds()
            logger.info(f"\n⏱️  Scraping took {duration:.1f} seconds")
            logger.info("="*80 + "\n")
            
            return self.all_judgments
            
        except Exception as e:
            logger.error(f"❌ Scraping failed: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    async def _get_all_case_types(self, page) -> Set[str]:
        """
        Dynamically extract all available case types from the browse judgments page
        """
        try:
            await page.goto(BROWSE_JUDGMENTS_URL, wait_until="networkidle", timeout=TIMEOUT_PER_PAGE)
            
            # Wait for the case type selector to load
            await page.wait_for_selector('select[name="type"]', timeout=10000)
            
            # Get all option values
            options = await page.locator('select[name="type"] >> option').all()
            
            case_types = set()
            for option in options:
                value = await option.get_attribute('value')
                text = await option.text_content()
                
                if value and value.strip() and value.lower() != 'select':
                    case_types.add(value.strip().lower())
                    
            logger.debug(f"Discovered case types: {case_types}")
            return case_types
            
        except Exception as e:
            logger.error(f"Error discovering case types: {e}")
            return set()
    
    async def _scrape_case_type_2026(self, page, case_type: str) -> List[Dict]:
        """
        Scrape all 2026 cases for a specific case type
        """
        cases = []
        page_num = 1
        
        try:
            await page.goto(BROWSE_JUDGMENTS_URL, timeout=TIMEOUT_PER_PAGE)
            await page.wait_for_selector('select[name="type"]', timeout=10000)
            
            # Select case type
            await page.select_option('select[name="type"]', case_type)
            await page.wait_for_load_state('networkidle')
            
            # Keep paginating until no more results or max pages reached
            while page_num <= MAX_PAGES_PER_TYPE:
                try:
                    # Try to go to next page if not first
                    if page_num > 1:
                        next_button = page.locator('a:has-text("Next")')
                        if await next_button.is_visible():
                            await next_button.click()
                            await page.wait_for_load_state('networkidle')
                        else:
                            break  # No more pages
                    
                    # Extract cases from current page
                    rows = await page.locator('table tbody tr').all()
                    
                    page_has_2026 = False
                    for row in rows:
                        cells = await row.locator('td').all()
                        
                        if len(cells) >= 5:
                            try:
                                date_text = await cells[0].text_content()
                                case_num = await cells[1].text_content()
                                
                                # Check if it's a 2026 case
                                if "2026" in str(date_text) or "2026" in str(case_num):
                                    page_has_2026 = True
                                    
                                    judgment_data = {
                                        "date_of_judgment": date_text.strip() if date_text else "",
                                        "title": case_num.strip() if case_num else "",
                                        "judges": (await cells[2].text_content()).strip() if len(cells) > 2 else "",
                                        "petitioner": (await cells[3].text_content()).strip() if len(cells) > 3 else "",
                                        "respondent": (await cells[4].text_content()).strip() if len(cells) > 4 else "",
                                    }
                                    
                                    # Try to get PDF link
                                    try:
                                        pdf_link = await cells[1].locator('a').get_attribute('href')
                                        if pdf_link:
                                            judgment_data["pdf_url"] = urljoin(BASE_URL, pdf_link)
                                    except:
                                        pass
                                    
                                    cases.append(judgment_data)
                            except Exception as cell_error:
                                logger.debug(f"Error extracting cell: {cell_error}")
                                continue
                    
                    # If no 2026 cases found on this page, might have already passed them
                    if not page_has_2026 and page_num > 1:
                        break
                    
                    page_num += 1
                    await asyncio.sleep(0.3)
                    
                except Exception as page_error:
                    logger.debug(f"Error on page {page_num}: {page_error}")
                    break
            
        except Exception as e:
            logger.error(f"Error scraping {case_type}: {e}")
        
        return cases
    
    def normalize_cases(self, raw_cases: List[Dict]) -> List[Dict]:
        """Normalize and clean case data"""
        normalized = []
        
        for case in raw_cases:
            try:
                # Extract case type from title
                case_type = self._extract_case_type(case.get("title", ""))
                
                # Parse date
                judgment_date = self._parse_date(case.get("date_of_judgment", ""))
                
                if not judgment_date or "2026" not in judgment_date:
                    continue  # Skip non-2026 cases
                
                normalized_case = {
                    "case_number": case.get("title", "").strip(),
                    "case_type": case_type,
                    "judgment_date": judgment_date,
                    "court_level": "High Court",
                    "judges": case.get("judges", "").strip(),
                    "petitioner": case.get("petitioner", "").strip(),
                    "respondent": case.get("respondent", "").strip(),
                    "status": "Decided",
                    "pdf_url": case.get("pdf_url", ""),
                    "source": "judiciary.karnataka.gov.in",
                    "scraped_at": datetime.now().isoformat()
                }
                
                if normalized_case["case_number"]:
                    normalized.append(normalized_case)
                    
            except Exception as e:
                logger.debug(f"Error normalizing case: {e}")
                continue
        
        return normalized
    
    def _parse_date(self, date_str: str) -> Optional[str]:
        """Parse date in various formats"""
        if not date_str:
            return None
        
        date_formats = [
            "%d-%m-%Y",
            "%d/%m/%Y",
            "%Y-%m-%d",
            "%d.%m.%Y",
            "%d %b %Y"
        ]
        
        date_str = str(date_str).strip()
        
        for fmt in date_formats:
            try:
                parsed = datetime.strptime(date_str, fmt)
                return parsed.isoformat()
            except ValueError:
                continue
        
        # If parsing fails but contains year, extract it
        if "2026" in date_str:
            return f"2026-01-01"  # Default to start of year if can't parse
        
        return None
    
    def _extract_case_type(self, case_title: str) -> str:
        """Extract case type from title"""
        if not case_title:
            return "OTHER"
        
        case_title = case_title.upper()
        
        # Check for known abbreviations first
        for case_code in ["WP", "CP", "WA", "FA", "RSA", "CAS"]:
            if case_code in case_title:
                return case_code
        
        # If not found, use first word
        words = case_title.split()
        if words:
            return words[0][:3].upper()
        
        return "OTHER"
    
    def save_to_json(self, filename: str) -> int:
        """Save scraped cases to JSON file"""
        try:
            # Normalize before saving
            normalized = self.normalize_cases(self.all_judgments)
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(normalized, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Saved {len(normalized)} cases to {filename}")
            return len(normalized)
        except Exception as e:
            logger.error(f"Error saving to JSON: {e}")
            return 0


async def scrape_comprehensive_2026() -> List[Dict]:
    """
    Main entry point - scrape all case types for 2026
    """
    scraper = KarnatakaHCComprehensiveScraper()
    
    # Scrape
    raw_cases = await scraper.scrape_all_2026_cases()
    
    # Normalize
    normalized_cases = scraper.normalize_cases(raw_cases)
    
    logger.info(f"\n✅ FINAL RESULT: {len(normalized_cases)} 2026 cases across all types")
    
    return normalized_cases


# For testing
if __name__ == "__main__":
    import asyncio
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Run scraper
    cases = asyncio.run(scrape_comprehensive_2026())
    
    # Save results
    scraper = KarnatakaHCComprehensiveScraper()
    scraper.all_judgments = cases
    scraper.save_to_json("/tmp/karnataka_hc_2026_complete.json")
    
    print(f"\n✅ Scraped {len(cases)} cases from all types for 2026")
