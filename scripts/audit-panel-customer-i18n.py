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
BARE_LANG_LISTENER = re.compile(r"\$\(document\)\.on\('veikor:lang'(?!\.)\s*,")
FORM_RENDER_NULL = re.compile(r"form\.render\s*\(\s*null")
FORM_RENDER_BARE = re.compile(r"form\.render\s*\(\s*\)")
LANG_HANDLER = re.compile(r"\$\(document\)\.on\('veikor:lang")
LAYER_CJK = re.compile(
    r"layer\.(?:msg|alert|confirm)\(\s*['\"]([^'\"]*[\u4e00-\u9fff][^'\"]*)"
)
RAW_RES_MSG = re.compile(r"layer\.msg\(\s*res\.msg\b")
JOBS_DONE_LAYER = re.compile(
    r"url:\s*['\"]/jobs[^'\"]*['\"][\s\S]{0,500}?done:\s*function\s*\([^)]*\)\s*\{([^}]{0,200})",
    re.DOTALL,
)
API_MSG_ENTRY = re.compile(
    r'"([^"\\]+)":\s*\{("zh-CN"|"zh-TW"|"en"):[^}]+\}'
)
I18N_JS = os.path.join(ROOT, "lib", "veikor-i18n.js")
REQUIRED_API_LANGS = ("zh-CN", "zh-TW", "en")
MIN_API_MSG_ENTRIES = 285
REQUIRED_UI_KEYS = (
    "export.excel",
    "export.csv",
    "layer.title.info",
    "table.none",
    "layer.ok",
    "layer.cancel",
)
REQUIRED_UI_LANGS = ("zh-CN", "zh-TW", "en")
REQUIRED_PAGE_KEYS = (
    "page.userHome.currencySuffix",
    "page.site.cert.search.selectPh",
    "page.finance.balance.pay.currencyUnit",
)
REQUIRED_AUTH_SHELL_PREFIX = "shell."

# Popups/partials owned by parent refresh*OpenLayers must not bind veikor:lang.*
OPEN_LAYER_PARTIAL_RE = re.compile(
    r"(?:"
    r"addform\.html$"
    r"|-add\.html$"
    r"|(?:unlock-ip|update-state|update-node-group|update-cname-mode|"
    r"backend_form|cache_form|req_header_form|resp_header_form|"
    r"url_rewrite_form|url_ratelimit_form)\.html$"
    r"|package/(?:buy/duration|my/(?:renew|buy-upgrade|detail|up_down))\.html$"
    r"|(?:site/site|stream/stream)/update_form\.html$"
    r"|site/cert/update-cert-type\.html$"
    r")"
)


def _is_open_layer_partial(rel: str) -> bool:
    rel = rel.replace("\\", "/")
    return bool(OPEN_LAYER_PARTIAL_RE.search(rel))


LIST_INDEX_ROUTE_GUARD = ("site/site/index.html", "stream/stream/index.html")
LIST_INDEX_GUARD_NEEDLE = "third && third !== 'index'"
EDIT_INDEX_ROUTE_GUARD = ("site/site/edit.html", "stream/stream/edit.html")
EDIT_ROUTE_NEEDLE = "path[2] !== 'edit'"
FINANCE_ROUTE_ONLY = {
    "finance/recharge/index.html": "finance",
}
# account/balance|order → finance/* symlinks: one script, dual account|finance prefix.
FINANCE_SYMLINK_ALIASES = {
    "finance/balance/index.html",
    "finance/order/index.html",
    "finance/order/count.html",
}


def _audit_finance_mirror_routes(rel: str, text: str) -> list[str]:
    bad: list[str] = []
    rel = rel.replace("\\", "/")
    compact = text.replace(" ", "")
    if rel in FINANCE_SYMLINK_ALIASES:
        dual = "path[0]!=='account'&&path[0]!=='finance'"
        if dual not in compact and 'path[0]!=="account"&&path[0]!=="finance"' not in compact:
            bad.append(
                f"{rel}: symlink alias must accept account and finance route prefixes"
            )
        return bad
    prefix = FINANCE_ROUTE_ONLY.get(rel)
    if prefix:
        needle = f"path[0]!=='{prefix}'"
        if needle not in compact and f'path[0]!=="{prefix}"' not in compact:
            bad.append(f"{rel}: alive guard must gate on {prefix}/* route only")
    return bad


