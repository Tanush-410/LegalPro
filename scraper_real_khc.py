#!/usr/bin/env python3
"""
Karnataka High Court Judgment Scraper - Fetches 80+ Real Cases
Targets: https://judiciary.karnataka.gov.in/ds_judgment.php
"""

import requests
from bs4 import BeautifulSoup
import re
import json
import time
from datetime import datetime
import sqlite3
import logging
from typing import List, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KarnatakaHCRealScraper:
    def __init__(self):
        self.base_url = "https://judiciary.karnataka.gov.in"
        self.judgment_url = f"{self.base_url}/ds_judgment.php"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        self.cases = []
        self.db_path = "/Volumes/PortableSSD/court-ecosystem/court_cases.db"
        
    def scrape_all_pages(self):
        """Scrape judgment data from all pages"""
        print("🔍 Starting Karnataka High Court Judgment Scraper...")
        print(f"📍 Target: {self.judgment_url}\n")
        
        page = 1
        max_pages = 10  # Estimate based on 80+ cases
        
        while page <= max_pages:
            try:
                print(f"📄 Fetching page {page}...")
                
                # Build page URL with pagination
                params = {
                    'page': page,
                    'length': 100  # Show more entries per page
                }
                
                response = self.session.get(self.judgment_url, params=params, timeout=15)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract cases from this page
                page_cases = self.extract_cases_from_page(soup, page)
                
                if not page_cases:
                    print(f"✓ No more cases found. Total pages crawled: {page-1}")
                    break
                
                self.cases.extend(page_cases)
                print(f"  ✓ Found {len(page_cases)} cases on page {page}")
                print(f"  ✓ Total cases so far: {len(self.cases)}")
                
                page += 1
                time.sleep(1)  # Respectful rate limiting
                
                if len(self.cases) >= 80:
                    print(f"\n✅ Target reached! Found {len(self.cases)} cases")
                    break
                    
            except Exception as e:
                logger.error(f"Error on page {page}: {e}")
                break
        
        return self.cases
    
    def extract_cases_from_page(self, soup: BeautifulSoup, page: int) -> List[Dict]:
        """Extract case data from HTML page"""
        cases = []
        
        # Find tables containing case data
        tables = soup.find_all('table')
        
        for table in tables:
            rows = table.find_all('tr')[1:]  # Skip header row
            
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 5:
                    try:
                        case = self.parse_case_row(cells)
                        if case:
                            cases.append(case)
                    except Exception as e:
                        logger.debug(f"Error parsing row: {e}")
        
        return cases
    
    def parse_case_row(self, cells) -> Dict:
        """Parse a single case row"""
        try:
            # Extract data from cells
            case_number_element = cells[0].find('a')
            case_number = case_number_element.get_text(strip=True) if case_number_element else cells[0].get_text(strip=True)
            
            # Try to get PDF URL
            pdf_url = case_number_element.get('href') if case_number_element else None
            if pdf_url and not pdf_url.startswith('http'):
                pdf_url = f"{self.base_url}{pdf_url}" if pdf_url.startswith('/') else f"{self.base_url}/{pdf_url}"
            
            # Parse case type from case number (e.g., "WP 1234 OF 2026" -> "WP")
            case_type_match = re.match(r'([A-Z]+)\s+(\d+)', case_number)
            case_type = case_type_match.group(1) if case_type_match else "UNKNOWN"
            
            # Extract judge name
            judge_name = cells[1].get_text(strip=True) if len(cells) > 1 else ""
            
            # Extract judgment date
            judgment_date_str = cells[2].get_text(strip=True) if len(cells) > 2 else ""
            judgment_date = self.parse_date(judgment_date_str)
            
            # Extract petitioner
            petitioner = cells[3].get_text(strip=True) if len(cells) > 3 else ""
            
            # Extract respondent
            respondent = cells[4].get_text(strip=True) if len(cells) > 4 else ""
            
            # Extract CNR if available
            cnr = ""
            if len(cells) > 5:
                cnr = cells[5].get_text(strip=True)
            
            case_obj = {
                'cnr': cnr or None,
                'case_number': case_number,
                'case_type': case_type,
                'judge_name': judge_name,
                'judgment_date': judgment_date,
                'petitioner': petitioner[:500] if petitioner else None,
                'respondent': respondent[:500] if respondent else None,
                'pdf_url': pdf_url,
                'source': 'judiciary.karnataka.gov.in'
            }
            
            return case_obj if case_obj['case_number'] else None
            
        except Exception as e:
            logger.debug(f"Error parsing case: {e}")
            return None
    
    def parse_date(self, date_str: str) -> str:
        """Parse date string to ISO format"""
        try:
            # Try DD-MM-YYYY format
            parsed = datetime.strptime(date_str.strip(), '%d-%m-%Y')
            return parsed.isoformat()
        except:
            try:
                # Try other common formats
                parsed = datetime.strptime(date_str.strip(), '%Y-%m-%d')
                return parsed.isoformat()
            except:
                return None
    
    def save_to_db(self):
        """Save scraped cases to SQLite database"""
        print(f"\n💾 Saving {len(self.cases)} cases to database...")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            
            # Ensure Karnataka High Court exists
            cur.execute("""
                INSERT OR IGNORE INTO courts (name, level, state, created_at)
                VALUES (?, ?, ?, ?)
            """, ("Karnataka High Court", "HIGH", "Karnataka", datetime.utcnow().isoformat()))
            conn.commit()
            
            # Get court ID
            cur.execute("SELECT id FROM courts WHERE name = 'Karnataka High Court'")
            court_id = cur.fetchone()[0]
            
            # Clear old sample data
            cur.execute("DELETE FROM judgments")
            cur.execute("DELETE FROM cases")
            conn.commit()
            
            # Insert cases
            added = 0
            for case in self.cases:
                try:
                    cur.execute("""
                        INSERT INTO cases 
                        (cnr, case_number, case_type, court_id, petitioner, respondent, 
                         case_date, pdf_url, case_status, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        case.get('cnr'),
                        case['case_number'],
                        case['case_type'],
                        court_id,
                        case.get('petitioner'),
                        case.get('respondent'),
                        case.get('judgment_date'),
                        case.get('pdf_url'),
                        'DISPOSED',
                        datetime.utcnow().isoformat()
                    ))
                    
                    # Get inserted case ID
                    case_id = cur.lastrowid
                    
                    # Insert judgment record
                    if case.get('judge_name'):
                        cur.execute("""
                            INSERT INTO judgments
                            (case_id, judge_name, judgment_date, verdict, created_at)
                            VALUES (?, ?, ?, ?, ?)
                        """, (
                            case_id,
                            case['judge_name'],
                            case.get('judgment_date'),
                            'DISPOSED',
                            datetime.utcnow().isoformat()
                        ))
                    
                    added += 1
                    
                except Exception as e:
                    logger.error(f"Error inserting case {case.get('case_number')}: {e}")
            
            conn.commit()
            conn.close()
            
            print(f"✅ Successfully added {added} cases to database")
            print(f"📊 Database path: {self.db_path}")
            
        except Exception as e:
            logger.error(f"Error saving to database: {e}")
    
    def generate_json_export(self):
        """Export cases as JSON"""
        json_path = "/Volumes/PortableSSD/court-ecosystem/karnataka_hc_cases_2026.json"
        with open(json_path, 'w') as f:
            json.dump(self.cases, f, indent=2)
        print(f"📄 JSON export saved to: {json_path}")
        return json_path


# Main execution
if __name__ == "__main__":
    scraper = KarnatakaHCRealScraper()
    
    # Scrape all pages
    cases = scraper.scrape_all_pages()
    
    print(f"\n{'='*60}")
    print(f"🎉 SCRAPING COMPLETE!")
    print(f"{'='*60}")
    print(f"Total cases fetched: {len(cases)}")
    
    if cases:
        # Show sample cases
        print(f"\n📋 Sample Cases:")
        for case in cases[:3]:
            print(f"\n  Case: {case['case_number']}")
            print(f"  Type: {case['case_type']}")
            print(f"  Judge: {case['judge_name']}")
            print(f"  Date: {case['judgment_date']}")
            print(f"  Petitioner: {case['petitioner']}")
            print(f"  Respondent: {case['respondent']}")
        
        # Save to database
        scraper.save_to_db()
        
        # Export as JSON
        scraper.generate_json_export()
        
        print(f"\n✅ All data saved! Ready to use.")
    else:
        print("❌ No cases were scraped. The website might be blocking requests.")
