#!/bin/bash
# Manual setup script for Supabase (No Docker needed!)

echo "🚀 Setup for Court Ecosystem Backend with Supabase"

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.11 or higher."
    exit 1
fi

echo "✅ Python 3 found"

# Navigate to backend
cd backend

# Create virtual environment
echo "📦 Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "📚 Installing Python dependencies..."
pip install -r requirements.txt

# Setup environment
echo "⚙️  Setting up environment..."
cp .env.example .env
echo ""
echo "⚠️  IMPORTANT: Follow these steps:"
echo ""
echo "   1. Go to: https://app.supabase.com"
echo "   2. Create new project (or use existing)"
echo "   3. Go to: Settings → Database → Connection Pooling"
echo "   4. Select 'psycopg2' mode"
echo "   5. Copy the connection string"
echo "   6. Edit: backend/.env"
echo "   7. Paste into DATABASE_URL"
echo ""

echo "✅ Setup Complete! 🎉"
echo ""
echo "📋 Next Steps:"
echo "   1. Get Supabase connection string (see above)"
echo "   2. Edit backend/.env and set DATABASE_URL"
echo "   3. Run: uvicorn app.main:app --reload"
echo "   4. Open http://localhost:8000/docs"
echo ""
