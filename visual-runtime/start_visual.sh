#!/bin/bash

# OpenHands Visual Runtime Startup Script

echo "🚀 Starting OpenHands Visual Runtime System"
echo "=========================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Build the visual runtime image
echo ""
echo "🐳 Building Visual Runtime Docker image..."
docker build -t openhands/visual-runtime .

if [ $? -eq 0 ]; then
    echo "✅ Docker image built successfully"
else
    echo "❌ Docker build failed"
    exit 1
fi

# Start the visual runtime container
echo ""
echo "🔧 Starting Visual Runtime container..."
docker-compose up -d visual-runtime

if [ $? -eq 0 ]; then
    echo "✅ Visual Runtime container started"
    echo ""
    echo "🌐 Access Points:"
    echo "   • Visual Desktop: http://localhost:7900/vnc.html"
    echo "   • OpenHands API:  http://localhost:3000"
    echo ""
    echo "📋 Test the system:"
    echo "   python test_visual.py"
    echo ""
    echo "📝 API Examples:"
    echo "   curl -X POST http://localhost:3000/api/visual-sessions \\"
    echo "     -H \"Content-Type: application/json\" \\"
    echo "     -d '{\"resolution\": \"1600x900\", \"timeout_minutes\": 60}'"
else
    echo "❌ Failed to start Visual Runtime container"
    exit 1
fi

echo ""
echo "🎯 Visual Runtime is ready!"
echo "   Agents will now run in visible desktop environments"