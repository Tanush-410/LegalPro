"""
Supabase Integration Module
Handles all database operations with Supabase PostgreSQL
"""

import os
from typing import List, Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Supabase client
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    logger.warning("⚠️ Supabase library not installed")


class SupabaseManager:
    """Manage all Supabase operations"""
    
    def __init__(self):
        if not SUPABASE_AVAILABLE:
            raise ImportError("Please install: pip install supabase")
        
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_ANON_KEY")
        
        if not self.url or not self.key:
            raise ValueError("❌ SUPABASE_URL and SUPABASE_ANON_KEY env vars required")
        
        self.client: Client = create_client(self.url, self.key)
        logger.info(f"✅ Connected to Supabase: {self.url}")
    
    # ============================================================================
    # CASES TABLE OPERATIONS
    # ============================================================================
    
    def create_case(self, case_data: Dict) -> Dict:
        """Insert a single case"""
        try:
            response = self.client.table("cases").insert(case_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error creating case: {e}")
            return None
    
    def create_cases_batch(self, cases: List[Dict]) -> int:
        """Insert multiple cases efficiently"""
        if not cases:
            return 0
        
        try:
            response = self.client.table("cases").insert(cases).execute()
            inserted = len(response.data) if response.data else 0
            logger.info(f"✅ Inserted {inserted} cases")
            return inserted
        except Exception as e:
            logger.error(f"Error batch inserting cases: {e}")
            return 0
    
    def get_all_cases(self, limit: int = 1000) -> List[Dict]:
        """Get all cases"""
        try:
            response = self.client.table("cases").select("*").limit(limit).execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error fetching cases: {e}")
            return []
    
    def get_cases_by_type(self, case_type: str) -> List[Dict]:
        """Get cases by type (WP, CP, WA, etc.)"""
        try:
            response = self.client.table("cases").select("*").eq("case_type", case_type).execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error fetching cases by type: {e}")
            return []
    
    def get_cases_by_year(self, year: int) -> List[Dict]:
        """Get cases from specific year"""
        try:
            # Extract year from judgment_date
            response = self.client.table("cases").select("*").ilike(
                "judgment_date", f"{year}%"
            ).execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error fetching cases by year: {e}")
            return []
    
    def get_case_stats(self) -> Dict:
        """Get statistics about stored cases"""
        try:
            all_cases = self.get_all_cases()
            
            stats = {
                "total_cases": len(all_cases),
                "by_type": {},
                "by_year": {},
                "last_synced": datetime.now().isoformat()
            }
            
            for case in all_cases:
                # Count by type
                case_type = case.get("case_type", "OTHER")
                stats["by_type"][case_type] = stats["by_type"].get(case_type, 0) + 1
                
                # Count by year
                if case.get("judgment_date"):
                    year = case["judgment_date"][:4]
                    stats["by_year"][year] = stats["by_year"].get(year, 0) + 1
            
            return stats
        except Exception as e:
            logger.error(f"Error fetching stats: {e}")
            return {}
    
    def clear_cases(self) -> bool:
        """Clear all cases (use carefully!)"""
        try:
            self.client.table("cases").delete().neq("id", None).execute()
            logger.info("⚠️ Cleared all cases")
            return True
        except Exception as e:
            logger.error(f"Error clearing cases: {e}")
            return False
    
    # ============================================================================
    # DOCUMENTS TABLE OPERATIONS
    # ============================================================================
    
    def create_document(self, doc_data: Dict) -> Dict:
        """Insert a single document/PDF reference"""
        try:
            response = self.client.table("documents").insert(doc_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error creating document: {e}")
            return None
    
    def create_documents_batch(self, documents: List[Dict]) -> int:
        """Insert multiple documents"""
        if not documents:
            return 0
        
        try:
            response = self.client.table("documents").insert(documents).execute()
            inserted = len(response.data) if response.data else 0
            logger.info(f"✅ Inserted {inserted} documents")
            return inserted
        except Exception as e:
            logger.error(f"Error batch inserting documents: {e}")
            return 0
    
    def get_documents_for_case(self, case_id: str) -> List[Dict]:
        """Get all documents for a specific case"""
        try:
            response = self.client.table("documents").select("*").eq("case_id", case_id).execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error fetching documents: {e}")
            return []
    
    def get_all_documents(self) -> List[Dict]:
        """Get all documents"""
        try:
            response = self.client.table("documents").select("*").limit(10000).execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error fetching all documents: {e}")
            return []
    
    # ============================================================================
    # SYNC STATUS TRACKING
    # ============================================================================
    
    def record_sync(self, sync_data: Dict) -> bool:
        """Record a sync operation"""
        try:
            sync_record = {
                "cases_synced": sync_data.get("cases_synced", 0),
                "documents_synced": sync_data.get("documents_synced", 0),
                "status": sync_data.get("status", "pending"),
                "source": "karnataka_hc",
                "sync_timestamp": datetime.now().isoformat(),
                "details": sync_data.get("details", "")
            }
            
            response = self.client.table("sync_logs").insert(sync_record).execute()
            return bool(response.data)
        except Exception as e:
            logger.error(f"Error recording sync: {e}")
            return False
    
    def get_last_sync(self) -> Optional[Dict]:
        """Get the last successful sync"""
        try:
            response = self.client.table("sync_logs").select("*").eq(
                "status", "completed"
            ).order("sync_timestamp", desc=True).limit(1).execute()
            
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error fetching last sync: {e}")
            return None


def normalize_judgment_for_supabase(judgment: Dict) -> Dict:
    """
    Normalize judgment data from scraper into Supabase schema
    """
    return {
        "case_number": judgment.get("case_number", ""),
        "case_type": judgment.get("case_type", "OTHER"),
        "judgment_date": judgment.get("judgment_date"),
        "court_level": "High Court",
        "judges": ",".join(judgment.get("judges", [])) if isinstance(judgment.get("judges"), list) else judgment.get("judges", ""),
        "petitioner": judgment.get("petitioner", ""),
        "respondent": judgment.get("respondent", ""),
        "status": "Decided",
        "pdf_url": judgment.get("pdf_url", ""),
        "source": judgment.get("source", "judiciary.karnataka.gov.in"),
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }


# Global instance
_supabase_manager: Optional[SupabaseManager] = None


def get_supabase_manager() -> SupabaseManager:
    """Get or create Supabase manager instance"""
    global _supabase_manager
    if _supabase_manager is None:
        _supabase_manager = SupabaseManager()
    return _supabase_manager
