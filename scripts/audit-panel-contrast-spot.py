#!/usr/bin/env python3
"""Heuristic: light shell must override admin.css dark chrome text colors."""
import re
import subprocess
import sys

TAR = "/workspace/cdnfly/cdnfly-master-v5.1.13-centos-7.tar.gz"
THEME = "cdnfly-master-v5.1.13/master/panel/src/style/veikor-theme.css"
ADMIN = "cdnfly-master-v5.1.13/master/panel/src/style/admin.css"


def tar_cat(path: str) -> str:
    proc = subprocess.run(
        ["tar", "-xOf", TAR, path],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        print(f"audit-panel-contrast-spot: missing {path}", file=sys.stderr)
        sys.exit(1)
    return proc.stdout


def main() -> int:
    theme = tar_cat(THEME)
    admin = tar_cat(ADMIN)
    required = [
        "layui-layout-left",
        "layui-layout-right",
        "layui-layer-setwin",
        "select2-selection__clear",
        ".layui-table-tool",
        "layadmin-tabs-control",
        "layui-tab-close",
        "layui-layer-btn0",
        "layui-icon[close]",
    ]
    for needle in required:
        if needle not in theme:
            print(f"audit-panel-contrast-spot: veikor-theme missing {needle!r}")
            return 1
    # admin still documents white logo link; theme must beat it
    if re.search(r"\.layui-logo a\{color:\s*#fff", admin.replace(" ", "")):
        if "#06172a" not in theme:
            print("audit-panel-contrast-spot: no logo contrast override")
            return 1
    print("audit-panel-contrast-spot: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())