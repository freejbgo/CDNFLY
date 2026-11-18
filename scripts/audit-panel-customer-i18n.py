#!/usr/bin/env python3
"""Customer-console i18n regression checks (M1). Admin views are out of scope."""
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
)
VIEWS = os.path.join(ROOT, "views")
CONTROLLERS = os.path.join(ROOT, "controller")

CUSTOMER_VIEW_PREFIXES = (
    "site",
    "stream",
    "account",
    "finance",
    os.path.join("package", "my"),
    os.path.join("package", "buy"),
)
CUSTOMER_CONTROLLERS = (
    "senior.js",
    "site-usage-senior.js",
    "stream_senior.js",
    "stream-usage-senior.js",
)

SCOPED_LANG = re.compile(r"\$\(document\)\.on\('veikor:lang\.([^']+)'")
GLOBAL_LANG = re.compile(r"\$\(document\)\.on\('veikor:lang'")
FORM_RENDER_NULL = re.compile(r"form\.render\s*\(\s*null")
LANG_HANDLER = re.compile(r"\$\(document\)\.on\('veikor:lang")
LAYER_CJK = re.compile(
    r"layer\.(?:msg|alert|confirm)\(\s*['\"]([^'\"]*[\u4e00-\u9fff][^'\"]*)"
)
RAW_RES_MSG = re.compile(r"layer\.msg\(\s*res\.msg\b")
API_MSG_ENTRY = re.compile(
    r'"([^"\\]+)":\s*\{("zh-CN"|"zh-TW"|"en"):[^}]+\}'
)
I18N_JS = os.path.join(ROOT, "lib", "veikor-i18n.js")
REQUIRED_API_LANGS = ("zh-CN", "zh-TW", "en")


def _is_customer_view(rel: str) -> bool:
    rel = rel.replace("\\", "/")
    for prefix in CUSTOMER_VIEW_PREFIXES:
        if rel == prefix or rel.startswith(prefix + "/"):
            return True
    if rel == "user_home.html":
        return True
    if rel.startswith("system/message/"):
        return True
    return False


def _audit_api_msg_map() -> list[str]:
    if not os.path.isfile(I18N_JS):
        return ["missing veikor-i18n.js"]
    text = open(I18N_JS, encoding="utf-8", errors="replace").read()
    start = text.find("var API_MSG_BY_SOURCE = {")
    if start < 0:
        return ["API_MSG_BY_SOURCE not found"]
    end = text.find("};", start)
    if end < 0:
        return ["API_MSG_BY_SOURCE unterminated"]
    block = text[start : end + 1]
    bad: list[str] = []
    for m in API_MSG_ENTRY.finditer(block):
        src = m.group(1)
        body = m.group(0)
        for loc in REQUIRED_API_LANGS:
            if f'"{loc}":' not in body:
                bad.append(f"{src} missing {loc}")
    if not API_MSG_ENTRY.search(block):
        bad.append("API_MSG_BY_SOURCE has no entries")
    return bad


def _missing_global_lang(text: str) -> bool:
    if not SCOPED_LANG.search(text):
        return False
    return not (GLOBAL_LANG.search(text) or re.search(r"\.on\('veikor:lang'", text))


def _audit_dynamic_host_i18n(rel: str, text: str) -> list[str]:
    """Flag hosts with both id and data-i18n on the same opening tag (buttons/inputs exempt)."""
    bad: list[str] = []
    for m in re.finditer(
        r"<(div|span|td|label)(\s[^>]*?)(/?)>",
        text,
        flags=re.IGNORECASE,
    ):
        attrs = m.group(2)
        if 'data-i18n' not in attrs:
            continue
        if 'data-veikor-dynamic' in attrs:
            continue
        if not re.search(r'\bid\s*=', attrs):
            continue
        if 'data-i18n-attr' in attrs or 'data-i18n-placeholder' in attrs:
            continue
        bad.append(f"{rel}: <{m.group(1)} id=… data-i18n=…> use data-veikor-dynamic + inner span")
    return bad


def _load_page_map() -> dict[str, dict[str, str]] | None:
    import json
    import re

    if not os.path.isfile(I18N_JS):
        return None
    text = open(I18N_JS, encoding="utf-8", errors="replace").read()
    m = re.search(
        r"var PAGE =(\{.*?\});\s*\n\s*var GEO_COUNTRY",
        text,
        flags=re.DOTALL,
    )
    if not m:
        return None
    try:
        return json.loads(m.group(1))
    except json.JSONDecodeError:
        return None


