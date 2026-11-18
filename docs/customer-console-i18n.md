# Customer console i18n plan (zh-CN / zh-TW / en)

Source of truth for rollout scope and pitfalls. **Baseline on `main`:** U0 (#137) + plan/CI (#138).

**Scheme review (2026-11-17):** Structural traps (gate, symlinks, markers, tabs, token login, dictionaries) are documented below and enforced by `verify-packages.sh`. Further “full scheme re-review” has low yield unless product scope changes — **execute U2a or U1 next**.

**M1 customer sign-off (2026-11-18, `main` through #237):** Customer console static UI, deliberate `layer.*` wraps, scoped + global `veikor:lang` refresh, and monitor/package popups are in place for **non-admin** sessions. CI: `scripts/audit-panel-customer-i18n.py` (no admin/`package/upgrade` paths). **Management console (`user_type === 1`) stays Simplified Chinese** — do not add zh-TW/en for `node/*`, `config/*`, `package/sold`, `package/upgrade`, etc. **M2** (API `res.msg`) remains optional follow-up.

## Product scope

| Audience | Inner pages after login | Language UI |
|----------|-------------------------|-------------|
| **Customer** (`user_type` known and `!== 1`) | Follows `panel-lang` when `customerI18nActive()` | Shown |
| **Administrator** (`user_type === 1`) | **Simplified Chinese** until ADMIN milestone | Hidden |
| **`user_type` unknown** | Inner copy stays **zh-CN** until `/users/:uid` hydrates type; then `applyConsoleI18n()` runs | **Hidden** until type is known (legacy sessions only — normal login sets `user_type` immediately) |

**M1:** shell + static UI + client dictionaries. **M2 (later):** API `res.msg` / server validation — not required for M1 sign-off.

**Role model:** backend `user_type === 1` is the administrator console; **any other known type** is treated as customer for M1 gating.

## Scope rule: role gate, not folders

`customerI18nActive()` decides whether inner `data-i18n`, menu, and breadcrumb translation run. The same template can serve admin and customer (e.g. site lists).

## Admin vs customer — two axes (do not conflate)

Shared modules (e.g. `site/site/index.html`) use **two independent signals**. Mixing them causes wrong i18n scope.

### Axis A — session role (`user_type`, i18n gate)

| `user_type` | `customerI18nActive()` | Language UI | Inner copy (M1) |
|-------------|------------------------|-------------|-----------------|
| `1` | `false` | Hidden | **简体 only** (`activeLang()` → `zh-CN`) |
| known, `!== 1` | `true` | Shown | **zh-CN / zh-TW / en** (`panel-lang`) |
| unknown / null | `false` | Hidden | 简体 until `/users/:uid` hydrates type |

**Impersonation:** from 所有网站, admin **切换用户** rewrites token + `user_type`, then reloads — the new session follows **customer** rules if `user_type !== 1`.

i18n work is **only required where customers actually read the UI** (`customerI18nActive()` true). Admins do not need dedicated zh-TW/en strings for M1; `veikorI18n.t` still resolves to zh-CN for them.

### Axis B — view mode (`show_all` hash query)

Same HTML/JS; Laytpl and `layui.router().search.show_all` choose columns, search rows, API `where.show_all`, and toolbar blocks. **`uid_hide`** in `site/site/index.html` is tied to this (`uid_hide = (show_all !== '1')`), not to `user_type`.

| | Typical URL | Entry | `uid_hide` |
|---|-------------|-------|------------|
| **我的网站** | `#/site/site/` | `user_home` → 我的网站 | `true` (hide 用户/区域/线路组列) |
| **所有网站** | `#/site/site/show_all=1/` | Admin `#/home` quick links only (`home.html`) | `false` |

Customers normally never use `show_all=1`; admins normally use it from the admin home. An admin *could* open `#/site/site/` without `show_all` — still **简体** (Axis A), but sees the **customer toolbar layout**.

### `site/site` toolbar (same template)

| Batch / action | `show_all` absent | `show_all=1` only |
|----------------|-------------------|-------------------|
| 新增 / 修改 / 启停 / 删除 | ✓ | ✓ |
| 申请证书 / 解锁黑名单 / 清缓存 / 清空白名单 | ✓ | ✓ |
| 设置状态 / CNAME域名 / CNAME模式 / 线路分组 | ✗ | ✓ |

### Batch popups — who opens what (i18n priority)

| Popup | Gated by | Customer M1 |
|-------|----------|-------------|
| `addform.html` | Both modes; user picker when `!uid_hide` (all-sites add) | **Yes** — customers use 新增 |
| `update_form.html` | Both modes; **`.admin-hide` panels shown when `uid_hide`** (my sites) | **Yes** — main customer batch editor |
| `unlock-ip.html` | Both modes | **Yes** |
| `update-state.html`, `update-node-group.html`, `update-cname-mode.html` | Toolbar only if `show_all=1` | Low — admin 简体 in practice |
| Nested forms from `update_form` / `edit` (`cache_form`, …) | Customer paths | **Yes**, with parent page |

**Policy:** localize batch UI that **customers** open under 我的网站 first (`update_form`, `unlock-ip`, add). Do **not** assume “batch = admin-only”. Conversely, do **not** require admin-only EN/zh-TW for `show_all=1` dialogs — Axis A already keeps admins on 简体.

## View aliases (symlinks — major trap)

Under `views/account/` these entries are **symlinks**, not separate files:

| Customer URL prefix | Symlink | Canonical templates |
|---------------------|---------|-------------------------|
| `account/log/*` | → `../system/log/` | Edit **`system/log/*.html`** only |
| `account/order/*` | → `../finance/order/` | Edit **`finance/order/*.html`** only |
| `account/balance/*` | → `../finance/balance/` | Edit **`finance/balance/*.html`** only |

Real directories under `account/`: **`personal/`**, **`config/`**, **`sub/`** only.

**Do not** maintain “account vs finance duplicate HTML” for order/balance/log — CI enforces symlinks via `audit-panel-view-aliases.py`.

**Markers:** routes may be `account/log/op` while `data-veikor-page="system/log/op"`. Keep `veikor-page.js` route aliases; do not “fix” by duplicating templates.

**Home links:** `user_home.html` uses `lay-href="system/log/op"` (not `account/log/...`). Smoke tests should cover **both** URL shapes.

## Route alias (markers only)

`MARKER_ROUTE_ROOTS` lets `veikorPageMarkerAlive('system/log/op')` succeed on `account/log/op`. This is independent of symlinks.

## Site vs stream (paired work)

These **relative paths** exist under both `views/site/` and `views/stream/` (same basename, different product line):

- `group/index.html`, `group/addform.html`
- `monitor/usage.html`, `monitor/top-res.html`, `monitor/realtime.html`

U2 for site monitor must include the matching `stream/monitor/*` files (or shared dictionary keys only). **`site/monitor/attack-rank.html` has no `stream/` twin** — site-only page.

## Side menu (API + dictionary trap)

Menu labels come from the **layout API** (`data-name` / `data-jump`) with Chinese `data-veikor-src` locked on first paint. `menuLabel()` only replaces text when `MENU[lang][key]` exists. Custom menu rows without a dictionary key **stay Chinese** even in en — add keys or accept fallback (do not compare translated text in JS logic).

## Dashboard entry points (do not conflate)

| File | Audience | Notes |
|------|----------|--------|
| `user_home.html` | Customer landing after login | i18n priority for U2a |
| `home.html` | Admin landing | **Out of customer M1** (stays Chinese until ADMIN i18n) |

## Per-route i18n (router hook)

`index.js` after each view render calls **`applyBreadcrumbI18n` + `applyDataI18n` only** (both gated by `customerI18nActive()`). Full **`applyConsoleI18n`** (menu, shell, etc.) runs on layout load, language change, and after `user_type` hydration — do not call the full helper on every tab switch (menu labels would re-lock wrong).

On language change, `applyConsoleI18n` also fires **`veikor:lang.<scope>`** for the active tab’s `data-veikor-page` (see `PAGE_LANG_SCOPES` in `veikor-i18n.js`), plus **`balanceForm`** when `#recharge` is present and **`userHomeBalance`** on `#/user_home`.

## Tab / document titles

Layui tab labels use each template’s `<title>` until U2 rewrites titles or adds `data-i18n`. Expect **Chinese tab text** on en body during early U2.

`applyConsoleTitle()` uses **`readUserType()`**; if type is unknown, browser tab title is left until `/users/:uid` returns (avoids showing customer title to admin).

## AJAX / layer errors

`view.req` / `view.error` paths still emit Chinese or hard-coded strings for many APIs (`res.msg`). U1 covers deliberate `layer.*` wraps; **M2** covers backend messages.

## Phases

| Phase | Content |
|-------|---------|
| **U0** | Gate, markers, tab ids, `audit-panel-i18n-guards`, `audit-panel-view-aliases`, this doc (**shipped on `main`**) |
| **U1** | Customer-only: `layer.msg/confirm` → `veikorI18n.t` / `UI` keys (~**340** calls under U2a view scope + controllers; shrink by module) |
| **U2** | `data-i18n` + dictionaries |
| **U2a** | `user_home.html`, `finance/order|balance|recharge`, `account/personal|config|sub`, `system/log/*`, `package/my|buy|upgrade` (not admin-only `package/*` ops views) |
| **U2b** (suggested) | High-traffic site customer core: `site/site`, `site/edit`, `site/cert`, `site/acl`, `site/cc`, `package/my` — still gated by `customerI18nActive()` on shared templates |

**Tab rule:** `data-veikor-tab` + `veikorActiveTabIdOr(scope, fallback)` **before** translating tab labels. Reference: `site/monitor/blackip.html` (`data-i18n` on tab + `data-veikor-tab` for logic). CI fails customer views that use `curr_tab` without `data-veikor-tab`.

## Shared templates (admin + customer)

- Use `data-i18n` + `applyDataI18n` (admin skipped by gate).
- UI gates: **`customerI18nActive()`**, not `isCustomerConsole()` and not folder name.

## Locale fallback

`veikorI18n.t(key)`: `UI`/`AUTH` for `activeLang()` → `en` block → `zh-CN` → raw key. Customer `activeLang()` uses `panel-lang`; admin inner forced `zh-CN`.

**Dictionary buckets:** `AUTH` (login), `MENU` + `TITLE` (side menu / breadcrumb cite via Chinese→map), `UI` (shared widgets). U2 page copy: prefer `data-i18n` keys backed by **`UI` or a new `PAGE` map** in `veikor-i18n.js` — ad hoc Chinese in `TITLE` only helps breadcrumbs that match exact 简体 source strings.

## Breadcrumb trap

`applyBreadcrumbI18n` only maps text present in `TITLE[lang]`. New breadcrumb `<cite>` strings need dictionary entries or stay Chinese.

## Admin-only debt (do not block customer M1)

`node/monitor/top-res.html` and `controller/node_senior.js` still branch on Chinese tab labels — **admin monitor only**. Customer monitor paths were migrated in U0.

## Cross-domain token login (`access_token` in hash)

Some flows open `/user/login/redirect=.../access_token=.../uid=...` (token mangled in hash). **Must hydrate `user_type` via `/users/:uid` before** entering the console (see `loginPage.js`); otherwise the language gate treats the session as unknown. Destination uses `loginDest()` + admin vs `user_home`.

## Failure modes

| Case | Behavior |
|------|----------|
| `/users/:uid` fails after old session (no `user_type`) | Lang select stays hidden; inner UI stays 简体 — user should re-login |
| Cross-domain token login | `user_type` fetched before redirect when `uid` present |

## Impersonation / 切换用户 (admin workflow)

From `site/site` (all sites), admin may switch into another user: token + `user_type` are rewritten, then **full reload** to `#/home` or `#/user_home`. Customer i18n applies on the new session like a normal login (`user_type` already set). Out of customer M1 scope; no extra gate work required.

## Engineering workflow

1. Edit `.veikor-build/.../panel/src` (preserve `account/` symlinks; `cp -a` in `sync-panel-to-master-tar.sh`)
2. `bash scripts/sync-panel-to-master-tar.sh`
3. `bash scripts/verify-packages.sh`

**Branching:** U1/U2 PRs target **`main`**; rebase off latest `main` (do not stack on old `cursor/panel-*` i18n branches).

**Repo trap:** Panel source is edited under **`.veikor-build/.../panel/src`** (local, often gitignored), then copied into **`cdnfly/*-master-*.tar.gz`** via `sync-panel-to-master-tar.sh`. CI audits read `.veikor-build`; releases ship the tar — never edit only the tar without syncing.

## Manual smoke matrix

| Role | `panel-lang` | Checks |
|------|----------------|--------|
| Customer | en / zh-TW | `user_home`, `finance/order`, `system/log/op`, `site/monitor/top-res` — tables/charts load |
| Customer | en | Open same log page via `account/log/op` — same content, alive guards OK |
| Admin | any | Shared site pages 简体; lang select hidden; switching stored lang does not change inner body |
| Customer | en, clear `user_type` once | Lang select hidden until hydrate; after `/users/:uid`, selector + menu/body align |
| Customer | token hash login | `access_token` handoff: lands with `user_type` set before `#/user_home` |

## Supersedes

#133 closed; #137 + #138 merged on `main`.