from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os
import sys

load_dotenv()

# Default to data directory for SQLite
# Use relative path that works on any system
_db_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")

# Ensure directory exists
try:
    os.makedirs(_db_dir, exist_ok=True)
    os.chmod(_db_dir, 0o755)
except Exception as e:
    print(f"ERROR: Could not create data directory {_db_dir}: {e}", file=sys.stderr)
    raise

_db_file = os.path.join(_db_dir, "court_ecosystem.db")
# Use sqlite:/// with absolute path (3 slashes for path starting with /)
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{_db_file}")

print(f"[DATABASE] Using database: {_db_file}", file=sys.stderr)
print(f"[DATABASE] Database URL: {DATABASE_URL}", file=sys.stderr)

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
