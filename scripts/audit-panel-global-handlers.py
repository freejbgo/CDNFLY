#!/usr/bin/env python3
"""Global onclick/search helpers must guard table.reload with page Alive."""
import os
import re
import sys

VIEWS = os.path.join(
    os.path.dirname(__file__),
    "..",
    ".veikor-build",
    "cdnfly-master-v5.1.13",
    "master",
    "panel",
    "src",
    "views",
)


def has_guard(body: str) -> bool:
    if re.search(r"\w+Alive\s*\(", body):
        return True
    if "refreshPageAlive" in body or "unlockIpPopupAlive" in body:
        return True
    if "siteBatchOnList" in body:
        return True
    if re.search(r"path\[0\]", body) and "router().path" in body:
        return True
    if "getElementById('LAY-popup" in body and "return" in body[:120]:
        return True
    return False


def main() -> int:
    issues: list[tuple[str, int, str]] = []
    for dirpath, _, files in os.walk(VIEWS):
        for fn in files:
            if not fn.endswith(".html"):
                continue
            path = os.path.join(dirpath, fn)
            text = open(path, encoding="utf-8", errors="replace").read()
            for m in re.finditer(
                r"(?:^|\n)\s*function\s+(\w+)\s*\([^)]*\)\s*\{",
                text,
            ):
                name = m.group(1)
                if name.startswith("stop") and name.endswith("Batch"):
                    continue
                body = text[m.end() : m.end() + 400]
                if "table.reload" not in body and "layui.table.reload" not in body:
                    continue
                if has_guard(body):
                    continue
                line = text[: m.start()].count("\n") + 1
                issues.append((os.path.relpath(path, VIEWS), line, name))
    if issues:
        print("=== global handler table.reload guard gaps ===")
        for rel, line, name in sorted(set(issues)):
            print(f"  {rel}:{line} {name}()")
        print("count", len(set(issues)))
        return 1
    print("=== global handler guards OK ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())