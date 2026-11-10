#!/usr/bin/env bash
# Repack agent tarball with node README fixes (filebeat.yml ownership/mode).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT_TAR="$ROOT/cdnfly/cdnfly-agent-v5.1.16-centos-7.tar.gz"
OFFICIAL_TAR="$ROOT/cdnfly/cdnfly-agent-v5.1.16-centos-7.official.tar.gz"
PKG_DIR="cdnfly-agent-v5.1.16"
FILEBEAT_REL="$PKG_DIR/agent/conf/filebeat.yml"

WORKDIR="$(mktemp -d)"
trap 'rm -rf "$WORKDIR"' EXIT

if [[ ! -f "$OFFICIAL_TAR" ]]; then
  [[ -f "$OUT_TAR" ]] || { echo "missing $OUT_TAR"; exit 1; }
  echo "Saving pristine official agent tarball to $OFFICIAL_TAR"
  cp -a "$OUT_TAR" "$OFFICIAL_TAR"
fi

echo "Extracting official agent package..."
tar -xzf "$OFFICIAL_TAR" -C "$WORKDIR"

FB="$WORKDIR/$FILEBEAT_REL"
[[ -f "$FB" ]] || { echo "missing $FB"; exit 1; }

echo "Applying filebeat.yml mode 0644 (archive owner root)..."
chmod 0644 "$FB"

"$ROOT/scripts/patch-cdnfly-repo-urls.sh" "$WORKDIR/$PKG_DIR"

echo "Repacking $OUT_TAR ..."
TMP_OUT="$WORKDIR/out.tar.gz"
tar --owner=0 --group=0 -czf "$TMP_OUT" -C "$WORKDIR" "$PKG_DIR"
mv "$TMP_OUT" "$OUT_TAR"
echo "Done: $OUT_TAR ($(du -h "$OUT_TAR" | awk '{print $1}'))"
