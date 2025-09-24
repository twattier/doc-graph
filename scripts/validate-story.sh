#!/bin/bash
# Validate a user story before merge to master
# Usage: ./scripts/validate-story.sh <story-id>

set -e

if [ $# -ne 1 ]; then
    echo "Usage: $0 <story-id>"
    echo "Example: $0 1.2"
    exit 1
fi

STORY_ID="$1"
STORY_FILE="docs/backlog/stories/${STORY_ID}.story.md"

echo "🔍 Validating Story ${STORY_ID}..."

# Check if story file exists
if [ ! -f "$STORY_FILE" ]; then
    echo "❌ Story file not found: $STORY_FILE"
    exit 1
fi

echo "📄 Story file found: $STORY_FILE"

# Check if we're on the correct branch
CURRENT_BRANCH=$(git branch --show-current)
if [[ ! $CURRENT_BRANCH =~ ^story/${STORY_ID}- ]]; then
    echo "⚠️  Warning: Current branch '$CURRENT_BRANCH' doesn't match story pattern 'story/${STORY_ID}-*'"
fi

# Update with latest master
echo "📥 Syncing with master branch..."
git fetch origin master
git rebase origin/master

# Start development environment
echo "🐳 Starting Docker development environment..."
docker-compose -f docker-compose.dev.yml up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Run type checking in containers
echo "🔧 Running type checks..."
if [ -f "apps/web/package.json" ]; then
    docker-compose -f docker-compose.dev.yml exec -T web npm run type-check || {
        echo "❌ TypeScript type checking failed"
        docker-compose -f docker-compose.dev.yml down
        exit 1
    }
fi

if [ -f "apps/api/mypy.ini" ]; then
    docker-compose -f docker-compose.dev.yml exec -T api python -m mypy src/ || {
        echo "❌ Python type checking failed"
        docker-compose -f docker-compose.dev.yml down
        exit 1
    }
fi

# Run linting in containers
echo "🧹 Running linting..."
if [ -f "apps/web/package.json" ]; then
    docker-compose -f docker-compose.dev.yml exec -T web npm run lint || {
        echo "❌ Frontend linting failed"
        docker-compose -f docker-compose.dev.yml down
        exit 1
    }
fi

if [ -f "apps/api/requirements.txt" ]; then
    docker-compose -f docker-compose.dev.yml exec -T api flake8 src/ || {
        echo "❌ Python linting failed"
        docker-compose -f docker-compose.dev.yml down
        exit 1
    }
fi

# Run tests in containers
echo "🧪 Running tests..."
if [ -f "apps/web/package.json" ]; then
    docker-compose -f docker-compose.dev.yml exec -T web npm test || {
        echo "❌ Frontend tests failed"
        docker-compose -f docker-compose.dev.yml down
        exit 1
    }
fi

if [ -f "apps/api/pytest.ini" ]; then
    docker-compose -f docker-compose.dev.yml exec -T api pytest tests/ || {
        echo "❌ Backend tests failed"
        docker-compose -f docker-compose.dev.yml down
        exit 1
    }
fi

# Build check in containers
echo "🏗️  Running build check..."
if [ -f "apps/web/package.json" ]; then
    docker-compose -f docker-compose.dev.yml exec -T web npm run build || {
        echo "❌ Build failed"
        docker-compose -f docker-compose.dev.yml down
        exit 1
    }
fi

# Stop development environment
echo "🐳 Stopping Docker development environment..."
docker-compose -f docker-compose.dev.yml down

echo "✅ All validation checks passed!"
echo "📋 Pre-merge checklist:"
echo "   □ All acceptance criteria implemented"
echo "   □ Dev notes updated in story file"
echo "   □ No sensitive data in commits"
echo "   □ Breaking changes documented"
echo "   □ Story status updated to 'Code Review'"
echo ""
echo "🎯 Ready for merge! Run 'scripts/merge-story.sh ${STORY_ID}' when ready."