#!/usr/bin/env python3
"""Pages with *Alive / *StillHere should guard table.on toolbar/tool handlers."""
import os
import re
import sys

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


def guard_names(text: str) -> list[str]:
    names = re.findall(r"function (\w+(?:Alive|StillHere))\s*\(", text)
    for m in re.finditer(r"veikorLocalBatch\.install\([^,]+,\s*(\w+)\s*\)", text):
        names.append(m.group(1))
    if re.search(r"function thisUpgrade\s*\(", text):
        names.append("thisUpgrade")
    return list(dict.fromkeys(names))


def handler_body(text: str, start: int) -> str:
    fn = text.find("function", start)
    if fn < 0:
        return ""
    brace = text.find("{", fn)
    if brace < 0:
        return ""
    return text[brace + 1 : brace + 401]


def main() -> int:
    issues: list[tuple[str, int, str]] = []
    pat = re.compile(r"table\.on\(\s*['\"]tool(?:bar)?")
    for dirpath, _, files in os.walk(VIEWS):
        for fn in files:
            if not fn.endswith(".html"):
                continue
            path = os.path.join(dirpath, fn)
            text = open(path, encoding="utf-8", errors="replace").read()
            guards = guard_names(text)
            if not guards:
                continue
            for m in pat.finditer(text):
                body = handler_body(text, m.end())
                if not any(g + "(" in body for g in guards):
                    line = text[: m.start()].count("\n") + 1
                    kind = "toolbar" if "toolbar" in m.group() else "tool"
                    issues.append((os.path.relpath(path, VIEWS), line, kind))
    if issues:
        print("=== table toolbar/tool guard gaps ===")
        for rel, line, kind in sorted(set(issues)):
            print(f"  {rel}:{line} table.on({kind})")
        print("count", len(set(issues)))
        return 1
    print("=== table toolbar/tool guards OK ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())