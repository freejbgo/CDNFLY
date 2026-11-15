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
tar -czf "$TAR" -C "$WORKDIR" "$PKG"
echo "Synced panel/src into $TAR"
