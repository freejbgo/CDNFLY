#!/usr/bin/env python3
"""Insert *Alive() guard at layer.confirm callbacks that call admin.req."""
import os
import re
from collections import Counter

VIEWS = os.path.join(
    os.path.dirname(__file__),
    "..",
    ".veikor-build",
    "cdnfly-master-v5.1.13",
    "master",
    "panel",
    "src",
    "views",
)


def primary_alive(text: str) -> str | None:
    defs = re.findall(r"function (\w+Alive)\s*\(", text)
    if not defs:
        return None
    uses = Counter(re.findall(r"(\w+Alive)\s*\(", text))
    for name in defs:
        uses.setdefault(name, 0)
    return max(defs, key=lambda n: (uses[n], -defs.index(n)))


def patch_text(text: str, guard: str) -> tuple[str, int]:
    needle = f"if (!{guard}())"
    inserts = 0

    def repl(m):
        nonlocal inserts
        lead = m.group(2)
        tail = m.string[m.end() : m.end() + 500]
        body = lead + tail
        if needle in body[:200]:
            return m.group(0)
        if "admin.req" not in body and "$.ajax" not in body:
            return m.group(0)
        line_indent = re.match(r"([ \t]*)", lead or tail).group(1) or "            "
        guard_line = f"{line_indent}if (!{guard}()) {{ layer.close(index); return; }}\n"
        inserts += 1
        return m.group(1) + lead + guard_line

    pat = re.compile(
        r"(layer\.confirm\([^;]{5,500}?,\s*function\s*\(\s*index[^)]*\)\s*\{)(\s*)",
        re.DOTALL,
    )
    new_text = pat.sub(repl, text)
    return new_text, inserts


def main():
    total = 0
    for dirpath, _, files in os.walk(VIEWS):
        for fn in files:
            if not fn.endswith(".html"):
                continue
            path = os.path.join(dirpath, fn)
            text = open(path, encoding="utf-8", errors="replace").read()
            guard = primary_alive(text)
            if not guard:
                continue
            new_text, n = patch_text(text, guard)
            if n:
                open(path, "w", encoding="utf-8").write(new_text)
                rel = os.path.relpath(path, VIEWS)
                print(f"{rel}: +{n} confirm guard(s)")
                total += n
    print("total inserts", total)


if __name__ == "__main__":
    main()