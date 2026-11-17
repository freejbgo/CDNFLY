#!/usr/bin/env python3
"""Pages with *Alive should guard element tab/collapse handlers that touch tables."""
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
    r"render_table|table\.resize|table\.reload|layui\.table\.reload|admin\.req"
)


def guard_names(text: str) -> list[str]:
    names = re.findall(r"function (\w+Alive)\s*\(", text)
    if re.search(r"function siteUpdatePopupAlive\s*\(", text):
        names.append("siteUpdatePopupAlive")
    return list(dict.fromkeys(names))


def handler_body(text: str, start: int) -> str:
    fn = text.find("function", start)
    if fn < 0:
        return ""
    brace = text.find("{", fn)
    if brace < 0:
        return ""
    return text[brace + 1 : brace + 401]


def main() -> int:
    issues: list[tuple[str, int]] = []
    pat = re.compile(r"(?:layui\.)?element\.on\(\s*['\"](?:tab|collapse)")
    for dirpath, _, files in os.walk(VIEWS):
        for fn in files:
            if not fn.endswith(".html"):
                continue
            path = os.path.join(dirpath, fn)
            text = open(path, encoding="utf-8", errors="replace").read()
            guards = guard_names(text)
            if not guards:
                continue
            for m in pat.finditer(text):
                body = handler_body(text, m.end())
                if not TOUCH.search(body):
                    continue
                if not any(g + "()" in body for g in guards):
                    line = text[: m.start()].count("\n") + 1
                    issues.append((os.path.relpath(path, VIEWS), line))
    if issues:
        print("=== element tab/collapse guard gaps ===")
        for rel, line in sorted(set(issues)):
            print(f"  {rel}:{line}")
        print("count", len(set(issues)))
        return 1
    print("=== element tab/collapse guards OK ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())