# 客户控制台三语 i18n — 开发交接报告（2026-11-18）

**仓库：** `freejbgo/CDNFLY`  
**主线：** `main` @ `e0999ee`（含 **#298–#337**）  
**受众：** 接替开发的 AI / 维护者  
**范围：** 仅客户会话（`user_type !== 1`）；管理端保持简体，不做三语。

---

## 1. 本轮复核与合并结论

### PR #298（U2B 作用域扫尾）

| 项 | 结果 |
|----|------|
| 变更 | `site/refresh/index.html`：`#clean-cache` 绑定改为 `bindSiteRefreshSubmit()` + `siteRefreshRootEl()`；导出 `window.siteRefreshRootEl` 供 `clean_cache_search()` 使用 |
| 客户视图 `$('#LAY_app_body` | **0**（脚本盘点 + tar 内 `panel/src` 抽查） |
| `scripts/verify-packages.sh` | 通过（合并前本地已跑） |
| `scripts/audit-panel-customer-i18n.py` | **ok** |
| GitHub CI | 该 PR 无上报 checks；以本地 verify + 审计为准 |
| **合并** | **已完成** — `248562b` Merge PR #298 |

**复核备注：** `site/refresh` 已仅用 `veikor:lang.siteRefresh` + 全局 `veikor:lang`（#307）。

### U2B 作用域线（#284–#298）

客户侧列表/工具栏/整页 lang 绑定从全局 `#LAY_app_body` 迁到 `*PageRootEl()` / `data-veikor-page` / `data-veikor-form` 模式，**本条线已收口**。

---

## 2. 当前能力状态（三语 M1）

依据 `docs/customer-console-i18n.md` 与 `scripts/audit-panel-customer-i18n.py`：

| 能力 | 状态 |
|------|------|
| 壳层 + `data-i18n` + `panel-lang` | M1 已签（#237 起基线；后续 PR 增量） |
| 客户页 `veikor:lang` 全局 + 作用域事件 | 主流程页已覆盖；审计无 regression |
| 客户页 `layer.*` 硬编码中文 | 客户视图盘点 **0** 处（`audit` 同类规则） |
| `layer.msg(res.msg)` 未翻译 | 客户视图 **0** 处（须 `translateResMsg` / `notifyResMsg`） |
| `API_MSG_BY_SOURCE` | **~332** 条（脚本下限 285）；未命中 API 文案仍回退简体 |
| 管理端 `node/*`、`config/*`、`package/sold` 等 | **明确不做** 三语 |

**源码编辑路径：** `.veikor-build/cdnfly-master-v5.1.13/master/panel/src/`（gitignore）→ `scripts/sync-panel-to-master-tar.sh` → 仅提交 `cdnfly/cdnfly-master-v5.1.13-centos-7.tar.gz`。

**分支命名：** `cursor/panel-u2b-<topic>-8f9f` 或 checklist 中的 P1/P2 切片名。

---

## 3. 尚未完成的三语实现（按优先级）

详细文件表见 **`docs/customer-console-i18n-can-do-checklist.md`**。以下为接手时建议执行顺序。

### P0 — 稳定性 / CI

| 工作 | 说明 |
|------|------|
| `site/acl/acllist-add.html` `#matchers` | 动态 DOM + `data-i18n` 同宿主，**语言切换有清空风险**（checklist 标注） |
| `form.render(null)` + `veikor:lang` | 审计当前客户页为 **0**；新 PR 勿引入；可做 CI 硬化 |
| `id` + `data-i18n` 同标签 | `audit-panel-customer-i18n.py` 已检；新页用 `data-veikor-dynamic` |

### P1 — 高频 + 图表

