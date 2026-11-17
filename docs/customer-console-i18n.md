# Customer console i18n plan (zh-CN / zh-TW / en)

Source of truth for rollout scope and pitfalls. **U0** is on `main` (#137).

## Product scope

| Audience | Inner pages after login | Language UI |
|----------|-------------------------|-------------|
| **Customer** (`user_type` known and `!== 1`) | Follows `panel-lang` when `customerI18nActive()` | Shown |
| **Administrator** (`user_type === 1`) | **Simplified Chinese** until ADMIN milestone | Hidden |
| **`user_type` unknown** | Inner copy stays **zh-CN** until `/users/:uid` hydrates type; then `applyConsoleI18n()` runs | Shown (not admin yet); brief EN menu vs 简体内页 possible until type returns |

**M1:** shell + static UI + client dictionaries. **M2 (later):** API `res.msg` / server validation — not required for M1 sign-off.

## Scope rule: role gate, not folders

`customerI18nActive()` decides whether inner `data-i18n`, menu, and breadcrumb translation run. The same template can serve admin and customer (e.g. site lists).

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

Many customer pages exist under both `views/site/` and `views/stream/` with the same basename (`usage.html`, `top-res.html`, `realtime.html`, …). **U2 monitor/site modules:** change both trees or extract shared keys; do not assume translating site alone covers L4 customers.

## Phases

| Phase | Content |
|-------|---------|
| **U0** | Gate, markers, tab ids, `audit-panel-i18n-guards`, view alias audit (**on main**) |
| **U1** | Customer-only: `layer.msg/confirm` → `veikorI18n.t` / `UI` keys (~171 call sites) |
| **U2** | `data-i18n` + dictionaries |
| **U2a** | `user_home.html`, `finance/order|balance|recharge`, `account/personal|config|sub`, `system/log/*`, high-traffic `package/my|buy|upgrade` as needed |

**Tab rule:** `data-veikor-tab` + `veikorActiveTabIdOr(scope, fallback)` **before** translating tab labels.

## Shared templates (admin + customer)

- Use `data-i18n` + `applyDataI18n` (admin skipped by gate).
- UI gates: **`customerI18nActive()`**, not `isCustomerConsole()` and not folder name.

## Locale fallback

`veikorI18n.t(key)`: `UI`/`AUTH` for `activeLang()` → `en` block → `zh-CN` → raw key. Customer `activeLang()` uses `panel-lang`; admin inner forced `zh-CN`.

## Engineering workflow

1. Edit `.veikor-build/.../panel/src` (preserve `account/` symlinks; `cp -a` in `sync-panel-to-master-tar.sh`)
2. `bash scripts/sync-panel-to-master-tar.sh`
3. `bash scripts/verify-packages.sh`

**Branching:** U1/U2 PRs should target **`main` after U0** (and after plan doc #138); avoid stacking on stale panel branches.

## Manual smoke matrix

| Role | `panel-lang` | Checks |
|------|----------------|--------|
| Customer | en / zh-TW | `user_home`, `finance/order`, `system/log/op`, `site/monitor/top-res` — tables/charts load |
| Customer | en | Open same log page via `account/log/op` — same content, alive guards OK |
| Admin | any | Shared site pages 简体; lang select hidden; switching stored lang does not change inner body |
| Customer | en, clear `user_type` once | After `/users/:uid`, menu/body align |

## Supersedes

#133 closed; U0 = #137 on `main`. Plan corrections = #138+.