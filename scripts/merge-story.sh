#!/bin/bash
# Merge a completed and validated user story to master
# Usage: ./scripts/merge-story.sh <story-id>

set -e

if [ $# -ne 1 ]; then
    echo "Usage: $0 <story-id>"
    echo "Example: $0 1.2"
    exit 1
fi

STORY_ID="$1"
STORY_FILE="docs/backlog/stories/${STORY_ID}.story.md"

# Find the story branch
STORY_BRANCH=$(git branch --list "story/${STORY_ID}-*" | sed 's/^..//')
if [ -z "$STORY_BRANCH" ]; then
    echo "❌ No story branch found for Story ${STORY_ID}"
    echo "Expected pattern: story/${STORY_ID}-*"
    exit 1
fi

echo "🔄 Merging Story ${STORY_ID} from branch: ${STORY_BRANCH}"

# Confirm the merge
read -p "⚠️  Are you sure you want to merge '$STORY_BRANCH' to master? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Merge cancelled"
    exit 1
fi

# Ensure we're on the story branch and up to date
echo "📥 Preparing for merge..."
git checkout "$STORY_BRANCH"
git fetch origin master
git rebase origin/master

# Final validation run
echo "🔍 Running final validation..."
./scripts/validate-story.sh "$STORY_ID"

# Switch to master and merge
echo "🔄 Merging to master..."
git checkout master
git pull origin master
git merge --no-ff "$STORY_BRANCH" -m "feat(story-${STORY_ID}): Complete Story ${STORY_ID}

$(git log --oneline master..${STORY_BRANCH} | sed 's/^/- /')

Story validation completed successfully.
All acceptance criteria met and tests passing."

# Push to remote
echo "📤 Pushing to remote..."
git push origin master

# Clean up the story branch
echo "🧹 Cleaning up story branch..."
git branch -d "$STORY_BRANCH"

# Try to delete remote branch (may not exist)
git push origin --delete "$STORY_BRANCH" 2>/dev/null || echo "ℹ️  Remote branch already deleted or doesn't exist"

# Update story status
if [ -f "$STORY_FILE" ]; then
    echo "📝 Updating story status to 'Done'..."
    sed -i 's/^## Status$/## Status/' "$STORY_FILE"
    sed -i '/^## Status$/,/^$/ { /^[^#]/ { /^Done$/! { /^In Progress$/c\Done
    /^Code Review$/c\Done
    /^Testing$/c\Done
    /^Backlog$/c\Done
    } } }' "$STORY_FILE"
fi

echo "✅ Story ${STORY_ID} successfully merged to master!"
echo "📊 Summary:"
echo "   ✓ Story branch merged and deleted"
echo "   ✓ Changes pushed to remote master"
echo "   ✓ Story status updated to 'Done'"
echo ""
echo "🎉 Great work! Story ${STORY_ID} is now complete and deployed."