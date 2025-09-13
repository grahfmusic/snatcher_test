#!/usr/bin/env bash
set -euo pipefail

to_ssh_url() {
  local input="$1"
  # Already SSH
  if [[ "$input" =~ ^git@github\.com:.*\.git$ ]]; then
    echo "$input"; return 0
  fi
  # Convert https://github.com/owner/repo(.git) to SSH
  if [[ "$input" =~ ^https?://github\.com/([^/]+)/([^/]+)(\.git)?$ ]]; then
    echo "git@github.com:${BASH_REMATCH[1]}/${BASH_REMATCH[2]}.git"; return 0
  fi
  # Convert owner/repo to SSH
  if [[ "$input" =~ ^[^/]+/[^/]+$ ]]; then
    echo "git@github.com:${input}.git"; return 0
  fi
  return 1
}

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <owner/repo | ssh-url | https-url>"
  echo "Examples:"
  echo "  $0 youruser/snatchernauts_framework"
  echo "  $0 git@github.com:youruser/snatchernauts_framework.git"
  echo "  $0 https://github.com/youruser/snatchernauts_framework.git"
  exit 1
fi

normalized_url=$(to_ssh_url "$1") || { echo "Unrecognized repo identifier. Use owner/repo or a GitHub URL."; exit 1; }

echo "Using SSH remote: $normalized_url"
git remote remove origin >/dev/null 2>&1 || true
git remote add origin "$normalized_url"

default_branch="main"
current_branch=$(git rev-parse --abbrev-ref HEAD)

if [[ "$current_branch" != "$default_branch" ]]; then
  echo "Renaming current branch '$current_branch' to '$default_branch'"
  git branch -M "$default_branch"
fi

echo "Pushing $default_branch and tags to origin (SSH)"
git push -u origin "$default_branch"
git push --tags origin || true

echo "Done. Repository is now linked to $normalized_url via SSH"
