#!/usr/bin/env python3
"""Ensure console layui.config.version matches panel setter.version in tarball."""
import re
import subprocess
import sys

ROOT = "/workspace"
TAR = f"{ROOT}/cdnfly/cdnfly-master-v5.1.13-centos-7.tar.gz"
CONFIG_PATH = "cdnfly-master-v5.1.13/master/panel/src/config.js"
CONSOLE_PATH = "cdnfly-master-v5.1.13/master/panel/console/index.html"
VIEW_PATH = "cdnfly-master-v5.1.13/master/panel/src/lib/view.js"


def tar_cat(path: str) -> str:
    proc = subprocess.run(
        ["tar", "-xOf", TAR, path],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        print(f"audit-panel-cache-version: failed to read {path}", file=sys.stderr)
        sys.exit(1)
    return proc.stdout


def main() -> int:
    config = tar_cat(CONFIG_PATH)
    console = tar_cat(CONSOLE_PATH)
    view = tar_cat(VIEW_PATH)

    m = re.search(r",version:\s*'([^']+)'", config)
    if not m:
        print("audit-panel-cache-version: missing setter.version in config.js")
        return 1
    panel_ver = m.group(1)
    cm = re.search(r",version:\s*'([^']+)'", console)
    if not cm or cm.group(1) != panel_ver:
        print(
            "audit-panel-cache-version: console index layui.config.version "
            f"mismatch (config {panel_ver!r}, console {cm.group(1) if cm else None!r})"
        )
        return 1

    if "layui.setter && layui.setter.version" not in view:
        print("audit-panel-cache-version: view.js must bust templates with setter.version")
        return 1

    index = tar_cat("cdnfly-master-v5.1.13/master/panel/src/index.js")
    if "setter.version || admin.v" not in index and "setter.version" not in index:
        print("audit-panel-cache-version: index.js should bust admin.css with setter.version")
        return 1

    layout = tar_cat("cdnfly-master-v5.1.13/master/panel/src/views/layout.html")
    if "veikor-theme.css?v={{ layui.setter.version }}" not in layout:
        print("audit-panel-cache-version: layout theme css must use setter.version")
        return 1

    print("audit-panel-cache-version: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())