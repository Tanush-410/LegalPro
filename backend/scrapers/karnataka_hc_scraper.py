"""
Karnataka High Court Judgment Scraper
Extracts judgment data from https://judiciary.karnataka.gov.in

Flow:
  Judgements → Browse Judgements → Case Type (Writ, CP, WA, etc) → Pages (2024, 2025, 2026)
  
For each judgment, we extract:
  - Case Number
  - Judgment Date
  - Judge(s)
  - Petitioner
  - Respondent
  - Case Type (Writ, Civil Petition, etc.)
  - PDF Link
"""

import logging
import json
from typing import List, Dict, Optional
from datetime import datetime
from urllib.parse import urljoin
import time

logger = logging.getLogger(__name__)

# Judgment types available on the website
JUDGMENT_TYPES = [
    "cp",  # Civil Petition
    "wp",  # Writ Petition
    "wa",  # Writ Appeal
    "fa",  # First Appeal
    "rsa", # Regular Second Appeal
    "cas", # Case
]

# Base URLs
BASE_URL = "https://judiciary.karnataka.gov.in"
JUDGMENTS_BASE = f"{BASE_URL}/hckn/"
BROWSE_JUDGMENTS_URL = f"{JUDGMENTS_BASE}index.php/browsejudgments"


class KarnatakaHCJudgmentScraper:
    """Scrapes judgments from Karnataka High Court website"""
    
    def __init__(self):
        self.session = self._create_session()
        self.judgments = []
        
    def _create_session(self):
        """Create a requests session with proper headers"""
        import requests
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        return session
    
    def scrape_all_judgments(self, years: List[int] = None) -> List[Dict]:
        """
        Scrape all judgments for specified years
        
        Args:
            years: List of years to scrape (e.g., [2024, 2025, 2026])
        
        Returns:
            List of judgment dictionaries
        """
        if years is None:
            years = [2024, 2025, 2026]
        
        logger.info(f"🔍 Starting scrape for years: {years}")
        
        all_judgments = []
        
        for case_type in JUDGMENT_TYPES:
            logger.info(f"📋 Processing case type: {case_type.upper()}")
            
            for year in years:
                try:
                    judgments = self._scrape_case_type_year(case_type, year)
                    all_judgments.extend(judgments)
                    logger.info(f"   ✅ {case_type.upper()} {year}: {len(judgments)} judgments")
                except Exception as e:
                    logger.error(f"   ❌ Error scraping {case_type.upper()} {year}: {e}")
                    continue
                
                # Be nice to the server
                time.sleep(1)
        
        logger.info(f"\n✅ Total judgments scraped: {len(all_judgments)}")
        return all_judgments
    
    def _scrape_case_type_year(self, case_type: str, year: int) -> List[Dict]:
        """
        Scrape judgments for a specific case type and year
        
        Args:
            case_type: Type of case (cp, wp, wa, etc.)
            year: Year to scrape
        
        Returns:
            List of judgment dictionaries
        """
        judgments = []
        page = 1
        max_pages = 20  # Limit pages to avoid infinite loops
        
        while page <= max_pages:
            try:
                page_judgments = self._scrape_page(case_type, year, page)
                
                if not page_judgments:
                    break  # No more results
                
                judgments.extend(page_judgments)
                page += 1
                time.sleep(0.5)
                
            except Exception as e:
                logger.debug(f"   Error on page {page}: {e}")
                break
        
        return judgments
    
    def _scrape_page(self, case_type: str, year: int, page: int = 1) -> List[Dict]:
        """
        Scrape a single page of judgments
        
        The actual scraping will use Playwright or Selenium since the website
        likely uses JavaScript to load data dynamically
        """
        # This would be implemented with Playwright/Selenium
        # For now, returning sample structure
        
        try:
            # URL pattern based on website navigation
            url = f"{BROWSE_JUDGMENTS_URL}?type={case_type}&year={year}&page={page}"
            
            logger.debug(f"   Fetching: {url}")
            
            # In production, use Playwright:
            # from playwright.async_api import async_playwright
            # async with async_playwright() as p:
            #     browser = await p.chromium.launch()
            #     page_obj = await browser.new_page()
            #     await page_obj.goto(url)
            
            # For now, return empty (will implement with Playwright)
            return []
            
        except Exception as e:
            logger.error(f"Error scraping page: {e}")
            return []
    
    def extract_judgment_data(self, row_data: Dict) -> Optional[Dict]:
        """
        Extract and normalize judgment data from a table row
        
        Args:
            row_data: Raw row data from website
        
        Returns:
            Normalized judgment dictionary or None if invalid
        """
        try:
            # Expected fields from Karnataka HC website:
            # Date of Judgment, Title, Judge(s), Petitioner, Respondent, PDF Link
            
            judgment = {
                "case_number": row_data.get("title", "").strip(),
                "judgment_date": self._parse_date(row_data.get("date_of_judgment")),
                "judges": [j.strip() for j in row_data.get("judges", "").split(",")],
                "petitioner": row_data.get("petitioner", "").strip(),
                "respondent": row_data.get("respondent", "").strip(),
                "case_type": self._extract_case_type(row_data.get("title", "")),
                "court_level": "High Court",
                "status": "Decided",
                "pdf_url": row_data.get("pdf_url", ""),
                "source": "judiciary.karnataka.gov.in",
                "scraped_at": datetime.now().isoformat()
            }
            
            # Validate essential fields
            if not judgment["case_number"] or not judgment["judgment_date"]:
                return None
            
            return judgment
            
        except Exception as e:
            logger.error(f"Error extracting judgment: {e}")
            return None
    
    def _parse_date(self, date_str: str) -> Optional[str]:
        """Parse date in various formats"""
        if not date_str:
            return None
        
        date_formats = [
            "%d-%m-%Y",
            "%d/%m/%Y",
            "%Y-%m-%d",
            "%d.%m.%Y"
        ]
        
        date_str = date_str.strip()
        
        for fmt in date_formats:
            try:
                parsed = datetime.strptime(date_str, fmt)
                return parsed.isoformat()
            except ValueError:
                continue
        
        return None
    
    def _extract_case_type(self, case_title: str) -> str:
        """Extract case type from title"""
        case_title = case_title.upper()
        
        for case_type in ["CP", "WP", "WA", "FA", "RSA", "CAS"]:
            if case_type in case_title:
                return case_type
        
        return "OTHER"
    
    def save_to_json(self, filename: str):
        """Save scraped judgments to JSON file"""
        with open(filename, 'w') as f:
            json.dump(self.judgments, f, indent=2)
        logger.info(f"✅ Saved {len(self.judgments)} judgments to {filename}")


