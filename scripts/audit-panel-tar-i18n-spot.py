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