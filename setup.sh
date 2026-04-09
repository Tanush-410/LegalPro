#!/bin/bash
# Setup script for Court Ecosystem Backend

echo "🚀 Setting up Court Ecosystem Backend..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose not found. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose found"

# Build and start services
echo "📦 Building Docker images..."
docker-compose build

echo "🚀 Starting services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check service status
echo "\n📊 Service Status:"
docker-compose ps

# Print access information
echo "\n✅ Setup Complete! 🎉"
echo ""
echo "📍 Access Points:"
echo "   API Documentation: http://localhost:8000/docs"
echo "   API Health Check: http://localhost:8000/health"
echo "   Dashboard: http://localhost:3000"
echo "   Database: localhost:5432 (user: court_user)"
echo ""
echo "📋 Next Steps:"
echo "   1. Open http://localhost:8000/docs for API documentation"
echo "   2. Open http://localhost:3000 to view the dashboard"
echo "   3. Check logs: docker-compose logs -f api"
echo ""
echo "🛑 To stop services: docker-compose down"
echo "🔄 To restart services: docker-compose restart"
