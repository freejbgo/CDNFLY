#!/usr/bin/env bash
# Copy fixed panel/src/lib/view.js from the published master tarball onto a running install.
# Use when the console is blank and the browser shows:
#   view.js:54 Uncaught SyntaxError: Unexpected token ','
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TAR="$ROOT/cdnfly/cdnfly-master-v5.1.13-centos-7.tar.gz"
MEMBER="cdnfly-master-v5.1.13/master/panel/src/lib/view.js"
TARGET_DIR="${1:-}"

if [[ -z "$TARGET_DIR" ]]; then
  echo "Usage: $0 /path/to/master/panel/src" >&2
  echo "Example: $0 /opt/cdnfly/master/panel/src" >&2
  exit 1
fi

[[ -f "$TAR" ]] || { echo "missing tarball: $TAR" >&2; exit 1; }
[[ -d "$TARGET_DIR/lib" ]] || { echo "not a panel src tree (no lib/): $TARGET_DIR" >&2; exit 1; }

OUT="$TARGET_DIR/lib/view.js"
BACKUP="$OUT.bak-$(date +%Y%m%d%H%M%S)"
cp -a "$OUT" "$BACKUP"
tar -xOf "$TAR" "$MEMBER" >"$OUT"

if node --check "$OUT" >/dev/null 2>&1; then
  echo "OK: installed $OUT (backup $BACKUP)"
else
  echo "ERROR: extracted view.js still has syntax errors" >&2
  cp -a "$BACKUP" "$OUT"
  exit 1
fi

if grep -q "  ,view = function(id)" "$OUT"; then
  echo "ERROR: view.js still contains broken ',view =' boot line" >&2
  cp -a "$BACKUP" "$OUT"
  exit 1
fi

CONFIG="$TARGET_DIR/config.js"
if [[ -f "$CONFIG" ]]; then
  PANEL_VER="$(tar -xOf "$TAR" cdnfly-master-v5.1.13/master/panel/src/config.js | grep -oP ",version: '\\K[^']+" | head -1 || true)"
  if [[ -n "$PANEL_VER" ]]; then
  sed -i "s/,version: '[^']*'/,version: '$PANEL_VER'/" "$CONFIG"
  echo "Updated config.js version to $PANEL_VER"
  fi
fi

echo "Hard-refresh the console (Ctrl+F5). In devtools, line ~56 should read: var view = function(id){"