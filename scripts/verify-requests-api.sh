#!/usr/bin/env bash
# On an installed master host: check whether requests/api.py was replaced (license patch).
set -euo pipefail
TARGET="${1:-/opt/venv/lib/python2.7/site-packages/requests/api.py}"
REF="${2:-}"

if [[ ! -f "$TARGET" ]]; then
  echo "[FAIL] missing $TARGET (not a CDNFLY master venv?)"
  exit 1
fi

if rg -q 'auth\.cdnfly\.cn|update\.cdnfly\.cn' "$TARGET" 2>/dev/null; then
  echo "[WARN] $TARGET contains CDNFLY URL redirects (license patch)."
  echo "       Only trust this file if it matches your audited copy (e.g. repo cdnfly/api.py)."
else
  echo "[OK] $TARGET has no CDNFLY redirect strings (likely stock requests)."
fi

if rg -qE 'exec\(|eval\(|os\.system|subprocess\.(call|Popen)|__import__\s*\(' "$TARGET" 2>/dev/null; then
  echo "[FAIL] suspicious execution primitives in $TARGET — treat as compromised."
  exit 1
fi

if [[ -n "$REF" && -f "$REF" ]]; then
  if cmp -s "$TARGET" "$REF"; then
    echo "[OK] $TARGET matches reference $REF"
  else
    echo "[WARN] $TARGET differs from reference $REF"
    diff -u "$REF" "$TARGET" | head -40 || true
  fi
fi