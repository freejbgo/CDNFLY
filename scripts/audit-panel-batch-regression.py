#!/usr/bin/env python3
"""Regression checks for Veikor cross-page table bulk (CheckedMap / veikorLocalBatch)."""
import os
import re
import sys
import tarfile

ROOT = os.path.join(
    os.path.dirname(__file__),
    "..",
)
PANEL = os.path.join(
    ROOT,
    ".veikor-build",
    "cdnfly-master-v5.1.13",
    "master",
    "panel",
    "src",
)
VIEWS = os.path.join(PANEL, "views")
TAR = os.path.join(ROOT, "cdnfly", "cdnfly-master-v5.1.13-centos-7.tar.gz")
PREFIX = "cdnfly-master-v5.1.13/master/panel/src/"

FAILURES = []


def fail(msg):
    FAILURES.append(msg)


def cross_page_helpers(text):
    return any(
        x in text
        for x in (
            "CheckedMap",
            "veikorLocalBatch",
            "vekorCollect",
            "collectChecked",
            "IdsForBatch",
        )
    )


def scan_views():
    for dirpath, _, files in os.walk(VIEWS):
        for fn in files:
            if not fn.endswith(".html"):
                continue
            rel = os.path.relpath(os.path.join(dirpath, fn), VIEWS)
            if rel.startswith("user/"):
                continue
            text = open(os.path.join(dirpath, fn), encoding="utf-8", errors="replace").read()

            if re.search(r"if \(!table_data\[i\]\['LAY_CHECKED'\]", text):
                fail(f"{rel}: legacy LAY_CHECKED delete filter still present")

            if re.search(r"type:\s*['\"]checkbox['\"]", text) and re.search(
                r",page:\s*true", text
            ):
                if cross_page_helpers(text) and "limits:" in text:
                    if not re.search(r"limits:\s*\[[^\]]*500", text):
                        fail(f"{rel}: paged bulk table missing limits 500 option")

            if "table.on('toolbar" in text or 'table.on("toolbar' in text:
                for m in re.finditer(
                    r"table\.on\(['\"]toolbar[^)]+\),[\s\S]{0,1600}?switch\s*\(\s*obj\.event\s*\)",
                    text,
                ):
                    block = m.group(0)
                    if "checkStatus.data" not in block:
                        continue
                    if cross_page_helpers(block):
                        continue
                    fail(f"{rel}: toolbar handler uses checkStatus.data without bulk helper")


def scan_index_preload():
    index_path = os.path.join(PANEL, "index.js")
    text = open(index_path, encoding="utf-8", errors="replace").read()
    if "define(['setter', 'admin', 'veikorLocalBatch']" not in text:
        fail("index.js: veikorLocalBatch not preloaded in main define()")


def scan_tar_drift():
    if not os.path.isfile(TAR) or not os.path.isdir(PANEL):
        return
    drift = 0
    with tarfile.open(TAR) as tf:
        for member in tf.getmembers():
            if not member.name.startswith(PREFIX) or member.isdir():
                continue
            rel = member.name[len(PREFIX) :]
            local = os.path.join(PANEL, rel)
            if not os.path.isfile(local):
                continue
            tb = tf.extractfile(member).read()
            lb = open(local, "rb").read()
            if tb != lb:
                drift += 1
    if drift:
        fail(f"published tar: {drift} panel file(s) differ from .veikor-build (run sync-panel-to-master-tar.sh)")


def main():
    scan_views()
    scan_index_preload()
    scan_tar_drift()
    if FAILURES:
        print("=== batch regression FAILED ===")
        for f in FAILURES:
            print(f)
        print(f"total {len(FAILURES)}")
        sys.exit(1)
    print("=== batch regression OK ===")


if __name__ == "__main__":
    main()