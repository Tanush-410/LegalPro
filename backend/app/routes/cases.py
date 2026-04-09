"""
Cases and Judgments Routes
"""
from fastapi import APIRouter, Depends, Query, HTTPException, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session, joinedload
from typing import List
from app.database import get_db
from app.models import Case, Judgment, Document
from app.schemas import CaseResponse, JudgmentResponse, DocumentResponse
from app.utils.pdf_report import build_case_report_pdf
from app.utils.case_ai import summarize_case, find_similar_cases
from app.case_types import get_case_type_info
import requests

router = APIRouter(prefix="/api", tags=["cases"])

@router.get("/cases", response_model=List[CaseResponse])
async def list_cases(
    skip: int = Query(0, ge=0),
    limit: int = Query(1000, ge=1, le=10000),
    court_id: int = Query(None),
    court_level: str = Query(None),
    case_type: str = Query(None),
    verified_only: bool = Query(False, description="Return only cases that have both judgment and document rows"),
    db: Session = Depends(get_db)
):
    """List cases with optional filters - defaults to all cases"""
    
    from app.models import Court
    
    query = (
        db.query(Case)
        .join(Court, Case.court_id == Court.id)
        .options(joinedload(Case.court), joinedload(Case.judgments))
    )
    
    if court_id:
        query = query.filter(Case.court_id == court_id)
    
    if court_level:
        # Accept both enum values and full string equivalents
        from app.models import CourtEnum
        level_map = {
            'SUPREME': CourtEnum.SUPREME.value,
            'HIGH': CourtEnum.HIGH.value,
            'LOWER': CourtEnum.LOWER.value,
            'Supreme Court': CourtEnum.SUPREME.value,
            'High Court': CourtEnum.HIGH.value,
            'Lower Court': CourtEnum.LOWER.value,
        }
        mapped_level = level_map.get(str(court_level).upper(), court_level)
        query = query.filter(Court.level == mapped_level)
    
    if case_type:
        query = query.filter(Case.case_type == case_type)

    if verified_only:
        query = query.filter(Case.judgments.any())
    
    cases = query.order_by(Case.created_at.desc()).offset(skip).limit(limit).all()
    # Attach court object for each case for dashboard compatibility
    result = []
    for case in cases:
        case_dict = case.__dict__.copy()
        # SQLAlchemy adds _sa_instance_state, remove it
        case_dict.pop('_sa_instance_state', None)
        latest_judgment = None
        if getattr(case, "judgments", None):
            latest_judgment = max(
                case.judgments,
                key=lambda j: (j.judgment_date or j.created_at, j.created_at),
            )
        case_dict["judge_name"] = latest_judgment.judge_name if latest_judgment else None

        # Add full case type information
        case_type_info = get_case_type_info(case.case_type)
        case_dict["case_type_full"] = case_type_info["full_name"]
        case_dict["case_type_description"] = case_type_info["description"]
        case_dict["case_type_category"] = case_type_info["category"]

        # Attach court info
        if hasattr(case, 'court') and case.court:
            court = case.court
            court_dict = court.__dict__.copy()
            court_dict.pop('_sa_instance_state', None)
            case_dict['court'] = court_dict
        else:
            case_dict['court'] = None
        result.append(case_dict)
    return result

@router.get("/cases/{case_id}", response_model=CaseResponse)
async def get_case(case_id: int, db: Session = Depends(get_db)):
    """Get individual case details"""
    return db.query(Case).filter(Case.id == case_id).first()


@router.get("/cases/{case_id}/detail")
async def get_case_detail(case_id: int, db: Session = Depends(get_db)):
    """Get case + latest judgment + primary document in one response."""
    case = (
        db.query(Case)
        .options(joinedload(Case.court), joinedload(Case.judgments), joinedload(Case.documents))
        .filter(Case.id == case_id)
        .first()
    )
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    judgments = sorted(list(case.judgments or []), key=lambda j: j.judgment_date or j.created_at, reverse=True)
    latest_judgment = judgments[0] if judgments else None
    documents = list(case.documents or [])
    primary_doc = documents[0] if documents else None

    return {
        "case": {
            "id": case.id,
            "case_number": case.case_number,
            "case_type": case.case_type,
            "petitioner": case.petitioner,
            "respondent": case.respondent,
            "case_date": case.case_date.isoformat() if case.case_date else None,
            "created_at": case.created_at.isoformat() if case.created_at else None,
            "court": {
                "id": case.court.id if case.court else None,
                "name": case.court.name if case.court else None,
                "level": case.court.level.value if case.court and case.court.level else None,
            },
        },
        "latest_judgment": {
            "id": latest_judgment.id if latest_judgment else None,
            "judge_name": latest_judgment.judge_name if latest_judgment else None,
            "judgment_date": latest_judgment.judgment_date.isoformat() if latest_judgment and latest_judgment.judgment_date else None,
            "judgment_text": latest_judgment.judgment_text if latest_judgment else None,
            "verdict": latest_judgment.verdict if latest_judgment else None,
        },
        "primary_document": {
            "id": primary_doc.id if primary_doc else None,
            "source_url": primary_doc.source_url if primary_doc else None,
            "file_path": primary_doc.file_path if primary_doc else None,
            "file_name": primary_doc.file_name if primary_doc else None,
            "file_type": primary_doc.file_type if primary_doc else None,
        },
    }

