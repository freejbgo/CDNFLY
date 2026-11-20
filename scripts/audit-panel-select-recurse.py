#!/usr/bin/env python3
"""Guard against refreshSelectElement self-recursion in panel tarball."""
import re
import subprocess
import sys

ROOT = "/workspace"
TAR = f"{ROOT}/cdnfly/cdnfly-master-v5.1.13-centos-7.tar.gz"
PATH_IN_TAR = "cdnfly-master-v5.1.13/master/panel/src/lib/veikor-page.js"
CONFIG_IN_TAR = "cdnfly-master-v5.1.13/master/panel/src/config.js"


def tar_cat(path: str) -> str:
    proc = subprocess.run(
        ["tar", "-xOf", TAR, path],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        print(f"audit-panel-select-recurse: failed to read {path}", file=sys.stderr)
        sys.exit(1)
    return proc.stdout


text = tar_cat(PATH_IN_TAR)
config = tar_cat(CONFIG_IN_TAR)
# Dangerous: recursive call on sibling after isolated render
if re.search(r"refreshSelectElement\s*\(\s*o\.el\s*\)", text):
    print("audit-panel-select-recurse: failed (recursive refreshSelectElement(o.el))")
    sys.exit(1)

if "refreshSelectElementNoCascade" in text:
    print("audit-panel-select-recurse: failed (removed helper should not exist)")
    sys.exit(1)

build_m = re.search(r"PANEL_FORM_SKIN_BUILD\s*=\s*'(\d{8}-\d+)'", text)
if not build_m:
    print("audit-panel-select-recurse: failed (missing PANEL_FORM_SKIN_BUILD stamp)")
    sys.exit(1)
ver_m = re.search(r",version:\s*'[^']*-panel(\d+)'", config)
if ver_m and not build_m.group(1).endswith("-" + ver_m.group(1)):
    print(
        "audit-panel-select-recurse: failed (PANEL_FORM_SKIN_BUILD "
        f"{build_m.group(1)!r} != config panel{ver_m.group(1)})"
    )
    sys.exit(1)

if "__veikorSelectRenderGuard" not in text:
    print("audit-panel-select-recurse: failed (missing form.render select guard)")
    sys.exit(1)

if "veikorScheduleFormBootstrap" not in text:
    print("audit-panel-select-recurse: failed (missing veikorScheduleFormBootstrap)")
    sys.exit(1)

if "veikorReinitSelect2InScope" not in text:
    print("audit-panel-select-recurse: failed (missing select2 tab hook)")
    sys.exit(1)

print("audit-panel-select-recurse: ok")