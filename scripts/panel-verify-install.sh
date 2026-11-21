#!/usr/bin/env bash
# Post-install checks on a LIVE master panel tree (admin + customer share this console).
set -euo pipefail

PANEL_SRC="${1:-}"
PANEL_CONSOLE="${2:-}"

if [[ -z "$PANEL_SRC" ]]; then
  echo "Usage: $0 /path/to/master/panel/src [/path/to/master/panel/console]" >&2
  exit 1
fi

failures=0
ok() { echo "[OK] $*"; }
bad() { echo "[FAIL] $*"; failures=$((failures + 1)); }

[[ -f "$PANEL_SRC/config.js" ]] || { bad "missing $PANEL_SRC/config.js"; exit 1; }
[[ -f "$PANEL_SRC/lib/view.js" ]] || bad "missing view.js"
[[ -f "$PANEL_SRC/lib/veikor-page.js" ]] || bad "missing veikor-page.js"
[[ -f "$PANEL_SRC/index.js" ]] || bad "missing index.js"

PANEL_VER="$(grep -oP ",version: '\\K[^']+" "$PANEL_SRC/config.js" | head -1 || true)"
if [[ -z "$PANEL_VER" ]]; then
  bad "config.js has no setter.version"
else
  ok "panel setter.version = $PANEL_VER"
fi

if grep -q "  ,view = function(id)" "$PANEL_SRC/lib/view.js" 2>/dev/null; then
  bad "view.js still has broken ',view =' syntax — console will not boot"
else
  ok "view.js boot syntax"
fi

if ! grep -q "var view = function(id)" "$PANEL_SRC/lib/view.js" 2>/dev/null; then
  bad "view.js missing var view = (SPA cannot load)"
fi

if ! grep -q "var \$ = layui.jquery" "$PANEL_SRC/lib/veikor-page.js" 2>/dev/null; then
  bad "veikor-page.js missing jquery binding — forms break globally"
fi

if ! grep -q "bootTabChrome" "$PANEL_SRC/lib/veikor-page.js" 2>/dev/null; then
  bad "veikor-page.js missing bootTabChrome — need panel550+ hotfix/tar"
fi

if ! grep -q "veikorBootTabChrome" "$PANEL_SRC/index.js" 2>/dev/null; then
  bad "index.js missing tab form bootstrap (panel550+)"
fi

if ! grep -q "veikorGuardHeaderLangSelect" "$PANEL_SRC/lib/veikor-page.js" 2>/dev/null; then
  bad "veikor-page.js missing header lang guard (panel551+ — top-right nav overlap)"
fi

if ! grep -q "ensureTabsBodyShell" "$PANEL_SRC/index.js" 2>/dev/null; then
  bad "index.js missing ensureTabsBodyShell (panel553+ — 2nd sidebar click blank)"
fi

if ! grep -q "veikor view parse" "$PANEL_SRC/lib/view.js" 2>/dev/null; then
  bad "view.js missing parse try/finally (panel553+ — stuck loading spinner)"
fi

if ! grep -q "function authBarePath" "$PANEL_SRC/lib/veikor-i18n.js" 2>/dev/null; then
  bad "veikor-i18n.js missing authBarePath (panel554+ — login/reg lang switch)"
fi

if [[ -n "$PANEL_CONSOLE" && -f "$PANEL_CONSOLE/index.html" ]]; then
  CONSOLE_VER="$(grep -oP ",version: '\\K[^']+" "$PANEL_CONSOLE/index.html" | head -1 || true)"
  if [[ -z "$CONSOLE_VER" ]]; then
    bad "console/index.html has no layui.config.version"
  elif [[ "$CONSOLE_VER" != "$PANEL_VER" ]]; then
    bad "version mismatch: config.js=$PANEL_VER console/index.html=$CONSOLE_VER (browser loads stale cache bust key)"
  else
    ok "console/index.html version matches config.js"
  fi
else
  echo "[WARN] console path not given — cannot check index.html version (common cause of 'everything broken')"
fi

if [[ "$failures" -eq 0 ]]; then
  echo "--- Install looks consistent. Hard-refresh browser (Ctrl+Shift+R). In console run: layui.setter.version === '$PANEL_VER' ---"
  exit 0
fi
echo "--- $failures problem(s) — run: bash scripts/panel-hotfix-console-boot.sh \"$PANEL_SRC\" \"${PANEL_CONSOLE:-}\" ---"
exit 1