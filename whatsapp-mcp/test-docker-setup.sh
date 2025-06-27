#!/bin/bash

echo "🚀 Testing WhatsApp MCP Docker Setup"
echo "====================================="

# Build and start the services
echo "📦 Building and starting services..."
docker-compose up -d --build

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 10

# Check if containers are running
echo "🔍 Checking container status..."
docker-compose ps

# Test WhatsApp bridge connectivity
echo "🌐 Testing WhatsApp bridge connectivity..."
if curl -s http://localhost:8080/api/send > /dev/null 2>&1; then
    echo "✅ WhatsApp bridge is responding"
else
    echo "❌ WhatsApp bridge is not responding"
fi

# Check container logs
echo "📋 Container logs:"
echo "WhatsApp Bridge logs:"
docker-compose logs whatsapp-bridge --tail=10

echo ""
echo "MCP Server logs:"
docker-compose logs whatsapp-mcp-server --tail=10

echo ""
echo "🎉 Setup complete! The services are running."
echo "📱 To use WhatsApp, scan the QR code that appears in the bridge logs."
echo "🔧 To stop services: docker-compose down" 