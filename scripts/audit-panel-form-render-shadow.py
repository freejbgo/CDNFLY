#!/usr/bin/env python3
"""Fail if inline views shadow layui.form with DOM `var form = *FormEl()` then call form.render."""
import re
import sys
import tarfile

TAR = "cdnfly/cdnfly-master-v5.1.13-centos-7.tar.gz"
PREFIX = "cdnfly-master-v5.1.13/master/panel/src/views/"

pat_fn = re.compile(r"function\s+\w+\s*\([^)]*\)\s*\{", re.M)
pat_shadow = re.compile(r"var\s+form\s*=\s*\w+(?:Search)?FormEl\(\)")
pat_bad = re.compile(r"(?<![\w.])form\.render\(")


def fn_body(text, start):
    j = start
    depth = 1
    while j < len(text) and depth:
        if text[j] == "{":
            depth += 1
        elif text[j] == "}":
            depth -= 1
        j += 1
    return text[start : j - 1]


def audit_html(name: str, text: str) -> list[str]:
    issues = []
    i = 0
    while i < len(text):
        m = pat_fn.search(text, i)
        if not m:
            break
        body = fn_body(text, m.end())
        if pat_shadow.search(body) and pat_bad.search(body):
            fn = re.search(r"function\s+(\w+)", m.group()).group(1)
            issues.append(f"{name}: {fn} shadows layui.form with DOM form")
        i = m.end() + len(body) + 1
    return issues


def main() -> int:
    bad = []
    with tarfile.open(TAR, "r:gz") as tf:
        for mi in tf.getmembers():
            if not mi.name.startswith(PREFIX) or not mi.name.endswith(".html"):
                continue
            raw = tf.extractfile(mi).read().decode("utf-8", errors="replace")
            rel = mi.name[len(PREFIX) :]
            bad.extend(audit_html(rel, raw))
    if bad:
        print("audit-panel-form-render-shadow: FAIL", file=sys.stderr)
        for line in bad:
            print(" ", line, file=sys.stderr)
        return 1
    print("audit-panel-form-render-shadow: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())