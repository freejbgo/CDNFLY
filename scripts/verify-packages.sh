#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
failures=0
ok() { echo "[OK] $*"; }
bad() { echo "[FAIL] $*"; failures=$((failures + 1)); }

scan_legacy_paths() {
  local path="$1"
  if rg -qi 'kaixin' "$path" \
    --glob '!*.tar.gz' \
    --glob '!cdnfly-全功能.tar.gz' \
    --glob '!scripts/patch-cdnfly-repo-urls.sh' \
    --glob '!scripts/verify-packages.sh' 2>/dev/null; then
    bad "legacy repo slug in $path"
    rg -ni 'kaixin' "$path" \
      --glob '!*.tar.gz' \
      --glob '!cdnfly-全功能.tar.gz' \
      --glob '!scripts/patch-cdnfly-repo-urls.sh' \
      --glob '!scripts/verify-packages.sh' | head -10
  else
    ok "no legacy slug under $path (except patch helper)"
  fi
}

scan_legacy_paths "$ROOT"

for sh in master.sh agent.sh 50113.sh; do
  grep -q 'freejbgo/CDNFLY' "$ROOT/$sh" && ok "$sh -> CDNFLY" || bad "$sh missing CDNFLY"
done
grep -q 'CDNFLY' "$ROOT/web/version.json" && ok version.json || bad version.json

for t in \
  "$ROOT/cdnfly/cdnfly-master-v5.1.13-centos-7.tar.gz" \
  "$ROOT/cdnfly/cdnfly-agent-v5.1.16-centos-7.tar.gz"; do
  [[ -f "$t" ]] || { bad "missing $t"; continue; }
  w=$(mktemp -d)
  tar -xzf "$t" -C "$w"
  if rg -qi 'kaixin' "$w" 2>/dev/null; then bad "legacy slug inside $(basename "$t")"; else ok "$(basename "$t") clean"; fi
  rm -rf "$w"
done

[[ "$failures" -eq 0 ]] && echo "--- All checks passed ---" || { echo "--- $failures failed ---"; exit 1; }
