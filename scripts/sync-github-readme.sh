#!/usr/bin/env bash
# Sync main README.md to GitHub-specific .github/README.md with platform modifications
set -euo pipefail

GRN="\033[32m"; YEL="\033[33m"; RED="\033[31m"; NC="\033[0m"

info() { printf "[sync-readme] %s\n" "$*"; }
success() { printf "${GRN}[sync-readme] %s${NC}\n" "$*"; }
warn() { printf "${YEL}[sync-readme] %s${NC}\n" "$*"; }
error() { printf "${RED}[sync-readme] %s${NC}\n" "$*"; }

# Check if we're in the project root
if [[ ! -f "README.md" ]]; then
    error "README.md not found. Run this script from the project root."
    exit 1
fi

info "Syncing main README.md to GitHub-specific version..."

# Create .github directory if it doesn't exist
mkdir -p .github

# Transform main README to GitHub version with platform-specific modifications
sed -E '
    # Remove GitLab pipeline badge line completely
    /^\[!\[gitlab pipeline\]/d;
    
    # Fix logo path: .gitbook/assets/ → ../Doc/
    s|!\[([^\]]*)\]\.gitbook/assets/([^)]+)|![\1](../Doc/\2)|g;
    
    # Add GitHub mirror badge after license badge if not already present
    /^\[!\[license: MIT\]/ {
        # Check if GitHub mirror badge already exists
        N
        /GitHub mirror/!{
            # If not found, add it
            s|(^\[!\[license: MIT\][^\n]*)\n|\1\n[![GitHub mirror](https://img.shields.io/badge/github-mirror-blue?logo=github)](https://github.com/grahfmusic/snatchernauts_framework)\n|
        }
        # Put back the extra line we read
        P
        D
    }
' README.md > .github/README.md

# Verify the transformation worked
if [[ ! -f ".github/README.md" ]]; then
    error "Failed to create .github/README.md"
    exit 1
fi

# Check what changed
if ! git diff --quiet .github/README.md 2>/dev/null; then
    success "GitHub README updated with platform-specific modifications:"
    echo "  ✅ Removed GitLab pipeline badge"
    echo "  ✅ Fixed logo path (.gitbook/assets/ → ../Doc/)"
    echo "  ✅ Added GitHub mirror badge"
    echo ""
    info "Changes ready to commit. Run 'git add .github/README.md' to stage them."
else
    info "GitHub README already up to date - no changes needed."
fi

success "GitHub README sync completed!"
