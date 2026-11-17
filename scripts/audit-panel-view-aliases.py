#!/usr/bin/env python3
"""
Guard customer menu paths that reuse templates via symlinks (see docs/customer-console-i18n.md).

Checks both .veikor-build sources and the published master tar (cp -a must preserve links).
"""
from __future__ import annotations

import os
import sys
import tarfile

REPO = os.path.join(os.path.dirname(__file__), "..")
ROOT = os.path.join(
    REPO,
    ".veikor-build",
    "cdnfly-master-v5.1.13",
    "master",
    "panel",
    "src",
    "views",
    "account",
)
TAR = os.path.join(REPO, "cdnfly", "cdnfly-master-v5.1.13-centos-7.tar.gz")
TAR_PREFIX = "cdnfly-master-v5.1.13/master/panel/src/views/account/"

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


def check_build_tree(bad: list[str]) -> None:
    if not os.path.isdir(ROOT):
        bad.append(f"missing {ROOT}")
        return
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


def check_tarball(bad: list[str]) -> None:
    if not os.path.isfile(TAR):
        bad.append(f"missing tarball {TAR}")
        return
    with tarfile.open(TAR, "r:gz") as tf:
        for name, want in EXPECTED_SYMLINKS.items():
            member_name = TAR_PREFIX + name
            try:
                member = tf.getmember(member_name)
            except KeyError:
                bad.append(f"tar missing account/{name}")
                continue
            if member.isdir():
                bad.append(f"tar account/{name} is a directory, expected symlink")
                continue
            if not member.issym():
                bad.append(f"tar account/{name} must be a symlink in the package")
                continue
            got = _norm_target(member.linkname)
            want_norm = _norm_target(want)
            if got != want_norm:
                bad.append(f"tar account/{name} -> {got!r}, expected {want_norm!r}")


def main() -> int:
    bad: list[str] = []
    check_build_tree(bad)
    check_tarball(bad)
    if bad:
        print("audit-panel-view-aliases:", file=sys.stderr)
        for line in bad:
            print(" ", line, file=sys.stderr)
        return 1
    print("audit-panel-view-aliases: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())