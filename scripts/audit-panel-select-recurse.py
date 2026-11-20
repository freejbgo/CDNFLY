#!/usr/bin/env python3
"""Guard against refreshSelectElement self-recursion in panel tarball."""
import re
import subprocess
import sys

ROOT = "/workspace"
TAR = f"{ROOT}/cdnfly/cdnfly-master-v5.1.13-centos-7.tar.gz"
PATH_IN_TAR = "cdnfly-master-v5.1.13/master/panel/src/lib/veikor-page.js"

proc = subprocess.run(
    ["tar", "-xOf", TAR, PATH_IN_TAR],
    capture_output=True,
    text=True,
    check=False,
)
if proc.returncode != 0:
    print("audit-panel-select-recurse: failed to read tarball", file=sys.stderr)
    sys.exit(1)

text = proc.stdout
# Dangerous: recursive call on sibling after isolated render
if re.search(r"refreshSelectElement\s*\(\s*o\.el\s*\)", text):
    print("audit-panel-select-recurse: failed (recursive refreshSelectElement(o.el))")
    sys.exit(1)

if "refreshSelectElementNoCascade" in text:
    print("audit-panel-select-recurse: failed (removed helper should not exist)")
    sys.exit(1)

if "PANEL_FORM_SKIN_BUILD" not in text or "20251120-532" not in text:
    print("audit-panel-select-recurse: failed (missing PANEL_FORM_SKIN_BUILD stamp)")
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