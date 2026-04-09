#!/bin/bash

# ============================================================================
# Court Ecosystem - Production Setup Script
# Sets up automatic data ingestion and starts the web server
# ============================================================================

PROJECT_DIR="/Users/tanush.s.vashisht/Desktop/Tanush/work/court-ecosystem"
BACKEND_DIR="$PROJECT_DIR/backend"
LOG_DIR="$PROJECT_DIR/logs"
SEED_DATA_FLAG="$PROJECT_DIR/.data_seeded"
CRON_JOB_FLAG="$PROJECT_DIR/.cron_installed"

# Create logs directory
mkdir -p "$LOG_DIR"

echo "=================================="
echo "🚀 Court Ecosystem Setup"
echo "=================================="

# ============================================================================
# Step 1: Initialize Database
# ============================================================================
echo ""
echo "📦 Step 1: Initializing database..."

cd "$BACKEND_DIR"

python3 << 'EOF'
import sys
sys.path.insert(0, '/Users/tanush.s.vashisht/Desktop/Tanush/work/court-ecosystem/backend')

from app.database import engine
from app.models import Base, Court, CourtEnum
from sqlalchemy.orm import sessionmaker

# Create tables
Base.metadata.create_all(bind=engine)
print("✅ Database schema created")

# Seed default courts
Session = sessionmaker(bind=engine)
db = Session()

default_courts = [
    ("High Court of India", CourtEnum.HIGH, "National"),
    ("National Judicial Grid", CourtEnum.SUPREME, "National"),
    ("Bengaluru District Court", CourtEnum.LOWER, "Karnataka"),
    ("Delhi District Court", CourtEnum.LOWER, "Delhi"),
    ("Bombay High Court", CourtEnum.HIGH, "Maharashtra"),
]

for name, level, state in default_courts:
    if not db.query(Court).filter(Court.name == name).first():
        db.add(Court(name=name, level=level, state=state))
        print(f"✅ Added: {name}")

db.commit()
db.close()
EOF

# ============================================================================
# Step 2: Run Initial Data Ingestion
# ============================================================================
echo ""
echo "📥 Step 2: Running initial data ingestion..."
echo "   (This may take 30-60 seconds)"
echo ""

cd "$BACKEND_DIR"
python3 ingest_real_ecourts_data.py >> "$LOG_DIR/initial_ingestion.log" 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Initial data ingestion complete"
    touch "$SEED_DATA_FLAG"
else
    echo "⚠️  Initial ingestion had errors (check logs/initial_ingestion.log)"
fi

# ============================================================================
# Step 3: Setup Automated Cron Job
# ============================================================================
echo ""
echo "⏰ Step 3: Setting up automated data updates..."

CRON_CMD="0 */6 * * * cd $BACKEND_DIR && python3 ingest_real_ecourts_data.py >> $LOG_DIR/cron_ingestion.log 2>&1"

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "ingest_real_ecourts_data.py"; then
    echo "✅ Cron job already installed"
else
    # Add cron job
    (crontab -l 2>/dev/null || echo ""; echo "$CRON_CMD") | crontab -
    if [ $? -eq 0 ]; then
        echo "✅ Cron job installed (runs every 6 hours)"
        touch "$CRON_JOB_FLAG"
    else
        echo "⚠️  Could not install cron job (may need manual setup)"
    fi
fi

# ============================================================================
# Step 4: Start Web Server
# ============================================================================
echo ""
echo "🌐 Step 4: Starting web server..."

# Kill any existing servers
pkill -f "uvicorn app.main:app" 2>/dev/null
sleep 2

# Start new server in background
cd "$PROJECT_DIR"
nohup bash -c "PYTHONPATH=$BACKEND_DIR:$PYTHONPATH python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000" > "$LOG_DIR/server.log" 2>&1 &

sleep 3

# Check if server started
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Web server started successfully"
else
    echo "⚠️  Server may be starting... (check logs/server.log)"
fi

# ============================================================================
# Step 5: Print Summary
# ============================================================================
echo ""
echo "=================================="
echo "✅ SETUP COMPLETE"
echo "=================================="
echo ""
echo "📊 Dashboard Statistics:"
curl -s http://localhost:8000/api/dashboard/stats | python3 -m json.tool 2>/dev/null || echo "  (Server starting, try again in 10 seconds)"
echo ""
echo "🌐 Access your website:"
echo "   URL: http://localhost:8000/dashboard"
echo ""
echo "📋 View API data:"
echo "   curl http://localhost:8000/api/dashboard/stats | jq ."
echo ""
echo "📊 Check logs:"
echo "   - Server: tail -f $LOG_DIR/server.log"
echo "   - Ingestion: tail -f $LOG_DIR/cron_ingestion.log"
echo ""
echo "⏰ Automatic updates:"
echo "   Every 6 hours: New data is automatically fetched from eCourts"
echo ""
echo "=================================="
