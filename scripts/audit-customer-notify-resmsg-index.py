#!/usr/bin/env python3
"""List HTTP paths in customer views that use notifyResMsg (P3 intake aid; read-only)."""
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
    "views",
)
CUSTOMER_PREFIXES = (
    "site/",
    "stream/",
    "account/",
    "finance/",
    os.path.join("package", "my") + os.sep,
    os.path.join("package", "buy") + os.sep,
    "user_home",
    os.path.join("system", "message") + os.sep,
)
URL_LITERAL = re.compile(r"""url:\s*['"]([^'"]+)['"]""")


def is_customer(rel: str) -> bool:
    if rel.startswith("package/upgrade") or rel.startswith("package/sold"):
        return False
    return any(rel.startswith(p) or rel == p.rstrip(os.sep) + ".html" for p in CUSTOMER_PREFIXES)


def main() -> int:
    hits: dict[str, list[str]] = {}
    for dirpath, _, files in os.walk(ROOT):
        for fn in files:
            if not fn.endswith(".html"):
                continue
            rel = os.path.relpath(os.path.join(dirpath, fn), ROOT)
            if not is_customer(rel):
                continue
            text = open(os.path.join(dirpath, fn), encoding="utf-8", errors="replace").read()
            if "notifyResMsg" not in text:
                continue
            for m in URL_LITERAL.finditer(text):
                path = m.group(1).split("?")[0]
                hits.setdefault(path, []).append(rel)

    if not hits:
        print("no customer views with notifyResMsg found")
        return 0

    for path in sorted(hits):
        files = ", ".join(sorted(set(hits[path])))
        print(f"{path}\t{files}")
    print(f"\n{len(hits)} distinct path prefix(es); add unmapped res.msg to API_MSG_BY_SOURCE", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())