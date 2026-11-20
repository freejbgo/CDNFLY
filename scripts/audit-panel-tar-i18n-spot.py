#!/usr/bin/env python3
"""Spot-check committed panel tarball for customer i18n landmarks (tar must match releases)."""
from __future__ import annotations

import os
import sys
import tarfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TAR = os.path.join(ROOT, "cdnfly", "cdnfly-master-v5.1.13-centos-7.tar.gz")
PREFIX = "cdnfly-master-v5.1.13/master/panel/src/"

# (path under panel/src, substring that must appear)
SPOTS = (
    (
        "views/package/my/index.html",
        "refreshMyPackageOpenLayer('LAY-popup-package-detail'",
        "package/my popup title refresh (#313)",
    ),
    (
        "views/finance/balance/index.html",
        "__veikorBalancePayTitleKey",
        "balance pay QR popup title (#311)",
    ),
    (
        "views/site/cc/rule.html",
        "refreshCcRuleOpenLayers",
        "CC rule open popup titles (#315)",
    ),
    (
        "views/site/site/update_form.html",
        "refreshSiteUpdateNestedOpenLayers",
        "site batch update nested popups (#317)",
    ),
    (
        "views/site/site/update_form.html",
        "if (!siteUpdatePopupAlive()",
        "site batch update nested layers gated on open popup",
    ),
    (
        "views/stream/stream/update_form.html",
        "veikorI18n.t('page.stream.stream.popup.updateForm')",
        "stream batch update popup title (#319)",
    ),
    (
        "views/site/site/edit.html",
        "rememberSiteEditPopupTitle",
        "site edit nested popup title map",
    ),
    (
        "views/site/cc/rule-add.html",
        "refreshCcRuleChildPopups",
        "CC rule/match nested popup titles (#323)",
    ),
    (
        "views/site/cc/rule-add.html",
        "renderCcRuleGroupSwitchI18n",
        "CC rule group visible switch lang re-skin",
    ),
    (
        "views/package/my/buy-upgrade.html",
        "querySelector('#buy-upgrade-confirm')",
        "package buy-upgrade partial shell marker",
    ),
    (
        "views/package/my/buy-upgrade.html",
        "window.refreshPackageBuyUpgradeI18n",
        "package my buy-upgrade i18n hook (#337)",
    ),
    (
        "views/package/my/index.html",
        "refreshMyPackageRenamePrompt",
        "package my rename prompt title refresh",
    ),
    (
        "views/site/monitor/blackip.html",
        "__veikorBlackipUnlockSitePromptIndex",
        "blackip unlock-site prompt title refresh",
    ),
    (
        "views/account/personal/index.html",
        "__veikorPersonalPromptTitleKey",
        "account personal prompt title refresh",
    ),
    (
        "views/user_home.html",
        "refreshUserHomeAnnouncementLayer",
        "user home announcement layer btn refresh",
    ),
    (
        "views/site/site/index.html",
        "__veikorSiteListCnamePromptIndex",
        "site list CNAME prompt (#329)",
    ),
    (
        "views/stream/stream/index.html",
        "__veikorStreamListCnamePromptIndex",
        "stream list CNAME prompt (#329)",
    ),
    (
        "views/package/my/index.html",
        "refreshPackageDetailI18n",
        "package my list delegates detail/renew i18n",
    ),
    (
        "views/site/monitor/realtime.html",
        "refreshSiteMonitorChartsI18n",
        "site realtime chart refresh delegate",
    ),
    (
        "views/stream/monitor/realtime.html",
        "refreshStreamMonitorChartsI18n",
        "stream realtime chart refresh delegate",
    ),
    (
        "views/stream/monitor/realtime.html",
        "path[2] !== 'realtime'",
        "stream realtime monitor route guard",
    ),
    (
        "views/site/monitor/usage.html",
        "refreshSiteUsageSeniorI18n",
        "site usage chart refresh delegate",
    ),
    (
        "views/stream/monitor/usage.html",
        "refreshStreamUsageSeniorI18n",
        "stream usage chart refresh delegate (#339)",
    ),
    (
        "controller/senior.js",
        "refreshSiteMonitorChartsI18n",
        "site monitor realtime charts i18n",
    ),
    (
        "controller/site-usage-senior.js",
        "veikorTableReloadI18nCols",
        "site usage detail tables lang reload",
    ),
    (
        "controller/site-usage-senior.js",
        "refreshSiteUsageSeniorI18n",
        "site usage charts i18n",
    ),
    (
        "controller/stream_senior.js",
        "refreshStreamMonitorChartsI18n",
        "stream monitor realtime charts i18n",
    ),
    (
        "controller/stream-usage-senior.js",
        "veikorTableReloadI18nCols",
        "stream usage detail tables lang reload",
    ),
    (
        "controller/stream-usage-senior.js",
        "refreshStreamUsageSeniorI18n",
        "stream usage charts i18n",
    ),
    (
        "views/package/buy/index.html",
        "refreshBuyPackageOpenLayers",
        "package buy duration popup title/body",
    ),
    (
        "views/package/buy/duration.html",
        "window.refreshPackageBuyDurationPopupI18n",
        "package buy duration partial hook (#343)",
    ),
    (
        "views/site/site/unlock-ip.html",
        "window.refreshSiteUnlockIpI18n",
        "site unlock-ip popup i18n",
    ),
    (
        "views/site/site/unlock-ip.html",
        "function refreshSiteUnlockIpI18n(langOnly)",
        "site unlock-ip lang-only radio skins",
    ),
    (
        "views/site/site/index.html",
        "refreshSiteUnlockIpI18n(true)",
        "site list unlock popup lang-only refresh",
    ),
    (
        "views/system/message/index.html",
        "if (!messagePageAlive()",
        "message detail open layer gated on list page",
    ),
    (
        "views/site/monitor/domain-rank.html",
        "window.refreshDomainRankI18n",
        "site monitor domain rank",
    ),
    (
        "views/site/monitor/attack-rank.html",
        "window.refreshAttackRankI18n",
        "site monitor attack rank",
    ),
    (
        "views/site/monitor/access-log.html",
        "window.refreshAccessLogI18n",
        "site monitor access log",
    ),
    (
        "views/site/monitor/access-log.html",
        "veikorSyncLayuiSelectTitles",
        "access log cache-status search lang sync",
    ),
    (
        "views/site/monitor/top-res.html",
        "window.refreshSiteTopResI18n",
        "site monitor top resources",
    ),
    (
        "views/stream/monitor/top-res.html",
        "window.refreshStreamTopResI18n",
        "stream monitor top resources",
    ),
    (
        "views/site/cert/dnsapi.html",
        "refreshDnsApiOpenLayer",
        "cert dnsapi popup titles",
    ),
    (
        "views/site/cert/cert.html",
        "refreshCertListOpenLayers",
        "cert list open popup titles",
    ),
    (
        "views/system/message/index.html",
        "refreshMessageDetailOpenLayer",
        "customer message detail popup",
    ),
    (
        "views/finance/balance/return.html",
        "addEventListener('veikor:lang', repaintReturnI18n)",
        "balance pay return standalone i18n (#306)",
    ),
    (
        "views/finance/order/index.html",
        "reloadOrderListPageI18n",
        "finance order list i18n",
    ),
    (
        "views/finance/order/count.html",
        "reloadOrderCountPageI18n",
        "finance order stats i18n",
    ),
    (
        "views/account/sub/index.html",
        "reloadAccountSubI18n",
        "account message subscription i18n",
    ),
    (
        "views/account/config/api.html",
        "updateApiSwitchLayText",
        "account API key switch lay-text",
    ),
    (
        "views/account/config/api.html",
        "veikorRenderFormControlSkins('account-api-config'",
        "account API config control skins on load",
    ),
    (
        "views/site/site/req_header_form.html",
        "refreshSiteReqHeaderFormI18n()",
        "req header partial init via refresh only",
    ),
    (
        "views/account/personal/index.html",
        "reloadPersonalPageI18n",
        "account personal page i18n",
    ),
    (
        "views/site/acl/index.html",
        "refreshAclOpenLayer",
        "site ACL list popup titles",
    ),
    (
        "views/site/acl/index.html",
        "reloadAclListI18n",
        "site ACL list page i18n",
    ),
    (
        "views/site/acl/acl-add.html",
        "window.refreshAclAddFormI18n",
        "site ACL add popup partial hook (#357)",
    ),
    (
        "views/site/acl/acllist-add.html",
        "window.refreshAclListAddPopupsI18n",
        "ACL rule match nested popups (#358)",
    ),
    (
        "views/site/refresh/index.html",
        "refreshSiteRefreshI18n",
        "site cache refresh page",
    ),
    (
        "views/site/refresh/index.html",
        "veikorSyncLayuiSelectTitles",
        "site refresh op-log search lang sync",
    ),
    (
        "views/site/refresh/index.html",
        "veikorRenderFormControlSkins('site-refresh-main-form'",
        "site refresh main form control skins",
    ),
    (
        "views/site/cert/update-cert-type.html",
        "refreshCertUpdateTypeI18n(true)",
        "cert batch type popup langOnly after DNS AJAX",
    ),
    (
        "views/site/cert/cert.html",
        "refreshCertUpdateTypeI18n(true)",
        "cert list open layers batch type langOnly",
    ),
    (
        "views/site/group/index.html",
        "refreshSiteGroupAddFormI18n(true)",
        "site group list open layer langOnly",
    ),
    (
        "views/package/buy/index.html",
        "refreshPackageBuyDurationPopupI18n(true)",
        "package buy duration popup langOnly on reload",
    ),
    (
        "views/package/my/index.html",
        "refreshPackageRenewPopupI18n(true)",
        "package my renew open layer langOnly",
    ),
    (
        "views/stream/stream/edit.html",
        "refreshStreamAclAddFormI18n(true)",
        "stream edit ACL edit prefill langOnly refresh",
    ),
    (
        "views/site/cc/rule.html",
        "LAY-popup-rulegroup-add",
        "CC rule open layers scoped rule/match refresh",
    ),
    (
        "views/package/my/up_down.html",
        "refreshPackageBuyUpgradeI18n",
        "package buy-upgrade popup open uses refresh partial",
    ),
    (
        "views/site/group/index.html",
        "window.refreshSiteGroupI18n",
        "site group list popups",
    ),
    (
        "views/site/site/addform.html",
        "window.refreshSiteAddFormI18n",
        "site add popup partial i18n",
    ),
    (
        "views/stream/stream/addform.html",
        "window.refreshStreamAddFormI18n",
        "stream add popup partial i18n",
    ),
    (
        "views/stream/group/index.html",
        "window.refreshStreamGroupI18n",
        "stream group list popups",
    ),
    (
        "views/stream/group/addform.html",
        "window.refreshStreamGroupAddFormI18n",
        "stream group add popup partial i18n",
    ),
    (
        "views/site/group/addform.html",
        "window.refreshSiteGroupAddFormI18n",
        "site group add popup partial i18n",
    ),
    (
        "views/site/group/index.html",
        "refreshSiteGroupAddFormI18n",
        "site group popup without full skins on open",
    ),
    (
        "views/stream/group/index.html",
        "refreshStreamGroupAddFormI18n",
        "stream group popup without full skins on open",
    ),
    (
        "views/site/site/update_form.html",
        "refreshSiteCacheFormI18n",
        "batch update cache edit popup sync after prefill",
    ),
    (
        "views/site/cert/addform.html",
        "window.refreshCertAddFormI18n",
        "cert add popup partial i18n",
    ),
    (
        "views/package/my/up_down.html",
        "window.refreshUpDownI18n",
        "package up_down partial i18n hook (#354)",
    ),
    (
        "views/package/my/detail.html",
        "window.refreshPackageDetailI18n",
        "package detail partial i18n",
    ),
    (
        "views/package/my/renew.html",
        "querySelector('#renew-confirm')",
        "package my renew partial shell marker",
    ),
    (
        "views/package/my/renew.html",
        "window.refreshPackageRenewPopupI18n",
        "package renew partial i18n",
    ),
    (
        "views/system/message/index.html",
        "reloadMessageQueryPageI18n",
        "customer message list i18n",
    ),
    (
        "views/site/site/index.html",
        "refreshSiteListOpenLayers",
        "site list nested popup titles",
    ),
    (
        "views/site/site/index.html",
        "refreshSiteAddFormI18n(true)",
        "site list open layers add popup langOnly",
    ),
    (
        "views/stream/stream/index.html",
        "refreshStreamListOpenLayers",
        "stream list nested popup titles",
    ),
    (
        "views/stream/stream/index.html",
        "refreshStreamAddFormI18n(true)",
        "stream list open layers add popup langOnly",
    ),
    (
        "views/site/acl/index.html",
        "refreshAclAddFormI18n(true)",
        "ACL list open layer langOnly",
    ),
    (
        "views/system/message/detail.html",
        "LAY-popup-message-detail-pane",
        "message detail popup static labels",
    ),
    (
        "views/site/site/index.html",
        "reloadSiteListPageI18n",
        "site list page lang reload",
    ),
    (
        "views/site/site/index.html",
        "veikorSyncLayuiSelectTitles",
        "site list search lang sync selects",
    ),
    (
        "views/stream/stream/index.html",
        "reloadStreamListPageI18n",
        "stream list page lang reload",
    ),
    (
        "views/stream/stream/index.html",
        "veikorSyncLayuiSelectTitles",
        "stream list search lang sync selects",
    ),
    (
        "views/stream/stream/index.html",
        "form.render('select', 'stream-list-search')",
        "stream list search scoped first render",
    ),
    (
        "views/site/cert/cert.html",
        "veikorSyncLayuiSelectTitles",
        "cert list search lang sync selects",
    ),
    (
        "views/site/cert/cert.html",
        "form.render('select', 'cert-list-search')",
        "cert list search scoped first render",
    ),
    (
        "views/site/cert/cert.html",
        "veikorRenderFormControlSkins(flt, $form)",
        "cert list lang skins use control skins",
    ),
    (
        "views/site/cc/filter-add.html",
        "refreshCcFilterAddFormI18n();",
        "CC filter add opens via refresh only",
    ),
    (
        "views/site/cc/rule.html",
        "refreshCcFilterAddFormI18n(true)",
        "CC filter edit prefill langOnly refresh",
    ),
    (
        "views/site/site/update_form.html",
        "refreshSiteCacheFormI18n(true)",
        "site batch update nested partials langOnly",
    ),
    (
        "views/finance/recharge/index.html",
        "form.render('radio', 'finance-admin-recharge-form')",
        "finance recharge form control skins pattern",
    ),
    (
        "views/site/site/index.html",
        "refreshSiteUpdatePopupFormLangSkins();\n                    }",
        "site batch update render uses refresh only",
    ),
    (
        "views/site/site/edit.html",
        "window.repaintSiteEditFormLangSkins",
        "site edit AJAX/prefill form lang skins export",
    ),
    (
        "views/site/site/edit.html",
        "repaintSiteEditFormLangSkins",
        "site edit page sync after AJAX and site load",
    ),
    (
        "views/stream/stream/edit.html",
        "window.repaintStreamEditFormLangSkins",
        "stream edit form lang skins export",
    ),
    (
        "views/stream/stream/edit.html",
        "repaintStreamEditFormLangSkins",
        "stream edit port form and nested popup sync",
    ),
    (
        "views/site/site/update_form.html",
        "window.refreshSiteUpdatePopupFormLangSkins",
        "site batch update lang form skins export",
    ),
    (
        "views/site/site/index.html",
        "refreshSiteUpdatePopupFormLangSkins",
        "site batch update AJAX select sync after render",
    ),
    (
        "views/stream/stream/update_form.html",
        "window.refreshStreamUpdatePopupFormLangSkins",
        "stream batch update lang form skins export",
    ),
    (
        "views/stream/stream/index.html",
        "refreshStreamUpdatePopupFormLangSkins",
        "stream batch update AJAX select sync after render",
    ),
    (
        "views/site/site/edit.html",
        "refreshSiteEditOpenLayers",
        "site edit nested popup titles",
    ),
    (
        "views/site/site/edit.html",
        "refreshSiteUrlRewriteFormI18n(true)",
        "site edit url-rewrite code prefill langOnly",
    ),
    (
        "views/site/site/edit.html",
        "fn(true)",
        "site edit open layers call nested refresh langOnly",
    ),
    (
        "views/site/site/backend_form.html",
        "getElementById('LAY-popup-backend-add')",
        "site backend form scoped to popup shell",
    ),
    (
        "views/site/site/backend_form.html",
        "window.refreshSiteBackendFormI18n",
        "site backend defers lang to edit open layers",
    ),
    (
        "views/stream/stream/backend_form.html",
        "getElementById('LAY-popup-backend-add')",
        "stream backend form scoped to popup shell",
    ),
    (
        "views/stream/stream/backend_form.html",
        "window.refreshStreamBackendFormI18n",
        "stream backend defers lang to edit open layers",
    ),
    (
        "views/site/site/cache_form.html",
        "getElementById('LAY-popup-cache-add')",
        "site cache form scoped to popup shell",
    ),
    (
        "views/site/site/resp_header_form.html",
        "getElementById('LAY-popup-resp_header-add')",
        "site resp header form scoped to popup shell",
    ),
    (
        "views/site/site/url_ratelimit_form.html",
        "getElementById('LAY-popup-url-ratelimit-add')",
        "site url ratelimit form scoped to popup shell",
    ),
    (
        "views/site/acl/acllist-add.html",
        "window.siteAclMatchPopupShellOk = siteAclMatchPopupShellOk",
        "ACL match popup shell helper exported",
    ),
    (
        "views/stream/stream/edit.html",
        "refreshStreamEditOpenLayers",
        "stream edit nested popup titles",
    ),
    (
        "views/finance/balance/index.html",
        "reloadBalancePageI18n",
        "finance balance page lang reload",
    ),
    (
        "views/finance/balance/index.html",
        "path[0] !== 'account' && path[0] !== 'finance'",
        "balance symlink accepts account and finance routes",
    ),
    (
        "views/finance/balance/index.html",
        "renderBalanceRechargeControlsI18n",
        "balance recharge pay-method checkbox lang skin",
    ),
    (
        "views/site/cc/rule.html",
        "reloadCcRulePageI18n",
        "CC rule page lang reload",
    ),
    (
        "views/site/cc/rule.html",
        "$(document).on('veikor:lang.ccRule', reloadCcRulePageI18n);",
        "CC rule page scoped lang only",
    ),
    (
        "views/site/cc/rule.html",
        "ccRuleOpenLayerShellOk('LAY-popup-rulelist-edit', ruleListEdit))",
        "CC rule open layer rulelist guard",
    ),
    (
        "views/site/site/edit.html",
        "$(document).on('veikor:lang.siteList', refreshSiteEditI18n);",
        "site edit scoped lang only",
    ),
    (
        "views/site/site/edit.html",
        "path[2] !== 'edit'",
        "site edit alive rejects list route",
    ),
    (
        "views/site/site/index.html",
        "third && third !== 'index'",
        "site list alive rejects edit route",
    ),
    (
        "views/package/my/index.html",
        "$(document).on('veikor:lang.packageMy', reloadMyPackageI18n);",
        "package my scoped lang only",
    ),
    (
        "views/site/group/index.html",
        "refreshSiteGroupAddFormI18n(true)",
        "site group list owns add popup lang refresh",
    ),
    (
        "views/stream/group/index.html",
        "refreshStreamGroupAddFormI18n(true)",
        "stream group list owns add popup lang refresh",
    ),
    (
        "views/site/site/index.html",
        "$(document).on('veikor:lang.siteList', reloadSiteListPageI18n);",
        "site list scoped lang only",
    ),
    (
        "views/site/site/index.html",
        "siteListOpenLayerShellOk('LAY-popup-node-add', siteAddPop)",
        "site list open-layer add guard (LAY-popup-node-add disambiguation)",
    ),
    (
        "views/stream/stream/index.html",
        "streamListOpenLayerShellOk('LAY-popup-stream-add', streamAddPop)",
        "stream list open-layer add guard (stream add disambiguation)",
    ),
    (
        "views/site/site/edit.html",
        "LAY-popup-backend-add', 'refreshSiteBackendFormI18n'",
        "site edit nested open-layer guard",
    ),
    (
        "views/site/cert/cert.html",
        "certListOpenLayerShellOk('LAY-popup-set-cert-type', certTypePop)",
        "cert list batch-type open-layer guard",
    ),
    (
        "views/site/site/update_form.html",
        "siteUpdateNestedFormI18n('LAY-popup-cache-add'",
        "site batch update nested open-layer guard",
    ),
    (
        "views/package/my/index.html",
        "myPackageOpenLayerShellOk('LAY-popup-package-renew', renewPop)",
        "package my renew open-layer guard",
    ),
    (
        "views/package/my/renew.html",
        "function packageRenewPopupRoot()",
        "package renew popup root helper",
    ),
    (
        "views/package/my/renew.html",
        "packageRenewSelectAlive()",
        "package renew duration handler alive gate",
    ),
    (
        "views/package/my/up_down.html",
        "if (upgradeRoot()) layer.close(index)",
        "up_down layer close scoped to upgrade popup shell",
    ),
    (
        "views/package/sold/up_down.html",
        "function upgradeRoot()",
        "package sold upgrade popup root helper",
    ),
    (
        "views/package/sold/up_down.html",
        "soldUpDownPopupAlive()",
        "package sold upgrade table reload alive gate",
    ),
    (
        "views/package/sold/up_down.html",
        "if (upgradeRoot()) layer.close(index)",
        "package sold up_down layer close scoped",
    ),
    (
        "views/package/my/index.html",
        "function myPackageOpenLayerShellOk(popupId, el)",
        "package my popup shell disambiguation",
    ),
    (
        "views/package/my/index.html",
        "window.myPackageOpenLayerShellOk = myPackageOpenLayerShellOk",
        "package my shell helper exported for nested partials",
    ),
    (
        "views/package/my/up_down.html",
        "myPackageOpenLayerShellOk('LAY-popup-package-buy-upgrade'",
        "package up_down nested buy-upgrade shell gate",
    ),
    (
        "views/site/group/index.html",
        "pop.querySelector('.site-group-add-root')",
        "site group open-layer guard",
    ),
    (
        "views/site/group/addform.html",
        "getElementById('LAY-popup-site-group-form')",
        "site group addform scoped to popup shell",
    ),
    (
        "views/stream/group/index.html",
        "pop.querySelector('.stream-group-add-root')",
        "stream group open-layer guard",
    ),
    (
        "views/stream/group/addform.html",
        "getElementById('LAY-popup-stream-group-form')",
        "stream group addform scoped to popup shell",
    ),
    (
        "views/site/site/update-node-group.html",
        "root.querySelector('#update-region')",
        "site node-group partial shell marker",
    ),
    (
        "views/stream/stream/update-node-group.html",
        "root.querySelector('#update-region')",
        "stream node-group partial shell marker",
    ),
    (
        "views/site/acl/acl-add.html",
        "getElementById('LAY-popup-acllist-add')",
        "ACL rule child popup lang guard",
    ),
    (
        "views/site/cc/rule-add.html",
        "refreshCcRulelistAddI18n(true)",
        "CC rulelist AJAX/prefill refresh langOnly",
    ),
    (
        "views/site/cc/match-add.html",
        "refreshCcMatchlistAddI18n(true)",
        "CC matchlist child popup refresh langOnly",
    ),
    (
        "views/site/acl/acl-add.html",
        "refreshRuleMatchFormI18n(root, true)",
        "ACL rule edit prefill langOnly refresh",
    ),
    (
        "views/site/acl/acllist-add.html",
        "repaintAclMatchSelectChrome",
        "ACL match-item select chrome after add/delete",
    ),
    (
        "views/stream/stream/acl-add.html",
        "repaintStreamAclMatchSelectChrome",
        "stream ACL match-item select chrome after add",
    ),
    (
        "views/stream/stream/edit.html",
        "refreshStreamAclAddFormI18n(true)",
        "stream edit ACL rule edit prefill langOnly",
    ),
    (
        "views/site/site/url_ratelimit_form.html",
        "refreshUrlRateLimitFormI18n(true)",
        "URL rate-limit sendParams and match select langOnly",
    ),
    (
        "views/site/site/edit.html",
        "refreshUrlRateLimitFormI18n(true)",
        "site edit URL rate-limit state prefill langOnly",
    ),
    (
        "views/site/site/edit.html",
        "refreshSiteBackendFormI18n(true)",
        "site edit backend state prefill langOnly",
    ),
    (
        "views/site/cert/dnsapi.html",
        "refreshDnsApiAddFormI18n(true)",
        "DNS API open layer and edit prefill langOnly",
    ),
    (
        "views/site/group/index.html",
        "refreshSiteGroupAddFormI18n(true)",
        "site group edit popup langOnly after prefill",
    ),
    (
        "views/site/cert/addform.html",
        "window.repaintCertAddSelectChrome",
        "cert add form AJAX select chrome helper",
    ),
    (
        "views/site/cert/cert.html",
        "repaintCertAddSelectChrome",
        "cert add popup user/dnsapi select sync after AJAX",
    ),
    (
        "views/site/cert/cert.html",
        "refreshCertAddFormI18n()",
        "cert edit popup refresh after cert detail prefill",
    ),
    (
        "views/site/cert/dnsapi.html",
        "refreshDnsApiAddFormI18n",
        "dnsapi popup refresh without full form skins on open",
    ),
    (
        "views/site/site/addform.html",
        "window.repaintSiteAddSelectChrome",
        "site add form AJAX select chrome helper",
    ),
    (
        "views/site/site/index.html",
        "repaintSiteAddSelectChrome",
        "site add popup package/user select sync after AJAX",
    ),
    (
        "views/stream/stream/addform.html",
        "window.repaintStreamAddSelectChrome",
        "stream add form AJAX select chrome helper",
    ),
    (
        "views/stream/stream/index.html",
        "repaintStreamAddSelectChrome",
        "stream add popup package/user select sync after AJAX",
    ),
    (
        "views/package/buy/index.html",
        "reloadBuyPackageI18n",
        "package buy page lang reload",
    ),
    (
        "views/user_home.html",
        "reloadUserHomeI18n",
        "user home overview lang reload",
    ),
    (
        "views/package/my/index.html",
        "reloadMyPackageI18n",
        "package my page lang reload",
    ),
    (
        "views/site/cert/cert.html",
        "reloadCertListPageI18n",
        "cert list page lang reload",
    ),
    (
        "views/finance/recharge/index.html",
        "reloadRechargePageI18n",
        "finance recharge page lang reload",
    ),
    (
        "views/system/log/login.html",
        "reloadLoginLogPageI18n",
        "customer login log page reload",
    ),
    (
        "views/system/log/login.html",
        "form.render('select', 'login-log-search')",
        "login log search control skins on first load",
    ),
    (
        "views/system/log/op.html",
        "form.render('select', 'op-log-search')",
        "operation log search control skins on first load",
    ),
    (
        "views/system/log/msg_send.html",
        "form.render('select', 'log-msg-send-search')",
        "message send log search control skins on first load",
    ),
    (
        "views/finance/order/index.html",
        "renderOrderListForm(true)",
        "finance order list lang-only search sync",
    ),
    (
        "views/finance/order/index.html",
        "path[0] !== 'account' && path[0] !== 'finance'",
        "order symlink accepts account and finance routes",
    ),
    (
        "views/stream/stream/edit.html",
        "if (!streamEditAlive()",
        "stream edit open layers gated on edit route",
    ),
    (
        "views/site/site/edit.html",
        "if (!siteEditAlive()",
        "site edit open layers gated on edit route",
    ),
    (
        "views/site/cc/rule.html",
        "ccRuleRefreshNestedForm('LAY-popup-rulegroup-add'",
        "CC rule group add lang-only on switch",
    ),
    (
        "views/site/acl/index.html",
        "if (!aclPageAlive()",
        "ACL list open layer refresh gated",
    ),
    (
        "views/site/cert/dnsapi.html",
        "if (!dnsApiPageAlive()",
        "DNS API open layer refresh gated",
    ),
    (
        "views/site/group/index.html",
        "if (!siteGroupAlive()",
        "site group open layer refresh gated",
    ),
    (
        "views/stream/group/index.html",
        "if (!streamGroupAlive()",
        "stream group open layer refresh gated",
    ),
    (
        "views/site/site/index.html",
        "refreshSiteNodeGroupPopupI18n(true)",
        "site list node-group lang refresh",
    ),
    (
        "views/stream/stream/index.html",
        "refreshStreamNodeGroupPopupI18n(true)",
        "stream list node-group lang refresh",
    ),
    (
        "views/site/site/update-node-group.html",
        "function refreshSiteNodeGroupPopupI18n(langOnly)",
        "site node-group partial accepts langOnly",
    ),
    (
        "views/account/sub/index.html",
        "veikorRenderFormControlSkins('account-sub-page'",
        "account sub lang reload uses control skins only",
    ),
    (
        "views/account/personal/index.html",
        "renderPersonalForms(true)",
        "account personal lang-only form skins",
    ),
    (
        "views/site/cc/rule.html",
        "if (!ccRuleAlive()",
        "CC rule per-popup refresh gated on cc page",
    ),
    (
        "views/site/cc/rule.html",
        "function ccRuleOpenLayerShellOk(popupId, el)",
        "CC rule popup shell disambiguation",
    ),
    (
        "views/site/cc/rule.html",
        "ccRuleRefreshNestedForm('LAY-popup-filter-add'",
        "CC rule nested form refresh gated on shell",
    ),
    (
        "views/site/cc/rule.html",
        "window.ccRuleOpenLayerShellOk = ccRuleOpenLayerShellOk",
        "CC rule shell helper exported for nested partials",
    ),
    (
        "views/site/cc/rule-add.html",
        "window.ccRuleOpenLayerShellOk && !window.ccRuleOpenLayerShellOk(popupId, el)",
        "CC rule group child popup shell gate",
    ),
    (
        "views/stream/stream/update_form.html",
        "if (!streamUpdatePopupAlive()",
        "stream batch update i18n gated on open popup",
    ),
    (
        "views/stream/stream/update_form.html",
        "return !!streamUpdatePopupRoot()",
        "stream batch update alive requires collapse shell marker",
    ),
    (
        "views/site/site/update_form.html",
        "if (!siteUpdatePopupAlive() || !veikorI18n) return",
        "site batch update form i18n gated on open popup",
    ),
    (
        "views/site/site/update_form.html",
        "function siteUpdateTableEventOk(tableId, obj)",
        "site batch update nested table handler disambiguation",
    ),
    (
        "views/site/site/update_form.html",
        "return !!siteUpdatePopupRoot()",
        "site batch update alive requires collapse shell marker",
    ),
    (
        "views/site/site/update_form.html",
        "function siteUpdateField(sel) {\n    var popup = siteUpdatePopupRoot();",
        "site batch update field lookup uses popup root",
    ),
    (
        "views/site/site/update_form.html",
        "form.on('checkbox(check-all-asia)', function(data){\n      if (!siteUpdatePopupAlive()) return;",
        "site batch update region check-all gated on popup",
    ),
    (
        "views/site/site/edit.html",
        "function siteEditBatchUpdatePopupRoot()",
        "site edit ssl_mode batch popup shell disambiguation",
    ),
    (
        "views/site/site/edit.html",
        "form.on('checkbox(check-all-asia)', function(data){\n      if (!siteEditEventHere(data)) return;",
        "site edit region check-all scoped to edit page",
    ),
    (
        "views/package/my/index.html",
        "if (!myPackageAlive() || !veikorI18n) return",
        "package my per-popup refresh gated on my-package page",
    ),
    (
        "views/package/buy/duration.html",
        "root.querySelector('[lay-filter=\"acl-add-form\"]')",
        "package buy duration popup rejects acl rule shell",
    ),
    (
        "views/package/buy/index.html",
        "function buyPackageOpenLayerShellOk(el)",
        "package buy popup shell disambiguation on LAY-popup-acl-add",
    ),
    (
        "views/package/buy/index.html",
        "window.buyPackageAlive = buyPackageAlive",
        "package buy alive exported for duration partial",
    ),
    (
        "views/system/message/index.html",
        "function messageDetailOpenLayerShellOk(el)",
        "message detail popup shell disambiguation",
    ),
    (
        "views/system/message/index.html",
        "#LAY-popup-message-detail-pane",
        "message detail partial shell marker",
    ),
    (
        "views/site/cert/cert.html",
        "function certListOpenLayerShellOk(popupId, el)",
        "cert list popup shell disambiguation",
    ),
    (
        "views/site/cert/cert.html",
        "function refreshCertOpenLayer(popupId, titleKey)",
        "cert list per-popup refresh gated on cert page",
    ),
    (
        "views/site/site/edit.html",
        "function refreshSiteEditOpenLayer(popupId, titleKey)",
        "site edit per-popup title refresh gated on edit page",
    ),
    (
        "views/site/site/index.html",
        "function refreshSiteListOpenLayer(popupId, titleKey)",
        "site list per-popup refresh gated; node-add requires package select",
    ),
    (
        "views/stream/stream/index.html",
        "function refreshStreamListOpenLayer(popupId, titleKey)",
        "stream list per-popup refresh gated on stream list page",
    ),
    (
        "views/stream/stream/edit.html",
        "function refreshStreamEditOpenLayer(popupId, titleKey)",
        "stream edit per-popup title refresh gated on edit page",
    ),
    (
        "views/finance/balance/index.html",
        "function balancePayPopupRoot()",
        "balance pay QR popup disambiguates LAY-popup-node-add",
    ),
    (
        "views/finance/balance/index.html",
        "var payRoot = balancePayPopupRoot()",
        "balance pay codepay DOM scoped to pay shell",
    ),
    (
        "views/layout.html",
        "function layoutNodeAddForeignShell(el)",
        "shell lang skips foreign LAY-popup-node-add shells",
    ),
    (
        "views/site/cert/cert.html",
        "certListOpenLayerShellOk('LAY-popup-node-add', popup)",
        "cert edit hides count only in cert node-add shell",
    ),
    (
        "views/site/cert/dnsapi.html",
        "site-dnsapi-add-root[data-veikor-form=\"dnsApiAdd\"]",
        "dns api open layer disambiguates node-add shell",
    ),
    (
        "views/site/cert/cert.html",
        "if (popupId === 'LAY-popup-node-add') return !!el.querySelector(\"textarea[name='cert']\")",
        "cert edit open layer disambiguates node-add shell",
    ),
    (
        "views/site/acl/index.html",
        "function aclRulePopupShellOk(el)",
        "acl rule popup shell disambiguation",
    ),
    (
        "views/site/acl/index.html",
        "!(aclRulePop && aclRulePopupShellOk(aclRulePop))",
        "acl list lang reload dedupes rule popup refresh",
    ),
    (
        "views/site/acl/index.html",
        "!el.querySelector('#buy-confirm')",
        "acl open layer skips package-buy duration shell",
    ),
    (
        "views/site/acl/acl-add.html",
        "function aclRuleChildPopupShellOk(el)",
        "acl rule child popup disambiguates stream ACL shell",
    ),
    (
        "views/site/acl/acl-add.html",
        "siteAclMatchPopupShellOk(pop))",
        "acl rule add matcher refresh gated by site shell",
    ),
    (
        "views/site/acl/acl-add.html",
        "aclRuleChildPopupShellOk(pop)) return",
        "acl rule matcher save gated by child shell",
    ),
    (
        "views/site/acl/acl-add.html",
        "aclRulePopupShellOk(root)) return root",
        "acl rule editor root scoped to rule popup shell",
    ),
    (
        "views/site/acl/acl-add.html",
        "function aclRuleAclistEl()",
        "acl rule editor aclist scoped under popup root",
    ),
    (
        "views/site/acl/acl-add.html",
        "function aclRuleAclTableEventOk(obj)",
        "acl rule editor disambiguates stream edit aclist handlers",
    ),
    (
        "views/stream/stream/edit.html",
        "function streamEditAclTableEventOk(obj)",
        "stream edit disambiguates site rule editor aclist handlers",
    ),
    (
        "views/stream/stream/edit.html",
        "function streamEditBackendTableEventOk(obj)",
        "stream edit disambiguates site edit backend handlers",
    ),
    (
        "views/site/site/edit.html",
        "function siteEditBackendTableEventOk(obj)",
        "site edit disambiguates stream edit backend handlers",
    ),
    (
        "views/site/site/edit.html",
        "function siteEditTableEventOk(tableId, obj)",
        "site edit nested table handler disambiguation",
    ),
    (
        "views/site/site/edit.html",
        "siteEditTableEventOk('cache', obj)",
        "site edit cache table disambiguates default config cache",
    ),
    (
        "views/config/default/index.html",
        "function defaultConfigCacheTableEventOk(obj)",
        "default config cache table disambiguates site edit cache",
    ),
    (
        "views/package/upgrade/addform.html",
        "function packageUpgradeAddformRoot()",
        "package upgrade addform scoped to edit popup",
    ),
    (
        "views/site/acl/index.html",
        "el.querySelector('#acllist') && !el.querySelector('#buy-confirm')",
        "acl rule popup shell disambiguates stream edit aclist",
    ),
    (
        "views/site/acl/index.html",
        "window.refreshAclAddFormI18n(true)",
        "acl list lang reload refreshes open rule editor popup",
    ),
    (
        "views/site/acl/acllist-add.html",
        "function siteAclMatchPopupShellOk(el)",
        "acl match popup shell gate",
    ),
    (
        "views/site/acl/acllist-add.html",
        "siteAclMatchPopupShellOk(popRoot)) refreshRuleMatchFormI18n",
        "acl match partial skips stream acl shell on load",
    ),
    (
        "views/site/acl/acllist-add.html",
        "!siteAclMatchPopupShellOk(root)) return",
        "acl match refresh gated by site shell",
    ),
    (
        "views/stream/stream/acl-add.html",
        "function streamAclAddPopupShellOk(el)",
        "stream ACL add popup shell gate",
    ),
    (
        "views/stream/stream/acl-add.html",
        "getElementById('LAY-popup-acllist-add')",
        "stream ACL add scoped to acllist popup shell",
    ),
    (
        "views/site/site/index.html",
        "function siteListOpenLayerShellOk(popupId, el)",
        "site list batch popup shell disambiguation",
    ),
    (
        "views/site/site/index.html",
        "popupId === 'LAY-popup-set-state') return !!el.querySelector('#site_state')",
        "site list state popup disambiguates stream state shell",
    ),
    (
        "views/stream/stream/index.html",
        "function streamListOpenLayerShellOk(popupId, el)",
        "stream list batch popup shell disambiguation",
    ),
    (
        "views/stream/stream/index.html",
        "popupId === 'LAY-popup-set-state') return !!el.querySelector('#stream_state')",
        "stream list state popup disambiguates site state shell",
    ),
    (
        "views/site/site/update_form.html",
        "function siteUpdateNestedOpenLayerShellOk(popupId, el)",
        "site batch update nested popup shell markers",
    ),
    (
        "views/site/cert/cert.html",
        "if (popupId === 'LAY-popup-cert-add') return !!el.querySelector(\"input[name='count']\")",
        "cert add open layer disambiguates node-add shells",
    ),
    (
        "views/site/site/edit.html",
        "function siteEditNestedShellOk(popupId, el)",
        "site edit nested popup lang refresh shell markers",
    ),
    (
        "views/site/site/edit.html",
        "!siteEditNestedShellOk(popupId, node)",
        "site edit open-layer title gated on nested shell",
    ),
    (
        "views/stream/stream/edit.html",
        "function streamEditNestedShellOk(popupId, el)",
        "stream edit nested popup shell markers",
    ),
    (
        "views/stream/stream/edit.html",
        ".stream-acl-add-root",
        "stream edit ACL popup disambiguates site acl shell",
    ),
    (
        "views/site/cert/cert.html",
        "if (popupId === 'LAY-popup-set-cert-type') return !!el.querySelector('.cert-update-type-root')",
        "cert update-type open layer shell marker",
    ),
    (
        "views/system/message/index.html",
        "form.render('select', 'system-message-search')",
        "system message search control skins on first load",
    ),
    (
        "views/site/monitor/access-log.html",
        "form.render('select', 'site-access-log-search')",
        "access log search control skins on first load",
    ),
    (
        "views/site/group/addform.html",
        "refreshSiteGroupAddFormI18n();",
        "site group add opens via refresh only",
    ),
    (
        "views/system/log/op.html",
        "reloadOpLogPageI18n",
        "customer operation log page reload",
    ),
    (
        "views/system/log/backup.html",
        "reloadBackupLogPageI18n",
        "customer backup log page reload",
    ),
    (
        "views/system/log/msg_send.html",
        "reloadMsgSendLogPageI18n",
        "customer message send log page reload",
    ),
    (
        "views/account/config/api.html",
        "reloadAccountApiI18n",
        "account API config page reload",
    ),
    (
        "views/site/cert/dnsapi.html",
        "refreshDnsApiI18n",
        "cert DNS API page i18n",
    ),
    (
        "views/site/monitor/realtime.html",
        "refreshSiteMonitorRealtimeChrome",
        "site monitor realtime chrome",
    ),
    (
        "views/stream/monitor/realtime.html",
        "applyStreamMonitorRealtimeChrome",
        "stream monitor realtime chrome",
    ),
    (
        "views/site/site/index.html",
        "refreshSiteStatePopupI18n(true)",
        "site list owns batch state popup lang refresh",
    ),
    (
        "views/stream/stream/index.html",
        "refreshStreamStatePopupI18n(true)",
        "stream list owns batch state popup lang refresh",
    ),
    (
        "views/package/my/index.html",
        "refreshPackageRenewPopupI18n(true)",
        "package my list owns renew popup lang refresh",
    ),
    (
        "views/package/buy/index.html",
        "refreshPackageBuyDurationPopupI18n(true)",
        "package buy list owns duration popup lang refresh",
    ),
    (
        "views/package/my/index.html",
        "refreshPackageDetailI18n",
        "package my list owns detail popup lang refresh",
    ),
    (
        "views/package/my/index.html",
        "refreshUpDownI18n",
        "package my list owns up_down popup lang refresh",
    ),
    (
        "views/site/monitor/usage.html",
        "renderSiteUsageUsers(true)",
        "site monitor usage AJAX user filter lang sync",
    ),
    (
        "views/stream/monitor/usage.html",
        "renderStreamUsageUsers(true)",
        "stream monitor usage AJAX user filter lang sync",
    ),
    (
        "views/site/acl/acl-add.html",
        "window.refreshAclAddFormI18n",
        "ACL add partial defers lang to list page open layers",
    ),
    (
        "views/site/acl/acllist-add.html",
        "window.refreshAclListAddPopupsI18n",
        "ACL matcher child defers lang to acl-add/page reload",
    ),
    (
        "views/stream/stream/acl-add.html",
        "window.refreshStreamAclAddFormI18n",
        "stream ACL add defers lang to edit open layers",
    ),
    (
        "views/site/cert/addform.html",
        "window.refreshCertAddFormI18n",
        "cert add partial defers lang to cert list open layers",
    ),
    (
        "views/site/site/addform.html",
        "window.refreshSiteAddFormI18n",
        "site add partial defers lang to site list open layers",
    ),
    (
        "views/stream/stream/addform.html",
        "window.refreshStreamAddFormI18n",
        "stream add partial defers lang to stream list open layers",
    ),
    (
        "views/site/cc/rulelist-add.html",
        "window.refreshCcRulelistAddI18n",
        "CC rulelist partial defers lang to rule page open layers",
    ),
    (
        "views/site/cc/matchlist-add.html",
        "window.refreshCcMatchlistAddI18n",
        "CC matchlist partial defers lang to rule page open layers",
    ),
    (
        "views/site/cert/dnsapi-add.html",
        "if (!popup) return null",
        "DNS API add form root scoped to node-add popup",
    ),
    (
        "views/site/cert/dnsapi-add.html",
        "window.refreshDnsApiAddFormI18n",
        "DNS API add defers lang to dnsapi page open layer",
    ),
    (
        "views/node/dns/index.html",
        "function nodeDnsApiAddShell()",
        "node dns select(dns) disambiguates cert DNS API popup shell",
    ),
    (
        "views/node/dns/index.html",
        "data.elem.getAttribute('name') !== 'dns'",
        "node dns select handler ignores cert DNS API type select",
    ),
    (
        "views/system/user/addform.html",
        "getElementById('LAY-popup-node-add')",
        "shell profile form scoped to node-add popup",
    ),
    (
        "views/site/site/update-cname-mode.html",
        "querySelector('#site_cname_mode')",
        "site cname mode batch partial shell marker",
    ),
    (
        "views/stream/stream/update-cname-mode.html",
        "querySelector('#stream_cname_mode')",
        "stream cname mode batch partial shell marker",
    ),
    (
        "views/site/site/update-state.html",
        "querySelector('#site_state')",
        "site batch state partial shell marker",
    ),
    (
        "views/stream/stream/update-state.html",
        "querySelector('#stream_state')",
        "stream batch state partial shell marker",
    ),
    (
        "views/site/group/addform.html",
        "window.refreshSiteGroupAddFormI18n",
        "site group add defers lang to group list open layer",
    ),
)


def read_member(tf: tarfile.TarFile, rel: str) -> str | None:
    name = PREFIX + rel
    try:
        member = tf.getmember(name)
    except KeyError:
        return None
    if not member.isfile():
        return None
    return tf.extractfile(member).read().decode("utf-8", "replace")


def main() -> int:
    if not os.path.isfile(TAR):
        print(f"audit-panel-tar-i18n-spot: missing {TAR}", file=sys.stderr)
        return 1
    bad: list[str] = []
    with tarfile.open(TAR) as tf:
        for rel, needle, label in SPOTS:
            text = read_member(tf, rel)
            if text is None:
                bad.append(f"{rel}: not in tar ({label})")
                continue
            if needle not in text:
                bad.append(f"{rel}: missing {needle!r} ({label})")
    if bad:
        print("audit-panel-tar-i18n-spot: failed", file=sys.stderr)
        for line in bad:
            print(" ", line, file=sys.stderr)
        return 1
    print("audit-panel-tar-i18n-spot: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())