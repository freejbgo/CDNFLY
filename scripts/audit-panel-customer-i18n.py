#!/usr/bin/env python3
"""Customer-console i18n regression checks (M1). Admin views are out of scope."""
from __future__ import annotations

import os
import re
import sys

ROOT = os.path.join(
    os.path.dirname(__file__),
    "..",
    ".veikor-build",
    "cdnfly-master-v5.1.13",
    "master",
    "panel",
    "src",
)
VIEWS = os.path.join(ROOT, "views")
CONTROLLERS = os.path.join(ROOT, "controller")

CUSTOMER_VIEW_PREFIXES = (
    "site",
    "stream",
    "account",
    "finance",
    os.path.join("package", "my"),
    os.path.join("package", "buy"),
)
CUSTOMER_CONTROLLERS = (
    "senior.js",
    "site-usage-senior.js",
    "stream_senior.js",
    "stream-usage-senior.js",
)

SCOPED_LANG = re.compile(r"\$\(document\)\.on\('veikor:lang\.([^']+)'")
GLOBAL_LANG = re.compile(r"\$\(document\)\.on\('veikor:lang'")
LAYER_CJK = re.compile(
    r"layer\.(?:msg|alert|confirm)\(\s*['\"]([^'\"]*[\u4e00-\u9fff][^'\"]*)"
)
RAW_RES_MSG = re.compile(r"layer\.msg\(\s*res\.msg\b")


def _is_customer_view(rel: str) -> bool:
    rel = rel.replace("\\", "/")
    for prefix in CUSTOMER_VIEW_PREFIXES:
        if rel == prefix or rel.startswith(prefix + "/"):
            return True
    if rel == "user_home.html":
        return True
    if rel.startswith("system/message/"):
        return True
    return False


def _missing_global_lang(text: str) -> bool:
    if not SCOPED_LANG.search(text):
        return False
    return not (GLOBAL_LANG.search(text) or re.search(r"\.on\('veikor:lang'", text))


def main() -> int:
    bad_lang: list[str] = []
    bad_layer: list[tuple[str, str]] = []
    bad_res_msg: list[str] = []

    for dirpath, _, files in os.walk(VIEWS):
        for fn in files:
            if not fn.endswith(".html"):
                continue
            path = os.path.join(dirpath, fn)
            rel = os.path.relpath(path, VIEWS)
            if not _is_customer_view(rel):
                continue
            text = open(path, encoding="utf-8", errors="replace").read()
            if _missing_global_lang(text):
                bad_lang.append(rel)
            for m in LAYER_CJK.finditer(text):
                bad_layer.append((rel, m.group(1)[:80]))
            if RAW_RES_MSG.search(text) and "translateResMsg" not in text:
                bad_res_msg.append(rel)

    for fn in CUSTOMER_CONTROLLERS:
        path = os.path.join(CONTROLLERS, fn)
        if not os.path.isfile(path):
            continue
        text = open(path, encoding="utf-8", errors="replace").read()
        if _missing_global_lang(text):
            bad_lang.append(os.path.join("controller", fn))

    if bad_lang:
        print(
            "customer views/controllers with scoped veikor:lang but no global listener:",
            file=sys.stderr,
        )
        for rel in sorted(bad_lang):
            print(" ", rel, file=sys.stderr)
    if bad_layer:
        print("customer layer.* with hardcoded Chinese (use veikorI18n):", file=sys.stderr)
        for rel, msg in bad_layer:
            print(f"  {rel}: {msg!r}", file=sys.stderr)
    if bad_res_msg:
        print("customer layer.msg(res.msg) without translateResMsg:", file=sys.stderr)
        for rel in sorted(bad_res_msg):
            print(" ", rel, file=sys.stderr)

    if bad_lang or bad_layer or bad_res_msg:
        return 1
    print("audit-panel-customer-i18n: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())