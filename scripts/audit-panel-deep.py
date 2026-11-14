#!/usr/bin/env python3
"""Deeper Veikor dev-table heuristics: req callbacks, date clear, global selectors."""
import os
import re

ROOT = os.path.join(
    os.path.dirname(__file__),
    "..",
    ".veikor-build",
    "cdnfly-master-v5.1.13",
    "master",
    "panel",
    "src",
)
PANEL = os.path.join(ROOT, "views")
CTRL = os.path.join(ROOT, "controller")

ISSUES = []


def add(rel, kind, detail=""):
    ISSUES.append((rel, kind, detail))


def walk():
    for dirpath, _, files in os.walk(PANEL):
        for fn in files:
            if not fn.endswith(".html"):
                continue
            path = os.path.join(dirpath, fn)
            rel = os.path.relpath(path, PANEL)
            text = open(path, encoding="utf-8", errors="replace").read()
            scan_file(rel, text)


def scan_file(rel, text):
    has_alive = bool(re.search(r"function \w+Alive", text))

    # laydate done: end may stick when value cleared (dev table)
    if "laydate.render" in text and "range: true" in text:
        blocks = re.findall(
            r"done:\s*function\s*\([^)]*\)\s*\{([^}]{0,600})",
            text,
            re.DOTALL,
        )
        for b in blocks:
            if "split" in b and "end" in b and "start" in b:
                if 'end = parts[1] || ""' not in b and 'end=""' not in b.replace(" ", ""):
                    if 'parts[1]' in b and '|| ""' not in b.split("end")[0][-80:]:
                        add(rel, "laydate_end_maybe_sticky", b[:80].replace("\n", " "))

    # Global LAY_app_body change handlers without alive on same block
    if has_alive:
        for m in re.finditer(
            r"\$\(['\"]#LAY_app_body[^)]+\)\.(?:on|change)\([^;]{0,200}",
            text,
        ):
            chunk = m.group(0)
            if "Alive()" not in chunk:
                # look ahead 5 lines in text
                pos = m.start()
                tail = text[pos : pos + 400]
                if "Alive()" not in tail.split("});")[0]:
                    add(rel, "lay_app_listener_maybe_no_alive", chunk[:70])

    # admin.req done touching DOM without Alive/popup guard (heuristic)
    if "admin.req" in text:
        for m in re.finditer(
            r",done:\s*function\s*\([^)]*\)\s*\{([\s\S]*?)\n\s*\}",
            text,
        ):
            body = m.group(1)
            if len(body) > 800:
                body = body[:800]
            touches = (
                "LAY_app_body" in body
                or re.search(r"\$\(['\"]\.", body)
                or ".html(" in body
                or ".val(" in body
            )
            guarded = (
                "Alive()" in body
                or "Still()" in body
                or "alive()" in body
                or "nodeDnsRoot()" in body
                or "querySelector('#LAY-popup" in body
                or "getElementById('LAY-popup" in body
                or "linePageAlive" in body
                or "$(layero)" in body
                or "layero" in body and "LAY-popup" in body
            )
            if touches and not guarded and has_alive:
                add(rel, "req_done_no_alive", body[:90].replace("\n", " "))

    # Realtime/monitor: admin.req in monitor paths without alive in done
    if any(
        x in rel
        for x in (
            "monitor/top",
            "monitor/usage",
            "monitor/realtime",
            "monitor/index",
        )
    ):
        if "admin.req" in text and has_alive:
            if text.count("admin.req") > text.count("Alive()"):
                add(rel, "monitor_req_vs_alive_imbalance", f"req={text.count('admin.req')} alive_checks={text.count('Alive()')}")


