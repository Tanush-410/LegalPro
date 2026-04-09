#!/usr/bin/env python3
import sys
import os

# Add backend to path
sys.path.insert(0, "/Volumes/PortableSSD/court-ecosystem/backend")

# Force the database URL to the PortableSSD location
os.environ["DATABASE_URL"] = "sqlite:////Volumes/PortableSSD/court-ecosystem/data/court_ecosystem.db"

# Ensure data directory exists
os.makedirs("/Volumes/PortableSSD/court-ecosystem/data", exist_ok=True)

try:
    from app.database import engine, Base
    from app.models import *
    
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully at:", os.path.expanduser("~/../../Volumes/PortableSSD/court-ecosystem/data/court_ecosystem.db"))
    
    # Verify
    db_file = "/Volumes/PortableSSD/court-ecosystem/data/court_ecosystem.db"
    if os.path.exists(db_file):
        print(f"✅ Database file exists: {db_file}")
    
    # Close connections
    engine.dispose()
    print("✅ Engine disposed")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
