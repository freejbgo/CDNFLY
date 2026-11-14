#!/usr/bin/env bash
# Copy .veikor-build panel tree into the published master tarball (required before repack).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PKG="cdnfly-master-v5.1.13"
PANEL_SRC="$ROOT/.veikor-build/$PKG/master/panel"
TAR="$ROOT/cdnfly/cdnfly-master-v5.1.13-centos-7.tar.gz"

[[ -d "$PANEL_SRC" ]] || { echo "missing $PANEL_SRC"; exit 1; }
[[ -f "$TAR" ]] || { echo "missing $TAR"; exit 1; }

WORKDIR="$(mktemp -d)"
trap 'rm -rf "$WORKDIR"' EXIT
tar -xzf "$TAR" -C "$WORKDIR"
rm -rf "$WORKDIR/$PKG/master/panel"
cp -a "$PANEL_SRC" "$WORKDIR/$PKG/master/"
tar -czf "$TAR" -C "$WORKDIR" "$PKG"
echo "Synced panel into $TAR"