def _audit_list_edit_lang_guards(rel: str, text: str) -> list[str]:
    bad: list[str] = []
    rel = rel.replace("\\", "/")
    if rel in LIST_INDEX_ROUTE_GUARD and LIST_INDEX_GUARD_NEEDLE not in text:
        bad.append(
            f"{rel}: list page root must reject non-index routes ({LIST_INDEX_GUARD_NEEDLE})"
        )
    if rel in EDIT_INDEX_ROUTE_GUARD:
        if EDIT_ROUTE_NEEDLE not in text and "path[2] === 'edit'" not in text:
            bad.append(f"{rel}: edit page alive must gate on edit route segment")
    return bad


BLOCK_REGION_INPUT = re.compile(
    r'<input[^>]*class="block_region[^"]*"[^>]*name="block_region"\s+value="[a-z]{2}"'
)
BLOCK_REGION_I18N = re.compile(
    r'name="block_region"\s+value="[a-z]{2}"[^>]*data-i18n-title="page\.geo\.country\.'
)


DUP_I18N_TITLE = re.compile(
    r"<input[^>]*\bdata-i18n-title=(?:\"[^\"]*\"|'[^']*')[^>]*\bdata-i18n-title=",
    re.IGNORECASE,
)


def _audit_dup_i18n_title(rel: str, text: str) -> list[str]:
    if not _is_customer_view(rel):
        return []
    bad: list[str] = []
    for i, line in enumerate(text.splitlines(), 1):
        if DUP_I18N_TITLE.search(line):
            bad.append(f"{rel}:{i}: duplicate data-i18n-title on input")
    return bad


def _audit_block_region_geo_titles(rel: str, text: str) -> list[str]:
    """Shield-region checkboxes must carry data-i18n-title for first paint + lang skins."""
    rel = rel.replace("\\", "/")
    if rel not in ("site/site/edit.html", "site/site/update_form.html"):
        return []
    need = len(BLOCK_REGION_INPUT.findall(text))
    have = len(BLOCK_REGION_I18N.findall(text))
    if need and have < need:
        return [f"{rel}: block_region inputs missing data-i18n-title ({have}/{need})"]
    return []


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


def _api_msg_source_block() -> tuple[str | None, list[str]]:
    if not os.path.isfile(I18N_JS):
        return None, ["missing veikor-i18n.js"]
    text = open(I18N_JS, encoding="utf-8", errors="replace").read()
    start = text.find("var API_MSG_BY_SOURCE = {")
    if start < 0:
        return None, ["API_MSG_BY_SOURCE not found"]
    end = text.find("};", start)
    if end < 0:
        return None, ["API_MSG_BY_SOURCE unterminated"]
    return text[start : end + 1], []


def _audit_api_msg_map() -> list[str]:
    block, err = _api_msg_source_block()
    if err:
        return err
    assert block is not None
    bad: list[str] = []
    seen: dict[str, int] = {}
    for m in API_MSG_ENTRY.finditer(block):
        src = m.group(1)
        seen[src] = seen.get(src, 0) + 1
        body = m.group(0)
        for loc in REQUIRED_API_LANGS:
            if f'"{loc}":' not in body:
                bad.append(f"{src} missing {loc}")
    dup = [k for k, n in seen.items() if n > 1]
    if dup:
        bad.append(f"API_MSG_BY_SOURCE duplicate keys: {dup[0]}")
    if not API_MSG_ENTRY.search(block):
        bad.append("API_MSG_BY_SOURCE has no entries")
    else:
        n_entries = len(API_MSG_ENTRY.findall(block))
        if n_entries < MIN_API_MSG_ENTRIES:
            bad.append(
                f"API_MSG_BY_SOURCE has {n_entries} entries (min {MIN_API_MSG_ENTRIES})"
            )
    return bad


def _missing_global_lang(text: str) -> bool:
    """Legacy: global listener optional when scoped exists (applyConsoleI18n fires scoped + shell only)."""
    return False


