from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

load_dotenv()

# Default to data directory for SQLite
# Use relative path that works on any system
_db_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")

# Ensure directory exists
os.makedirs(_db_dir, exist_ok=True)

_db_file = os.path.join(_db_dir, "court_ecosystem.db")
# Use sqlite:/// with path
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
