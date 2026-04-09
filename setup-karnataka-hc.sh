#!/bin/bash

# ============================================================================
# KARNATAKA HIGH COURT INTEGRATION SETUP GUIDE
# ============================================================================
# This script helps you set up the court ecosystem to use real judgment data
# from: https://judiciary.karnataka.gov.in
#
# Steps:
# 1. Create Supabase project
# 2. Configure environment variables
# 3. Create database schema
# 4. Install dependencies
# 5. Start backend and sync data
#
# ============================================================================

set -e

echo ""
echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                            ║"
echo "║          KARNATAKA HIGH COURT COURT ECOSYSTEM SETUP                        ║"
echo "║            Real Data from judiciary.karnataka.gov.in                       ║"
echo "║                                                                            ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Step 1: Check if Supabase credentials are configured
echo "📋 STEP 1: Checking Supabase configuration..."
echo ""

if [ -f ".env" ]; then
    if grep -q "SUPABASE_URL" .env && grep -q "SUPABASE_ANON_KEY" .env; then
        echo "✅ Found .env with Supabase credentials"
    else
        echo "⚠️  .env exists but missing Supabase settings"
        echo "   Please add SUPABASE_URL and SUPABASE_ANON_KEY"
    fi
else
    echo "❌ No .env file found"
    echo ""
    echo "Please follow these steps to get Supabase credentials:"
    echo ""
    echo "1️⃣  Go to: https://supabase.com/dashboard"
    echo "2️⃣  Sign up or log in"
    echo "3️⃣  Create a new project (if needed)"
    echo "4️⃣  Go to Settings → API"
    echo "5️⃣  Copy 'Project URL' → SUPABASE_URL"
    echo "6️⃣  Copy 'anon public' key → SUPABASE_ANON_KEY"
    echo ""
    echo "Then create backend/.env:"
    echo ""
    cat << 'ENVFILE'
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here
COURT_SOURCE=karnataka_hc
COURT_LEVEL=High Court
ENABLE_SCHEDULER=true
SYNC_INTERVAL_HOURS=24
ENVFILE
    echo ""
    exit 1
fi

echo ""
echo "📋 STEP 2: Checking database schema..."
echo ""

if [ -f "SUPABASE_SCHEMA.sql" ]; then
    echo "✅ Found database schema file"
    echo ""
    echo "⚠️  IMPORTANT: Run this SQL in Supabase before continuing:"
    echo ""
    echo "1️⃣  Go to: https://supabase.com/dashboard"
    echo "2️⃣  Select your project"
    echo "3️⃣  Go to SQL Editor"
    echo "4️⃣  Click 'New Query'"
    echo "5️⃣  Copy & paste contents of SUPABASE_SCHEMA.sql"
    echo "6️⃣  Click 'Run'"
    echo ""
    read -p "Press Enter once you've created the schema in Supabase..."
else
    echo "❌ SUPABASE_SCHEMA.sql not found"
    exit 1
fi

echo ""
echo "📋 STEP 3: Installing Python dependencies..."
echo ""

cd backend

# Check if venv exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate venv
source .venv/bin/activate || . .venv/Scripts/activate

# Install requirements
echo "Installing packages..."
pip install -q -r requirements.txt

echo "✅ Dependencies installed"

echo ""
echo "📋 STEP 4: Starting backend server..."
echo ""

# Kill any existing process on port 8000
pkill -f "uvicorn" || true
sleep 2

# Start server
echo "Starting FastAPI server..."
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > /tmp/server.log 2>&1 &

SERVER_PID=$!
sleep 5

# Check if server started
if kill -0 $SERVER_PID 2>/dev/null; then
    echo "✅ Server started (PID: $SERVER_PID)"
else
    echo "❌ Server failed to start!"
    echo "Check server log:"
    tail -20 /tmp/server.log
    exit 1
fi

echo ""
echo "📋 STEP 5: Syncing Karnataka HC judgment data..."
echo ""

# Give server a moment to fully initialize
sleep 3

# Trigger sync
echo "Fetching data from judiciary.karnataka.gov.in..."

SYNC_RESPONSE=$(curl -s http://localhost:8000/api/karnataka-hc/sync -X POST)

echo "$SYNC_RESPONSE" | python3 -m json.tool

# Check stats
echo ""
echo "Checking data status..."
STATS=$(curl -s http://localhost:8000/api/karnataka-hc/stats)

TOTAL=$(echo "$STATS" | python3 -c "import sys, json; print(json.load(sys.stdin).get('stats', {}).get('total_cases', 0))")

if [ "$TOTAL" -gt 0 ]; then
    echo "✅ Data synced! Found $TOTAL cases"
else
    echo "⚠️  Still loading data... Check again in a moment"
fi

echo ""
echo "═══════════════════════════════════════════════════════════════════════════════"
echo "✅ SETUP COMPLETE"
echo "═══════════════════════════════════════════════════════════════════════════════"
echo ""
echo "🌐 Access your dashboard:"
echo "   http://localhost:8000/dashboard"
echo ""
echo "📊 API Endpoints:"
echo "   GET  http://localhost:8000/api/karnataka-hc/statistics"
echo "   GET  http://localhost:8000/api/karnataka-hc/cases"
echo "   GET  http://localhost:8000/api/karnataka-hc/cases/{case_number}"
echo "   GET  http://localhost:8000/api/karnataka-hc/documents"
echo "   POST http://localhost:8000/api/karnataka-hc/sync (manual sync)"
echo ""
echo "💾 Data Source:"
echo "   Website: https://judiciary.karnataka.gov.in"
echo "   Data: Real judgment orders from Karnataka High Court"
echo "   Database: Supabase PostgreSQL"
echo ""
echo "📚 Documentation:"
echo "   See KARNATAKA_HC_SETUP.md for detailed instructions"
echo ""
echo "═══════════════════════════════════════════════════════════════════════════════"
echo ""
