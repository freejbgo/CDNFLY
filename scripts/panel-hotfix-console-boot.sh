#!/usr/bin/env bash
# Apply console boot fixes from the published master tar onto a live install.
# Fixes:
#   - view.js ',view =' syntax error (panel543+)
#   - veikor-page.js missing layui.jquery (panel544+)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TAR="$ROOT/cdnfly/cdnfly-master-v5.1.13-centos-7.tar.gz"
PREFIX="cdnfly-master-v5.1.13/master/panel"
PANEL_SRC="${1:-}"
PANEL_CONSOLE="${2:-}"

if [[ -z "$PANEL_SRC" ]]; then
  echo "Usage: $0 /path/to/master/panel/src [/path/to/master/panel/console]" >&2
  echo "Example: $0 /opt/cdnfly/master/panel/src /opt/cdnfly/master/panel/console" >&2
  exit 1
fi

[[ -f "$TAR" ]] || { echo "missing tarball: $TAR" >&2; exit 1; }
[[ -d "$PANEL_SRC/lib" ]] || { echo "not a panel src tree: $PANEL_SRC" >&2; exit 1; }

extract_one() {
  local member="$1"
  local dest="$2"
  local backup="$dest.bak-$(date +%Y%m%d%H%M%S)"
  cp -a "$dest" "$backup"
  tar -xOf "$TAR" "$member" >"$dest"
  echo "OK $dest (backup $backup)"
}

extract_one "$PREFIX/src/lib/view.js" "$PANEL_SRC/lib/view.js"
extract_one "$PREFIX/src/lib/veikor-page.js" "$PANEL_SRC/lib/veikor-page.js"
extract_one "$PREFIX/src/lib/admin.js" "$PANEL_SRC/lib/admin.js"
extract_one "$PREFIX/src/config.js" "$PANEL_SRC/config.js"
for v in system/more.html system/about.html; do
  extract_one "$PREFIX/src/views/$v" "$PANEL_SRC/views/$v"
done

if grep -q "  ,view = function(id)" "$PANEL_SRC/lib/view.js"; then
  echo "ERROR: view.js still broken" >&2
  exit 1
fi
if ! grep -q "var \$ = layui.jquery" "$PANEL_SRC/lib/veikor-page.js"; then
  echo "ERROR: veikor-page.js missing var \$ = layui.jquery" >&2
  exit 1
fi

PANEL_VER="$(grep -oP ",version: '\\K[^']+" "$PANEL_SRC/config.js" | head -1 || true)"
echo "Panel cache version: ${PANEL_VER:-unknown}"

if [[ -n "$PANEL_CONSOLE" && -f "$PANEL_CONSOLE/index.html" && -n "$PANEL_VER" ]]; then
  sed -i "s/,version: '[^']*'/,version: '$PANEL_VER'/" "$PANEL_CONSOLE/index.html"
  echo "Synced layui.config.version in $PANEL_CONSOLE/index.html"
fi

echo "Done. Hard-refresh console (Ctrl+Shift+R). Expect: layui.setter.version === '$PANEL_VER'"