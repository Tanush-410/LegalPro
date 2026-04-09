#!/usr/bin/env python3
"""
Standalone 2026 Cases Scraper
Scrapes ALL 73+ case types from judiciary.karnataka.gov.in for 2026 only
No Supabase required - just shows what we're getting
"""

import asyncio
import json
import logging
from datetime import datetime
import sys

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def scrape_all_2026():
    """Scrape ALL 2026 cases from all case types"""
    
    try:
        from playwright.async_api import async_playwright
        from urllib.parse import urljoin
        import asyncio
        
        BASE_URL = "https://judiciary.karnataka.gov.in"
        JUDGMENTS_BASE = f"{BASE_URL}/hckn/"
        BROWSE_JUDGMENTS_URL = f"{JUDGMENTS_BASE}index.php/browsejudgments"
        
        all_cases = []
        case_types_found = set()
        
        logger.info("\n" + "="*80)
        logger.info("🔍 SCRAPING ALL 2026 CASES FROM KARNATAKA HIGH COURT")
        logger.info("="*80)
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                # Go to browse judgments
                logger.info("\n📋 Opening Karnataka HC website...")
                await page.goto(BROWSE_JUDGMENTS_URL, wait_until="networkidle", timeout=20000)
                
                # Get all available case types
                logger.info("🔍 Discovering all available case types (this may take a moment)...")
                await page.wait_for_selector('select[name="type"]', timeout=10000)
                
                options = await page.locator('select[name="type"] >> option').all()
                case_types = []
                
                for option in options:
                    value = await option.get_attribute('value')
                    text = await option.text_content()
                    if value and value.strip() and value.lower() != 'select':
                        case_types.append(value.strip())
                
                logger.info(f"✅ Found {len(case_types)} case types:")
                for i, ct in enumerate(case_types[:20], 1):
                    logger.info(f"   {i:2d}. {ct}")
                if len(case_types) > 20:
                    logger.info(f"   ... and {len(case_types) - 20} more")
                
                # Scrape each type
                logger.info(f"\n📋 Scraping all {len(case_types)} types for 2026 cases...")
                logger.info("(This will take several minutes - getting full data...)\n")
                
                for idx, case_type in enumerate(case_types, 1):
                    try:
                        logger.info(f"[{idx:2d}/{len(case_types)}] Processing: {case_type.upper():<20}", end=" ")
                        sys.stdout.flush()
                        
                        # Go back to browse page
                        await page.goto(BROWSE_JUDGMENTS_URL, timeout=20000)
                        await page.wait_for_selector('select[name="type"]', timeout=10000)
                        
                        # Select case type
                        await page.select_option('select[name="type"]', case_type)
                        await page.wait_for_load_state('networkidle')
                        
                        page_num = 1
                        type_cases = 0
                        
                        # Paginate through all pages
                        while page_num <= 200:
                            try:
                                # Skip to next page if not first
                                if page_num > 1:
                                    next_btn = page.locator('a:has-text("Next")')
                                    if await next_btn.is_visible():
                                        await next_btn.click()
                                        await page.wait_for_load_state('networkidle')
                                    else:
                                        break
                                
                                # Extract all rows
                                rows = await page.locator('table tbody tr').all()
                                
                                found_2026_on_page = False
                                
                                for row in rows:
                                    try:
                                        cells = await row.locator('td').all()
                                        if len(cells) >= 5:
                                            date_text = await cells[0].text_content()
                                            case_num = await cells[1].text_content()
                                            judges = await cells[2].text_content()
                                            petitioner = await cells[3].text_content()
                                            respondent = await cells[4].text_content()
                                            
                                            # Check if 2026
                                            if "2026" in str(date_text) or "2026" in str(case_num):
                                                found_2026_on_page = True
                                                
                                                case_data = {
                                                    "case_number": case_num.strip() if case_num else "",
                                                    "case_type": case_type.upper(),
                                                    "judgment_date": date_text.strip() if date_text else "",
                                                    "judges": judges.strip() if judges else "",
                                                    "petitioner": petitioner.strip() if petitioner else "",
                                                    "respondent": respondent.strip() if respondent else "",
                                                    "court": "High Court",
                                                    "source": "judiciary.karnataka.gov.in"
                                                }
                                                
                                                # Try to get PDF
                                                try:
                                                    pdf_link = await cells[1].locator('a').get_attribute('href')
                                                    if pdf_link:
                                                        case_data["pdf_url"] = urljoin(BASE_URL, pdf_link)
                                                except:
                                                    pass
                                                
                                                all_cases.append(case_data)
                                                type_cases += 1
                                    except Exception as e:
                                        continue
                                
                                if not found_2026_on_page and page_num > 1:
                                    break  # No more 2026 cases
                                
                                page_num += 1
                                await asyncio.sleep(0.2)
                                
                            except Exception as page_error:
                                break
                        
                        logger.info(f"✅ {type_cases:4d} cases")
                        case_types_found.add(case_type)
                        
                        await asyncio.sleep(0.3)
                        
                    except Exception as type_error:
                        logger.info(f"⚠️  Error: {str(type_error)[:40]}")
                        continue
                
                await browser.close()
                
            except Exception as e:
                logger.error(f"Error during scraping: {e}")
                import traceback
                traceback.print_exc()
                await browser.close()
        
        return all_cases
        
    except ImportError:
        logger.error("❌ Playwright not installed!")
        logger.info("Install with: pip install playwright")
        logger.info("Then run: playwright install")
        return []
    except Exception as e:
        logger.error(f"❌ Scraping failed: {e}")
        import traceback
        traceback.print_exc()
        return []


