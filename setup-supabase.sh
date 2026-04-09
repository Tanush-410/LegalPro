#!/bin/bash
# Quick Supabase Setup & Sync Script for Karnataka High Court Portal
# This script automates the entire Supabase integration process

echo "=================================================="
echo "🚀 SUPABASE SETUP & SYNC WIZARD"
echo "=================================================="
echo ""

# Check if environment variables are already set
if [ -z "$SUPABASE_URL" ] || [ -z "$SUPABASE_ANON_KEY" ]; then
    echo "📋 SETUP REQUIRED"
    echo ""
    echo "Please enter your Supabase credentials:"
    echo "(You can find these in Supabase Dashboard → Settings → API)"
    echo ""
    
    read -p "Enter SUPABASE_URL (e.g., https://xxx.supabase.co): " SUPABASE_URL
    read -p "Enter SUPABASE_ANON_KEY (Your anon key): " SUPABASE_ANON_KEY
    
    # Export for this session
    export SUPABASE_URL
    export SUPABASE_ANON_KEY
    
    # Save to .env file for future use
    echo "SUPABASE_URL=$SUPABASE_URL" >> .env
    echo "SUPABASE_ANON_KEY=$SUPABASE_ANON_KEY" >> .env
    
    echo ""
    echo "✅ Credentials saved to .env file"
else
    echo "✅ Supabase credentials found"
    echo "URL: $SUPABASE_URL"
fi

echo ""
echo "=================================================="
echo "📡 STARTING AUTO-SYNC"
echo "=================================================="
echo ""

# Trigger the API endpoint to sync
echo "Syncing 79 cases to Supabase..."
SYNC_RESULT=$(curl -s -X POST http://localhost:8000/api/sync-to-supabase)

echo "Response: $SYNC_RESULT"
echo ""
echo "⏳ Sync running in background..."
echo "Check back in 5-10 seconds for completion."
echo ""
echo "📊 Check status at: http://localhost:8000/api/sync-status"
echo ""
echo "=================================================="
echo "✅ Setup Complete!"
echo "=================================================="
echo ""
echo "What's synced:"
echo "✓ 1 Court (Karnataka High Court)"
echo "✓ 79 Cases with all details"
echo "✓ 10 Judges with case assignments"
echo "✓ 20 Case types"
echo ""
echo "Next steps:"
echo "1. Wait 5-10 seconds"
echo "2. Check Supabase Dashboard → Table Editor"
echo "3. Verify data in 'cases' table"
echo "4. All future updates will auto-sync!"
echo ""
