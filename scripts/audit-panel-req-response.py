#!/usr/bin/env python3
"""Heuristic: admin.req done must guard !res before using res.data (not only var data =)."""
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

SKIP_REL = (
    "config/default/index.html",
    "config/res/index.html",
)


def block_has_res_guard(block: str) -> bool:
    head = block[:320]
    if re.search(r"!\s*res\b", head):
        return True
    if re.search(r"res\s*&&\s*res\.data", head):
        return True
    if re.search(r"if\s*\(\s*res\.data\s*\)", head):
        return True
    return False


def main() -> int:
    issues = []
    for dirpath, _, files in os.walk(VIEWS):
        for fn in files:
            if not fn.endswith(".html") or fn.endswith("-bak"):
                continue
            rel = os.path.relpath(os.path.join(dirpath, fn), VIEWS)
            if rel in SKIP_REL:
                continue
            text = open(
                os.path.join(dirpath, fn), encoding="utf-8", errors="replace"
            ).read()
            for m in re.finditer(r",done:\s*function\s*\(res\)\s*\{", text):
                start = m.end()
                depth = 1
                i = start
                while i < len(text) and depth > 0:
                    if text[i] == "{":
                        depth += 1
                    elif text[i] == "}":
                        depth -= 1
                    i += 1
                block = text[start : i - 1]
                if "res.data" not in block:
                    continue
                if block_has_res_guard(block):
                    continue
                line = text[: m.start()].count("\n") + 1
                hint = block.strip().split("\n")[0][:72]
                issues.append((rel, line, hint))
    if issues:
        print("=== done(res) uses res.data without !res guard ===")
        for rel, ln, hint in sorted(issues):
            print(f"  {rel}:{ln}: {hint}")
        print("count", len(issues))
        return 1
    print("=== req response guards OK ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())