| 模块 | 文件 / 控制器 | 类型 |
|------|----------------|------|
| 监控图表 | `site/monitor/*.html`、`stream/monitor/*.html` | STATIC + **CHART** |
| 图表 JS | `controller/senior.js`、`site-usage-senior.js`、`stream_senior.js`、`stream-usage-senior.js` | 各约 **11–14** 处中文轴/系列/提示字面量，需 `veikorI18n.t` + `veikor:lang` 重绘 |
| 站点/流编辑抛光 | `site/site/edit.html`、`stream/stream/edit.html` | 剩余 `lay-text`、placeholder、字典 title |
| 财务 / 首页 / 套餐 | `finance/balance/*`、`user_home.html`、`package/buy|my/index.html` | STATIC + **M2** 增补 API 文案样本 |

### P2 — 弹窗与 partial（约 36 个无 `data-veikor-page` 的 partial）

多为 Layer 片段，父页已 scoped；需在 **打开时 + `veikor:lang`** 对 popup 根做 `applyDataI18n`，并避免全局选择器。

代表性路径：

- `finance/balance/alipay.html`、`weixin.html`
- `package/buy/duration.html`、`package/my/detail.html`、`renew.html`、`buy-upgrade.html`、`up_down.html`
- `site/site/addform.html`、`update_form.html`、各类 `*_form.html`、`unlock-ip.html`
- `site/cert/addform.html`、`dnsapi-add.html`、`update-cert-type.html`
- `site/acl/*-add.html`、`site/cc/*-add.html`、`site/group/addform.html`
- `stream/stream/addform.html`、`update_form.html`、`backend_form.html` 等
- `system/message/detail.html`

### P3 — M2 与全局字典

| 工作 | 说明 |
|------|------|
| `API_MSG_BY_SOURCE` | 从生产/测试收集未映射 `res.msg`，只增客户相关条目 |
| `notifyResMsg` 扫尾 | 新接口失败路径接入 |
| `lib/veikor-i18n.js` — `MENU`/`TITLE` | 自定义菜单、新面包屑 cite |

### P4 — 抛光

| 项 | 说明 |
|----|------|
| Layui **Tab 标题** 随语言切换 | `index.js` / `applyLayuiTabTitlesI18n`（checklist） |
| `site/refresh` 的 `veikor:lang.siteList` | 可改名为 refresh 专用 scope |
| `finance/balance/return.html` | 独立支付回跳页可选 lang 监听 |
| `package/my/detail.html` | 数值格 dynamic 抛光 |

### 明确不做（产品范围）

- 管理端全部内页三语
- `package/upgrade/*`（checklist 排除）
- API 查询参数中的中文枚举（按设计保留）
- **后端下发的** 公告标题、业务名称等（需产品与后端，非单文件 UI）

---

## 4. 建议的下一批 PR 切片（来自 checklist §Suggested PR slices）

1. **P0** — `acllist-add` dynamic + `veikorRenderFormSkins` 规范  
2. **P1** — finance + home + package my/buy 的 M2 样本  
3. **P1** — site/stream list + edit 剩余开关/placeholder  
4. **P1** — monitors + 四个 `*-senior.js` 图表文案  
5. **P2** — addform / `update_form` / cert|acl|cc 弹窗批量  
6. **P3** — 仅改 `veikor-i18n.js` 与跨页 `notifyResMsg`

---

## 5. 接手命令速查

```bash
cd /agent/repos/CDNFLY
python3 scripts/audit-panel-customer-i18n.py
bash scripts/sync-panel-to-master-tar.sh
bash scripts/verify-packages.sh
```

客户视图 `$('#LAY_app_body` 回归：

```bash
rg "\$\(['\"]#LAY_app_body" .veikor-build/cdnfly-master-v5.1.13/master/panel/src/views \
  --glob '{site,stream,account,finance,package,user_home,system/message}/**'
```

---

## 6. 报告自核（复核清单）

| 断言 | 核证方式 | 结论 |
|------|----------|------|
| #298 已合并 | `git log -1 main` → `248562b` | ✓ |
| U2B jQuery 全局选择器为 0 | Python 扫描客户 views | ✓ |
| 客户 i18n 审计 ok | `audit-panel-customer-i18n.py` | ✓ |
| layer 硬编码中文（客户） | Python `LAYER_CJK` 扫描 | ✓ 0 处 |
| 剩余工作以 checklist P0–P4 为准 | 与 `customer-console-i18n-can-do-checklist.md` 交叉 | ✓ 一致 |
| 管理端未纳入剩余项 | `customer-console-i18n.md` scope | ✓ |

