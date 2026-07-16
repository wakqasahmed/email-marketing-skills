#!/usr/bin/env bash
set -euo pipefail

repo="$(cd "$(dirname "$0")/.." && pwd)"
target="${1:?Usage: scripts/link-skills.sh /path/to/skills-directory}"

mkdir -p "$target"
for skill in "$repo"/skills/*; do
  ln -sfn "$skill" "$target/$(basename "$skill")"
done
