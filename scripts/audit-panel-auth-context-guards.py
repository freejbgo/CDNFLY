#!/usr/bin/env python3
"""Auth i18n guards: critical early-returns must not miss authPageFromContext()."""
import os
import re
import sys

ROOT = os.path.join(os.path.dirname(__file__), "..")
I18N = os.path.join(
    ROOT,
    ".veikor-build",
    "cdnfly-master-v5.1.13",
    "master",
    "panel",
    "src",
    "lib",
    "veikor-i18n.js",
)

# function name -> must call authPageFromContext in first auth-related if in body prefix
GUARDED = (
    "activeLang",
    "customerI18nActive",
    "updateConsoleLangSelect",
    "applyConsoleTitle",
    "applyConsoleI18n",
)


def body_after_def(text: str, name: str) -> str:
    m = re.search(rf"function {name}\(\)\s*\{{", text)
    if not m:
        return ""
    start = m.end()
    depth = 1
    i = start
    while i < len(text) and depth:
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
        i += 1
    return text[start : i - 1]


def main() -> int:
    if not os.path.isfile(I18N):
        print("audit-panel-auth-context-guards: FAIL missing veikor-i18n.js", file=sys.stderr)
        return 1
    text = open(I18N, encoding="utf-8", errors="replace").read()
    bad = []
    for fn in GUARDED:
        body = body_after_def(text, fn)
        if not body:
            bad.append(f"missing function {fn}()")
            continue
        head = body[:600]
        if "currentAuthPage()" in head and "authPageFromContext()" not in head:
            bad.append(f"{fn}(): uses currentAuthPage without authPageFromContext in guard")

    soft = []
    for fn in ("applyConsoleTitle", "applyConsoleI18n"):
        body = body_after_def(text, fn)
        if not body:
            continue
        head = body[:400]
        if re.search(r"if\s*\(\s*currentAuthPage\(\)\s*\)\s*return", head):
            if "authPageFromContext()" not in head:
                soft.append(f"{fn}(): early return on currentAuthPage only (race with DOM login)")

    for fn in ("detectBrowserLang", "ensureLangPreference", "bindLangSelect", "applyAuthPage"):
        if f"function {fn}" not in text:
            bad.append(f"missing function {fn}()")

    if soft:
        for line in soft:
            print("audit-panel-auth-context-guards: WARN", line, file=sys.stderr)

    if bad:
        print("audit-panel-auth-context-guards: FAIL", file=sys.stderr)
        for line in bad:
            print(" ", line, file=sys.stderr)
        return 1
    print("audit-panel-auth-context-guards: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())