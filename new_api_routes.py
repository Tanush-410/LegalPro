#!/usr/bin/env python3
"""
New API Routes for Advanced Case Features
Added to backend/app/routes/cases.py
"""

# Add these routes to the cases router

additional_routes = '''

@router.get("/cases/{case_id}/timeline")
async def get_case_timeline(case_id: int, db: Session = Depends(get_db)):
    """Get timeline of events for a case"""
    from sqlalchemy import func
    
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    # Import timeline model if needed
    from app.models import CaseTimeline
    
    events = db.query(CaseTimeline).filter(
        CaseTimeline.case_id == case_id
    ).order_by(CaseTimeline.event_date).all()
    
    return {
        "case_id": case_id,
        "case_number": case.case_number,
        "timeline_events": [
            {
                "event_date": e.event_date.isoformat() if e.event_date else None,
                "event_type": e.event_type,
                "description": e.event_description
            }
            for e in events
        ]
    }


@router.get("/cases/{case_id}/hearings")
async def get_case_hearings(case_id: int, db: Session = Depends(get_db)):
    """Get hearing schedule for a case"""
    
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    from app.models import HearingDate
    
    hearings = db.query(HearingDate).filter(
        HearingDate.case_id == case_id
    ).order_by(HearingDate.hearing_date).all()
    
    return {
        "case_id": case_id,
        "case_number": case.case_number,
        "hearings": [
            {
                "hearing_date": h.hearing_date.isoformat() if h.hearing_date else None,
                "hearing_type": h.hearing_type,
                "court_room": h.court_room,
                "status": h.status
            }
            for h in hearings
        ]
    }


@router.get("/cases/{case_id}/appeals")
async def get_case_appeals(case_id: int, db: Session = Depends(get_db)):
    """Get appeal history for a case"""
    
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    from app.models import CaseAppeal
    
    appeals = db.query(CaseAppeal).filter(
        CaseAppeal.original_case_id == case_id
    ).all()
    
    return {
        "case_id": case_id,
        "case_number": case.case_number,
        "appeals": [
            {
                "appeal_case_number": a.appeal_case_number,
                "appeal_type": a.appeal_type,
                "appeal_date": a.appeal_date.isoformat() if a.appeal_date else None,
                "appeal_status": a.appeal_status,
                "appellate_court": a.appellate_court,
                "next_hearing_date": a.next_hearing_date.isoformat() if a.next_hearing_date else None
            }
            for a in appeals
        ]
    }


@router.get("/cases/{case_id}/references")
async def get_case_references(case_id: int, db: Session = Depends(get_db)):
    """Get related/referenced cases"""
    
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    from app.models import CaseReference
    
    references = db.query(CaseReference).filter(
        CaseReference.case_id == case_id
    ).all()
    
    return {
        "case_id": case_id,
        "case_number": case.case_number,
        "references": [
            {
                "referenced_case_number": r.referenced_case_number,
                "reference_type": r.reference_type,
                "description": r.description
            }
            for r in references
        ]
    }


@router.get("/cases/{case_id}/notes")
async def get_case_notes(case_id: int, db: Session = Depends(get_db)):
    """Get internal notes for a case"""
    
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    from app.models import CaseNote
    
    notes = db.query(CaseNote).filter(
        CaseNote.case_id == case_id
    ).order_by(CaseNote.created_at.desc()).all()
    
    return {
        "case_id": case_id,
        "case_number": case.case_number,
        "notes": [
            {
                "note_text": n.note_text,
                "note_type": n.note_type,
                "created_at": n.created_at.isoformat() if n.created_at else None
            }
            for n in notes
        ]
    }


@router.get("/cases-with-pending-appeals")
async def get_cases_with_pending_appeals(db: Session = Depends(get_db)):
    """Get all cases that have pending appeals"""
    
    from app.models import CaseAppeal
    
    cases_with_appeals = db.query(Case).join(
        CaseAppeal, Case.id == CaseAppeal.original_case_id
    ).filter(
        CaseAppeal.appeal_status.in_(["Pending", "Listed for Hearing"])
    ).all()
    
    return [
        {
            "case_id": c.id,
            "case_number": c.case_number,
            "case_type": c.case_type,
            "petitioner": c.petitioner,
            "respondent": c.respondent
        }
        for c in cases_with_appeals
    ]


@router.get("/upcoming-hearings")
async def get_upcoming_hearings(days: int = Query(30), db: Session = Depends(get_db)):
    """Get upcoming hearings in the next N days"""
    
    from app.models import HearingDate
    from sqlalchemy import func
    from datetime import datetime, timedelta
    
    future_date = datetime.utcnow() + timedelta(days=days)
    
    hearings = db.query(HearingDate, Case).join(
        Case, HearingDate.case_id == Case.id
    ).filter(
        HearingDate.hearing_date.between(datetime.utcnow(), future_date)
    ).order_by(HearingDate.hearing_date).all()
    
    return [
        {
            "case_number": c.case_number,
            "case_type": c.case_type,
            "hearing_date": h.hearing_date.isoformat() if h.hearing_date else None,
            "hearing_type": h.hearing_type,
            "court_room": h.court_room,
            "petitioner": c.petitioner,
            "respondent": c.respondent
        }
        for h, c in hearings
    ]


@router.get("/case-by-appeal-number/{appeal_case_number}")
async def get_case_by_appeal_number(appeal_case_number: str, db: Session = Depends(get_db)):
    """Find original case by appeal case number"""
    
    from app.models import CaseAppeal
    
    appeal = db.query(CaseAppeal).filter(
        CaseAppeal.appeal_case_number == appeal_case_number
    ).first()
    
    if not appeal:
        raise HTTPException(status_code=404, detail="Appeal not found")
    
    original_case = db.query(Case).filter(Case.id == appeal.original_case_id).first()
    
    return {
        "appeal_case_number": appeal_case_number,
        "original_case_number": original_case.case_number if original_case else None,
        "appeal_type": appeal.appeal_type,
        "appeal_status": appeal.appeal_status,
        "appellate_court": appeal.appellate_court
    }

'''

print("""
✅ Advanced API Routes Created!

These new endpoints should be added to: backend/app/routes/cases.py

New Endpoints:
1. GET /api/cases/{case_id}/timeline - Case event timeline
2. GET /api/cases/{case_id}/hearings - Hearing schedule
3. GET /api/cases/{case_id}/appeals - Appeal history
4. GET /api/cases/{case_id}/references - Related cases
5. GET /api/cases/{case_id}/notes - Internal notes
6. GET /api/cases-with-pending-appeals - Cases with pending appeals
7. GET /api/upcoming-hearings?days=30 - Upcoming hearings
8. GET /api/case-by-appeal-number/{number} - Find by appeal number

These routes enable:
📅 Case timeline tracking
⚖️ Appeal management
📋 Hearing scheduling
🔗 Case cross-references
📝 Internal documentation
⏰ Future hearing alerts
""")
