#!/usr/bin/env python3
"""setInterval poll helpers that call admin.req must *Alive() at function entry."""
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


def callee_name(expr: str) -> str | None:
    expr = expr.strip()
    m = re.match(r"(?:window\.)?(\w+)\s*\(", expr)
    return m.group(1) if m else None


def find_function_body(text: str, name: str) -> str | None:
    for pat in (
        r"function\s+" + re.escape(name) + r"\s*\(",
        re.escape(name) + r"\s*=\s*function\s*\(",
        r"window\." + re.escape(name) + r"\s*=\s*function\s*\(",
    ):
        m = re.search(pat, text)
        if not m:
            continue
        start = m.end()
        brace = text.find("{", start - 1)
        if brace < 0:
            brace = text.find("{", start)
        if brace < 0:
            continue
        return text[brace + 1 : brace + 200]
    return None


def main() -> int:
    issues: list[tuple[str, str]] = []
    for dirpath, _, files in os.walk(VIEWS):
        for fn in files:
            if not fn.endswith(".html"):
                continue
            path = os.path.join(dirpath, fn)
            text = open(path, encoding="utf-8", errors="replace").read()
            if "setInterval" not in text:
                continue
            seen = set()
            for m in re.finditer(r"setInterval\s*\(\s*['\"]([^'\"]+)", text):
                expr = m.group(1)
                name = callee_name(expr)
                if not name or name in seen:
                    continue
                seen.add(name)
                body = find_function_body(text, name)
                if not body or "admin.req" not in text[text.find(name) : text.find(name) + 1200]:
                    continue
                if not re.search(r"\w+Alive\s*\(", body) and "clearInterval" not in body[:120]:
                    rel = os.path.relpath(path, VIEWS)
                    issues.append((rel, name))
    if issues:
        print("=== setInterval admin.req poll guard gaps ===")
        for rel, name in sorted(set(issues)):
            print(f"  {rel}: {name}()")
        print("count", len(set(issues)))
        return 1
    print("=== setInterval poll guards OK ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())