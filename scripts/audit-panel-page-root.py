#!/usr/bin/env python3
"""Fail CI when list pages use broken data-veikor-page → .layui-fluid resolution."""
from __future__ import annotations

import re
import sys
from pathlib import Path

PANEL_VIEWS = (
    Path(__file__).resolve().parent.parent
    / ".veikor-build/cdnfly-master-v5.1.13/master/panel/src/views"
)

BAD_CLOSEST = re.compile(r"marker\.closest\(\s*['\"]\.layui-fluid['\"]\s*\)")
BAD_CONTAINS = re.compile(r"!?\s*root\.contains\(\s*marker\s*\)")


def main() -> int:
    if not PANEL_VIEWS.is_dir():
        print("audit-panel-page-root: skip (panel tree missing)")
        return 0
    errors: list[str] = []
    for path in sorted(PANEL_VIEWS.rglob("*.html")):
        text = path.read_text(encoding="utf-8", errors="replace")
        rel = path.relative_to(PANEL_VIEWS)
        if BAD_CLOSEST.search(text):
            errors.append(f"{rel}: marker.closest('.layui-fluid') breaks sibling marker layout")
        if BAD_CONTAINS.search(text):
            errors.append(f"{rel}: root.contains(marker) is false for standard page templates")
    if errors:
        print("=== panel page-root audit FAILED ===")
        for line in errors:
            print(line)
        return 1
    print("=== panel page-root audit OK ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())