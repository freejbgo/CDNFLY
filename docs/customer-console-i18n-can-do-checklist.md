# Customer console i18n — can-do backlog by module

Scope: **`user_type !== 1` only** (see `customer-console-i18n.md`). Edit panel under `.veikor-build/.../panel/src`, then `sync-panel-to-master-tar.sh` + `verify-packages.sh`.

**Batch delivered (through 2026-11-19, PR #298–#384):** U2B + alive guards (#298–#306); nested popup titles (#307–#323); finance/package/monitor (#325–#347); **78** tar i18n spots + partial export fixes `up_down` / `acl-add` / `acllist-add` (#349–#370); handoff doc (#371–#374); `site/refresh` lang scope (#381); package detail remain cells (#383). **Remaining:** P3 production `res.msg` → `API_MSG_BY_SOURCE`（见 dev report §P3 操作约束，禁止臆造）；P4 admin popups (out of scope); API-authored titles (out of scope).

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
| `account/log/*` | `system/log/*` (customer; `reload*LogPageI18n` tar spot #366) |

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
| `views/user_home.html` | P1 | STATIC, DYNAMIC | `reloadUserHomeI18n` (tar #362); announcement buttons (#333); API title/body |

---

## Finance (`views/finance/`)

| File | P | Types | Notes |
|------|---|-------|-------|
| `finance/balance/index.html` | P1 | DYNAMIC, M2 | `reloadBalancePageI18n` (tar #362); pay QR title (#311) |
| `finance/balance/return.html` | P4 | STATIC, POPUP | `panel-lang` + **`veikor:lang`**; tar spot (#347) |
| `finance/balance/alipay.html` | P2 | POPUP, STATIC | Parent refreshes layer title + body on lang (#311) |
| `finance/balance/weixin.html` | P2 | POPUP, STATIC | Same as alipay fragment (#311) |
| `finance/order/index.html` | P1 | STATIC, M2 | `reloadOrderListPageI18n` (tar #347) |
| `finance/order/count.html` | P2 | STATIC | `reloadOrderCountPageI18n` (tar #347) |
| `finance/recharge/index.html` | P2 | M2 | `reloadRechargePageI18n` (tar #364); `notifyResMsg` |

---

## Account (`views/account/` — real dirs only)

| File | P | Types | Notes |
|------|---|-------|-------|
| `account/personal/index.html` | P1 | STATIC, DYNAMIC, M2 | Captcha radios/checkboxes `title`; `lastPersonalUser` replay; `layer.prompt` titles (#331); `reloadPersonalPageI18n` (tar #349) |
| `account/config/api.html` | P2 | STATIC | `reloadAccountApiI18n` (tar #368); `updateApiSwitchLayText` (#349) |
| `account/sub/index.html` | P2 | STATIC | `reloadAccountSubI18n` (tar #347) |

---

## Package — buy / my (`views/package/buy|my/`)

| File | P | Types | Notes |
|------|---|-------|-------|
| `package/buy/index.html` | P1 | STATIC, M2 | `reloadBuyPackageI18n` (tar #362); `notifyResMsg` on purchase fail |
| `package/buy/duration.html` | P2 | POPUP, STATIC | `window.refreshPackageBuyDurationPopupI18n` (#343); parent `LAY-popup-acl-add` |
| `package/my/index.html` | P1 | STATIC | `reloadMyPackageI18n` (tar #364); popups/prompts (#335) |
| `package/my/detail.html` | P2 | POPUP | `refreshPackageDetailI18n` 剩余/不限 on lang (#383) |
| `package/my/renew.html` | P2 | POPUP, STATIC | `window.refreshPackageRenewPopupI18n` |
| `package/my/buy-upgrade.html` | P2 | POPUP, STATIC | `window.refreshPackageBuyUpgradeI18n` title + body (#337) |
| `package/my/up_down.html` | P2 | POPUP, STATIC | Nested buy-upgrade title (#325); `window.refreshUpDownI18n` (#354) |

**Out of customer checklist:** `package/upgrade/*` (admin / doc excluded).

---

## Site — core (`views/site/site/`)

| File | P | Types | Notes |
|------|---|-------|-------|
| `site/site/index.html` | P1 | STATIC, M2 | `reloadSiteListPageI18n` + `refreshSiteListOpenLayers` (#329, tar #355/#360) |
| `site/site/edit.html` | P1 | DYNAMIC, STATIC | `refreshSiteEditOpenLayers` + `rememberSiteEditPopupTitle` (tar #360) |
| `site/site/addform.html` | P2 | POPUP, STATIC | New site |
| `site/site/update_form.html` | P1 | POPUP, STATIC, M2 | Nested layer titles on `veikor:lang` (#317) |
| `site/site/unlock-ip.html` | P2 | POPUP, M2 | `window.refreshSiteUnlockIpI18n`; title via `site/index` open layers |
| `site/site/update-state.html` | P4 | POPUP | **Out of scope** — admin `show_all` toolbar |
| `site/site/update-cname-mode.html` | P4 | POPUP | **Out of scope** — admin toolbar |
| `site/site/update-node-group.html` | P4 | POPUP | **Out of scope** — admin toolbar |
| `site/site/backend_form.html` | P2 | POPUP | Content i18n; layer title via `edit.html` `refreshSiteEditOpenLayers` |
| `site/site/cache_form.html` | P2 | POPUP | Switch `lay-text` |
| `site/site/req_header_form.html` | P2 | POPUP | Same parent refresh as `backend_form` |
| `site/site/resp_header_form.html` | P2 | POPUP | Same parent refresh as `backend_form` |
| `site/site/url_ratelimit_form.html` | P2 | POPUP | Same parent refresh as `backend_form` |
| `site/site/url_rewrite_form.html` | P2 | POPUP | Same parent refresh as `backend_form` |

---

## Site — cert (`views/site/cert/`)

| File | P | Types | Notes |
|------|---|-------|-------|
| `site/cert/cert.html` | P1 | STATIC, M2 | `reloadCertListPageI18n` + `refreshCertListOpenLayers` (tar #364/#345) |
| `site/cert/dnsapi.html` | P2 | STATIC | `refreshDnsApiI18n` + open layer (tar #368/#345) |
| `site/cert/addform.html` | P2 | POPUP, STATIC | |
| `site/cert/dnsapi-add.html` | P2 | POPUP, STATIC | DNS type names = brands (keep) |
| `site/cert/update-cert-type.html` | P2 | POPUP | `refreshCertUpdateTypeI18n` + `cert.html` layer titles |

---

## Site — ACL / CC / group / refresh

| File | P | Types | Notes |
|------|---|-------|-------|
| `site/acl/index.html` | P1 | STATIC | `refreshAclOpenLayer` (tar #349) |
| `site/acl/acl-add.html` | P2 | POPUP | `window.refreshAclAddFormI18n` (#357); nested rule popups (#323) |
| `site/acl/acllist-add.html` | P0 | POPUP, DYNAMIC | `#matchers` lang replay (#299); `window.refreshAclListAddPopupsI18n` (#358) |
| `site/cc/rule.html` | P1 | STATIC | `reloadCcRulePageI18n` + open layers (#315, tar #362) |
| `site/cc/rule-add.html` | P2 | POPUP | Nested rulelist/matchlist layer titles (#323) |
| `site/cc/rulelist-add.html` | P2 | POPUP | `refreshCcRulelistAddI18n` switch `lay-text`; title via `rule-add` (#323) |
| `site/cc/match-add.html` | P2 | POPUP | Nested matchlist layer titles (#323) |
| `site/cc/matchlist-add.html` | P2 | POPUP | Content i18n; title via `match-add` (#323) |
| `site/cc/filter-add.html` | P2 | POPUP | Content i18n; filter layer title via `rule.html` (#315) |
| `site/group/index.html` | P2 | STATIC | `window.refreshSiteGroupI18n` (tar #349) |
| `site/group/addform.html` | P2 | POPUP | `refreshSiteGroupAddFormI18n` + `site/group/index.html` layer title |
| `site/refresh/index.html` | P2 | STATIC | `veikor:lang.siteRefresh` only (#381); tar #349 |

---

## Site — monitor (`views/site/monitor/`)

| File | P | Types | Notes |
|------|---|-------|-------|
| `site/monitor/realtime.html` | P1 | STATIC, CHART | `refreshSiteMonitorRealtimeChrome` + charts (#341, tar #368) |
| `site/monitor/usage.html` | P1 | STATIC, CHART | |
| `site/monitor/top-res.html` | P1 | STATIC, CHART | `window.refreshSiteTopResI18n` (tar #345) |
| `site/monitor/domain-rank.html` | P2 | STATIC, CHART | |
| `site/monitor/attack-rank.html` | P2 | STATIC, CHART | Site-only |
| `site/monitor/blackip.html` | P2 | STATIC | Tabs + `data-veikor-tab`; unlock-site `layer.prompt` title (#331) |
| `site/monitor/access-log.html` | P2 | STATIC, M2 | Apply/download flows |

---

## Stream (`views/stream/`)

Mirror site where paths exist:

| File | P | Types | Notes |
|------|---|-------|-------|
| `stream/stream/index.html` | P1 | STATIC, M2 | `reloadStreamListPageI18n` + `refreshStreamListOpenLayers` (#329, tar #355/#360) |
| `stream/stream/edit.html` | P1 | DYNAMIC, STATIC | `refreshStreamEditOpenLayers` (tar #360); meta replay (#242) |
| `stream/stream/addform.html` | P2 | POPUP | `refreshStreamAddFormI18n`; title via list `refreshStreamListOpenLayers` |
| `stream/stream/update_form.html` | P2 | POPUP | Batch edit layer title on `veikor:lang` (#319) |
| `stream/stream/update-state.html` | P4 | POPUP | **Out of scope** — admin skew |
| `stream/stream/update-cname-mode.html` | P4 | POPUP | **Out of scope** |
| `stream/stream/update-node-group.html` | P4 | POPUP | **Out of scope** |
| `stream/stream/backend_form.html` | P2 | POPUP | Content i18n; titles via `stream/edit.html` `refreshStreamEditOpenLayers` |
| `stream/stream/acl-add.html` | P2 | POPUP | Content i18n; acl layer title via `stream/edit.html` |
| `stream/group/index.html` | P2 | STATIC | `window.refreshStreamGroupI18n` (tar #350) |
| `stream/group/addform.html` | P2 | POPUP | `refreshStreamGroupAddFormI18n` + `stream/group/index.html` layer title |
| `stream/monitor/realtime.html` | P1 | CHART | `applyStreamMonitorRealtimeChrome` + charts (#341, tar #368) |
| `stream/monitor/usage.html` | P1 | CHART | Delegates `refreshStreamUsageSeniorI18n` on lang (#339) |
| `stream/monitor/top-res.html` | P1 | CHART | `window.refreshStreamTopResI18n` (tar #345) |

---

## Messages (`views/system/message/`)

| File | P | Types | Notes |
|------|---|-------|-------|
| `system/message/index.html` | P2 | STATIC | List chrome i18n; **titles from API** |
| `system/message/detail.html` | P2 | POPUP, STATIC | Static `data-i18n` labels (tar #355); body from API |

---

## Customer controllers (`panel/src/controller/`)

| File | P | Types | Notes |
|------|---|-------|-------|
| `senior.js` | P1 | CHART | `refreshSiteMonitorChartsI18n` (tar spot #339) |
| `site-usage-senior.js` | P1 | CHART | `refreshSiteUsageSeniorI18n` |
| `stream_senior.js` | P1 | CHART | `refreshStreamMonitorChartsI18n` |
| `stream-usage-senior.js` | P1 | CHART | `refreshStreamUsageSeniorI18n` |

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