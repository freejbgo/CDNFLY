#!/usr/bin/env bash
# Merge 全功能 overlay onto the official v5.1.13 master tarball and repack for install.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OVERLAY_TAR="$ROOT/cdnfly-全功能.tar.gz"
OUT_TAR="$ROOT/cdnfly/cdnfly-master-v5.1.13-centos-7.tar.gz"
OFFICIAL_TAR="$ROOT/cdnfly/cdnfly-master-v5.1.13-centos-7.official.tar.gz"
PKG_DIR="cdnfly-master-v5.1.13"
TASK_HTML="$PKG_DIR/master/panel/src/views/system/task/index.html"

WORKDIR="$(mktemp -d)"
trap 'rm -rf "$WORKDIR"' EXIT

[[ -f "$OVERLAY_TAR" ]] || { echo "missing $OVERLAY_TAR"; exit 1; }
if [[ ! -f "$OFFICIAL_TAR" ]]; then
  [[ -f "$OUT_TAR" ]] || { echo "missing official $OUT_TAR"; exit 1; }
  echo "Saving pristine official tarball to $OFFICIAL_TAR"
  cp -a "$OUT_TAR" "$OFFICIAL_TAR"
fi

echo "Extracting official package..."
tar -xzf "$OFFICIAL_TAR" -C "$WORKDIR"

echo "Extracting 全功能 overlay..."
tar -xzf "$OVERLAY_TAR" -C "$WORKDIR"
OVERLAY_ROOT="$WORKDIR/cdnfly"

if [[ ! -d "$OVERLAY_ROOT/master" ]]; then
  echo "overlay missing cdnfly/master"
  exit 1
fi

DST="$WORKDIR/$PKG_DIR"

merge_tree() {
  local src="$1" dest="$2"
  shift 2
  local -a excludes=("$@")
  ( cd "$src" && find . -type f \( -name '.DS_Store' -o -name '._*' \) -prune -o -type f -print ) | while IFS= read -r rel; do
    rel="${rel#./}"
    for ex in "${excludes[@]}"; do
      [[ "$rel" == "$ex" || "$rel" == */"$ex" ]] && continue 2
    done
    mkdir -p "$dest/$(dirname "$rel")"
    cp -a "$src/$rel" "$dest/$rel"
  done
  ( cd "$src" && find . -type l -print ) | while IFS= read -r rel; do
    rel="${rel#./}"
    for ex in "${excludes[@]}"; do
      [[ "$rel" == "$ex" || "$rel" == */"$ex" ]] && continue 2
    done
    mkdir -p "$dest/$(dirname "$rel")"
    ln -sf "$(readlink "$src/$rel")" "$dest/$rel"
  done
}

echo "Merging master/ and script/ from overlay..."
if [[ -d "$OVERLAY_ROOT/script" ]]; then
  rm -rf "$DST/script"
  mkdir -p "$DST/script"
  merge_tree "$OVERLAY_ROOT/script" "$DST/script"
fi

MASTER_EXCLUDES=(
  'conf/config.py' 'conf/config.py2' 'conf/config.pyc'
  'conf/ssl.cert' 'conf/ssl.key'
  'panel/src/controller/senior.js2'
  'panel/src/controller/site-usage-senior.js2'
  'tasks/bandwidth_monitor.so2'
)
merge_tree "$OVERLAY_ROOT/master" "$DST/master" "${MASTER_EXCLUDES[@]}"

echo "Fixing duplicate 504-error-page option in task/index.html..."
python3 - "$WORKDIR/$TASK_HTML" <<'PY'
import sys
path = sys.argv[1]
with open(path, 'rb') as f:
    data = f.read()
text = data.decode('utf-8', errors='replace')
needle = "<option value='504-error-page'>默认504页面</option>"
first = text.find(needle)
if first == -1:
    print("warning: 504 option not found", file=sys.stderr)
    sys.exit(0)
second = text.find(needle, first + len(needle))
if second != -1:
    text = text[:second] + text[second + len(needle):]
    # drop an extra newline if present
    if text.startswith('\r\n', second):
        pass
with open(path, 'wb') as f:
    f.write(text.encode('utf-8'))
print("504 duplicate removed" if second != -1 else "504 already single")
PY

"$ROOT/scripts/patch-cdnfly-repo-urls.sh" "$WORKDIR/$PKG_DIR"

echo "Repacking $OUT_TAR ..."
TMP_OUT="$WORKDIR/out.tar.gz"
tar -czf "$TMP_OUT" -C "$WORKDIR" "$PKG_DIR"
mv "$TMP_OUT" "$OUT_TAR"
echo "Done: $OUT_TAR ($(du -h "$OUT_TAR" | awk '{print $1}'))"
