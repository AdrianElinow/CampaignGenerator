#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<EOF
Usage: $(basename "$0") [-n]

Recursively delete all "__pycache__" directories from the current directory.

Options:
  -n    Dry-run: list directories that would be removed, do not delete.
EOF
}

dry_run=false
while getopts ":n" opt; do
  case "$opt" in
    n) dry_run=true ;;
    *) usage; exit 1 ;;
  esac
done

if $dry_run; then
  echo "Dry run: listing __pycache__ directories (no deletion)"
  find . -type d -name '__pycache__' -print
  exit 0
fi

echo "Searching for __pycache__ directories..."
# macOS ships with Bash 3.x where `mapfile`/`readarray` is unavailable.
# Use a portable find + read -d '' loop to collect results safely.
found_dirs=()
count=0
while IFS= read -r -d '' dir; do
  found_dirs+=("$dir")
  count=$((count + 1))
done < <(find . -type d -name '__pycache__' -print0)

if [ "$count" -eq 0 ]; then
  echo "No __pycache__ directories found."
  exit 0
fi

for d in "${found_dirs[@]}"; do
  echo "Removing: $d"
  rm -rf -- "$d"
done

echo "All done. Removed $count __pycache__ directories."
