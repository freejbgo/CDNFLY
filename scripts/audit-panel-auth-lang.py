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
        handler = text.split("function handleLangSelectChange")[1][:900] if "function handleLangSelectChange" in text else ""
        if "authPageFromContext" not in handler or "applyAuthPage" not in handler:
            bad.append("handleLangSelectChange must apply auth i18n before admin-console guard")
        if "function resolveAuthPage" not in text:
            bad.append("veikor-i18n.js: missing resolveAuthPage() for auth apply fallback")
        if "function ensureLangPreference" not in text:
            bad.append("veikor-i18n.js: missing ensureLangPreference() for browser locale")
        if "function detectBrowserLang" not in text:
            bad.append("veikor-i18n.js: missing detectBrowserLang()")
        else:
            detect = text.split("function detectBrowserLang")[1].split("function ", 1)[0]
            if "navigator.languages" not in detect and "navigator.language" not in detect:
                bad.append("detectBrowserLang must read navigator.languages / navigator.language")
            if "return 'en'" not in detect:
                bad.append("detectBrowserLang must fall back to en for non zh/en locales")
        norm = text.split("function normalize")[1].split("function ", 1)[0] if "function normalize" in text else ""
        if "zh-hk" not in norm or "zh-tw" not in norm.lower():
            bad.append("normalize must map zh-HK/zh-TW region tags")
        if "function authT(" not in text:
            bad.append("veikor-i18n.js: missing authT() for auth page copy from panel-lang")
        if "lay-filter=\"veikor-lang\"" not in open(
            os.path.join(PANEL, "views", "user", "login.html"), encoding="utf-8", errors="replace"
        ).read():
            bad.append("login.html: #veikor-lang-select needs lay-filter=veikor-lang")
        if "function activeLang()" in text:
            active = text.split("function activeLang()")[1].split("function ", 1)[0]
            if "authPageFromContext()" not in active:
                bad.append("activeLang must treat auth DOM/hash fallbacks like currentAuthPage (use authPageFromContext)")
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