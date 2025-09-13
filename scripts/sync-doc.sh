#!/usr/bin/env bash
# Universal doc sync script - syncs local Doc/ directory to both GitLab and GitHub wikis
set -euo pipefail

# Configuration
WIKI_SRC_DIR="Doc"
GITLAB_WIKI_REMOTE="git@gitlab.com:grahfmusic/snatchernauts_framework.wiki.git"
GITHUB_WIKI_REMOTE="git@github.com:grahfmusic/snatchernauts_framework.wiki.git"
GITLAB_BRANCH="main"
GITHUB_BRANCH="master"

GRN="\033[32m"; YEL="\033[33m"; RED="\033[31m"; BLU="\033[34m"; NC="\033[0m"

info() { printf "[wiki-sync] %s\n" "$*"; }
success() { printf "${GRN}[wiki-sync] %s${NC}\n" "$*"; }
warn() { printf "${YEL}[wiki-sync] %s${NC}\n" "$*"; }
error() { printf "${RED}[wiki-sync] %s${NC}\n" "$*"; }
section() { printf "${BLU}[wiki-sync] === %s ===${NC}\n" "$*"; }

show_usage() {
    cat << EOF
Universal Doc Sync - Deploy documentation to both GitLab and GitHub wikis

USAGE:
    scripts/sync-doc.sh [OPTIONS]

OPTIONS:
    --dry-run          Show what would be synced without making changes
    --gitlab-only      Sync only to GitLab wiki
    --github-only      Sync only to GitHub wiki  
    --help             Show this help message

EXAMPLES:
    scripts/sync-doc.sh                    # Sync to both GitLab and GitHub
    scripts/sync-doc.sh --dry-run          # Preview changes without syncing
    scripts/sync-doc.sh --gitlab-only      # Sync only to GitLab
    scripts/sync-doc.sh --github-only      # Sync only to GitHub

REQUIREMENTS:
    - SSH access configured for both GitLab and GitHub
    - Wiki repositories enabled on both platforms
    - Local Doc/ directory with documentation files

EOF
}

ensure_requirements() {
    if [[ ! -d .git ]]; then
        error "Run from the repository root (where .git exists)"
        exit 1
    fi
    
    if [[ ! -d "$WIKI_SRC_DIR" ]]; then
        error "Missing $WIKI_SRC_DIR directory"
        exit 1
    fi
    
    local wiki_files
    wiki_files=$(find "$WIKI_SRC_DIR" -name "*.md" | wc -l)
    if [[ $wiki_files -eq 0 ]]; then
        error "No .md files found in $WIKI_SRC_DIR directory"
        exit 1
    fi
    
    info "Found $wiki_files documentation files to sync"
}

sync_to_wiki() {
    local platform="$1"
    local remote_url="$2"
    local temp_dir="$3"
    
    # Determine the correct branch for this platform
    local branch_name
    if [[ "$platform" == "GitLab" ]]; then
        branch_name="$GITLAB_BRANCH"
    else
        branch_name="$GITHUB_BRANCH"
    fi
    
    section "Syncing to $platform wiki (branch: $branch_name)"
    
    # Create clean temporary repository
    rm -rf "$temp_dir"
    mkdir -p "$temp_dir"
    
    # Copy wiki files to temporary directory
    info "Preparing $platform wiki content..."
    rsync -av --delete "$WIKI_SRC_DIR"/ "$temp_dir"/
    
    # Initialize git repository in temp directory
    (
        cd "$temp_dir"
        
        # Initialize and configure repository
        git init -q
        git checkout -q -b "$branch_name"
        
        # Add all wiki files
        git add -A
        
        # Check if there are any changes to commit
        if ! git diff --cached --quiet; then
            # Commit with timestamp and platform info
            local commit_msg="docs: sync wiki documentation from project Doc/ directory

Updated: $(date -u +"%Y-%m-%d %H:%M:%S UTC")
Platform: $platform
Branch: $branch_name
Source: Local Doc/ directory"
            
            git -c user.name="wiki-sync" -c user.email="wiki-sync@local" commit -q -m "$commit_msg"
            
            # Add remote and push
            git remote add origin "$remote_url"
            info "Pushing to $platform wiki repository ($branch_name)..."
            
            if git push -f -u origin "$branch_name"; then
                success "$platform wiki sync completed successfully"
                return 0
            else
                warn "$platform wiki sync failed - continuing with other platforms"
                return 1
            fi
        else
            info "$platform wiki already up to date"
            return 0
        fi
    )
}

main() {
    local dry_run=false
    local gitlab_only=false
    local github_only=false
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --dry-run)
                dry_run=true
                shift
                ;;
            --gitlab-only)
                gitlab_only=true
                shift
                ;;
            --github-only)
                github_only=true
                shift
                ;;
            --help|-h)
                show_usage
                exit 0
                ;;
            *)
                error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
    
    ensure_requirements
    
    if [[ "$dry_run" == "true" ]]; then
        section "DRY RUN - No changes will be made"
        info "Would sync Doc/ directory contents:"
        find "$WIKI_SRC_DIR" -name "*.md" | sed 's/^/  • /'
        
        if [[ "$gitlab_only" == "false" && "$github_only" == "false" ]] || [[ "$gitlab_only" == "true" ]]; then
            info "Would sync to GitLab wiki: $GITLAB_WIKI_REMOTE"
        fi
        
        if [[ "$gitlab_only" == "false" && "$github_only" == "false" ]] || [[ "$github_only" == "true" ]]; then
            info "Would sync to GitHub wiki: $GITHUB_WIKI_REMOTE"
        fi
        
        success "Dry run completed - no changes made"
        exit 0
    fi
    
    # Create temporary directories (global scope for cleanup)
    gitlab_temp="/tmp/snatchernauts-gitlab-wiki-$$"
    github_temp="/tmp/snatchernauts-github-wiki-$$"
    
    # Cleanup function
    cleanup() {
        [[ -n "${gitlab_temp:-}" && -d "$gitlab_temp" ]] && rm -rf "$gitlab_temp"
        [[ -n "${github_temp:-}" && -d "$github_temp" ]] && rm -rf "$github_temp"
    }
    trap cleanup EXIT
    
    local sync_count=0
    local success_count=0
    
    # Sync to GitLab if requested
    if [[ "$github_only" == "false" ]]; then
        sync_count=$((sync_count + 1))
        info "Starting GitLab wiki sync..."
        if sync_to_wiki "GitLab" "$GITLAB_WIKI_REMOTE" "$gitlab_temp"; then
            success_count=$((success_count + 1))
        fi
    else
        info "Skipping GitLab sync (github-only mode)"
    fi
    
    # Sync to GitHub if requested
    if [[ "$gitlab_only" == "false" ]]; then
        sync_count=$((sync_count + 1))
        info "Starting GitHub wiki sync..."
        if sync_to_wiki "GitHub" "$GITHUB_WIKI_REMOTE" "$github_temp"; then
            success_count=$((success_count + 1))
        fi
    else
        info "Skipping GitHub sync (gitlab-only mode)"
    fi
    
    # Report results
    section "Wiki Sync Summary"
    if [[ $success_count -eq $sync_count ]]; then
        success "All wiki syncs completed successfully ($success_count/$sync_count)"
        info "Documentation is now live on both platforms!"
    elif [[ $success_count -gt 0 ]]; then
        warn "Some wiki syncs completed ($success_count/$sync_count)"
        info "Check the logs above for details on any failures"
    else
        error "All wiki syncs failed ($success_count/$sync_count)"
        exit 1
    fi
}

main "$@"