@router.get("/judgments", response_model=List[JudgmentResponse])
async def list_judgments(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    case_id: int = Query(None),
    db: Session = Depends(get_db)
):
    """List judgments"""
    
    query = db.query(Judgment)
    
    if case_id:
        query = query.filter(Judgment.case_id == case_id)
    
    judgments = query.order_by(Judgment.judgment_date.desc()).offset(skip).limit(limit).all()
    return judgments

@router.get("/cases/{case_id}/documents", response_model=List[DocumentResponse])
async def get_case_documents(case_id: int, db: Session = Depends(get_db)):
    """Get documents for a case"""
    return db.query(Document).filter(Document.case_id == case_id).all()


@router.get("/cases/{case_id}/pdf")
async def download_case_pdf(case_id: int, db: Session = Depends(get_db)):
    """
    Fetch and serve the official court PDF for download
    """
    import logging
    logger = logging.getLogger(__name__)
    
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    if not case.pdf_url:
        raise HTTPException(status_code=404, detail="PDF not available for this case")
    
    logger.info(f"PDF download requested for case {case_id}: {case.pdf_url}")
    
    # The official PDFs are not available for programmatic download
    # Redirect users to the official website
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url=case.pdf_url)

@router.get("/cases/{case_id}/pdf-url")
async def get_pdf_url(case_id: int, db: Session = Depends(get_db)):
    """Get the PDF URL for a case (useful for checking availability)"""
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    return {"case_id": case_id, "case_number": case.case_number, "pdf_url": case.pdf_url}


@router.get("/cases/{case_id}/ai-summary")
async def get_case_ai_summary(case_id: int, db: Session = Depends(get_db)):
    """Generate an AI-style summary for a case."""
    case = (
        db.query(Case)
        .options(joinedload(Case.court), joinedload(Case.judgments))
        .filter(Case.id == case_id)
        .first()
    )
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    payload = summarize_case(case)
    return {
        "case_id": case.id,
        "case_number": case.case_number,
        "summary": payload["summary"],
        "method": payload["method"],
    }


@router.get("/cases/{case_id}/similar")
async def get_similar_cases(
    case_id: int,
    limit: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db),
):
    """Recommend similar cases based on text and metadata similarity."""
    target = (
        db.query(Case)
        .options(joinedload(Case.court), joinedload(Case.judgments))
        .filter(Case.id == case_id)
        .first()
    )
    if not target:
        raise HTTPException(status_code=404, detail="Case not found")

    # Limit comparison set to verified cases for better quality.
    pool = (
        db.query(Case)
        .options(joinedload(Case.court), joinedload(Case.judgments))
        .filter(Case.judgments.any())
        .all()
    )

    recommendations = find_similar_cases(target, pool, limit=limit)
    return {
        "case_id": target.id,
        "case_number": target.case_number,
        "count": len(recommendations),
        "items": recommendations,
    }


@router.get("/judges")
async def get_judges(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get list of all judges"""
    from sqlalchemy import func
    
    # Get distinct judges with their case counts
    judges_data = (
        db.query(
            Judgment.judge_name,
            func.count(Judgment.id).label('case_count'),
            func.max(Judgment.judgment_date).label('last_judgment_date')
        )
        .filter(Judgment.judge_name.isnot(None))
        .group_by(Judgment.judge_name)
        .order_by(func.count(Judgment.id).desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    
    return [
        {
            "judge_name": judge[0],
            "case_count": judge[1],
            "last_judgment_date": judge[2].isoformat() if judge[2] else None
        }
        for judge in judges_data
    ]


@router.get("/judges/{judge_name}/cases")
async def get_judge_cases(
    judge_name: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get all cases handled by a specific judge"""
    
    cases = (
        db.query(Case)
        .join(Judgment, Case.id == Judgment.case_id)
        .filter(Judgment.judge_name == judge_name)
        .options(joinedload(Case.court), joinedload(Case.judgments))
        .order_by(Case.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    
    result = []
    for case in cases:
        case_dict = case.__dict__.copy()
        case_dict.pop('_sa_instance_state', None)
        
        latest_judgment = max(
            case.judgments,
            key=lambda j: (j.judgment_date or j.created_at, j.created_at),
        ) if case.judgments else None
        
        case_dict["judge_name"] = latest_judgment.judge_name if latest_judgment else None
        
        if case.court:
            court_dict = case.court.__dict__.copy()
            court_dict.pop('_sa_instance_state', None)
            case_dict['court'] = court_dict
        
        result.append(case_dict)
    
    return result
