#!/usr/bin/env python3
"""
Guard customer menu paths that reuse templates via symlinks (see docs/customer-console-i18n.md).

Editing finance/order or system/log is enough — account/order and account/log are aliases.
"""
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
    "account",
)

# link name under views/account/ -> expected target (relative to views/account/)
EXPECTED_SYMLINKS = {
    "log": "../system/log",
    "order": "../finance/order",
    "balance": "../finance/balance",
}


def _norm_target(raw: str) -> str:
    raw = raw.rstrip("/")
    if raw.endswith("/."):
        raw = raw[:-2]
    return raw


def main() -> int:
    bad: list[str] = []
    if not os.path.isdir(ROOT):
        print(f"missing {ROOT}", file=sys.stderr)
        return 1
    for name, want in EXPECTED_SYMLINKS.items():
        path = os.path.join(ROOT, name)
        if not os.path.lexists(path):
            bad.append(f"missing alias: account/{name}")
            continue
        if not os.path.islink(path):
            bad.append(f"account/{name} must stay a symlink to {want} (got plain file/dir)")
            continue
        got = _norm_target(os.readlink(path))
        want_norm = _norm_target(want)
        if got != want_norm:
            bad.append(f"account/{name} -> {got!r}, expected {want_norm!r}")
    if bad:
        print("audit-panel-view-aliases:", file=sys.stderr)
        for line in bad:
            print(" ", line, file=sys.stderr)
        return 1
    print("audit-panel-view-aliases: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())