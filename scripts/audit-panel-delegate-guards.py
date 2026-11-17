#!/usr/bin/env python3
"""List pages: #LAY_app_body delegated clicks must call *Alive before side effects."""
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

TOUCH = re.compile(
    r"admin\.(?:popup|req)|layer\.prompt|location\.hash|table\.reload|update_stream"
)


def main() -> int:
    issues: list[tuple[str, int]] = []
    patterns = (
        re.compile(
            r'\$\(\s*["\']#LAY_app_body[^"\']*["\']\s*\)\.(?:click\s*\(\s*function|on\s*\(\s*["\']click)',
        ),
        re.compile(r'\$\(\s*["\']#recharge["\']\s*\)\.click\s*\(\s*function'),
    )
    for dirpath, _, files in os.walk(VIEWS):
        for fn in files:
            if not fn.endswith(".html"):
                continue
            path = os.path.join(dirpath, fn)
            text = open(path, encoding="utf-8", errors="replace").read()
            guards = list(dict.fromkeys(re.findall(r"function (\w+Alive)\s*\(", text)))
            if not guards:
                continue
            for pat in patterns:
                for m in pat.finditer(text):
                    body = text[m.end() : m.end() + 180]
                    if not TOUCH.search(body):
                        continue
                    if not any(g + "()" in body for g in guards):
                        line = text[: m.start()].count("\n") + 1
                        issues.append((os.path.relpath(path, VIEWS), line))
    if issues:
        print("=== LAY_app_body delegate click guard gaps ===")
        for rel, line in sorted(set(issues)):
            print(f"  {rel}:{line}")
        print("count", len(set(issues)))
        return 1
    print("=== LAY_app_body delegate click guards OK ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())