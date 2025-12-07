#!/bin/bash
# Quick start script for Cyber Essentials Controller

set -e

echo "================================="
echo "Cyber Essentials Controller"
echo "================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    
    # Generate SECRET_KEY
    SECRET_KEY=$(openssl rand -hex 32)
    sed -i "s/your-secret-key-here-generate-with-openssl-rand-hex-32/$SECRET_KEY/" .env
    
    echo "✓ .env file created with random SECRET_KEY"
    echo "⚠️  Please review and update .env for production use"
    echo ""
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "ERROR: docker-compose not found"
    echo "Please install Docker and Docker Compose"
    exit 1
fi

echo "Starting services with Docker Compose..."
docker-compose up -d

echo ""
echo "Waiting for services to be ready..."
sleep 5

# Check health
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✓ Controller is running!"
    echo ""
    echo "================================="
    echo "Access Points:"
    echo "================================="
    echo "API:          http://localhost:8000"
    echo "API Docs:     http://localhost:8000/docs"
    echo "Health Check: http://localhost:8000/health"
    echo ""
    echo "Default Credentials:"
    echo "  Username: admin"
    echo "  Password: changeme"
    echo ""
    echo "⚠️  CHANGE DEFAULT PASSWORD IMMEDIATELY!"
    echo ""
    echo "To view logs:"
    echo "  docker-compose logs -f"
    echo ""
    echo "To stop:"
    echo "  docker-compose down"
    echo "================================="
else
    echo "⚠️  Controller may not be ready yet"
    echo "Check logs: docker-compose logs -f"
fi