def _audit_jobs_done_alive(rel: str, text: str) -> list[str]:
    """Jobs async toast must not run after customer page navigates away."""
    if not re.search(r"function \w+Alive\s*\(", text):
        return []
    bad: list[str] = []
    for m in JOBS_DONE_LAYER.finditer(text):
        body = m.group(1)
        if not re.search(r"layer\.(msg|alert)\(", text[m.start() : m.start() + 600]):
            continue
        if re.search(r"\w+Alive\s*\(", body):
            continue
        bad.append(f"{rel}: /jobs done missing *Alive() guard")
        break
    return bad


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
    import json
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
    text = open(I18N_JS, encoding="utf-8", errors="replace").read()
    if "function refreshLayuiTableDomChrome" not in text:
        bad.append("missing refreshLayuiTableDomChrome (Layui table/lang switch)")
    if "function uiText" not in text:
        bad.append("missing uiText() (UI locale lookup)")
    ui_body = text.split("function uiText", 1)
    if len(ui_body) > 1 and "if (lang === 'en')" not in ui_body[1][:800]:
        bad.append("uiText must gate UI.en fallback on lang === 'en' (zh-TW vs #559)")
    layui_m = re.search(
        r"var LAYUI_STATIC = (\{[\s\S]*?\});\s*\n\s*function translateLayuiStaticText",
        text,
    )
    if not layui_m:
        bad.append("LAYUI_STATIC block not found")
    else:
        block = layui_m.group(1)
        for src in re.findall(r"'([^']+)':\s*\{", block):
            snippet = re.search(
                rf"'{re.escape(src)}':\s*\{{([^}}]+)\}}",
                block,
            )
            if not snippet:
                bad.append(f"LAYUI_STATIC[{src!r}] malformed")
                continue
            inner = snippet.group(1)
            if "'zh-TW':" not in inner:
                bad.append(f"LAYUI_STATIC[{src!r}] missing zh-TW")
            if "'en':" not in inner:
                bad.append(f"LAYUI_STATIC[{src!r}] missing en")
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
        for loc in REQUIRED_API_LANGS:
            block = page.get(loc) or {}
            missing = [k for k in REQUIRED_PAGE_KEYS if k not in block]
            if missing:
                bad.append(f"PAGE {loc} missing keys: {', '.join(missing)}")
    ui_line = None
    for line in open(I18N_JS, encoding="utf-8", errors="replace"):
        if line.startswith("  var UI ="):
            ui_line = line
            break
    auth_line = None
    for line in open(I18N_JS, encoding="utf-8", errors="replace"):
        if line.startswith("  var AUTH ="):
            auth_line = line
            break
    if auth_line is None:
        bad.append("AUTH assignment not found in veikor-i18n.js")
    else:
        raw = auth_line.split("=", 1)[1].strip().rstrip(";")
        try:
            auth = json.loads(raw)
        except json.JSONDecodeError:
            bad.append("AUTH JSON could not be parsed")
        else:
            zh_auth = auth.get("zh-CN") or {}
            zh_shell = [k for k in zh_auth if k.startswith(REQUIRED_AUTH_SHELL_PREFIX)]
            for loc in ("zh-TW", "en"):
                block = auth.get(loc) or {}
                gaps = [k for k in zh_shell if k not in block]
                if gaps:
                    bad.append(
                        f"AUTH {loc} missing {len(gaps)} shell.* keys (e.g. {gaps[0]})"
                    )
    if ui_line is None:
        bad.append("UI assignment not found in veikor-i18n.js")
    else:
        raw = ui_line.split("=", 1)[1].strip().rstrip(";")
        try:
            ui = json.loads(raw)
        except json.JSONDecodeError:
            bad.append("UI JSON could not be parsed")
        else:
            for loc in REQUIRED_UI_LANGS:
                block = ui.get(loc) or {}
                gaps = [k for k in REQUIRED_UI_KEYS if k not in block]
                if gaps:
                    bad.append(f"UI {loc} missing keys: {', '.join(gaps)}")
            zh_ui = set((ui.get("zh-CN") or {}).keys())
            for loc in ("zh-TW", "en"):
                block = ui.get(loc) or {}
                gaps = sorted(zh_ui - set(block.keys()))
                if gaps:
                    bad.append(
                        f"UI {loc} missing {len(gaps)} keys from zh-CN (e.g. {gaps[0]})"
                    )
    return bad


