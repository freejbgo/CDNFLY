#!/usr/bin/env python3
"""Site ACL add popup must not reuse stream edit table id acllist."""
import subprocess
import sys

ROOT = "/workspace"
TAR = f"{ROOT}/cdnfly/cdnfly-master-v5.1.13-centos-7.tar.gz"
ACL_ADD = "cdnfly-master-v5.1.13/master/panel/src/views/site/acl/acl-add.html"


def tar_cat(path: str) -> str:
    proc = subprocess.run(
        ["tar", "-xOf", TAR, path],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        print(f"audit-panel-site-acl-rulelist-id: missing {path}", file=sys.stderr)
        return ""
    return proc.stdout


def main() -> int:
    text = tar_cat(ACL_ADD)
    if 'id="acllist"' in text or "lay-filter=\"acllist\"" in text:
        print("audit-panel-site-acl-rulelist-id: site/acl/acl-add.html still uses id=acllist")
        return 1
    if "site-acl-add-rulelist" not in text:
        print("audit-panel-site-acl-rulelist-id: expected site-acl-add-rulelist table id")
        return 1
    print("audit-panel-site-acl-rulelist-id: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())