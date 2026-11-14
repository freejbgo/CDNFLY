#!/usr/bin/env python3
"""Scope bare form.render() calls in panel views using lay-filter on the same file."""
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

SKIP_FILTERS = {"breadcrumb", "docDemoTabBrief"}

EXTRA_FILTERS = {
    "account/config/api.html": ("<div class=\"layui-fluid\">", '<div class="layui-fluid" lay-filter="account-api-config">'),
    "account/sub/index.html": (
        '<div class="layui-card-body">',
        '<div class="layui-card-body" lay-filter="account-sub-page">',
    ),
    "finance/balance/index.html": (
        '<div class="layui-tab-item layui-show">',
        '<div class="layui-tab-item layui-show" lay-filter="finance-balance-page">',
    ),
    "account/balance/index.html": (
        '<div class="layui-tab-item layui-show">',
        '<div class="layui-tab-item layui-show" lay-filter="account-balance-page">',
    ),
    "finance/recharge/index.html": (
        'lay-filter="layuiadmin-form-nodeadmin"',
        'lay-filter="finance-admin-recharge-form"',
    ),
    "package/basic/sync.html": (
        '<div class="layui-form"',
        '<div class="layui-form" lay-filter="package-basic-sync-form"',
    ),
}

FILE_FILTERS = {
    "account/config/api.html": "account-api-config",
    "account/sub/index.html": "account-sub-page",
    "finance/balance/index.html": "finance-balance-page",
    "account/balance/index.html": "account-balance-page",
    "finance/recharge/index.html": "finance-admin-recharge-form",
    "package/basic/sync.html": "package-basic-sync-form",
}


def pick_filter(text: str, rel: str) -> str | None:
    if rel in FILE_FILTERS:
        return FILE_FILTERS[rel]
    for f in re.findall(r'lay-filter=["\']([^"\']+)["\']', text):
        if f in SKIP_FILTERS:
            continue
        if "layuiadmin-form" in f or f.endswith("admin") or f in (
            "log-tab",
            "forget-pass-tab",
            "LAY-user-reg-submit",
            "type",
            "duration",
        ):
            return f
    for f in re.findall(r'lay-filter=["\']([^"\']+)["\']', text):
        if f not in SKIP_FILTERS:
            return f
    return None


def main() -> int:
    changed = 0
    for dirpath, _, files in os.walk(PANEL):
        for fn in files:
            if not fn.endswith(".html"):
                continue
            path = os.path.join(dirpath, fn)
            rel = os.path.relpath(path, PANEL)
            text = open(path, encoding="utf-8", errors="replace").read()
            orig = text
            if rel in EXTRA_FILTERS:
                old, new = EXTRA_FILTERS[rel]
                if old in text and new.split("lay-filter")[0] in text:
                    text = text.replace(old, new, 1)
            flt = pick_filter(text, rel)
            if not flt:
                continue
            if re.search(r"\bform\.render\s*\(\s*\)", text):
                text = re.sub(
                    r"\bform\.render\s*\(\s*\)",
                    f"form.render(null, '{flt}')",
                    text,
                )
            if re.search(r'\bform\.render\s*\(\s*["\']checkbox["\']\s*\)', text):
                text = re.sub(
                    r'\bform\.render\s*\(\s*["\']checkbox["\']\s*\)',
                    f"form.render('checkbox', '{flt}')",
                    text,
                )
            if re.search(r"\blayui\.form\.render\s*\(\s*\)", text):
                text = re.sub(
                    r"\blayui\.form\.render\s*\(\s*\)",
                    f"layui.form.render(null, '{flt}')",
                    text,
                )
            if text != orig:
                open(path, "w", encoding="utf-8").write(text)
                changed += 1
                print("updated", rel, "->", flt)
    print("files changed:", changed)
    return 0


if __name__ == "__main__":
    sys.exit(main())
