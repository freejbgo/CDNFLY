#!/usr/bin/env python3
"""Account-style pages: #id click handlers with admin.req need *Alive at entry."""
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

SKIP = {"finance/recharge/index.html"}


def main() -> int:
    issues: list[tuple[str, int, str]] = []
    pat = re.compile(r'\$\(\s*["\']#[^"\']+["\']\s*\)\.click\s*\(\s*function')
    for dirpath, _, files in os.walk(VIEWS):
        for fn in files:
            if not fn.endswith(".html"):
                continue
            rel = os.path.relpath(os.path.join(dirpath, fn), VIEWS)
            if rel in SKIP:
                continue
            path = os.path.join(dirpath, fn)
            text = open(path, encoding="utf-8", errors="replace").read()
            guards = list(dict.fromkeys(re.findall(r"function (\w+Alive)\s*\(", text)))
            if not guards:
                continue
            for m in pat.finditer(text):
                body = text[m.end() : m.end() + 450]
                if "admin.req" not in body and "layer.prompt" not in body:
                    continue
                head = body[:160]
                if any(g + "()" in head for g in guards):
                    continue
                line = text[: m.start()].count("\n") + 1
                sel = m.group(0)[:40]
                issues.append((rel, line, sel))
    if issues:
        print("=== #id click admin.req guard gaps ===")
        for rel, line, sel in sorted(set(issues)):
            print(f"  {rel}:{line} {sel}")
        print("count", len(set(issues)))
        return 1
    print("=== #id click guards OK ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())