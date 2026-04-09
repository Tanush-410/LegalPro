from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

load_dotenv()

# Default to data directory for SQLite
# Explicitly set to absolute path
_db_file = "/Volumes/PortableSSD/court-ecosystem/data/court_ecosystem.db"
os.makedirs(os.path.dirname(_db_file), exist_ok=True)
# Use sqlite:// with absolute path
# For absolute paths on Unix, the format is: sqlite:////absolute/path
# The four slashes are: sqlite:// (scheme) + // (authority) + /absolute/path
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{_db_file}")

# Configure engine based on database type
if DATABASE_URL.startswith("sqlite"):
    # SQLite configuration
    engine = create_engine(
        DATABASE_URL,
        echo=False,
        connect_args={"check_same_thread": False}
    )
    
    # Enable foreign keys for SQLite
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
else:
    # PostgreSQL configuration
    engine = create_engine(
        DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
