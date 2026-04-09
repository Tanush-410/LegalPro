"""
Karnataka High Court API Routes
Serves judgment data from Supabase
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import logging

from ..supabase_manager import get_supabase_manager, SUPABASE_AVAILABLE
from ..scheduler.karnataka_hc_jobs import get_karnataka_hc_statistics

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/karnataka-hc", tags=["Karnataka High Court"])


# ============================================================================
# HEALTH & STATUS ENDPOINTS
# ============================================================================

@router.get("/health", tags=["Health"])
async def health_check():
    """Check if Supabase connection is working"""
    if not SUPABASE_AVAILABLE:
        return {
            "status": "error",
            "message": "Supabase not configured - check .env file"
        }
    
    try:
        supabase = get_supabase_manager()
        # Test connection
        stats = supabase.get_case_stats()
        return {
            "status": "ok",
            "court": "Karnataka High Court",
            "data_source": "judiciary.karnataka.gov.in",
            "cases_available": stats.get("total_cases", 0)
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "error",
            "message": str(e)
        }


# ============================================================================
# STATISTICS ENDPOINTS
# ============================================================================

@router.get("/statistics")
async def get_statistics():
    """Get overall statistics about Karnataka HC judgments"""
    try:
        return get_karnataka_hc_statistics()
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_stats():
    """
    Get dashboard statistics
    Returns: total_cases, by_case_type, by_year, etc.
    """
    try:
        stats = get_karnataka_hc_statistics()
        
        return {
            "stats": {
                "total_cases": stats.get("total_cases", 0),
                "high_courts": stats.get("total_cases", 0),  # All are High Court
                "case_types": stats.get("by_case_type", {}),
                "by_year": stats.get("by_year", {}),
                "last_synced": stats.get("last_synced", "Never"),
                "court": "Karnataka High Court",
                "source": "judiciary.karnataka.gov.in"
            }
        }
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# CASE ENDPOINTS
# ============================================================================

@router.get("/cases")
async def list_cases(
    case_type: Optional[str] = Query(None),
    year: Optional[int] = Query(None),
    limit: int = Query(100, le=1000),
    offset: int = Query(0, ge=0)
):
    """
    List Karnataka HC judgment cases
    
    Query Parameters:
    - case_type: Filter by type (WP, CP, WA, FA, RSA, etc.)
    - year: Filter by judgment year (2024, 2025, 2026, etc.)
    - limit: Number of results (max 1000)
    - offset: Pagination offset
    """
    try:
        supabase = get_supabase_manager()
        
        if case_type:
            cases = supabase.get_cases_by_type(case_type)
        elif year:
            cases = supabase.get_cases_by_year(year)
        else:
            cases = supabase.get_all_cases(limit=10000)
        
        # Apply pagination
        paginated = cases[offset:offset + limit]
        
        return {
            "total": len(cases),
            "count": len(paginated),
            "offset": offset,
            "cases": paginated
        }
        
    except Exception as e:
        logger.error(f"Error listing cases: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cases/{case_number}")
async def get_case_detail(case_number: str):
    """
    Get detailed information about a specific case
    """
    try:
        supabase = get_supabase_manager()
        cases = supabase.get_all_cases()
        
        case = next((c for c in cases if c.get("case_number") == case_number), None)
        
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")
        
        # Get documents for this case
        documents = supabase.get_documents_for_case(case_number)
        
        return {
            "case": case,
            "documents": documents
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting case details: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# CASE TYPE ENDPOINTS
# ============================================================================

@router.get("/cases-by-type/{case_type}")
async def get_cases_by_type(case_type: str):
    """
    Get all cases of a specific type
    
    Case Types:
    - WP: Writ Petition
    - CP: Civil Petition
    - WA: Writ Appeal
    - FA: First Appeal
    - RSA: Regular Second Appeal
    """
    try:
        supabase = get_supabase_manager()
        cases = supabase.get_cases_by_type(case_type.upper())
        
        return {
            "case_type": case_type.upper(),
            "count": len(cases),
            "cases": cases
        }
        
    except Exception as e:
        logger.error(f"Error getting cases by type: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# DOCUMENT ENDPOINTS
# ============================================================================

@router.get("/documents")
async def list_documents(limit: int = Query(100, le=1000)):
    """
    List all judgment documents/PDFs
    """
    try:
        supabase = get_supabase_manager()
        documents = supabase.get_all_documents()
        
        return {
            "total": len(documents),
            "count": len(documents[:limit]),
            "documents": documents[:limit]
        }
        
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents/{case_number}")
async def get_case_documents(case_number: str):
    """
    Get all documents/PDFs for a specific case
    """
    try:
        supabase = get_supabase_manager()
        documents = supabase.get_documents_for_case(case_number)
        
        if not documents:
            raise HTTPException(status_code=404, detail=f"No documents found for {case_number}")
        
        return {
            "case_number": case_number,
            "count": len(documents),
            "documents": documents
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# PDF/LINK ENDPOINTS
# ============================================================================

@router.get("/pdf/{case_number}")
async def get_pdf_link(case_number: str):
    """
    Get PDF link for a judgment
    Redirects to the actual PDF on judiciary.karnataka.gov.in
    """
    try:
        supabase = get_supabase_manager()
        cases = supabase.get_all_cases()
        case = next((c for c in cases if c.get("case_number") == case_number), None)
        
        if not case or not case.get("pdf_url"):
            raise HTTPException(status_code=404, detail="PDF not found")
        
        return {
            "case_number": case_number,
            "pdf_url": case["pdf_url"],
            "source": "judiciary.karnataka.gov.in"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting PDF: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# SEARCH ENDPOINTS
# ============================================================================

@router.get("/search")
async def search_cases(
    q: str = Query(..., min_length=2),
    limit: int = Query(20, le=100)
):
    """
    Full-text search across cases and parties
    
    Search by:
    - Case number (WP 1983, CP 312, etc.)
    - Petitioner name
    - Respondent name
    - Judge name
    """
    try:
        supabase = get_supabase_manager()
        all_cases = supabase.get_all_cases()
        
        q_lower = q.lower()
        results = [
            case for case in all_cases
            if q_lower in case.get("case_number", "").lower()
            or q_lower in case.get("petitioner", "").lower()
            or q_lower in case.get("respondent", "").lower()
            or q_lower in case.get("judges", "").lower()
        ][:limit]
        
        return {
            "query": q,
            "count": len(results),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Error searching: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# SYNC ENDPOINT
# ============================================================================

@router.post("/sync")
async def trigger_sync():
    """
    Manually trigger a data sync from judiciary.karnataka.gov.in
    
    This scrapes the website and populates Supabase
    """
    try:
        from ..scheduler.karnataka_hc_jobs import sync_karnataka_hc_judgments
        
        logger.info("🚀 Manual sync triggered")
        result = sync_karnataka_hc_judgments()
        
        return result
        
    except Exception as e:
        logger.error(f"Error during sync: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# DASHBOARD ENDPOINT (for frontend)
# ============================================================================

@router.get("/dashboard")
async def get_dashboard_data():
    """
    Get complete dashboard data
    Includes statistics, recent cases, and case type breakdown
    """
    try:
        supabase = get_supabase_manager()
        
        stats = get_karnataka_hc_statistics()
        all_cases = supabase.get_all_cases()
        
        # Most recent cases
        recent_cases = sorted(
            all_cases,
            key=lambda x: x.get("judgment_date", ""),
            reverse=True
        )[:10]
        
        # Cases by type
        by_type = {}
        for case in all_cases:
            case_type = case.get("case_type", "OTHER")
            if case_type not in by_type:
                by_type[case_type] = []
            by_type[case_type].append(case)
        
        return {
            "court": "Karnataka High Court",
            "source": "judiciary.karnataka.gov.in",
            "statistics": {
                "total_cases": len(all_cases),
                "by_case_type": {k: len(v) for k, v in by_type.items()},
                "by_year": stats.get("by_year", {})
            },
            "recent_cases": recent_cases,
            "cases_by_type": {k: v[:5] for k, v in by_type.items()},  # Top 5 of each type
            "last_synced": stats.get("last_synced")
        }
        
    except Exception as e:
        logger.error(f"Error getting dashboard data: {e}")
        raise HTTPException(status_code=500, detail=str(e))
