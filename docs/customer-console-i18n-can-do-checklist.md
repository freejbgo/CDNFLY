# Customer console i18n — can-do backlog by module

Scope: **`user_type !== 1` only** (see `customer-console-i18n.md`). Edit panel under `.veikor-build/.../panel/src`, then `sync-panel-to-master-tar.sh` + `verify-packages.sh`.

**Batch delivered (slices through 2026-11-19, PR #298–#306):** U2B scope; P0 `acllist-add` dynamic lang; `up_down` / `/jobs` alive guards; `siteRefresh` lang scope; cache edit popup title; `API_MSG` samples; CI rule for `/jobs` done + `*Alive()`. Plus earlier: `applyLayerPopupI18n`, tab title i18n, monitor chrome, pay return `panel-lang` storage. **Remaining:** production-only `res.msg` samples (P3), P4 polish, backend-authored API text (out of scope).

**Legend**

| Tag | Meaning |
|-----|---------|
| **P0** | Stability (lang switch breaks UI / wipes data) |
| **P1** | High-traffic customer pages |
| **P2** | Popups / batch forms (customer uses under 我的网站) |
| **P3** | M2 `res.msg` / `notifyResMsg` sweep |
| **P4** | Polish (tabs, switches, low-traffic) |

| Work type | What to do |
|-----------|------------|
| **STATIC** | Missing `data-i18n` / `PAGE` keys, placeholders, table `cols`, breadcrumbs |
| **POPUP** | Layer templates: open + `veikor:lang` refresh (`applyDataI18n` on popup root) |
| **DYNAMIC** | `data-veikor-dynamic` + cache replay on `veikor:lang` (no `data-i18n` on JS-filled hosts) |
| **M2** | `notifyResMsg` / expand `API_MSG_BY_SOURCE` for this module’s APIs |
| **CHART** | Customer `controller/*-senior.js`: axis/legend/tooltip via `veikorI18n.t` + lang refresh |

**Symlinks (edit canonical path only)**

| URL | Edit |
|-----|------|
| `account/balance/*` | `finance/balance/*` |
| `account/order/*` | `finance/order/*` |
| `account/log/*` | `system/log/*` (customer smoke; log pages mostly done in U2a) |

---

## Global / shared (`panel/src/lib`, layout)

| Item | P | Types | Notes |
|------|---|-------|-------|
| `lib/veikor-i18n.js` — `API_MSG_BY_SOURCE` | P3 | M2 | ~42 entries; grow from prod/test `res.msg` samples |
| `lib/veikor-i18n.js` — `MENU` / `TITLE` | P2 | STATIC | Custom menu rows; new breadcrumb cite strings |
| `lib/veikor-i18n.js` — `applyDataI18n` + `data-veikor-dynamic` | P0 | DYNAMIC | Documented; extend CI to ban risky patterns |
| `lib/view.js` — customer `reqErrorHtml` | — | Done | Keep mapping table in sync with M2 |
| `index.js` — Layui **tab title** on lang change | P4 | Done | `bindLayuiTabTitleFromBody` + `applyLayuiTabTitlesI18n`; customer tab chip avoids stale `res.title` (#307) |
| `scripts/audit-panel-customer-i18n.py` | P0 | CI | Ban `id` + `data-i18n` on same host (exceptions for `button`/`input`) |

---

## `user_home.html`

| File | P | Types | Notes |
|------|---|-------|-------|
| `views/user_home.html` | P1 | STATIC, DYNAMIC | Overview replay done (#242); announcements are **API title text** (display only; true tri-lang needs backend) |

---

## Finance (`views/finance/`)

| File | P | Types | Notes |
|------|---|-------|-------|
| `finance/balance/index.html` | P1 | DYNAMIC, M2 | Balance + pay UI (#242); pay method `title` + `form.render` on lang |
| `finance/balance/return.html` | P4 | STATIC, POPUP | `panel-lang` + **`veikor:lang`**; 3s redirect (#306) |
| `finance/balance/alipay.html` | P2 | POPUP, STATIC | Pay layer fragment |
| `finance/balance/weixin.html` | P2 | POPUP, STATIC | Pay QR layer fragment |
| `finance/order/index.html` | P1 | STATIC, M2 | Enum **display** mapped; query params stay Chinese (by design) |
| `finance/order/count.html` | P2 | STATIC | Stats / count widgets |
| `finance/recharge/index.html` | P2 | M2 | Uses `notifyResMsg` pattern — extend for other fails |

---

## Account (`views/account/` — real dirs only)

| File | P | Types | Notes |
|------|---|-------|-------|
| `account/personal/index.html` | P1 | STATIC, DYNAMIC, M2 | Captcha radios/checkboxes `title`; `lastPersonalUser` replay on lang |
| `account/config/api.html` | P2 | STATIC | API key switch / labels |
| `account/sub/index.html` | P2 | STATIC | Sub-account list/forms |

---

## Package — buy / my (`views/package/buy|my/`)

| File | P | Types | Notes |
|------|---|-------|-------|
| `package/buy/index.html` | P1 | STATIC, M2 | `notifyResMsg` on purchase fail |
| `package/buy/duration.html` | P2 | POPUP, STATIC | Duration picker layer |
| `package/my/index.html` | P1 | STATIC | My plans list |
| `package/my/detail.html` | P2 | POPUP | Usage cells have no `data-i18n` (OK); `refreshDetailI18n` on `veikor:lang` — polish only |
| `package/my/renew.html` | P2 | POPUP, STATIC | |
| `package/my/buy-upgrade.html` | P2 | POPUP, STATIC | |
| `package/my/up_down.html` | P3 | POPUP, STATIC | |

**Out of customer checklist:** `package/upgrade/*` (admin / doc excluded).

---

## Site — core (`views/site/site/`)

| File | P | Types | Notes |
|------|---|-------|-------|
| `site/site/index.html` | P1 | STATIC, M2 | List, batch actions, certs/cache/unlock |
| `site/site/edit.html` | P1 | DYNAMIC, STATIC | Meta header replay (#242); `lay-text` switches via `refreshSiteEditSwitchLayText`; geo `title` on lang |
| `site/site/addform.html` | P2 | POPUP, STATIC | New site |
| `site/site/update_form.html` | P1 | POPUP, STATIC, M2 | Main customer batch editor |
| `site/site/unlock-ip.html` | P2 | POPUP, M2 | |
| `site/site/update-state.html` | P4 | POPUP | Mostly `show_all` admin toolbar |
| `site/site/update-cname-mode.html` | P4 | POPUP | Admin toolbar |
| `site/site/update-node-group.html` | P4 | POPUP | Admin toolbar |
| `site/site/backend_form.html` | P2 | POPUP | |
| `site/site/cache_form.html` | P2 | POPUP | Switch `lay-text` |
| `site/site/req_header_form.html` | P2 | POPUP | |
| `site/site/resp_header_form.html` | P2 | POPUP | |
| `site/site/url_ratelimit_form.html` | P2 | POPUP | |
| `site/site/url_rewrite_form.html` | P2 | POPUP | |

---

## Site — cert (`views/site/cert/`)

| File | P | Types | Notes |
|------|---|-------|-------|
| `site/cert/cert.html` | P1 | STATIC, M2 | |
| `site/cert/dnsapi.html` | P2 | STATIC | |
| `site/cert/addform.html` | P2 | POPUP, STATIC | |
| `site/cert/dnsapi-add.html` | P2 | POPUP, STATIC | DNS type names = brands (keep) |
| `site/cert/update-cert-type.html` | P2 | POPUP | |

---

## Site — ACL / CC / group / refresh

| File | P | Types | Notes |
|------|---|-------|-------|
| `site/acl/index.html` | P1 | STATIC | |
| `site/acl/acl-add.html` | P2 | POPUP | |
| `site/acl/acllist-add.html` | P0 | POPUP, DYNAMIC | **Done #299** — `#matchers` lang replay |
| `site/cc/rule.html` | P1 | STATIC | |
| `site/cc/rule-add.html` | P2 | POPUP | |
| `site/cc/rulelist-add.html` | P2 | POPUP | Switch `lay-text` |
| `site/cc/match-add.html` | P2 | POPUP | |
| `site/cc/matchlist-add.html` | P2 | POPUP | |
| `site/cc/filter-add.html` | P2 | POPUP | |
| `site/group/index.html` | P2 | STATIC | |
| `site/group/addform.html` | P2 | POPUP | |
| `site/refresh/index.html` | P2 | STATIC | Clear cache |

---

## Site — monitor (`views/site/monitor/`)

| File | P | Types | Notes |
|------|---|-------|-------|
| `site/monitor/realtime.html` | P1 | STATIC, CHART | Pair with `stream/monitor/realtime.html` |
| `site/monitor/usage.html` | P1 | STATIC, CHART | |
| `site/monitor/top-res.html` | P1 | STATIC, CHART | |
| `site/monitor/domain-rank.html` | P2 | STATIC, CHART | |
| `site/monitor/attack-rank.html` | P2 | STATIC, CHART | Site-only |
| `site/monitor/blackip.html` | P2 | STATIC | Tabs + `data-veikor-tab` |
| `site/monitor/access-log.html` | P2 | STATIC, M2 | Apply/download flows |

---

## Stream (`views/stream/`)

Mirror site where paths exist:

| File | P | Types | Notes |
|------|---|-------|-------|
| `stream/stream/index.html` | P1 | STATIC, M2 | |
| `stream/stream/edit.html` | P1 | DYNAMIC, STATIC | Meta replay (#242) |
| `stream/stream/addform.html` | P2 | POPUP | |
| `stream/stream/update_form.html` | P2 | POPUP | |
| `stream/stream/update-state.html` | P4 | POPUP | Admin skew |
| `stream/stream/update-cname-mode.html` | P4 | POPUP | |
| `stream/stream/update-node-group.html` | P4 | POPUP | |
| `stream/stream/backend_form.html` | P2 | POPUP | |
| `stream/stream/acl-add.html` | P2 | POPUP | |
| `stream/group/index.html` | P2 | STATIC | |
| `stream/group/addform.html` | P2 | POPUP | |
| `stream/monitor/realtime.html` | P1 | CHART | |
| `stream/monitor/usage.html` | P1 | CHART | |
| `stream/monitor/top-res.html` | P1 | CHART | |

---

## Messages (`views/system/message/`)

| File | P | Types | Notes |
|------|---|-------|-------|
| `system/message/index.html` | P2 | STATIC | List chrome i18n; **titles from API** |
| `system/message/detail.html` | P2 | POPUP, STATIC | Body from API |

---

## Customer controllers (`panel/src/controller/`)

| File | P | Types | Notes |
|------|---|-------|-------|
| `senior.js` | P1 | CHART | Site monitor charts / polling UI |
| `site-usage-senior.js` | P1 | CHART | Usage charts |
| `stream_senior.js` | P1 | CHART | Stream monitor |
| `stream-usage-senior.js` | P1 | CHART | Stream usage |

**Not customer scope:** `node_senior.js` (admin).

---

## Suggested PR slices (one branch each)

1. **P0 `veikorRenderFormSkins`** — customer `form.render(null)` sweep (CI fails if `veikor:lang` pages regress). **P0 dynamic** — `acllist-add.html` `#matchers`, package `detail.html` numeric cells, any new `id`+`data-i18n` hosts; CI rule.
2. **P1 finance + home + package my/buy** — M2 samples from recharge/buy/order APIs.
3. **P1 site/stream list + edit** — remaining `lay-text` / placeholder sweep on edit.
4. **P1 monitors + 4 senior controllers** — chart labels on `veikor:lang`.
5. **P2 all popups** — batch: addforms, `update_form`, cert/acl/cc forms (shared `veikor:lang.siteList` / parent refresh).
6. **P3 global M2** — only `veikor-i18n.js` + cross-cutting `notifyResMsg` in views touched by 1–5.

---

## Explicitly not in this checklist

See `customer-console-i18n.md` — admin console, `package/upgrade`, API Chinese enums in URLs, and **backend-authored** announcement/transfer/business names (require product/backend, not a single-file UI pass).