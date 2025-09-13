#!/usr/bin/env bash
set -euo pipefail

# Default RENPY_SDK if not provided
RENPY_SDK="${RENPY_SDK:-$HOME/renpy-8.4.1-sdk}"

if [[ ! -x "$RENPY_SDK/renpy.sh" ]]; then
  echo "RENPY_SDK not found or invalid at: $RENPY_SDK" 1>&2
  echo "Set RENPY_SDK to your Ren'Py 8.4.x SDK directory or install at ~/renpy-8.4.1-sdk" 1>&2
  exit 1
fi

"$RENPY_SDK/renpy.sh" . lint
