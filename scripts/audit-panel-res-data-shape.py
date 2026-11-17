#!/usr/bin/env python3
"""Regression: every `var data = res.data` in panel views should have a shape guard."""
import os
import re
import sys

PANEL_VIEWS = os.path.join(
    os.path.dirname(__file__),
    "..",
    ".veikor-build",
    "cdnfly-master-v5.1.13",
    "master",
    "panel",
    "src",
    "views",
)


def is_guard_line(line: str) -> bool:
    s = line.strip()
    if not s.startswith("if"):
        return False
    if re.search(r"typeof\s+data\s*[=!]", s):
        return True
    if "Array.isArray(data)" in s:
        return True
    if re.search(r"data\s*==\s*null", s):
        return True
    if re.search(r"if\s*\(\s*!data\s*(\|\||\)|&&)", s):
        return True
    if re.search(r"if\s*\(\s*data\s*==\s*null", s):
        return True
    return False


def main() -> int:
    missing = []
    for dirpath, _, files in os.walk(PANEL_VIEWS):
        for fn in files:
            if not fn.endswith(".html") or fn.endswith("-bak"):
                continue
            rel = os.path.relpath(os.path.join(dirpath, fn), PANEL_VIEWS)
            lines = open(
                os.path.join(dirpath, fn), encoding="utf-8", errors="replace"
            ).read().split("\n")
            for i, line in enumerate(lines):
                if not re.match(r"\s*var data = res\.data\s*$", line):
                    continue
                j = i + 1
                while j < len(lines) and not lines[j].strip():
                    j += 1
                if j >= len(lines):
                    missing.append((rel, i + 1, "eof after res.data"))
                    continue
                if is_guard_line(lines[j]):
                    continue
                if lines[j].strip().startswith("window.region_list = data"):
                    continue
                if re.match(
                    r"\s*if\s*\(\s*!Array\.isArray\(data\)\)\s*data\s*=", lines[j]
                ):
                    continue
                missing.append((rel, i + 1, lines[j].strip()[:72]))
    if missing:
        print("=== res.data shape guard missing ===")
        for rel, ln, hint in sorted(missing):
            print(f"  {rel}:{ln}: {hint}")
        print("count", len(missing))
        return 1
    print("=== res.data shape guards OK ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())