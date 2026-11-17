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
ALIVE_OPEN = re.compile(r"function\s+(\w+Alive)\s*\([^)]*\)\s*\{")


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


def main() -> int:
    bad: list[str] = []
    for dirpath, _, files in os.walk(VIEWS):
        for fn in files:
            if not fn.endswith(".html"):
                continue
            path = os.path.join(dirpath, fn)
            text = open(path, encoding="utf-8", errors="replace").read()
            if "Alive" not in text:
                continue
            if alive_uses_visible_text(text):
                bad.append(os.path.relpath(path, VIEWS))
    if bad:
        print("page-alive still depends on visible text in:", file=sys.stderr)
        for rel in sorted(bad):
            print(" ", rel, file=sys.stderr)
        return 1
    print("audit-panel-i18n-guards: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())