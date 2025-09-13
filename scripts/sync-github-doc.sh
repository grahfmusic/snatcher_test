#!/usr/bin/env bash
set -euo pipefail

# Syncs the local Doc/ directory to the GitHub wiki repository via SSH.
# Requires: wiki enabled on GitHub repo, SSH access configured.
# Repo wiki URL: git@github.com:grahfmusic/snatchernauts_framework.wiki.git
#
# Usage:
#   scripts/sync-github-doc.sh           # full sync (force-push new snapshot)
#   scripts/sync-github-doc.sh dry-run   # show what would be done

WIKI_SRC_DIR="Doc"
GITHUB_WIKI_REMOTE="git@github.com:grahfmusic/snatchernauts_framework.wiki.git"
DEFAULT_BRANCH="master"

msg() { echo "[wiki-sync] $*"; }
err() { echo "[wiki-sync][ERROR] $*" >&2; }

ensure_repo_root() {
  if [[ ! -d .git ]]; then
    err "Run from the repo root (where .git exists)."
    exit 1
  fi
}

ensure_wiki_dir() {
  if [[ ! -d "$WIKI_SRC_DIR" ]]; then
    err "Missing $WIKI_SRC_DIR directory."
    exit 1
  fi
}

main() {
  ensure_repo_root
  ensure_wiki_dir

  local dry_run=${1-}
  local TMPDIR_WIKI
  TMPDIR_WIKI=$(mktemp -d)
  cleanup() { if [[ -n "${TMPDIR_WIKI:-}" ]]; then rm -rf "$TMPDIR_WIKI"; fi }
  trap cleanup EXIT

  msg "Preparing temporary wiki repo: $TMPDIR_WIKI"

  rsync -a --delete "$WIKI_SRC_DIR"/ "$TMPDIR_WIKI"/

  if [[ "$dry_run" == "dry-run" ]]; then
    msg "Dry run: would initialize git repo in $TMPDIR_WIKI and push to $GITHUB_WIKI_REMOTE ($DEFAULT_BRANCH)"
    exit 0
  fi

  (
    cd "$TMPDIR_WIKI"
    git init -q
    # Set default branch to master for GitHub wiki compatibility
    git checkout -q -b "$DEFAULT_BRANCH"
    git add -A
    git -c user.name="wiki-sync" -c user.email="wiki-sync@local" commit -q -m "docs: sync wiki from project Doc/"
    git remote add origin "$GITHUB_WIKI_REMOTE"
    msg "Pushing to $GITHUB_WIKI_REMOTE ($DEFAULT_BRANCH)"
    git push -f -u origin "$DEFAULT_BRANCH"
  )

  msg "Wiki sync complete."
}

main "$@"
