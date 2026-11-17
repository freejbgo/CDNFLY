# Customer console i18n plan (zh-CN / zh-TW / en)

This document is the **source of truth** for rollout scope and pitfalls. Implementation baseline: U0 merged (`veikor-i18n` gate, `veikor-page` markers, CI audits).

## Product scope

| Audience | Inner pages after login | Language UI |
|----------|-------------------------|-------------|
| **Customer** (`user_type` known and `!== 1`) | May follow `panel-lang` | Shown |
| **Administrator** (`user_type === 1`) | **Stay Simplified Chinese** until a later ADMIN milestone | Hidden |
| **`user_type` unknown** (stale session) | **No inner translation** until `/users/:uid` hydrates type | Shown for non-admin layout only after type known |

**M1 (this program):** shell + static UI + client dictionaries. **M2 (later):** API `res.msg` and server validation copy — not part of M1 “done”.

## Do not scope by URL folder

Customers use routes such as `finance/order/` from `user_home` and `system/log/*` for logs. Administrators may open templates under `finance/*` or `system/*`. **Role gate** (`customerI18nActive()`), not directory lists, decides whether copy runs.

## Mirror routes (common traps)

### A. Byte-identical templates (must stay in sync)

These pairs must remain **identical file content** (U2 PRs touch both or CI fails):

- `views/account/log/*.html` ↔ `views/system/log/*.html` (4 files)

### B. Route alias only (marker / alive checks)

`veikor-page.js` maps menu path roots so `data-veikor-page="system/log/op"` still matches route `account/log/op`. This does **not** mean whole `views/account/` and `views/finance/` trees are duplicates.

### C. Split customer trees (do not “only translate account/”)

Under `views/`:

- **Customer profile / API / sub:** `account/config`, `account/personal`, `account/sub` (no twin under `finance/`)
- **Customer billing:** `finance/balance`, `finance/order`, `finance/recharge` (linked from `user_home` as `finance/order/`)

U2a must cover **`user_home.html` + `finance/*` + `account/personal|config|sub` + log pair**, not “account vs finance mirror everything”.

## Phases

| Phase | Content |
|-------|---------|
| **U0** | Gate, markers, tab ids, `audit-panel-i18n-guards`, log mirror audit (**done on main**) |
| **U1** | Customer routes: `layer.msg/confirm` → `veikorI18n.t` / shared `UI` keys |
| **U2** | Module `data-i18n` + dictionaries; start **U2a** at home + account/finance split above |

**Tab rule (before translating tab labels):** use `data-veikor-tab` and `veikorActiveTabIdOr(scope, fallback)`.

## Shared templates (admin + customer same HTML)

- Prefer `data-i18n` + `applyDataI18n` (no-op for admin via gate).
- Do not branch templates by folder; do not call `isCustomerConsole()` for gating — use **`customerI18nActive()`**.

## Locale fallback

`veikorI18n.t(key)`: current `UI`/`AUTH` block → `en` → `zh-CN` string → raw key. Missing zh-TW keys may show简体 until filled.

## Engineering workflow

1. Edit `.veikor-build/.../panel/src`
2. `bash scripts/sync-panel-to-master-tar.sh`
3. `bash scripts/verify-packages.sh`

## Manual smoke matrix (minimal)

| Role | `panel-lang` | Checks |
|------|----------------|--------|
| Customer | en / zh-TW | `user_home`, `finance/order`, `site/monitor/top-res`, `account/log/op` — data loads, tabs work |
| Admin | any stored lang | Shared site pages: inner copy **简体**; lang select hidden |
| Customer, clear `user_type` once | en | After one `/users/:uid`, menu + inner align |

## Supersedes

Close stale PR **#133**; U0 baseline is merged PR **#137**.