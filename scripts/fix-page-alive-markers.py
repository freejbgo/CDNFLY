#!/usr/bin/env python3
"""Replace page-alive checks that depend on visible Chinese text with data-veikor-page markers."""
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


def page_id_from_path(path: str) -> str:
    rel = os.path.relpath(path, ROOT).replace("\\", "/")
    if rel.endswith("/index.html"):
        rel = rel[: -len("/index.html")]
    elif rel.endswith(".html"):
        rel = rel[: -len(".html")]
    return rel


def ensure_marker(html: str, page_id: str) -> str:
    marker = (
        f'<span data-veikor-page="{page_id}" class="layui-hide" '
        f'aria-hidden="true"></span>'
    )
    if f'data-veikor-page="{page_id}"' in html:
        return html
    # After <title>...</title> if present
    m = re.search(r"(<title>[^<]*</title>\s*)", html, re.I)
    if m:
        return html[: m.end()] + "\n\n  " + marker + "\n" + html[m.end() :]
    if html.lstrip().startswith("<div"):
        return re.sub(r"(^\s*)<div", r"\1" + marker + "\n\\1<div", html, count=1)
    return marker + "\n" + html


def patch_alive(html: str, page_id: str) -> tuple[str, bool]:
    changed = False
    extra = ""
    # Optional anchor: table id or unique input marker already in file
    m_table = re.search(r"id=[\"'](test-table-toolbar|rule|dnsapi)[\"']", html)
    if m_table:
        extra = ", '#" + m_table.group(1) + "'"
    marker_call = f"return window.veikorPageMarkerAlive('{page_id}'{extra});"

    patterns = [
        r"return\s+!!\(body\s+&&\s+\(body\.textContent\s*\|\|\s*''\)\.indexOf\([^)]+\)\s*>=\s*0\);",
        r"return\s+!!\(body\s+&&\s+body\.querySelector\([^)]+\)\s+&&\s+\(body\.textContent\s*\|\|\s*''\)\.indexOf\([^)]+\)\s*>=\s*0\);",
        r"return\s+text\.indexOf\([^)]+\)\s*>=\s*0\s*&&\s*text\.indexOf\([^)]+\)\s*>=\s*0;",
        r"return\s+text\.indexOf\([^)]+\)\s*>=\s*0;",
    ]
    for pat in patterns:
        if re.search(pat, html):
            html = re.sub(pat, marker_call, html)
            changed = True
            break

    # Drop unused body/text vars when only used for indexOf (heuristic trim)
    if changed:
        html = re.sub(
            r"\s*var body = document\.querySelector\('#LAY_app_body'\);\s*"
            r"var text = body \? \(body\.textContent \|\| ''\) : '';\s*",
            "\n      ",
            html,
        )
        html = re.sub(
            r"\s*var body = document\.querySelector\('#LAY_app_body'\);\s*"
            r"return window\.veikorPageMarkerAlive",
            "\n      return window.veikorPageMarkerAlive",
            html,
        )
    return html, changed


def main() -> int:
    touched = 0
    for dirpath, _, files in os.walk(ROOT):
        for fn in files:
            if not fn.endswith(".html"):
                continue
            path = os.path.join(dirpath, fn)
            page_id = page_id_from_path(path)
            text = open(path, encoding="utf-8", errors="replace").read()
            if "Alive" not in text and "Alive(" not in text:
                continue
            if "indexOf(" not in text and "textContent" not in text:
                continue
            new_text, changed = patch_alive(text, page_id)
            if changed:
                new_text = ensure_marker(new_text, page_id)
                open(path, "w", encoding="utf-8").write(new_text)
                touched += 1
                print("patched", page_id)
    print("files_patched", touched)
    return 0


if __name__ == "__main__":
    sys.exit(main())