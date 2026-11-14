#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=legacy-repo-slug.sh
source "$ROOT/scripts/legacy-repo-slug.sh"
LEGACY="$(legacy_repo_slug_decode)"
FORBIDDEN_LABEL="$(forbidden_edition_label)"
failures=0
ok() { echo "[OK] $*"; }
bad() { echo "[FAIL] $*"; failures=$((failures + 1)); }

scan_forbidden_terms() {
  local path="$1"
  local exclude_globs=(
    --glob '!*.tar.gz'
    --glob '!scripts/legacy-repo-slug.sh'
    --glob '!scripts/patch-cdnfly-repo-urls.sh'
    --glob '!scripts/verify-packages.sh'
  )
  local had=0
  if rg -qiF "$LEGACY" "$path" "${exclude_globs[@]}" 2>/dev/null; then
    bad "legacy GitHub repo segment in $path"
    rg -niF "$LEGACY" "$path" "${exclude_globs[@]}" | head -10
    had=1
  fi
  if rg -qF "$FORBIDDEN_LABEL" "$path" "${exclude_globs[@]}" 2>/dev/null; then
    bad "forbidden branding text in $path"
    rg -nF "$FORBIDDEN_LABEL" "$path" "${exclude_globs[@]}" | head -10
    had=1
  fi
  [[ "$had" -eq 0 ]] && ok "no legacy repo slug / branding under $path (except helpers)"
}

scan_forbidden_terms "$ROOT"

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
  if rg -qiF "$LEGACY" "$w" -g '*.{sh,html,js,py,md,txt,json}' 2>/dev/null; then
    bad "legacy repo segment inside $(basename "$t")"
  elif rg -qF "$FORBIDDEN_LABEL" "$w" -g '*.{sh,html,js,py,md,txt,json}' 2>/dev/null; then
    bad "branding text inside $(basename "$t")"
  else
    ok "$(basename "$t") clean"
  fi
  
  rm -rf "$w"
done

[[ "$failures" -eq 0 ]] && echo "--- All checks passed ---" || { echo "--- $failures failed ---"; exit 1; }