**结论（2026-11-19 更新）：** U2B 已收口；**#299–#306** 已交付 P0–P4 增量（含 `acllist-add` 动态 lang、`up_down`/`jobs` alive、`siteRefresh` scope、缓存弹窗标题、`API_MSG` 样本、**`/jobs` done 回归审计**、缓存/URL 三条 API 映射、`return.html` `veikor:lang`）。**客户静态/弹窗三语 + `audit-panel-customer-i18n.py` 已绿**；剩余主要为 **P3 生产 `res.msg` 增量映射**、P4 Layui tab 标题等低流量抛光。

| PR | 摘要 |
|----|------|
| #299 | `acllist-add` 语言切换徽章/option 刷新 |
| #300 | `up_down` layer alive；`site/refresh` → `veikor:lang.siteRefresh` |
| #301 | `update_form` 缓存编辑弹窗标题 i18n |
| #302 | refresh jobs `done` alive；3 条 `API_MSG_BY_SOURCE` |
| #303 | site list / blackip `/jobs` 成功 toast alive |
| #304 | `audit-panel-customer-i18n` 锁定 `/jobs` done `*Alive()` |
| #305 | 交接报告 + checklist 同步 #298–#304 |
| #306 | +3 `API_MSG`；`return.html` `veikor:lang` |
| #307 | 客户 tab 标签不写死 `res.title`；`site/refresh` 去掉 `siteList` 监听 |
| #308 | 交接报告主线 SHA |
| #309 | `package/my` 详情/升级包/续费弹窗标题随语言刷新（文档；tar 缺码 **#313** 补） |
| #311 | 充值页微信/支付宝扫码弹窗标题随语言刷新 |
| #313 | 落地 #309：`index.html` 三弹窗 + `up_down` 升级包层标题 |
| #314 | 交接报告主线 SHA |
| #315 | `site/cc/rule` 规则/匹配/过滤弹窗标题随语言刷新 |
| #316 | 交接报告主线 SHA |
| #317 | `site/site/update_form` 批量修改及嵌套弹窗标题随语言刷新 |
| #318 | 交接报告主线 SHA |
| #319 | `stream/stream/update_form` 批量修改弹窗标题随语言刷新 |
| #320 | 交接报告主线 SHA |
| #321 | CI：`audit-panel-tar-i18n-spot.py` 校验 tar 内 i18n 地标 |
| #322 | 交接报告主线 SHA |
| #323 | CC/ACL 嵌套弹窗（rulelist/matchlist/acllist）标题随语言刷新 |
| #324 | 主线 SHA + tar spot `refreshCcRuleChildPopups` |
| #325 | 我的套餐「购买升级」嵌套弹窗标题随语言刷新 |
| #326 | 交接报告主线 SHA |
| #327 | 我的套餐重命名 `layer.prompt` 标题随语言刷新 |
| #328 | 交接报告主线 SHA |
| #329 | 网站/转发列表批量 CNAME 域名 `layer.prompt` 标题随语言刷新 |
| #330 | 交接报告主线 SHA |
| #331 | 黑名单解锁站点 / 账户资料 `layer.prompt` 标题随语言刷新 |
| #332 | 交接报告主线 SHA |
| #333 | 用户首页公告 `layer.open` 按钮文案随语言刷新 |
| #334 | 交接报告主线 SHA |
| #335 | 我的套餐列表委托 detail/renew i18n；tar spot CNAME prompt；checklist 扫尾 |
| #336 | 交接报告主线 SHA |
| #337 | `buy-upgrade` 导出 `refreshPackageBuyUpgradeI18n` 供父页委托 |

---

## 7. 相关文档

- `docs/customer-console-i18n.md` — 范围、双轴（role / `show_all`）、陷阱  
- `docs/customer-console-i18n-can-do-checklist.md` — 按模块 backlog  