def _audit_veikor_i18n_js() -> list[str]:
    """PAGE blob must parse; duplicate locale markers indicate a corrupt merge."""
    bad: list[str] = []
    if not os.path.isfile(I18N_JS):
        return ["missing veikor-i18n.js"]
    import subprocess

    for line in open(I18N_JS, encoding="utf-8", errors="replace"):
        if line.startswith("  var PAGE ="):
            n_zh = line.count('"zh-CN":')
            if n_zh != 1:
                bad.append(f"PAGE line has {n_zh} zh-CN markers (expected 1)")
            break
    else:
        bad.append("PAGE assignment not found in veikor-i18n.js")
    r = subprocess.run(
        ["node", "--check", I18N_JS],
        capture_output=True,
        text=True,
    )
    if r.returncode:
        bad.append("veikor-i18n.js fails node --check (syntax)")
    page = _load_page_map()
    if page is None:
        bad.append("PAGE JSON could not be parsed")
    else:
        for loc in REQUIRED_API_LANGS:
            if loc not in page:
                bad.append(f"PAGE missing locale {loc}")
        zh = page.get("zh-CN") or {}
        for loc in ("en", "zh-TW"):
            other = page.get(loc) or {}
            gaps = [k for k in zh if k.startswith("page.") and k not in other]
            if gaps:
                bad.append(
                    f"PAGE {loc} missing {len(gaps)} page.* keys (e.g. {gaps[0]})"
                )
    return bad


def main() -> int:
    bad_lang: list[str] = []
    bad_layer: list[tuple[str, str]] = []
    bad_res_msg: list[str] = []
    bad_dynamic: list[str] = []
    form_render_null_advisory: list[str] = []
    bad_i18n_js = _audit_veikor_i18n_js()

    for dirpath, _, files in os.walk(VIEWS):
        for fn in files:
            if not fn.endswith(".html"):
                continue
            path = os.path.join(dirpath, fn)
            rel = os.path.relpath(path, VIEWS)
            if not _is_customer_view(rel):
                continue
            text = open(path, encoding="utf-8", errors="replace").read()
            if _missing_global_lang(text):
                bad_lang.append(rel)
            if LANG_HANDLER.search(text) and FORM_RENDER_NULL.search(text):
                form_render_null_advisory.append(rel)
            for m in LAYER_CJK.finditer(text):
                bad_layer.append((rel, m.group(1)[:80]))
            if RAW_RES_MSG.search(text) and "translateResMsg" not in text and "notifyResMsg" not in text:
                bad_res_msg.append(rel)
            bad_dynamic.extend(_audit_dynamic_host_i18n(rel, text))

    for fn in CUSTOMER_CONTROLLERS:
        path = os.path.join(CONTROLLERS, fn)
        if not os.path.isfile(path):
            continue
        text = open(path, encoding="utf-8", errors="replace").read()
        if _missing_global_lang(text):
            bad_lang.append(os.path.join("controller", fn))

    bad_api = _audit_api_msg_map()

    if bad_lang:
        print(
            "customer views/controllers with scoped veikor:lang but no global listener:",
            file=sys.stderr,
        )
        for rel in sorted(bad_lang):
            print(" ", rel, file=sys.stderr)
    if bad_layer:
        print("customer layer.* with hardcoded Chinese (use veikorI18n):", file=sys.stderr)
        for rel, msg in bad_layer:
            print(f"  {rel}: {msg!r}", file=sys.stderr)
    if bad_res_msg:
        print("customer layer.msg(res.msg) without translateResMsg:", file=sys.stderr)
        for rel in sorted(bad_res_msg):
            print(" ", rel, file=sys.stderr)

    if bad_api:
        print("API_MSG_BY_SOURCE locale gaps:", file=sys.stderr)
        for line in bad_api:
            print(" ", line, file=sys.stderr)
    if bad_dynamic:
        print("customer views: id + data-i18n on same host (use data-veikor-dynamic):", file=sys.stderr)
        for line in sorted(bad_dynamic):
            print(" ", line, file=sys.stderr)

    if bad_i18n_js:
        print("veikor-i18n.js structural checks:", file=sys.stderr)
        for line in bad_i18n_js:
            print(" ", line, file=sys.stderr)

    if form_render_null_advisory:
        print(
            "customer pages with veikor:lang and form.render(null):",
            file=sys.stderr,
        )
        for rel in sorted(form_render_null_advisory):
            print(" ", rel, file=sys.stderr)

    if bad_lang or bad_layer or bad_res_msg or bad_api or bad_dynamic or bad_i18n_js or form_render_null_advisory:
        return 1
    print("audit-panel-customer-i18n: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())