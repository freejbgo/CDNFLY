#!/usr/bin/env bash
# Point embedded download URLs at freejbgo/CDNFLY when repacking install tarballs.
set -euo pipefail

TARGET="${1:?usage: patch-cdnfly-repo-urls.sh <directory>}"
LEGACY='cdnfly-kaixin'

while IFS= read -r -d '' f; do
  if grep -qF "$LEGACY" "$f" 2>/dev/null; then
    sed -i "s|$LEGACY|CDNFLY|g" "$f"
    echo "patched: $f"
  fi
done < <(find "$TARGET" -type f -print0)

if grep -rqF "$LEGACY" "$TARGET" 2>/dev/null; then
  echo "error: legacy GitHub repo path still present under $TARGET" >&2
  grep -rn "$LEGACY" "$TARGET" | head -20 >&2
  exit 1
fi
