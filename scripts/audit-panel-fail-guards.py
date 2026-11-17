#!/usr/bin/env python3
"""Pages with *Alive should guard batch fail: and stop*Batch with Alive."""
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


def main() -> int:
    issues = []
    for dirpath, _, files in os.walk(VIEWS):
        for fn in files:
            if not fn.endswith(".html"):
                continue
            rel = os.path.relpath(os.path.join(dirpath, fn), VIEWS)
            text = open(
                os.path.join(dirpath, fn), encoding="utf-8", errors="replace"
            ).read()
            guards = re.findall(r"function (\w+Alive)\s*\(", text)
            if re.search(r"function siteBatchOnList\s*\(", text):
                guards.append("siteBatchOnList")
            if not guards:
                continue
            for m in re.finditer(r"function (stop\w+Batch)\s*\(", text):
                fn_name = m.group(1)
                body = text[m.end() : m.end() + 200].split("}")[0]
                if not any(g + "()" in body for g in guards):
                    issues.append(
                        (rel, fn_name, f"{fn_name} missing batch guard ({guards[0]}…)")
                    )
    if issues:
        print("=== fail / stopBatch guard gaps ===")
        for rel, kind, detail in sorted(set(issues)):
            print(f"  {rel}: {kind} — {detail}")
        print("count", len(set(issues)))
        return 1
    print("=== fail / stopBatch guards OK ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())