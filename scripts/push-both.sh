#!/usr/bin/env bash
set -euo pipefail

# Push to all configured push URLs on the 'origin' remote (GitLab + GitHub).
# Usage:
#   scripts/push-both.sh              # push current branch and tags
#   scripts/push-both.sh all          # push all branches and tags
#   scripts/push-both.sh branch <br>  # push only the named branch and tags
#
# This assumes 'origin' has multiple push URLs configured.

ensure_repo() {
  if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "Error: not inside a git repository" >&2
    exit 1
  fi
}

show_remotes() {
  echo "Remotes (push):"
  git remote -v | awk '$3=="(push)" {print " - "$1": "$2}'
}

push_current_branch() {
  local branch
  branch=$(git rev-parse --abbrev-ref HEAD)
  echo "Pushing branch: ${branch}"
  git push origin "${branch}"
  echo "Pushing tags"
  git push origin --tags
}

push_all() {
  echo "Pushing all branches"
  git push origin --all
  echo "Pushing tags"
  git push origin --tags
}

push_named_branch() {
  local branch=$1
  echo "Pushing branch: ${branch}"
  git push origin "${branch}"
  echo "Pushing tags"
  git push origin --tags
}

main() {
  ensure_repo
  show_remotes

  case "${1-}" in
    all)
      push_all
      ;;
    branch)
      if [[ $# -lt 2 ]]; then
        echo "Usage: $0 branch <branch-name>" >&2
        exit 2
      fi
      push_named_branch "$2"
      ;;
    "" )
      push_current_branch
      ;;
    *)
      echo "Usage: $0 [all|branch <name>]" >&2
      exit 2
      ;;
  esac

  echo "Done."
}

main "$@"
