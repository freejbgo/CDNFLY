#!/usr/bin/env python3
"""Fail when page-alive guards still depend on visible DOM text (breaks under i18n)."""
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
ALIVE_OPEN = re.compile(r"function\s+(\w+Alive)\s*\([^)]*\)\s*\{")

TAB_TEXT_GUARD = re.compile(
    r"curr_tab\s*==\s*[\"'][^\"']*[\u4e00-\u9fff]"
)
CUSTOMER_VIEW_PREFIXES = (
    "site",
    "stream",
    "account",
    "finance",
    os.path.join("package", "my"),
    os.path.join("package", "buy"),
)
CUSTOMER_CONTROLLERS = (
    "site-usage-senior.js",
    "stream-usage-senior.js",
    "senior.js",
    "stream_senior.js",
)


def _alive_function_body(html: str, start: int) -> str:
    depth = 1
    i = start
    n = len(html)
    while i < n and depth:
        ch = html[i]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
        i += 1
    if depth != 0:
        return ""
    return html[start : i - 1]


def alive_uses_visible_text(html: str) -> bool:
    for m in ALIVE_OPEN.finditer(html):
        body = _alive_function_body(html, m.end())
        if not body:
            continue
        if "textContent" in body and "indexOf" in body:
            return True
        if re.search(r"\btext\s*\.\s*indexOf\s*\(", body):
            return True
        if re.search(r"\.text\s*\(\s*\)\s*;?", body) and re.search(
            r"curr_tab\s*==\s*[\"'][^\"']*[\u4e00-\u9fff]", body
        ):
            return True
    return False


def _is_customer_view(rel: str) -> bool:
    rel = rel.replace("\\", "/")
    for prefix in CUSTOMER_VIEW_PREFIXES:
        if rel == prefix or rel.startswith(prefix + "/"):
            return True
    if rel == "user_home.html":
        return True
    return False


def tab_logic_uses_visible_label(text: str) -> bool:
    return bool(TAB_TEXT_GUARD.search(text))


def customer_tab_missing_stable_id(text: str) -> bool:
    """Tabs driven by curr_tab must use data-veikor-tab before label translation."""
    if "curr_tab" not in text or "layui-tab-title" not in text:
        return False
    return "data-veikor-tab" not in text


def main() -> int:
    bad_alive: list[str] = []
    bad_tabs: list[str] = []
    bad_tab_ids: list[str] = []
    for dirpath, _, files in os.walk(VIEWS):
        for fn in files:
            if not fn.endswith(".html"):
                continue
            path = os.path.join(dirpath, fn)
            rel = os.path.relpath(path, VIEWS)
            text = open(path, encoding="utf-8", errors="replace").read()
            if "Alive" in text and alive_uses_visible_text(text):
                bad_alive.append(rel)
            if _is_customer_view(rel) and tab_logic_uses_visible_label(text):
                bad_tabs.append(rel)
            if _is_customer_view(rel) and customer_tab_missing_stable_id(text):
                bad_tab_ids.append(rel)
    for fn in CUSTOMER_CONTROLLERS:
        path = os.path.join(CONTROLLERS, fn)
        if not os.path.isfile(path):
            continue
        text = open(path, encoding="utf-8", errors="replace").read()
        if tab_logic_uses_visible_label(text):
            bad_tabs.append(os.path.join("controller", fn))
    if bad_alive:
        print("page-alive still depends on visible text in:", file=sys.stderr)
        for rel in sorted(bad_alive):
            print(" ", rel, file=sys.stderr)
    if bad_tabs:
        print("customer tab logic still compares Chinese labels in:", file=sys.stderr)
        for rel in sorted(bad_tabs):
            print(" ", rel, file=sys.stderr)
    if bad_tab_ids:
        print("customer tabs use curr_tab without data-veikor-tab in:", file=sys.stderr)
        for rel in sorted(bad_tab_ids):
            print(" ", rel, file=sys.stderr)
    if bad_alive or bad_tabs or bad_tab_ids:
        return 1
    print("audit-panel-i18n-guards: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())