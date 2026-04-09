"""
Base scraper class for court documents
"""
from abc import ABC, abstractmethod
from datetime import datetime
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseScraper(ABC):
    """Abstract base class for court scrapers"""
    
    def __init__(self, court_name: str, court_level: str):
        self.court_name = court_name
        self.court_level = court_level
        self.base_url = None
        self.session = None
        
    @abstractmethod
    def get_writ_petitions(self, from_date=None, to_date=None):
        """
        Fetch writ petition cases from the court
        Should return list of case dictionaries
        """
        pass
    
    @abstractmethod
    def parse_case_details(self, case_url):
        """
        Parse individual case details from URL
        Should return case info dict with judgment details
        """
        pass
    
    def scrape(self, from_date=None, to_date=None):
        """
        Main scraping method
        """
        try:
            logger.info(f"Starting scrape for {self.court_name}")
            cases = self.get_writ_petitions(from_date, to_date)
            
            detailed_cases = []
            for case in cases:
                time.sleep(1)  # Rate limiting
                try:
                    details = self.parse_case_details(case)
                    detailed_cases.append(details)
                except Exception as e:
                    logger.error(f"Error parsing case {case}: {str(e)}")
                    continue
            
            logger.info(f"Scrape completed for {self.court_name}. Found {len(detailed_cases)} cases")
            return detailed_cases
        except Exception as e:
            logger.error(f"Scrape failed for {self.court_name}: {str(e)}")
            raise
