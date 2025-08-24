#!/bin/bash

echo "🚀 Starting Social Media Forge..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Please copy .env.example to .env and configure your API keys."
    exit 1
fi

# Start services with Docker Compose
echo "📦 Starting services with Docker Compose..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Check service health
echo "🔍 Checking service health..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend is healthy"
else
    echo "❌ Backend health check failed"
    echo "📋 Service logs:"
    docker-compose logs backend
    exit 1
fi

# Initialize database
echo "🗄️ Initializing database..."
docker-compose exec -T backend python -m app.scripts.init_db

echo ""
echo "🎉 Social Media Forge is ready!"
echo ""
echo "📱 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo "🔐 Admin Login: admin@example.com"
echo "🔑 Admin Password: JustinIsNotReallySocial%789"
echo ""
echo "To stop services: docker-compose down"
echo "To view logs: docker-compose logs -f"
