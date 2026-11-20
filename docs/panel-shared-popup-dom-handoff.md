# Panel shared popup DOM — handoff (signed off 2026-11-20)

Scope: **all business panel pages** where Layui `admin.popup` reuses ids such as `LAY-popup-node-add` or `LAY-popup-acl-add`. Goal: global listeners and DOM reads must not target the wrong open layer.

## Delivered (PR #501–#505, `main` @ `540ebec+)

| PR | Focus |
|----|--------|
| #501 | Package buy/renew/upgrade; group edit `des` prefill |
| #502 | Cert/ACL/batch banner roots; announcement/node/DNS API |
| #503 | CC rule/filter saves; package/site/stream batch (no `layero` fallback) |
| #504 | Layout profile/password; CC rulelist/matchlist nested; cert edit |
| #505 | Rename unused popup callbacks `layero` → `_layero` in `views/**` (118 callbacks) |

## Patterns (use on new popups)

1. **`window.*FormRoot()` / `*PopupRoot()`** in the partial: `getElementById('LAY-popup-…')` plus shell markers (`lay-filter`, `#save`, tables, etc.).
2. **`page*Alive()`** on `form.on` / `table.on` / toolbar handlers.
3. **`root.contains(data.elem)`** on `form.on('submit'…)` when the filter is shared.
4. **Never `$(layero).find(...)`** in business views; prefer live root from partial export.
5. **Batch id banners**: `*BatchIdsBannerRoot()` via `#veikor-batch-*-count` + `#…_id` inside the open popup.
6. Layui still passes a layer node: use **`_layero`** when only `index` is needed (e.g. `layer.close(index)`).

## Verification (expect 0 issues)

```bash
bash scripts/sync-panel-to-master-tar.sh
python3 scripts/audit-panel-tar-i18n-spot.py
python3 scripts/audit-panel-deep.py
python3 scripts/audit-panel-customer-i18n.py
python3 scripts/audit-panel-global-handlers.py
```

Tar spot catalog: `scripts/audit-panel-tar-i18n-spot.py` (FormRoot exports, alive gates, disambiguation strings).

## Explicitly out of scope / left as-is

| Item | Why |
|------|-----|
| `lib/admin.js`, `lib/view.js` | LayuiAdmin framework; `layero` used intentionally |
| Unique popup id per feature | Large refactor; FormRoot disambiguation is the supported approach |
| P3 `res.msg` → `API_MSG_BY_SOURCE` | Customer i18n M2 track (`customer-console-i18n-can-do-checklist.md`) |
| `controller/useradmin.js` | Demo JSON tables; aligned with view FormRoots in **#506** (same PR as this doc) |

## For agents / next slices

- New popup partial: export **one** `*FormRoot()`, add **1–3 tar spots**, gate parent page handler with **`*Alive()`**.
- If a list page opens a popup: bind buttons inside **`$root.find(...)`** after `FormRoot()` is non-null.
- Do not remove `getElementById` from FormRoot helpers; that is how shared ids are disambiguated.