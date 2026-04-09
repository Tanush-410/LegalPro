from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
import uuid
from .database import Base

class CourtEnum(str, enum.Enum):
    SUPREME = "Supreme Court"
    HIGH = "High Court"
    LOWER = "Lower Court"

class User(Base):
    """User model for authentication"""
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, index=True)
    password_hash = Column(String(255), nullable=True)
    name = Column(String(255))
    google_id = Column(String(255), nullable=True, unique=True, index=True)
    profile_picture = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<User {self.email}>"

class Court(Base):
    __tablename__ = "courts"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True)
    level = Column(Enum(CourtEnum))
    state = Column(String(100), nullable=True)  # For high courts
    district = Column(String(100), nullable=True)  # For lower courts
    created_at = Column(DateTime, default=datetime.utcnow)
    
    cases = relationship("Case", back_populates="court")
    scrape_logs = relationship("ScrapeLog", back_populates="court")

class Case(Base):
    __tablename__ = "cases"
    
    id = Column(Integer, primary_key=True, index=True)
    cnr = Column(String(255), unique=True, index=True, nullable=True)  # Case Number Record (e.g., DELHC0123456789)
    case_number = Column(String(255), unique=True, index=True)
    case_type = Column(String(100), index=True)  # "Writ Petition", etc.
    case_description = Column(String(2000), nullable=True)  # Detailed case description for reports
    court_id = Column(Integer, ForeignKey("courts.id"))
    petitioner = Column(String(500), nullable=True)
    respondent = Column(String(500), nullable=True)
    case_date = Column(DateTime, index=True)
    pdf_url = Column(String(2048), nullable=True)  # Link to PDF judgment document
    case_status = Column(String(100), default="Pending", nullable=True)  # Pending, Active, Closed, etc.
    priority = Column(Integer, default=0, nullable=True)  # Priority level (0-5, 0 = lowest)
    is_new = Column(Boolean, default=True, index=True)  # Track if this is a freshly detected case
    first_detected_at = Column(DateTime, default=datetime.utcnow, index=True)  # When we first found this case
    created_at = Column(DateTime, default=datetime.utcnow)
    
    court = relationship("Court", back_populates="cases")
    judgments = relationship("Judgment", back_populates="case")
    documents = relationship("Document", back_populates="case")

class Judgment(Base):
    __tablename__ = "judgments"
    
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"))
    judge_name = Column(String(255), nullable=True)
    judgment_date = Column(DateTime, index=True)
    judgment_text = Column(Text, nullable=True)
    verdict = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    case = relationship("Case", back_populates="judgments")
    documents = relationship("Document", back_populates="judgment")

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"))
    judgment_id = Column(Integer, ForeignKey("judgments.id"), nullable=True)
    file_name = Column(String(512))
    file_path = Column(String(2048))  # Local path or URL
    file_type = Column(String(20))  # pdf, html, txt
    file_size = Column(Integer, nullable=True)
    source_url = Column(String(2048), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    case = relationship("Case", back_populates="documents")
    judgment = relationship("Judgment", back_populates="documents")
    extracted_metadata = relationship("DocumentMetadata", back_populates="document")

class DocumentMetadata(Base):
    __tablename__ = "document_metadata"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    key = Column(String(255))
    value = Column(Text)
    extracted_at = Column(DateTime, default=datetime.utcnow)
    
    document = relationship("Document", back_populates="extracted_metadata")

class ScrapeLog(Base):
    __tablename__ = "scrape_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    court_id = Column(Integer, ForeignKey("courts.id"))
    scrape_date = Column(DateTime, index=True)
    status = Column(String(50))  # "success", "failure"
    cases_found = Column(Integer, default=0)
    cases_saved = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    execution_time = Column(Integer, nullable=True)  # seconds
    created_at = Column(DateTime, default=datetime.utcnow)
    
    court = relationship("Court", back_populates="scrape_logs")
