"""
Metadata extraction from court documents
"""
import re
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class MetadataExtractor:
    """Extract structured metadata from judgment text"""
    
    @staticmethod
    def extract_case_number(text: str) -> str:
        """Extract case number from judgment text"""
        patterns = [
            r'Case No\.?\s*:?\s*([A-Z/\d]+)',
            r'Writ Petition\s*:?\s*([A-Z/\d]+)',
            r'\(WP\)\s*([A-Z/\d]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return "Unknown"
    
    @staticmethod
    def extract_judge_names(text: str) -> list:
        """Extract judge names from judgment text"""
        judge_patterns = [
            r'(?:Hon\'ble\s+)?(?:Justice|Judge)\s+([A-Z][a-z\s\.]+)',
            r'(?:Honourable\s+)?(?:Justice)\s+([A-Z][a-z\s\.]+)',
        ]
        
        judges = []
        for pattern in judge_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                judge_name = match.group(1).strip()
                if judge_name not in judges and len(judge_name) > 3:
                    judges.append(judge_name)
        
        return judges
    
    @staticmethod
    def extract_parties(text: str) -> dict:
        """Extract petitioner and respondent"""
        result = {
            'petitioner': None,
            'respondent': None
        }
        
        # Look for common party indicators
        petitioner_patterns = [
            r'(?:Petitioner|Appellant)\s*:?\s*([^\n]+)',
            r'between\s+([^\n]+?)\s+and',
        ]
        
        respondent_patterns = [
            r'Respondent\s*:?\s*([^\n]+)',
            r'and\s+([^\n]+?)(?:\s+(?:Respondent|vs\.)|$)',
        ]
        
        for pattern in petitioner_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result['petitioner'] = match.group(1).strip()[:200]
                break
        
        for pattern in respondent_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result['respondent'] = match.group(1).strip()[:200]
                break
        
        return result
    
    @staticmethod
    def extract_judgment_date(text: str) -> datetime:
        """Extract judgment date from text"""
        date_patterns = [
            r'(?:Judgment|Order)\s+(?:dated|on)\s+(\d{1,2}[\.\-/]\d{1,2}[\.\-/]\d{4})',
            r'(\d{1,2})\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})',
            r'(\d{1,2}[\.\-/]\d{1,2}[\.\-/]\d{4})',
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    date_str = match.group(0)
                    # Try parsing various date formats
                    for fmt in ['%d/%m/%Y', '%d-%m-%Y', '%d.%m.%Y', '%d %B %Y']:
                        try:
                            return datetime.strptime(date_str, fmt)
                        except ValueError:
                            continue
                except:
                    continue
        
        return datetime.utcnow()
    
    @staticmethod
    def extract_verdict(text: str) -> str:
        """Extract verdict/order from judgment text"""
        verdict_indicators = [
            'allowed',
            'dismissed',
            'quashed',
            'granted',
            'rejected',
            'upheld',
            'set aside',
            'partly allowed'
        ]
        
        text_lower = text.lower()
        
        # Look for verdict in common phrases
        phrases = [
            r'(?:This\s+)?(?:Petition|Appeal)\s+is\s+(?:hereby\s+)?([a-z\s]+)(?:\.|,)',
            r'(?:We|I)\s+(?:hereby\s+)?([a-z\s]+)(?:\s+the\s+)?(?:Petition|Appeal)',
        ]
        
        for pattern in phrases:
            match = re.search(pattern, text_lower)
            if match:
                verdict = match.group(1).strip()
                # Check if it matches known verdicts
                for indicator in verdict_indicators:
                    if indicator in verdict:
                        return verdict[:200]
        
        # Default search
        for sentence in text.split('.'):
            sentence_lower = sentence.lower()
            for indicator in verdict_indicators:
                if indicator in sentence_lower:
                    return sentence.strip()[:200]
        
        return "Order passed as per judgment"
    
    @staticmethod
    def extract_all_metadata(judgment_text: str) -> dict:
        """Extract all metadata from judgment text"""
        if not judgment_text or len(judgment_text) < 50:
            return {}
        
        return {
            'case_number': MetadataExtractor.extract_case_number(judgment_text),
            'judges': MetadataExtractor.extract_judge_names(judgment_text),
            'parties': MetadataExtractor.extract_parties(judgment_text),
            'judgment_date': MetadataExtractor.extract_judgment_date(judgment_text),
            'verdict': MetadataExtractor.extract_verdict(judgment_text),
        }
