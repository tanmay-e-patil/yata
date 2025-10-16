#!/bin/bash

echo "🚀 Starting Yata Todo App Test Script"
echo "====================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Please copy .env.example to .env and configure it."
    exit 1
fi

# Check if Google OAuth credentials are set
if ! grep -q "GOOGLE_CLIENT_ID=your-google-client-id" .env; then
    echo "✅ Google OAuth credentials appear to be configured"
else
    echo "⚠️  Warning: Google OAuth credentials are not configured in .env file"
    echo "   The app will start but authentication won't work until you configure them."
fi

echo ""
echo "🐳 Starting Docker Compose..."
docker-compose -f docker-compose.dev.yml up --build -d

echo ""
echo "⏳ Waiting for services to start..."
sleep 10

# Check if backend is healthy
echo "🔍 Checking backend health..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend is healthy"
else
    echo "❌ Backend is not responding"
    docker-compose -f docker-compose.dev.yml logs backend
    exit 1
fi

# Check if frontend is accessible
echo "🔍 Checking frontend..."
if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ Frontend is accessible"
else
    echo "❌ Frontend is not responding"
    docker-compose -f docker-compose.dev.yml logs frontend
    exit 1
fi

echo ""
echo "🎉 Application is running successfully!"
echo ""
echo "📱 Access the application at:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Documentation: http://localhost:8000/docs"
echo ""
echo "📝 To test the application:"
echo "   1. Open http://localhost:3000 in your browser"
echo "   2. Click 'Sign in with Google' to authenticate"
echo "   3. Create, edit, and delete todos"
echo ""
echo "🛑 To stop the application, run:"
echo "   docker-compose -f docker-compose.dev.yml down"
echo ""
echo "📋 To view logs, run:"
echo "   docker-compose -f docker-compose.dev.yml logs -f"