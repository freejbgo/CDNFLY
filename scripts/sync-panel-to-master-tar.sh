#!/usr/bin/env bash
# Copy .veikor-build panel/src into the published master tarball.
# Leave console/, static/, and other panel files in the package alone.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PKG="cdnfly-master-v5.1.13"
SRC_ONLY="$ROOT/.veikor-build/$PKG/master/panel/src"
TAR="$ROOT/cdnfly/cdnfly-master-v5.1.13-centos-7.tar.gz"

[[ -d "$SRC_ONLY" ]] || { echo "missing $SRC_ONLY"; exit 1; }
[[ -f "$TAR" ]] || { echo "missing $TAR"; exit 1; }

WORKDIR="$(mktemp -d)"
trap 'rm -rf "$WORKDIR"' EXIT
tar -xzf "$TAR" -C "$WORKDIR"
rm -rf "$WORKDIR/$PKG/master/panel/src"
cp -a "$SRC_ONLY" "$WORKDIR/$PKG/master/panel/src"
CONSOLE_SRC="$ROOT/.veikor-build/$PKG/master/panel/console/index.html"
if [[ -f "$CONSOLE_SRC" ]]; then
  cp -a "$CONSOLE_SRC" "$WORKDIR/$PKG/master/panel/console/index.html"
fi
CONSOLE_INDEX="$WORKDIR/$PKG/master/panel/console/index.html"
PANEL_CONFIG="$WORKDIR/$PKG/master/panel/src/config.js"
if [[ -f "$CONSOLE_INDEX" && -f "$PANEL_CONFIG" ]]; then
  PANEL_VER="$(grep -oP ",version: '\\K[^']+" "$PANEL_CONFIG" | head -1 || true)"
  if [[ -n "$PANEL_VER" ]]; then
    sed -i "s/,version: '[^']*'/,version: '$PANEL_VER'/" "$CONSOLE_INDEX"
  fi
fi
tar -czf "$TAR" -C "$WORKDIR" "$PKG"
echo "Synced panel/src into $TAR"
