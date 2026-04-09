import requests
from bs4 import BeautifulSoup
from datetime import datetime
import logging
import time
import json
import re
import os
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

class AIROnlineScraper:
    """Scraper for AIR Online (https://www.aironline.in)"""
    def __init__(self, court_name: str, court_level: str):
        self.base_url = "https://www.aironline.in"
        self.court_name = court_name
        self.court_level = court_level
        self.court_level_key = self._normalize_court_level(court_level)
        self.session = self._create_session()
        self.request_delay = 2  # seconds between requests
        self.last_request_time = 0
        self.air_search_url = os.getenv("AIR_AUTH_SEARCH_URL", f"{self.base_url}/search")
        self.air_auth_max_pages = max(1, int(os.getenv("AIR_AUTH_MAX_PAGES", "1")))
        self.air_auth_enabled = self._load_auth_cookie()

    def _normalize_court_level(self, raw_level: str) -> str:
        text = (raw_level or "").strip().upper()
        if "SUPREME" in text:
            return "SUPREME"
        if "HIGH" in text:
            return "HIGH"
        if "LOWER" in text or "DISTRICT" in text:
            return "LOWER"
        return text

    def _extract_citation_id_map(self, soup: BeautifulSoup):
        """
        AIR renders clickable links client-side.
        Extract mapping from citation text -> citationID from embedded JSON.
        """
        citation_id_map = {}
        for script in soup.find_all("script"):
            raw = script.string or script.get_text(strip=True)
            if not raw:
                continue
            raw = raw.strip()
            if not (raw.startswith("{") and "digestView" in raw and "citationID" in raw):
                continue
            try:
                payload = json.loads(raw)
            except Exception:
                continue
            for outer in payload.values():
                if not isinstance(outer, dict):
                    continue
                bucket = outer.get("b", {}) or {}
                if not isinstance(bucket, dict):
                    continue
                digest = bucket.get("digestView", [])
                if not isinstance(digest, list):
                    continue
                for row in digest:
                    if not isinstance(row, dict):
                        continue
                    citation_name = (row.get("citationName") or "").strip()
                    citation_id = (row.get("citationID") or "").strip()
                    if citation_name and citation_id:
                        citation_id_map[citation_name] = citation_id
        return citation_id_map

    def _extract_digest_rows(self, soup: BeautifulSoup):
        """Extract AIR digest rows from embedded JSON blocks."""
        rows = []
        for script in soup.find_all("script"):
            raw = script.string or script.get_text(strip=True)
            if not raw:
                continue
            raw = raw.strip()
            if not (raw.startswith("{") and "digestView" in raw):
                continue
            try:
                payload = json.loads(raw)
            except Exception:
                continue
            for outer in payload.values():
                if not isinstance(outer, dict):
                    continue
                bucket = outer.get("b", {}) or {}
                if not isinstance(bucket, dict):
                    continue
                digest = bucket.get("digestView", [])
                if isinstance(digest, list):
                    rows.extend([row for row in digest if isinstance(row, dict)])
        return rows

    def _load_auth_cookie(self) -> bool:
        """
        Optional authenticated mode:
        AIR_SESSION_COOKIE should contain raw cookie header, e.g. "k1=v1; k2=v2".
        """
        raw_cookie = (os.getenv("AIR_SESSION_COOKIE") or "").strip()
        if not raw_cookie:
            return False
        try:
            for pair in raw_cookie.split(";"):
                if "=" not in pair:
                    continue
                key, value = pair.split("=", 1)
                key = key.strip()
                value = value.strip()
                if key:
                    self.session.cookies.set(key, value, domain=".aironline.in")
            logger.info("AIR authenticated cookie mode enabled")
            return True
        except Exception as exc:
            logger.warning(f"Failed to parse AIR_SESSION_COOKIE: {exc}")
            return False

    def _parse_date(self, value):
        if not value:
            return datetime.utcnow()
        txt = str(value).strip()
        for fmt in ("%d-%m-%Y", "%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"):
            try:
                return datetime.strptime(txt, fmt)
            except Exception:
                continue
        return datetime.utcnow()

    def _looks_supreme(self, citation: str, court: str) -> bool:
        token = f"{citation or ''} {court or ''}".upper()
        return ("SUPREME COURT" in token) or (" SC " in f" {token} ")

    def _court_matches_level(self, citation: str, court: str) -> bool:
        court_text = court or ""
        if self.court_level_key == "SUPREME":
            return self._looks_supreme(citation, court_text)
        if self.court_level_key == "HIGH":
            if "High Court" in court_text:
                return True
            return ("HIGH COURT" in (citation or "").upper()) and not self._looks_supreme(citation, court_text)
        if self.court_level_key == "LOWER":
            return ("District Court" in court_text) or ("Lower Court" in court_text)
        return True

    def _build_case_from_digest_row(self, row):
        citation = (
            row.get("citationName")
            or row.get("citation")
            or row.get("caseNo")
            or row.get("title")
            or "Unknown"
        ).strip()
        court = (
            row.get("courtName")
            or row.get("court")
            or row.get("courtTitle")
            or ""
        ).strip()
        if not self._court_matches_level(citation, court):
            return None
        judge = (
            row.get("judgeName")
            or row.get("judge")
            or row.get("judges")
            or row.get("coram")
            or None
        )
        date_value = (
            row.get("judgmentDate")
            or row.get("dateOfJudgment")
            or row.get("date")
            or row.get("displayDate")
        )
        summary = (
            row.get("headNote")
            or row.get("summary")
            or row.get("digest")
            or ""
        )
        citation_id = (row.get("citationID") or row.get("citationId") or "").strip()
        source_url = f"{self.base_url}/judgment/{citation_id}" if citation_id else f"{self.base_url}/search?query={requests.utils.quote(citation)}"
        return {
            "title": citation,
            "case_number": citation,
            "court": court or None,
            "judge": (str(judge).strip() if judge else None),
            "case_date": self._parse_date(date_value),
            "case_type": "Judgment",
            "petitioner": None,
            "respondent": None,
            "judgment_text": str(summary).strip(),
            "url": source_url,
        }

    def _build_auth_query(self):
        if self.court_level_key == "SUPREME":
            return "Supreme Court of India"
        if self.court_level_key == "HIGH":
            return "High Court"
        return "District Court"

    def _scrape_authenticated_search(self, max_cases=None):
        """
        Attempt paginated AIR search scraping when session cookie is available.
        Falls back silently when page structure does not expose more rows.
        """
        if not self.air_auth_enabled:
            return []

        query = self._build_auth_query()
        cases = []
        seen_case_numbers = set()
        for page in range(1, self.air_auth_max_pages + 1):
            self._rate_limit()
            try:
                response = self.session.get(
                    self.air_search_url,
                    params={"q": query, "query": query, "page": page},
                    timeout=20,
                )
                response.raise_for_status()
            except Exception as exc:
                logger.warning(f"AIR authenticated page fetch failed at page {page}: {exc}")
                break

            soup = BeautifulSoup(response.content, "html.parser")
            digest_rows = self._extract_digest_rows(soup)
            if not digest_rows:
                break

            added_this_page = 0
            for row in digest_rows:
                case_obj = self._build_case_from_digest_row(row)
                if not case_obj:
                    continue
                key = (case_obj.get("case_number") or "").strip().upper()
                if not key or key in seen_case_numbers:
                    continue
                seen_case_numbers.add(key)
                cases.append(case_obj)
                added_this_page += 1
                if max_cases is not None and len(cases) >= max_cases:
                    logger.info(f"AIR authenticated search collected {len(cases)} cases")
                    return cases

            if added_this_page == 0:
                break

        logger.info(f"AIR authenticated search collected {len(cases)} cases")
        return cases

    def _create_session(self):
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': self.base_url,
            'Connection': 'keep-alive',
        })
        return session

    def _rate_limit(self):
        elapsed = time.time() - self.last_request_time
        if elapsed < self.request_delay:
            time.sleep(self.request_delay - elapsed)
        self.last_request_time = time.time()

    def scrape(self, from_date=None, to_date=None, max_cases=None):
        """Fetch recent judgments for the specified court level from AIR Online"""
        cases = []
        seen_case_numbers = set()

        # First try authenticated paginated mode (if configured).
        auth_cases = self._scrape_authenticated_search(max_cases=max_cases)
        for case_obj in auth_cases:
            key = (case_obj.get("case_number") or "").strip().upper()
            if not key or key in seen_case_numbers:
                continue
            seen_case_numbers.add(key)
            cases.append(case_obj)
            if max_cases is not None and len(cases) >= max_cases:
                logger.info(f"Fetched {len(cases)} judgments from AIR Online for {self.court_level_key}")
                return cases

        self._rate_limit()
        url = f"{self.base_url}/judgementUpdate/"
        logger.info(f"Fetching AIR Online judgments: {url}")
        resp = self.session.get(url, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.content, 'html.parser')
        citation_id_map = self._extract_citation_id_map(soup)
        digest_rows = self._extract_digest_rows(soup)

        for row in digest_rows:
            try:
                case_obj = self._build_case_from_digest_row(row)
                if not case_obj:
                    continue
                key = (case_obj.get("case_number") or "").strip().upper()
                if not key or key in seen_case_numbers:
                    continue
                seen_case_numbers.add(key)
                if key and key in seen_case_numbers:
                    continue
                if key:
                    seen_case_numbers.add(key)
                cases.append(case_obj)
                if max_cases is not None and len(cases) >= max_cases:
                    break
            except Exception as e:
                logger.warning(f"Error parsing AIR digest row: {e}")
                continue

        articles = soup.find_all('article', class_='col34 jugmentHeader')
        for article in articles:
            try:
                # Citation
                citation_span = article.find('span', class_='citationJudgementHeading')
                citation = citation_span.get_text(strip=True) if citation_span else None
                # Court
                court_span = article.find('span', class_='searchResultCourtHeading')
                court = court_span.get_text(strip=True) if court_span else None
                # Date
                date_span = article.find('span', string=lambda s: s and s.strip().startswith('D/-'))
                date_str = date_span.get_text(strip=True).replace('D/-', '') if date_span else None
                case_date = None
                if date_str:
                    try:
                        case_date = datetime.strptime(date_str, '%d-%m-%Y')
                    except Exception:
                        case_date = datetime.utcnow()
                else:
                    case_date = datetime.utcnow()
                # Judge(s): robust extraction from article text
                judge = None
                article_text = " ".join(article.get_text(" ", strip=True).split())
                marker_match = re.search(r"HON[’']?BLE\s+JUDGE\(S\)\s*:\s*", article_text, flags=re.IGNORECASE)
                if marker_match:
                    tail = article_text[marker_match.end():]
                    date_match = re.search(r"\bD\s*/?\s*-\s*\d{1,2}-\d{1,2}-\d{4}\b", tail, flags=re.IGNORECASE)
                    if date_match:
                        tail = tail[:date_match.start()]
                    para_match = re.search(r"\s\([A-Z]\)\s", tail)
                    if para_match:
                        tail = tail[:para_match.start()]
                    read_more_idx = tail.find("...Read")
                    if read_more_idx >= 0:
                        tail = tail[:read_more_idx]
                    judge = tail.strip(" .;,-")
                # Summary
                summary = ''
                ul = article.find('ul')
                if ul:
                    summary = '\n'.join([li.get_text(strip=True) for li in ul.find_all('li')])
                # Source URL: AIR uses js links; build stable deep-link from citationID when available.
                article_link = article.find('a', href=True)
                source_url = urljoin(self.base_url, article_link['href']) if article_link else url
                citation_id = citation_id_map.get(citation or "")
                if citation_id:
                    source_url = f"{self.base_url}/judgment/{citation_id}"
                elif not source_url or source_url.startswith("javascript"):
                    source_url = f"{self.base_url}/search?query={requests.utils.quote(citation or '')}"

                # Filter by court level
                if not self._court_matches_level(citation or "", court or ""):
                    continue
                case_obj = {
                    'title': citation or 'Unknown',
                    'case_number': citation or 'Unknown',
                    'court': court,
                    'judge': judge,
                    'case_date': case_date,
                    'case_type': 'Judgment',
                    'petitioner': None,
                    'respondent': None,
                    'judgment_text': summary,
                    'url': source_url
                }
                key = (case_obj.get("case_number") or "").strip().upper()
                if key and key in seen_case_numbers:
                    continue
                if key:
                    seen_case_numbers.add(key)
                cases.append(case_obj)
                if max_cases is not None and len(cases) >= max_cases:
                    break
            except Exception as e:
                logger.warning(f"Error parsing AIR Online article: {e}")
                continue
        logger.info(f"Fetched {len(cases)} judgments from AIR Online for {self.court_level_key}")
        return cases
