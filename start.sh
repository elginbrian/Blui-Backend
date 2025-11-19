#!/bin/bash

# Blui Backend Docker Setup Script

echo "🚀 Starting Blui Backend with Docker Compose..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed."
    exit 1
fi

echo "🐳 Building and starting services..."
docker-compose up --build -d

echo "⏳ Waiting for services to be healthy..."
sleep 10

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    echo "✅ Services are running!"
    echo ""
    echo "🌐 API available at: http://localhost:8000"
    echo "📚 Documentation at: http://localhost:8000/docs"
    echo "🗄️ Database at: localhost:5432"
    echo ""
    echo "📋 Useful commands:"
    echo "  docker-compose logs -f          # View logs"
    echo "  docker-compose down             # Stop services"
    echo "  docker-compose restart          # Restart services"
else
    echo "❌ Failed to start services. Check logs with: docker-compose logs"
    exit 1
fi