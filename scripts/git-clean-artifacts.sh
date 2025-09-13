#!/usr/bin/env bash
set -euo pipefail

# Remove generated Ren'Py artifacts from Git index (one-time cleanup)
# - Untracks compiled .rpyc/.rpymc/.rpyb and cached dirs (game/cache, game/saves)
# - Preserves working files; only removes from Git index
#
# Usage:
#   bash scripts/git-clean-artifacts.sh --dry-run   # show what would change
#   bash scripts/git-clean-artifacts.sh             # perform cleanup

dry_run=false
if [[ "${1:-}" == "--dry-run" ]]; then dry_run=true; fi

# Ensure we're in a Git repo
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "ERROR: Not inside a Git repository" >&2
  exit 1
fi

echo "Scanning tracked files for generated artifacts..."

# Collect tracked compiled files
mapfile -t compiled_files < <(git ls-files | grep -E '\\.(rpyc|rpymc|rpyb)$' || true)

# Collect tracked files under cached directories
tracked_dirs=("game/cache" "game/saves" "cache" "saves")
declare -a dir_targets=()
for d in "${tracked_dirs[@]}"; do
  if git ls-files -- "$d" >/dev/null 2>&1; then
    if [[ -n "$(git ls-files -- "$d" | head -n1 || true)" ]]; then
      dir_targets+=("$d")
    fi
  fi
done

echo "Found ${#compiled_files[@]} compiled files and ${#dir_targets[@]} tracked dirs to clean."

if $dry_run; then
  if ((${#compiled_files[@]}==0 && ${#dir_targets[@]}==0)); then
    echo "Nothing to clean."
    exit 0
  fi
  if ((${#compiled_files[@]})); then
    echo "-- Compiled files to untrack --"
    printf '%s\n' "${compiled_files[@]}"
  fi
  if ((${#dir_targets[@]})); then
    echo "-- Directories to untrack (recursively) --"
    printf '%s\n' "${dir_targets[@]}"
  fi
  echo "Dry run complete. No changes made."
  exit 0
fi

# Untrack compiled files (preserve in working tree)
if ((${#compiled_files[@]})); then
  echo "Untracking compiled files..."
  for f in "${compiled_files[@]}"; do
    git rm --cached -- "$f" >/dev/null
  done
fi

# Untrack cached directories recursively
if ((${#dir_targets[@]})); then
  echo "Untracking cached directories..."
  for d in "${dir_targets[@]}"; do
    git rm --cached -r -- "$d" >/dev/null || true
  done
fi

echo "Cleanup complete. Next steps:"
echo "  1) Review changes:   git status"
echo "  2) Commit cleanup:   git commit -m \"chore: stop tracking generated artifacts\""
echo "  3) Push changes:     git push"

