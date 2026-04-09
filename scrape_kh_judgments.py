#!/usr/bin/env python3
"""
Comprehensive scraper for Karnataka High Court Judgments
Fetches real case data from judiciary.karnataka.gov.in
"""

import requests
from bs4 import BeautifulSoup
import re
import json
import time
from datetime import datetime
import sqlite3
import sys

sys.path.insert(0, "/Volumes/PortableSSD/court-ecosystem/backend")

class KarnatakaHCJudgmentScraper:
    def __init__(self):
        self.base_url = "https://judiciary.karnataka.gov.in"
        self.judgment_url = f"{self.base_url}/ds_judgment.php"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        self.cases = []
        
    def fetch_judgments(self):
        """Fetch judgment list from the website"""
        try:
            print("🔍 Fetching judgment list from Karnataka High Court...")
            response = self.session.get(self.judgment_url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Try multiple parsing strategies
            cases_found = 0
            
            # Strategy 1: Look for tables with judgment data
            tables = soup.find_all('table')
            print(f"Found {len(tables)} tables on page")
            
            for table_idx, table in enumerate(tables):
                rows = table.find_all('tr')
                print(f"  Table {table_idx}: {len(rows)} rows")
                
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 3:
                        cell_text = [cell.get_text(strip=True) for cell in cells]
                        print(f"    Row: {cell_text[:4]}")
                        cases_found += 1
                        if cases_found >= 5:
                            break
                if cases_found >= 5:
                    break
            
            # Strategy 2: Look for links to individual judgments
            print("\n📄 Looking for judgment links...")
            judgment_links = []
            for link in soup.find_all('a'):
                href = link.get('href', '')
                text = link.get_text(strip=True)
                if 'judgment' in href.lower() or 'order' in href.lower():
                    judgment_links.append({
                        'href': href,
                        'text': text
                    })
                    if len(judgment_links) <= 5:
                        print(f"  Found: {text} -> {href}")
            
            print(f"✓ Found {len(judgment_links)} judgment links")
            return soup, judgment_links
            
        except Exception as e:
            print(f"❌ Error fetching judgments: {e}")
            return None, []
    
    def extract_case_details_from_page(self, soup):
        """Extract case details from the HTML"""
        cases = []
        
        # Look for any text that looks like case numbers
        text = soup.get_text()
        
        # Patterns for Indian case numbers
        # Example: WP 1234/2026, CA 5678/2026
        case_number_pattern = r'([A-Z]{2,4})\s*(\d+)/(\d{4})'
        matches = re.findall(case_number_pattern, text)
        
        if matches:
            print(f"✓ Found {len(matches)} potential case numbers")
            for match in matches[:10]:
                print(f"  - {match[0]} {match[1]}/{match[2]}")
        
        return cases

# Run scraper
if __name__ == "__main__":
    scraper = KarnatakaHCJudgmentScraper()
    soup, links = scraper.fetch_judgments()
    
    if soup:
        print("\n✓ Successfully fetched the page")
        print("✓ Now analyzing page structure...")
        scraper.extract_case_details_from_page(soup)
    else:
        print("❌ Failed to fetch page")
