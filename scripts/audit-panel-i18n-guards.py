#!/usr/bin/env python3
"""Fail if page-alive guards still depend on Chinese text in the DOM."""
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
PAT = re.compile(
    r"function\s+\w+Alive\s*\([^)]*\)\s*\{[\s\S]*?"
    r"(textContent|\.text\(\))\s*[^\n]*indexOf\(",
    re.M,
)


def main() -> int:
    bad = []
    for dirpath, _, files in os.walk(VIEWS):
        for fn in files:
            if not fn.endswith(".html"):
                continue
            path = os.path.join(dirpath, fn)
            text = open(path, encoding="utf-8", errors="replace").read()
            if not re.search(r"function\s+\w+Alive", text):
                continue
            if PAT.search(text):
                bad.append(os.path.relpath(path, VIEWS))
    if bad:
        print("page-alive still uses textContent/indexOf in:", file=sys.stderr)
        for rel in sorted(bad):
            print(" ", rel, file=sys.stderr)
        return 1
    print("audit-panel-i18n-guards: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())