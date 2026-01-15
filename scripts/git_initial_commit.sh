#!/bin/bash
# Script to create the initial Git commit

set -e

echo "=========================================="
echo "Preparing Initial Git Commit"
echo "=========================================="
echo ""

# Check if git is initialized
if [ ! -d .git ]; then
    echo "Initializing Git repository..."
    git init
    git branch -M main
    echo "✓ Git repository initialized"
else
    echo "✓ Git repository already initialized"
fi

# Stage all files
echo ""
echo "Staging files..."
git add .

# Show what will be committed
echo ""
echo "Files to be committed:"
git status --short

# Commit with the message
echo ""
echo "Creating commit..."
git commit -F COMMIT_MESSAGE.txt

echo ""
echo "=========================================="
echo "✓ Initial commit created!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Create a GitHub repository"
echo "  2. Add remote: git remote add origin <repository-url>"
echo "  3. Push: git push -u origin main"
echo ""
echo "Or connect to existing repository:"
echo "  git remote add origin <repository-url>"
echo "  git push -u origin main"
echo ""
