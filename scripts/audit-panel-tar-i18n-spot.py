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
        "views/stream/stream/index.html",
        "refreshStreamListOpenLayers",
        "stream list nested popup titles",
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
        "views/site/cert/cert.html",
        "veikorSyncLayuiSelectTitles",
        "cert list search lang sync selects",
    ),
    (
        "views/site/site/edit.html",
        "veikorSyncLayuiSelectTitles",
        "site edit lang refresh sync selects",
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
        "veikorSyncLayuiSelectTitles(popRoot)",
        "site edit nested popup select sync after prefill",
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
        "veikorSyncLayuiSelectTitles(filterPopRoot)",
        "CC filter edit popup select sync after prefill",
    ),
    (
        "views/site/cc/rule-add.html",
        "veikorSyncLayuiSelectTitles(root)",
        "CC rulelist edit popup select sync after prefill",
    ),
    (
        "views/site/acl/acl-add.html",
        "window.refreshRuleMatchFormI18n",
        "ACL rule add/edit nested popup refresh after prefill",
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
        "refreshStreamAclAddFormI18n",
        "stream edit ACL rule popup refresh after prefill",
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
        "veikorSyncLayuiSelectTitles",
        "login log search lang sync selects",
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