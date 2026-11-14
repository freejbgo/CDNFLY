#!/usr/bin/env python3
"""Heuristic scan of panel views against Veikor dev-table patterns."""
import os
import re
import sys

PANEL = os.path.join(
    os.path.dirname(__file__),
    "..",
    ".veikor-build",
    "cdnfly-master-v5.1.13",
    "master",
    "panel",
    "src",
    "views",
)


def scan():
    reload_no_page = []
    bare_render = []
    laydate_bad = []
    req_no_alive_hint = []

    for dirpath, _, files in os.walk(PANEL):
        for fn in files:
            if not fn.endswith(".html"):
                continue
            path = os.path.join(dirpath, fn)
            rel = os.path.relpath(path, PANEL)
            text = open(path, encoding="utf-8", errors="replace").read()
            has_alive = bool(re.search(r"function \w+Alive", text))

            if re.search(r"\bform\.render\s*\(\s*\)", text) or re.search(
                r"\blayui\.form\.render\s*\(\s*\)", text
            ):
                bare_render.append(rel)

            if re.search(r"elem:\s*['\"]#date['\"]", text):
                if 'id="date"' not in text and "id='date'" not in text:
                    laydate_bad.append(rel)

            def extract_calls(txt, name="table.reload"):
                out, i = [], 0
                while True:
                    j = txt.find(name, i)
                    if j < 0:
                        break
                    k = txt.find("(", j)
                    if k < 0:
                        break
                    depth, end = 0, k
                    for idx in range(k, len(txt)):
                        c = txt[idx]
                        if c == "(":
                            depth += 1
                        elif c == ")":
                            depth -= 1
                            if depth == 0:
                                end = idx + 1
                                break
                    out.append(txt[j:end])
                    i = end
                return out

            for call in extract_calls(text):
                if "where" in call and "curr" not in call:
                    if "sort" not in call.lower():
                        reload_no_page.append(rel)
                        break

            if "admin.req" in text and has_alive:
                # done callbacks without Alive check (rough)
                blocks = re.findall(
                    r",done:\s*function\s*\([^)]*\)\s*\{([^}]{0,400})",
                    text,
                    re.DOTALL,
                )
                for b in blocks:
                    if "LAY_app_body" in b or ".val(" in b or ".text(" in b:
                        popup_guarded = (
                            "LAY-popup" in b
                            or "layero" in b
                            or "nodeDnsRoot" in b
                        )
                        if (
                            "Alive()" not in b
                            and "alive()" not in b
                            and not popup_guarded
                        ):
                            req_no_alive_hint.append((rel, b[:60].replace("\n", " ")))
                            break

    return reload_no_page, bare_render, laydate_bad, req_no_alive_hint


def main():
    r1, r2, r3, r4 = scan()
    print("=== reload where without page.curr (unique files) ===")
    for f in sorted(set(r1)):
        print(f)
    print("count", len(set(r1)))
    print("=== bare form.render ===", r2)
    print("=== laydate missing #date ===", r3)
    print("=== admin.req done may lack Alive (hint) ===")
    for rel, hint in sorted(set((a, b) for a, b in r4))[:40]:
        print(rel, ":", hint)
    print("hint count", len(set((a, b) for a, b in r4)))
    return 0


if __name__ == "__main__":
    sys.exit(main())