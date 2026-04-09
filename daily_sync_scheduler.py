#!/usr/bin/env python3
"""
Automatic Daily Sync Scheduler for Karnataka High Court Cases
- Runs automatically every day
- Fetches new cases from website
- Detects new cases not in database
- Adds them automatically
"""

import requests
from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime, timedelta
import logging
import json
import re
from typing import List, Dict, Optional
import time
from apscheduler.schedulers.background import BackgroundScheduler
import pytz

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KarnatakaHCDailySync:
    """Automatically sync cases from Karnataka High Court website"""
    
    def __init__(self):
        self.base_url = "https://judiciary.karnataka.gov.in"
        self.judgment_url = f"{self.base_url}/ds_judgment.php"
        self.db_path = "/Volumes/PortableSSD/court-ecosystem/court_cases.db"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        self.sync_log_file = "/Volumes/PortableSSD/court-ecosystem/sync_log.json"
        
    def get_existing_case_numbers(self) -> set:
        """Get all case numbers already in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cur.execute("SELECT case_number FROM cases")
            existing = {row[0] for row in cur.fetchall()}
            conn.close()
            return existing
        except Exception as e:
            logger.error(f"Error getting existing cases: {e}")
            return set()
    
    def fetch_new_cases(self, max_pages: int = 5) -> List[Dict]:
        """Fetch cases from website"""
        all_cases = []
        
        for page in range(1, max_pages + 1):
            try:
                logger.info(f"🌐 Fetching page {page}...")
                
                params = {'page': page, 'length': 100}
                response = self.session.get(
                    self.judgment_url,
                    params=params,
                    timeout=20,
                    verify=False
                )
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                page_cases = self._parse_html(soup)
                
                if page_cases:
                    all_cases.extend(page_cases)
                else:
                    break
                    
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                logger.warning(f"Error fetching page {page}: {e}")
                break
        
        return all_cases
    
    def _parse_html(self, soup: BeautifulSoup) -> List[Dict]:
        """Parse HTML to extract cases"""
        cases = []
        try:
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')[1:]
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 3:
                        case = self._extract_case(cells)
                        if case:
                            cases.append(case)
            return cases
        except Exception as e:
            logger.error(f"Error parsing HTML: {e}")
            return []
    
    def _extract_case(self, cells) -> Optional[Dict]:
        """Extract case from table row"""
        try:
            case_elem = cells[0].find('a')
            case_number = case_elem.get_text(strip=True) if case_elem else cells[0].get_text(strip=True)
            
            if not case_number:
                return None
            
            case_type_match = re.match(r'^([A-Z]+)\s+', case_number)
            case_type = case_type_match.group(1) if case_type_match else "UNKNOWN"
            
            return {
                'case_number': case_number,
                'case_type': case_type,
                'judge_name': cells[1].get_text(strip=True) if len(cells) > 1 else None,
                'judgment_date': self._parse_date(cells[2].get_text(strip=True)) if len(cells) > 2 else None,
                'petitioner': cells[3].get_text(strip=True)[:500] if len(cells) > 3 else None,
                'respondent': cells[4].get_text(strip=True)[:500] if len(cells) > 4 else None,
                'pdf_url': case_elem.get('href') if case_elem else None,
            }
        except:
            return None
    
    def _parse_date(self, date_str: str) -> Optional[str]:
        """Parse date"""
        if not date_str:
            return None
        for fmt in ['%d-%m-%Y', '%Y-%m-%d']:
            try:
                return datetime.strptime(date_str.strip(), fmt).isoformat()
            except:
                pass
        return None
    
    def add_cases_to_db(self, cases: List[Dict]) -> int:
        """Add new cases to database"""
        added = 0
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            
            # Ensure court exists
            cur.execute("""
                INSERT OR IGNORE INTO courts (name, level, state, created_at)
                VALUES (?, ?, ?, ?)
            """, ("Karnataka High Court", "HIGH", "Karnataka", datetime.utcnow().isoformat()))
            conn.commit()
            
            cur.execute("SELECT id FROM courts WHERE name = 'Karnataka High Court'")
            court_id = cur.fetchone()[0]
            
            for case in cases:
                # Check if exists
                cur.execute("SELECT id FROM cases WHERE case_number = ?", (case['case_number'],))
                if cur.fetchone():
                    continue
                
                try:
                    cur.execute("""
                        INSERT INTO cases 
                        (case_number, case_type, court_id, petitioner, respondent, 
                         case_date, pdf_url, case_status, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
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
                    
                    case_id = cur.lastrowid
                    
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
                    logger.info(f"✅ Added: {case['case_number']}")
                    
                except Exception as e:
                    logger.error(f"Error: {e}")
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Database error: {e}")
        
        return added
    
    def run_daily_sync(self):
        """Run sync job"""
        print("\n" + "="*60)
        print("🔄 DAILY SYNC STARTED")
        print("="*60)
        
        existing = self.get_existing_case_numbers()
        print(f"📊 Database has {len(existing)} cases")
        
        fetched = self.fetch_new_cases(max_pages=3)
        print(f"📥 Fetched {len(fetched)} cases from website")
        
        new_cases = [c for c in fetched if c['case_number'] not in existing]
        print(f"✨ Found {len(new_cases)} new cases")
        
        added = self.add_cases_to_db(new_cases)
        print(f"✅ Added {added} cases to database")
        
        # Log
        self._log_sync(len(existing), len(fetched), added, [c['case_number'] for c in new_cases[:10]])
        
        print("="*60)
    
    def _log_sync(self, existing, fetched, added, new_names):
        """Log sync activity"""
        try:
            logs = []
            try:
                with open(self.sync_log_file) as f:
                    logs = json.load(f)
            except:
                pass
            
            logs.append({
                'timestamp': datetime.utcnow().isoformat(),
                'existing_cases': existing,
                'fetched': fetched,
                'new_added': added,
                'sample_new_cases': new_names
            })
            
            with open(self.sync_log_file, 'w') as f:
                json.dump(logs[-100:], f, indent=2)
                
        except Exception as e:
            logger.error(f"Log error: {e}")


def start_daily_scheduler():
    """Start daily sync scheduler"""
    syncer = KarnatakaHCDailySync()
    scheduler = BackgroundScheduler()
    
    # Run every day at 3 AM IST
    ist = pytz.timezone('Asia/Kolkata')
    scheduler.add_job(
        syncer.run_daily_sync,
        'cron',
        hour=3,
        minute=0,
        timezone=ist,
        id='daily_sync'
    )
    
    scheduler.start()
    logger.info("✅ Daily sync scheduler started (3 AM IST)")
    
    return scheduler


if __name__ == "__main__":
    import atexit
    
    syncer = KarnatakaHCDailySync()
    print("\n🚀 Running initial sync...")
    syncer.run_daily_sync()
    
    print("\n📅 Starting scheduler for daily syncs at 3 AM IST...")
    scheduler = start_daily_scheduler()
    
    # Keep scheduler running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        scheduler.shutdown()
        print("\n✅ Scheduler stopped")
