#!/bin/bash

# Reset development databases script
# WARNING: This will delete all data

set -e

echo "⚠️  WARNING: This will delete all development data!"
read -p "Are you sure you want to continue? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 1
fi

echo "🛑 Stopping database services..."
docker-compose -f docker-compose.dev.yml down

echo "🗑️ Removing data volumes..."
docker-compose -f docker-compose.dev.yml down -v
rm -rf data/

echo "📁 Creating fresh data directories..."
mkdir -p data/postgres data/neo4j/data data/neo4j/logs data/neo4j/import data/redis

echo "🚀 Starting database services..."
docker-compose -f docker-compose.dev.yml up -d

echo "⏳ Waiting for databases to be ready..."
sleep 15

echo "✅ Development databases have been reset!"
echo "📊 Sample data has been loaded automatically."