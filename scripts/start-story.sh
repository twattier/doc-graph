#!/bin/bash
# Start development on a new user story
# Usage: ./scripts/start-story.sh <story-id> <short-description>

set -e

if [ $# -ne 2 ]; then
    echo "Usage: $0 <story-id> <short-description>"
    echo "Example: $0 1.2 user-authentication"
    exit 1
fi

STORY_ID="$1"
DESCRIPTION="$2"
BRANCH_NAME="story/${STORY_ID}-${DESCRIPTION}"

echo "🚀 Starting development for Story ${STORY_ID}: ${DESCRIPTION}"
echo "📝 Branch name: ${BRANCH_NAME}"

# Ensure we're on master and up to date
echo "📥 Updating master branch..."
git checkout master
git pull origin master

# Create and checkout the story branch
echo "🌿 Creating story branch..."
git checkout -b "$BRANCH_NAME"

echo "✅ Story branch created successfully!"
echo "📋 Next steps:"
echo "   1. Update story status to 'In Progress'"
echo "   2. Start Docker development environment:"
echo "      docker-compose -f docker-compose.dev.yml up -d"
echo "   3. Follow acceptance criteria in docs/backlog/stories/${STORY_ID}.story.md"
echo "   4. Access container shells for development:"
echo "      docker-compose -f docker-compose.dev.yml exec web bash"
echo "      docker-compose -f docker-compose.dev.yml exec api bash"
echo "   5. Make frequent commits with descriptive messages"
echo "   6. Run 'scripts/validate-story.sh ${STORY_ID}' before completion"
echo ""
echo "🐳 Remember: All development happens in Docker containers!"
echo "🎯 Happy coding!"