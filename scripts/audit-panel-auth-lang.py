#!/usr/bin/env python3
"""Login/reg/forget must detect auth routes with redirect= segments and refresh copy on lang change."""
import os
import sys

ROOT = os.path.join(os.path.dirname(__file__), "..")
PANEL = os.path.join(ROOT, ".veikor-build", "cdnfly-master-v5.1.13", "master", "panel", "src")
I18N = os.path.join(PANEL, "lib", "veikor-i18n.js")
INDEX = os.path.join(PANEL, "index.js")


def main() -> int:
    bad = []
    if os.path.isfile(I18N):
        text = open(I18N, encoding="utf-8", errors="replace").read()
        if "function authBarePath()" not in text:
            bad.append("veikor-i18n.js: missing authBarePath()")
        if "function authBarePath()" in text and "authBarePath()" not in text.split("function currentAuthPage")[1][:400]:
            bad.append("currentAuthPage must use authBarePath()")
        bind = text.split("function bindLangSelect")[1][:900] if "function bindLangSelect" in text else ""
        if "if (authPage)" not in bind or ("authPageFromContext" not in bind and "currentAuthPage()" not in bind):
            bad.append("bindLangSelect must apply auth i18n before admin-console guard")
        if "function resolveAuthPage" not in text:
            bad.append("veikor-i18n.js: missing resolveAuthPage() for auth apply fallback")
        if "function ensureLangPreference" not in text:
            bad.append("veikor-i18n.js: missing ensureLangPreference() for browser locale")
    else:
        bad.append("missing veikor-i18n.js under .veikor-build")
    if os.path.isfile(INDEX):
        idx = open(INDEX, encoding="utf-8", errors="replace").read()
        if "/^\\w+=/.test(seg)" not in idx:
            bad.append("index.js entryPage must strip redirect= path segments")
    if bad:
        print("audit-panel-auth-lang: FAIL", file=sys.stderr)
        for line in bad:
            print(" ", line, file=sys.stderr)
        return 1
    print("audit-panel-auth-lang: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())