def main() -> int:
    bad_lang: list[str] = []
    bad_layer: list[tuple[str, str]] = []
    bad_res_msg: list[str] = []
    bad_dynamic: list[str] = []
    bad_jobs_done: list[str] = []
    bad_bare_lang: list[str] = []
    bad_open_partial_lang: list[str] = []
    bad_list_edit_guard: list[str] = []
    form_render_null_advisory: list[str] = []
    form_render_bare_advisory: list[str] = []
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
            if BARE_LANG_LISTENER.search(text):
                bad_bare_lang.append(rel)
            if _is_open_layer_partial(rel) and SCOPED_LANG.search(text):
                bad_open_partial_lang.append(rel)
            bad_list_edit_guard.extend(_audit_list_edit_lang_guards(rel, text))
            bad_list_edit_guard.extend(_audit_finance_mirror_routes(rel, text))
            if _missing_global_lang(text):
                bad_lang.append(rel)
            if LANG_HANDLER.search(text) and FORM_RENDER_NULL.search(text):
                form_render_null_advisory.append(rel)
            if LANG_HANDLER.search(text) and FORM_RENDER_BARE.search(text):
                form_render_bare_advisory.append(rel)
            for m in LAYER_CJK.finditer(text):
                bad_layer.append((rel, m.group(1)[:80]))
            if RAW_RES_MSG.search(text) and "translateResMsg" not in text and "notifyResMsg" not in text:
                bad_res_msg.append(rel)
            bad_dynamic.extend(_audit_dynamic_host_i18n(rel, text))
            bad_jobs_done.extend(_audit_jobs_done_alive(rel, text))
            bad_list_edit_guard.extend(_audit_block_region_geo_titles(rel, text))
            bad_list_edit_guard.extend(_audit_dup_i18n_title(rel, text))

    bad_monitor_controller_lang: list[str] = []
    for fn in CUSTOMER_CONTROLLERS:
        path = os.path.join(CONTROLLERS, fn)
        if not os.path.isfile(path):
            continue
        text = open(path, encoding="utf-8", errors="replace").read()
        if BARE_LANG_LISTENER.search(text):
            bad_bare_lang.append(os.path.join("controller", fn))
        if SCOPED_LANG.search(text):
            bad_monitor_controller_lang.append(
                os.path.join("controller", fn)
            )
        if _missing_global_lang(text):
            bad_lang.append(os.path.join("controller", fn))

    bad_api = _audit_api_msg_map()

    if bad_bare_lang:
        print(
            "customer views/controllers must not use bare veikor:lang listeners:",
            file=sys.stderr,
        )
        for rel in sorted(bad_bare_lang):
            print(" ", rel, file=sys.stderr)

    if bad_open_partial_lang:
        print(
            "open-layer partials must not bind veikor:lang.* (parent refresh*OpenLayers):",
            file=sys.stderr,
        )
        for rel in sorted(bad_open_partial_lang):
            print(" ", rel, file=sys.stderr)

    if bad_list_edit_guard:
        print("site/stream list+edit lang route guards:", file=sys.stderr)
        for line in sorted(bad_list_edit_guard):
            print(" ", line, file=sys.stderr)

    if bad_monitor_controller_lang:
        print(
            "monitor senior controllers must not bind veikor:lang (views orchestrate):",
            file=sys.stderr,
        )
        for rel in sorted(bad_monitor_controller_lang):
            print(" ", rel, file=sys.stderr)

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

    if form_render_bare_advisory:
        print(
            "customer pages with veikor:lang and form.render() (use scoped render):",
            file=sys.stderr,
        )
        for rel in sorted(form_render_bare_advisory):
            print(" ", rel, file=sys.stderr)

    if bad_jobs_done:
        print("customer views: /jobs done should guard with *Alive():", file=sys.stderr)
        for line in sorted(bad_jobs_done):
            print(" ", line, file=sys.stderr)

    if (
        bad_bare_lang
        or         bad_open_partial_lang
        or         bad_list_edit_guard
        or bad_monitor_controller_lang
        or bad_lang
        or bad_layer
        or bad_res_msg
        or bad_api
        or bad_dynamic
        or bad_i18n_js
        or form_render_null_advisory
        or form_render_bare_advisory
        or bad_jobs_done
    ):
        return 1
    block, _ = _api_msg_source_block()
    n_api = len(API_MSG_ENTRY.findall(block)) if block else 0
    print(
        f"audit-panel-customer-i18n: ok "
        f"(API_MSG_BY_SOURCE {n_api} entries, min {MIN_API_MSG_ENTRIES})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())