# For live scraping with Playwright
async def scrape_karnataka_hc_with_playwright() -> List[Dict]:
    """
    Live scraper using Playwright for JavaScript-heavy website
    """
    from playwright.async_api import async_playwright
    
    all_judgments = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        try:
            # Navigate to browse judgments page
            await page.goto("https://judiciary.karnataka.gov.in/hckn/index.php/browsejudgments", 
                          wait_until="networkidle")
            
            # Extract all available case types
            case_types = await page.locator('select[name="type"] >> option').all_text_contents()
            
            logger.info(f"Available case types: {case_types}")
            
            for case_type in case_types:
                if not case_type or case_type == "Select":
                    continue
                
                # Select case type
                await page.select_option('select[name="type"]', case_type)
                await page.wait_for_load_state('networkidle')
                
                # Get all pages for this case type
                page_num = 1
                while page_num <= 50:  # Max 50 pages
                    
                    # Get table rows
                    rows = await page.locator('table tbody tr').all()
                    
                    if not rows:
                        break
                    
                    for row in rows:
                        cells = await row.locator('td').all()
                        
                        if len(cells) >= 5:
                            judgment_data = {
                                "date_of_judgment": await cells[0].text_content(),
                                "title": await cells[1].text_content(),
                                "judges": await cells[2].text_content(),
                                "petitioner": await cells[3].text_content(),
                                "respondent": await cells[4].text_content(),
                            }
                            
                            # Get PDF link if exists
                            pdf_link = await cells[1].locator('a').get_attribute('href') if await cells[1].locator('a').count() > 0 else None
                            if pdf_link:
                                judgment_data["pdf_url"] = urljoin(BASE_URL, pdf_link)
                            
                            all_judgments.append(judgment_data)
                    
                    # Try to go to next page
                    next_button = await page.locator('a:has-text("Next")').first
                    if next_button and await next_button.is_enabled():
                        await next_button.click()
                        await page.wait_for_load_state('networkidle')
                        page_num += 1
                    else:
                        break
        
        finally:
            await browser.close()
    
    logger.info(f"✅ Scraped {len(all_judgments)} judgments with Playwright")
    return all_judgments


if __name__ == "__main__":
    import asyncio
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Run scraper
    scraper = KarnatakaHCJudgmentScraper()
    judgments = asyncio.run(scrape_karnataka_hc_with_playwright())
    
    # Save results
    scraper.judgments = judgments
    scraper.save_to_json("karnataka_hc_judgments.json")
