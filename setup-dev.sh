#!/bin/bash

# DocGraph Development Setup Script
# This script sets up the Docker-based development environment for DocGraph

set -e

echo "🚀 Setting up DocGraph Docker development environment..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if Docker Compose is available
if ! docker compose version > /dev/null 2>&1; then
    echo "❌ Docker Compose is not available. Please install Docker Compose and try again."
    exit 1
fi

echo "✅ Prerequisites check passed (Docker only - no local Node.js/Python required)"

# Copy environment files if they don't exist
if [ ! -f .env ]; then
    echo "📄 Creating .env file from .env.example..."
    cp .env.example .env
else
    echo "📄 .env file already exists, skipping..."
fi

if [ ! -f apps/web/.env.local ]; then
    echo "📄 Creating frontend .env.local file..."
    cp apps/web/.env.example apps/web/.env.local
else
    echo "📄 Frontend .env.local file already exists, skipping..."
fi

# Note: Dependencies will be installed inside Docker containers during build
echo "📦 Dependencies will be installed automatically in Docker containers"

# Create data directories
echo "📁 Creating data directories..."
mkdir -p data/postgres data/neo4j/data data/neo4j/logs data/neo4j/import data/redis

# Start database services
echo "🗄️ Starting database services..."
docker-compose -f docker-compose.dev.yml up -d

# Wait for databases to be ready
echo "⏳ Waiting for databases to be ready..."
sleep 10

# Check database health
echo "🏥 Checking database health..."
timeout 30s bash -c 'until docker-compose -f docker-compose.dev.yml exec -T postgres pg_isready -U docgraph_user; do sleep 1; done' || {
    echo "❌ PostgreSQL failed to start properly"
    docker-compose -f docker-compose.dev.yml logs postgres
    exit 1
}

timeout 30s bash -c 'until docker-compose -f docker-compose.dev.yml exec -T redis redis-cli -a secure_dev_redis_password ping | grep -q PONG; do sleep 1; done' || {
    echo "❌ Redis failed to start properly"
    docker-compose -f docker-compose.dev.yml logs redis
    exit 1
}

timeout 30s bash -c 'until docker-compose -f docker-compose.dev.yml exec -T neo4j cypher-shell -u neo4j -p secure_dev_neo4j_password "RETURN 1"; do sleep 1; done' || {
    echo "❌ Neo4j failed to start properly"
    docker-compose -f docker-compose.dev.yml logs neo4j
    exit 1
}

echo "✅ All databases are running and healthy!"

echo "🎉 Development environment setup complete!"
echo ""
echo "Next steps:"
echo "  1. Start all services: docker compose up -d"
echo "  2. Open http://localhost:3000 in your browser"
echo "  3. View application containers: docker compose ps"
echo ""
echo "Database access:"
echo "  - PostgreSQL: localhost:5433 (user: docgraph_user, password: secure_dev_password)"
echo "  - Neo4j Browser: http://localhost:7475 (user: neo4j, password: secure_dev_neo4j_password)"
echo "  - Redis: localhost:6380 (password: secure_dev_redis_password)"
echo ""
echo "To stop the databases: docker-compose -f docker-compose.dev.yml down"