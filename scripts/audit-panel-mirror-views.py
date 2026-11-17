#!/usr/bin/env python3
"""Enforce byte-identical mirror view pairs (scheme section A in docs/customer-console-i18n.md)."""
from __future__ import annotations

import os
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

# rel paths under views/ — left and right must match per relative path
MIRROR_DIRS = (
    ("account/log", "system/log"),
)


def file_map(base: str) -> dict[str, bytes]:
    out: dict[str, bytes] = {}
    if not os.path.isdir(base):
        return out
    for dirpath, _, files in os.walk(base):
        for fn in files:
            if not fn.endswith(".html"):
                continue
            path = os.path.join(dirpath, fn)
            rel = os.path.relpath(path, base).replace("\\", "/")
            with open(path, "rb") as f:
                out[rel] = f.read()
    return out


def main() -> int:
    bad: list[str] = []
    for left, right in MIRROR_DIRS:
        la = os.path.join(ROOT, left)
        rb = os.path.join(ROOT, right)
        ma, mb = file_map(la), file_map(rb)
        only_l = set(ma) - set(mb)
        only_r = set(mb) - set(ma)
        for rel in sorted(only_l):
            bad.append(f"missing in {right}: {left}/{rel}")
        for rel in sorted(only_r):
            bad.append(f"missing in {left}: {right}/{rel}")
        for rel in sorted(set(ma) & set(mb)):
            if ma[rel] != mb[rel]:
                bad.append(f"content drift: {left}/{rel} vs {right}/{rel}")
    if bad:
        print("audit-panel-mirror-views:", file=sys.stderr)
        for line in bad:
            print(" ", line, file=sys.stderr)
        return 1
    print("audit-panel-mirror-views: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())