#!/usr/bin/env python3
"""
Simple HTTP Scraper for Karnataka HC 2026 Cases
Uses requests + BeautifulSoup instead of Playwright
No headless browser needed!
"""

import requests
import json
import logging
from typing import List, Dict
from datetime import datetime
from bs4 import BeautifulSoup
import asyncio
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

BASE_URL = "https://judiciary.karnataka.gov.in"
BROWSE_URL = f"{BASE_URL}/hckn/index.php/browsejudgments"


def scrape_2026_with_http():
    """Simple HTTP scraper for 2026 cases"""
    
    logger.info("\n" + "="*80)
    logger.info("🔍 KARNATAKA HC 2026 CASES SCRAPER (HTTP-BASED)")
    logger.info("="*80 + "\n")
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    all_cases = []
    
    try:
        # Step 1: Get the browse page to discover all case types
        logger.info("📋 Fetching Karnataka HC browse page...")
        response = session.get(BROWSE_URL, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the case type dropdown
        case_type_select = soup.find('select', {'name': 'type'})
        if not case_type_select:
            logger.error("❌ Could not find case type dropdown")
            return []
        
        # Extract all case types
        case_types = []
        for option in case_type_select.find_all('option'):
            value = option.get('value', '').strip()
            text = option.text.strip()
            if value and value.lower() != 'select':
                case_types.append({
                    'value': value,
                    'text': text
                })
        
        logger.info(f"✅ Found {len(case_types)} case types\n")
        
        # Show first 15
        logger.info("Case types discovered:")
        for i, ct in enumerate(case_types[:15], 1):
            logger.info(f"   {i:2d}. {ct['text']:<50} ({ct['value']})")
        if len(case_types) > 15:
            logger.info(f"   ... and {len(case_types) - 15} more types\n")
        
        # Step 2: For each case type, try to get 2026 cases
        logger.info(f"\n📋 Scraping all {len(case_types)} types for 2026 cases...\n")
        
        for idx, case_type in enumerate(case_types, 1):
            ctype_value = case_type['value']
            ctype_text = case_type['text'][:40]
            
            logger.info(f"[{idx:2d}/{len(case_types)}] {ctype_text:<40}", end=" ")
            
            try:
                # Try to fetch cases with this type
                # First request to get the page with this type selected
                params1 = {'type': ctype_value}
                response1 = session.get(BROWSE_URL, params=params1, timeout=30)
                soup1 = BeautifulSoup(response1.content, 'html.parser')
                
                # Look for table with case data
                table = soup1.find('table')
                if not table:
                    logger.info("❌ No table")
                    continue
                
                rows = table.find_all('tr')[1:]  # Skip header
                type_count = 0
                
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) < 5:
                        continue
                    
                    # Extract data
                    try:
                        date_text = cells[0].text.strip()
                        case_num_cell = cells[1]
                        judges_text = cells[2].text.strip() if len(cells) > 2 else ""
                        petitioner_text = cells[3].text.strip() if len(cells) > 3 else ""
                        respondent_text = cells[4].text.strip() if len(cells) > 4 else ""
                        
                        # Check for 2026
                        if "2026" in date_text or "2026" in case_num_cell.text:
                            case_num = case_num_cell.text.strip()
                            
                            case_data = {
                                "case_number": case_num,
                                "case_type": ctype_value.upper(),
                                "case_type_name": ctype_text,
                                "judgment_date": date_text,
                                "judges": judges_text,
                                "petitioner": petitioner_text,
                                "respondent": respondent_text,
                                "court": "High Court",
                                "source": "judiciary.karnataka.gov.in"
                            }
                            
                            # Try to get PDF link
                            pdf_link = case_num_cell.find('a')
                            if pdf_link:
                                href = pdf_link.get('href', '')
                                if href:
                                    case_data["pdf_url"] = f"{BASE_URL}{href}" if href.startswith('/') else href
                            
                            all_cases.append(case_data)
                            type_count += 1
                    except Exception as e:
                        continue
                
                if type_count > 0:
                    logger.info(f"✅ Found {type_count:>4} cases")
                else:
                    logger.info("⚠️  No 2026 cases")
                
                time.sleep(0.3)  # Be nice to server
                
            except Exception as e:
                logger.info(f"⚠️  Error: {str(e)[:40]}")
                continue
        
        logger.info("\n" + "="*80)
        logger.info(f"✅ COMPLETE - Total: {len(all_cases)} cases found")
        logger.info("="*80)
        
        # Statistics
        if all_cases:
            by_type = {}
            for case in all_cases:
                ct = case.get('case_type', 'UNKNOWN')
                by_type[ct] = by_type.get(ct, 0) + 1
            
            logger.info(f"\n📊 Results by case type:")
            for ct in sorted(by_type.keys()):
                logger.info(f"   {ct:<20} {by_type[ct]:>5} cases")
            
            # Save to JSON
            output_file = "/tmp/karnataka_hc_2026_scraped.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(all_cases, f, indent=2, ensure_ascii=False)
            logger.info(f"\n💾 Saved to: {output_file}")
            
            # Show sample
            logger.info(f"\n📋 Sample cases (first 3):")
            for i, case in enumerate(all_cases[:3], 1):
                logger.info(f"\n   {i}. {case['case_number']} ({case['case_type_name']})")
                logger.info(f"      Date: {case['judgment_date']}")
                logger.info(f"      Judges: {case['judges'][:60]}")
                logger.info(f"      Petitioner: {case['petitioner'][:50]}")
                logger.info(f"      Respondent: {case['respondent'][:50]}")
        
        return all_cases
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return []


if __name__ == "__main__":
    cases = scrape_2026_with_http()
    
    if cases:
        logger.info(f"\n✅ Successfully scraped {len(cases)} 2026 cases!")
    else:
        logger.info("\n❌ No cases scraped")