async def main():
    """Main entry point"""
    
    logger.info("\n" + "🔍 "* 40)
    logger.info("COMPREHENSIVE 2026 CASES SCRAPER")
    logger.info("🔍 " * 40 + "\n")
    
    # Run scraper
    cases = await scrape_all_2026()
    
    if cases:
        logger.info("\n" + "="*80)
        logger.info(f"✅ SCRAPING COMPLETE - FOUND {len(cases)} TOTAL 2026 CASES")
        logger.info("="*80)
        
        # Statistics
        logger.info("\n📊 STATISTICS:")
        
        # By type
        by_type = {}
        for case in cases:
            ct = case.get("case_type", "UNKNOWN")
            by_type[ct] = by_type.get(ct, 0) + 1
        
        logger.info(f"\n   Total unique case types: {len(by_type)}")
        logger.info(f"   Total cases: {len(cases)}\n")
        
        for case_type in sorted(by_type.keys()):
            count = by_type[case_type]
            logger.info(f"   {case_type:<20} {count:>6} cases")
        
        # Save to file
        output_file = "/tmp/karnataka_hc_2026_all_cases.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(cases, f, indent=2, ensure_ascii=False)
        
        logger.info(f"\n💾 Saved all {len(cases)} cases to: {output_file}")
        
        # Show sample cases
        logger.info("\n📋 SAMPLE CASES (first 5):")
        for i, case in enumerate(cases[:5], 1):
            logger.info(f"\n   {i}. {case['case_number']} ({case['case_type']})")
            logger.info(f"      Date: {case['judgment_date']}")
            logger.info(f"      Petitioner: {case['petitioner']}")
            logger.info(f"      Respondent: {case['respondent']}")
            if case.get('pdf_url'):
                logger.info(f"      PDF: {case['pdf_url'][:60]}...")
        
        logger.info(f"\n... and {len(cases) - 5} more cases")
        
        logger.info("\n" + "="*80)
        logger.info("Next Step: Use this data to populate Supabase or your database")
        logger.info("="*80 + "\n")
        
        return cases
    else:
        logger.error("❌ No cases scraped!")
        return []


if __name__ == "__main__":
    cases = asyncio.run(main())
    sys.exit(0 if cases else 1)
