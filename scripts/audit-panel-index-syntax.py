#!/usr/bin/env python3
"""Ensure panel index.js inside the tarball is valid JavaScript."""
import subprocess
import sys
import tempfile
import os

ROOT = "/workspace"
TAR = f"{ROOT}/cdnfly/cdnfly-master-v5.1.13-centos-7.tar.gz"
PATH_IN_TAR = "cdnfly-master-v5.1.13/master/panel/src/index.js"


def main() -> int:
    proc = subprocess.run(
        ["tar", "-xOf", TAR, PATH_IN_TAR],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        print("audit-panel-index-syntax: failed to read index.js", file=sys.stderr)
        return 1
    with tempfile.NamedTemporaryFile(mode="w", suffix=".js", delete=False) as f:
        f.write(proc.stdout)
        path = f.name
    try:
        check = subprocess.run(
            ["node", "--check", path],
            capture_output=True,
            text=True,
        )
    finally:
        os.unlink(path)
    if check.returncode != 0:
        print("audit-panel-index-syntax: failed")
        if check.stderr:
            print(check.stderr.strip(), file=sys.stderr)
        return 1
    print("audit-panel-index-syntax: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())