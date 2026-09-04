#!/usr/bin/env bash
set -euo pipefail

if [ $# -ne 1 ]; then
  echo "usage: install.sh TARGET_REPO" >&2
  exit 2
fi

target_repo="$1"
if [ ! -d "$target_repo" ]; then
  echo "Target directory does not exist: $target_repo" >&2
  exit 2
fi

kit_root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
timestamp="$(date +%Y%m%d-%H%M%S)"

mkdir -p "$target_repo/scripts"

if [ -f "$target_repo/CLAUDE.md" ]; then
  backup="$target_repo/CLAUDE.md.bak.$timestamp"
  cp "$target_repo/CLAUDE.md" "$backup"
  echo "Backed up: $backup"
fi

cp "$kit_root/templates/CLAUDE-root.md" "$target_repo/CLAUDE.md"
echo "Wrote: $target_repo/CLAUDE.md"

for script in "$kit_root"/scripts/*; do
  name="$(basename "$script")"
  cp "$script" "$target_repo/scripts/$name"
  chmod +x "$target_repo/scripts/$name"
  echo "Wrote: $target_repo/scripts/$name"
done
