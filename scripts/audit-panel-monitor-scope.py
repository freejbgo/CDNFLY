#!/usr/bin/env python3
"""Reject global #date bindings in monitor controllers and search pages."""
import os
import re
import sys

ROOT = os.path.join(os.path.dirname(__file__), "..")
PANEL = os.path.join(ROOT, ".veikor-build", "cdnfly-master-v5.1.13", "master/panel/src")
FAILURES = []


def fail(msg):
    FAILURES.append(msg)


def scan_senior_controllers():
    patterns = [
        "elem: '#date'",
        '$("#date")',
        '$("#date_tip")',
        '$("#query")',
        '$(".active-btn").data("hour")',
        '$(".active-btn").data("day")',
    ]
    for name in (
        "node_senior.js",
        "senior.js",
        "stream_senior.js",
        "site-usage-senior.js",
        "stream-usage-senior.js",
    ):
        path = os.path.join(PANEL, "controller", name)
        if not os.path.isfile(path):
            continue
        text = open(path, encoding="utf-8", errors="replace").read()
        for p in patterns:
            if p in text:
                fail(f"{name}: still uses global selector pattern {p!r}")


def scan_views_date_id():
    views = os.path.join(PANEL, "views")
    for dirpath, _, files in os.walk(views):
        for fn in files:
            if not fn.endswith(".html"):
                continue
            rel = os.path.relpath(os.path.join(dirpath, fn), views)
            text = open(os.path.join(dirpath, fn), encoding="utf-8", errors="replace").read()
            if 'id="date"' in text and "monitor" in rel:
                fail(f"views/{rel}: duplicate id=date in monitor view")
            if "elem: '#date'" in text:
                fail(f"views/{rel}: laydate still binds elem #date")


def main():
    scan_senior_controllers()
    scan_views_date_id()
    if FAILURES:
        print("=== monitor scope audit FAILED ===", file=sys.stderr)
        for f in FAILURES:
            print(f, file=sys.stderr)
        sys.exit(1)
    print("[OK] monitor scope audit")
    return 0


if __name__ == "__main__":
    main()