#!/usr/bin/env python3
"""Flag list views that resolve page root via header.nextElementSibling without veikorMarkerPageFluid."""
import re
import subprocess
import sys

ROOT = "/workspace"
TAR = f"{ROOT}/cdnfly/cdnfly-master-v5.1.13-centos-7.tar.gz"
VIEWS_PREFIX = "cdnfly-master-v5.1.13/master/panel/src/views/"

FRAGILE = re.compile(
    r"header\.nextElementSibling[\s\S]{0,120}?layui-fluid",
    re.MULTILINE,
)
HAS_HELPER = re.compile(r"veikorMarkerPageFluid\s*\(")


def tar_cat(path: str) -> str:
    proc = subprocess.run(
        ["tar", "-xOf", TAR, path],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        return ""


def list_view_paths() -> list[str]:
    proc = subprocess.run(
        ["tar", "-tzf", TAR],
        capture_output=True,
        text=True,
        check=True,
    )
    out = []
    for line in proc.stdout.splitlines():
        if line.startswith(VIEWS_PREFIX) and line.endswith(".html"):
            out.append(line)
    return out


def main() -> int:
    offenders = []
    for path in list_view_paths():
        text = tar_cat(path)
        if not text or not FRAGILE.search(text):
            continue
        if HAS_HELPER.search(text):
            continue
        offenders.append(path[len(VIEWS_PREFIX) :])
    if offenders:
        print("audit-panel-page-fluid-sibling: fragile page root (no veikorMarkerPageFluid):")
        for p in sorted(offenders):
            print("  ", p)
        return 1
    print("audit-panel-page-fluid-sibling: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())