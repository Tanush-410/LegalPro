"""
Scraper for Indian Kanoon (indiankanoon.org) - works for Supreme Court, High Courts, Lower Courts
Document URL format: https://indiankanoon.org/doc/{doc_id}/

This module provides a factory function that automatically selects the best scraper:
1. Playwright scraper (handles JavaScript and CAPTCHA)
2. Enhanced requests scraper (with better headers and session management)
3. Basic requests scraper (fallback)
"""
import os
from datetime import datetime
from app.scrapers.aironline_scraper import AIROnlineScraper
from app.scrapers.enhanced_indian_kanoon import EnhancedIndianKanoonScraper
import logging

logger = logging.getLogger(__name__)

def _as_bool(value: str, default: bool = False) -> bool:
    if value is None:
        return default
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


class CompositeCourtScraper:
    """Aggregate cases from multiple sources with normalized output schema."""

    def __init__(self, court_name: str, court_level: str):
        self.court_name = court_name
        self.court_level = court_level
        self.sources = [s.strip().lower() for s in os.getenv("SCRAPER_SOURCES", "air,ik").split(",") if s.strip()]
        self.air_max_cases = int(os.getenv("AIR_MAX_CASES_PER_COURT", "0"))
        self.ik_max_cases = int(os.getenv("IK_MAX_CASES_PER_COURT", "120"))

    def _normalize_case(self, raw: dict):
        case_number = raw.get("case_number") or raw.get("title")
        if not case_number:
            return None
        return {
            "title": (raw.get("title") or case_number)[:200],
            "case_number": str(case_number).strip(),
            "court": raw.get("court") or self.court_name,
            "judge": raw.get("judge") or raw.get("judge_name"),
            "case_date": raw.get("case_date") or raw.get("judgment_date") or datetime.utcnow(),
            "case_type": raw.get("case_type") or "Judgment",
            "petitioner": raw.get("petitioner"),
            "respondent": raw.get("respondent"),
            "judgment_text": raw.get("judgment_text") or "",
            "url": raw.get("url") or raw.get("source_url") or raw.get("file_path"),
        }

    def scrape(self, from_date=None, to_date=None):
        aggregated = []
        seen = set()

        if "air" in self.sources:
            air_scraper = AIROnlineScraper(self.court_name, self.court_level)
            max_cases = self.air_max_cases if self.air_max_cases > 0 else None
            for raw in air_scraper.scrape(from_date=from_date, to_date=to_date, max_cases=max_cases):
                normalized = self._normalize_case(raw)
                if not normalized:
                    continue
                key = normalized["case_number"].upper()
                if key in seen:
                    continue
                seen.add(key)
                aggregated.append(normalized)

        if "ik" in self.sources and _as_bool(os.getenv("IK_ENABLE_BACKFILL", "true"), True):
            ik_scraper = EnhancedIndianKanoonScraper(self.court_name, self.court_level)
            ik_cases = ik_scraper.scrape(from_date=from_date, to_date=to_date)[: self.ik_max_cases]
            for raw in ik_cases:
                normalized = self._normalize_case(raw)
                if not normalized:
                    continue
                key = normalized["case_number"].upper()
                if key in seen:
                    continue
                seen.add(key)
                aggregated.append(normalized)

        logger.info(
            "Composite scraper collected %s cases for %s from sources=%s",
            len(aggregated),
            self.court_name,
            ",".join(self.sources),
        )
        return aggregated


# Factory function to create appropriate scraper
def get_scraper(court_name: str, court_level: str):
    """
    Factory function to get the appropriate scraper
    
    Tries in order:
    1. PlaywrightScraper (best for CAPTCHA/JS-heavy sites)
    2. EnhancedIndianKanoonScraper (good compromise)
    3. Falls back to enhanced if Playwright not available
    """
    logger.info(f"Using CompositeCourtScraper for {court_name}")
    return CompositeCourtScraper(court_name, court_level)
