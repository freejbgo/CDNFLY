#!/usr/bin/env python3
"""Ensure multi-tab views get hidden-pane form control bootstrap in veikor-page.js."""
import re
import subprocess
import sys

ROOT = "/workspace"
TAR = f"{ROOT}/cdnfly/cdnfly-master-v5.1.13-centos-7.tar.gz"
VIEWS_PREFIX = "cdnfly-master-v5.1.13/master/panel/src/views/"
PAGE_JS = "cdnfly-master-v5.1.13/master/panel/src/lib/veikor-page.js"

CTRL_RE = re.compile(
    r'<input[^>]+type=["\'](?:checkbox|radio)["\']|lay-skin=["\'](?:switch|primary)',
    re.I,
)


def tar_cat(path: str) -> str:
    proc = subprocess.run(
        ["tar", "-xOf", TAR, path],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        print(f"audit-panel-tab-form-skins: failed to read {path}", file=sys.stderr)
        sys.exit(1)
    return proc.stdout


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
    page = tar_cat(PAGE_JS)
    if "bootstrapLayuiTabFormControls" not in page:
        print("audit-panel-tab-form-skins: veikor-page.js missing bootstrapLayuiTabFormControls")
        return 1
    if "veikorBootstrapLayuiTabFormControls" not in page:
        print("audit-panel-tab-form-skins: must export veikorBootstrapLayuiTabFormControls")
        return 1

    multi = []
    for path in list_view_paths():
        text = tar_cat(path)
        items = len(re.findall(r'class=["\'][^"\']*layui-tab-item', text))
        if items < 2:
            continue
        if not CTRL_RE.search(text):
            continue
        multi.append(path.replace(VIEWS_PREFIX, ""))

    if not multi:
        print("audit-panel-tab-form-skins: ok (no multi-tab control views)")
        return 0

    print(
        "audit-panel-tab-form-skins: ok "
        f"(global tab bootstrap; {len(multi)} multi-tab view(s) with controls)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())