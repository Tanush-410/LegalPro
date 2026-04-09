from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class CourtBase(BaseModel):
    name: str
    level: str
    state: Optional[str] = None
    district: Optional[str] = None

class CourtResponse(CourtBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class CaseBase(BaseModel):
    case_number: str
    case_type: str
    court_id: int
    petitioner: Optional[str] = None
    respondent: Optional[str] = None
    case_date: Optional[datetime] = None

class CaseResponse(CaseBase):
    id: int
    created_at: datetime
    court: Optional[CourtResponse] = None
    judge_name: Optional[str] = None
    pdf_url: Optional[str] = None
    case_status: Optional[str] = None
    case_description: Optional[str] = None
    priority: Optional[int] = None
    class Config:
        from_attributes = True

class JudgmentBase(BaseModel):
    case_id: int
    judge_name: Optional[str] = None
    judgment_date: datetime
    judgment_text: Optional[str] = None
    verdict: Optional[str] = None

class JudgmentResponse(JudgmentBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class DocumentBase(BaseModel):
    case_id: int
    judgment_id: Optional[int] = None
    file_name: str
    file_path: str
    file_type: str
    source_url: Optional[str] = None

class DocumentResponse(DocumentBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class DashboardStats(BaseModel):
    total_cases: int
    total_judgments: int
    supreme_court_count: int
    high_court_count: int
    lower_court_count: int
    today_cases: int
    last_scrape_time: Optional[datetime] = None