def scan_controllers():
    if not os.path.isdir(CTRL):
        return
    for fn in os.listdir(CTRL):
        if not fn.endswith(".js"):
            continue
        path = os.path.join(CTRL, fn)
        text = open(path, encoding="utf-8", errors="replace").read()
        still_m = re.search(r"function (\w+Still)\s*\(", text)
        if not still_m and "RealtimeStill" not in text:
            continue
        still_names = re.findall(r"function (\w+Still)\s*\(", text)
        for m in re.finditer(
            r",done:\s*function\s*\([^)]*\)\s*\{([\s\S]*?)\n\s*\}",
            text,
        ):
            body = m.group(1)[:600]
            if not re.search(r"setOption|\.val\(|echarts|table\.reload", body):
                continue
            if any(s + "()" in body for s in still_names):
                continue
            if "Alive()" in body:
                continue
            if "layer.msg" in body and ".val(" not in body:
                continue
            add(f"controller/{fn}", "controller_done_no_still", body[:70].replace("\n", " "))


def _form_on_guarded(text, flt):
    pat = re.escape(flt)
    m = re.search(
        r"form\.on\(\s*['\"]" + pat + r"['\"]\s*,\s*function\s*\([^)]*\)\s*\{",
        text,
    )
    if not m:
        m = re.search(
            r'form\.on\(\s*["\']' + pat.replace(r"\(", r"\(") + r'["\']\s*,\s*function',
            text,
        )
    if not m:
        return True
    start = m.end() - 1
    depth = 0
    end = start
    for i in range(start, min(start + 500, len(text))):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                end = i
                break
    body = text[start : end + 1]
    return bool(
        re.search(
            r"Alive\(\)|Still\(\)|contains\(data\.elem\)|nodeDnsRoot\(\)|AddRoot\(\)|getElementById\('LAY-popup|LAY-popup",
            body,
        )
    )


def scan_batch_map_gap():
    """Hint: high page-size tables with toolbar bulk but no cross-page CheckedMap."""
    for dirpath, _, files in os.walk(PANEL):
        for fn in files:
            if not fn.endswith(".html"):
                continue
            path = os.path.join(dirpath, fn)
            rel = os.path.relpath(path, PANEL)
            text = open(path, encoding="utf-8", errors="replace").read()
            if "limits:" not in text or "500" not in text:
                continue
            if not re.search(r"type:\s*['\"]checkbox['\"]", text):
                continue
            if (
                "CheckedMap" in text
                or "IdsForBatch" in text
                or "veikorLocalBatch" in text
            ):
                continue
            if "table.on('toolbar" not in text and 'table.on("toolbar' not in text:
                continue
            add(rel, "limits500_no_checked_map", "limits 500 + bulk toolbar, no CheckedMap")


def scan_duplicate_form_on():
    by_filter = {}
    file_text = {}
    for dirpath, _, files in os.walk(PANEL):
        for fn in files:
            if not fn.endswith(".html"):
                continue
            rel = os.path.relpath(os.path.join(dirpath, fn), PANEL)
            text = open(os.path.join(dirpath, fn), encoding="utf-8", errors="replace").read()
            file_text[rel] = text
            for m in re.finditer(r"form\.on\(\s*['\"]([^'\"]+)['\"]", text):
                by_filter.setdefault(m.group(1), []).append(rel)
    for flt, files in sorted(by_filter.items()):
        u = sorted(set(files))
        if len(u) < 2:
            continue
        unguarded = [r for r in u if not _form_on_guarded(file_text[r], flt)]
        if len(unguarded) >= 2:
            add(
                "global",
                "duplicate_form_on_unguarded",
                f"{flt} -> {', '.join(unguarded[:5])}",
            )


def main():
    walk()
    scan_controllers()
    scan_batch_map_gap()
    by_kind = {}
    for rel, kind, detail in ISSUES:
        by_kind.setdefault(kind, []).append((rel, detail))
    for kind in sorted(by_kind):
        print(f"=== {kind} ({len(by_kind[kind])}) ===")
        seen = set()
        for rel, detail in sorted(by_kind[kind]):
            key = (rel, detail[:40])
            if key in seen:
                continue
            seen.add(key)
            print(f"  {rel}: {detail}")
    print("total issues", len(ISSUES))


if __name__ == "__main__":
    main()
