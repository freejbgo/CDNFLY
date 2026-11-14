#!/usr/bin/env bash
# Point embedded download URLs at freejbgo/CDNFLY when repacking install tarballs.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=legacy-repo-slug.sh
source "$ROOT/scripts/legacy-repo-slug.sh"
TARGET="${1:?usage: patch-cdnfly-repo-urls.sh <directory>}"
LEGACY="$(legacy_repo_slug_decode)"

while IFS= read -r -d '' f; do
  if grep -qF "$LEGACY" "$f" 2>/dev/null; then
    sed -i "s|$LEGACY|CDNFLY|g" "$f"
    echo "patched: $f"
  fi
done < <(find "$TARGET" -type f -print0)

if grep -rqF "$LEGACY" "$TARGET" 2>/dev/null; then
  echo "error: legacy GitHub repo path still present under $TARGET" >&2
  grep -rnF "$LEGACY" "$TARGET" | head -20 >&2
  exit 1
fi
