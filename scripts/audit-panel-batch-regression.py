#!/usr/bin/env python3
"""Regression checks for Veikor cross-page table bulk (CheckedMap / veikorLocalBatch)."""
import os
import re
import sys
import tarfile

ROOT = os.path.join(
    os.path.dirname(__file__),
    "..",
)
PANEL = os.path.join(
    ROOT,
    ".veikor-build",
    "cdnfly-master-v5.1.13",
    "master",
    "panel",
    "src",
)
VIEWS = os.path.join(PANEL, "views")
TAR = os.path.join(ROOT, "cdnfly", "cdnfly-master-v5.1.13-centos-7.tar.gz")
PREFIX = "cdnfly-master-v5.1.13/master/panel/src/"

FAILURES = []


def fail(msg):
    FAILURES.append(msg)


def cross_page_helpers(text):
    return any(
        x in text
        for x in (
            "CheckedMap",
            "veikorLocalBatch",
            "vekorCollect",
            "collectChecked",
            "IdsForBatch",
        )
    )


def scan_views():
    for dirpath, _, files in os.walk(VIEWS):
        for fn in files:
            if not fn.endswith(".html"):
                continue
            rel = os.path.relpath(os.path.join(dirpath, fn), VIEWS)
            if rel.startswith("user/"):
                continue
            text = open(os.path.join(dirpath, fn), encoding="utf-8", errors="replace").read()

            if re.search(r"if \(!table_data\[i\]\['LAY_CHECKED'\]", text):
                fail(f"{rel}: legacy LAY_CHECKED delete filter still present")

            if re.search(r"type:\s*['\"]checkbox['\"]", text) and re.search(
                r",page:\s*true", text
            ):
                if cross_page_helpers(text) and "limits:" in text:
                    if not re.search(r"limits:\s*\[[^\]]*500", text):
                        fail(f"{rel}: paged bulk table missing limits 500 option")

            if "table.on('toolbar" in text or 'table.on("toolbar' in text:
                for m in re.finditer(
                    r"table\.on\(['\"]toolbar[^)]+\),[\s\S]{0,1600}?switch\s*\(\s*obj\.event\s*\)",
                    text,
                ):
                    block = m.group(0)
                    if "checkStatus.data" not in block:
                        continue
                    if cross_page_helpers(block):
                        continue
                    fail(f"{rel}: toolbar handler uses checkStatus.data without bulk helper")


def scan_index_preload():
    index_path = os.path.join(PANEL, "index.js")
    text = open(index_path, encoding="utf-8", errors="replace").read()
    if "define(['setter', 'admin', 'veikorLocalBatch']" not in text:
        fail("index.js: veikorLocalBatch not preloaded in main define()")


# A new search or filter is a different result set. Cross-page ids from the previous query must not stay selected.
FILTER_CLEARS = {
    "views/site/site/index.html": "__veikorSiteListCheckedMap = {}",
    "views/node/node/index.html": "__veikorNodeListCheckedMap = {}",
    "views/node/group/index.html": "__veikorNodeGroupListCheckedMap = {}",
    "views/stream/stream/index.html": "__veikorStreamListCheckedMap = {}",
    "views/system/user/index.html": "__veikorSystemUserListCheckedMap = {}",
    "views/system/task/index.html": "__veikorSystemTaskListCheckedMap = {}",
    "views/site/cert/cert.html": "__veikorCertListCheckedMap = {}",
    "views/site/acl/index.html": "__veikorAclListCheckedMap = {}",
    "views/package/sold/index.html": "__veikorSoldPackageListCheckedMap = {}",
    "views/package/basic/index.html": "__veikorBasicPackageListCheckedMap = {}",
    "views/site/monitor/blackip.html": "veikorLocalBatch.clearMap('test-table-toolbar')",
}


def scan_map_reset_on_entry():
    """Opening a list again must drop checks the user can no longer see."""
    if not os.path.isfile(TAR):
        return
    keep_init = re.compile(r"CheckedMap = window\.__veikor\w+CheckedMap \|\| \{\}")
    with tarfile.open(TAR) as tf:
        for member in tf.getmembers():
            if not member.name.startswith(PREFIX) or not member.name.endswith(".html"):
                continue
            text = tf.extractfile(member).read().decode("utf-8", "replace")
            rel = member.name[len(PREFIX):]
            if keep_init.search(text) or "window[mapKey] = window[mapKey] || {}" in text:
                fail(f"{rel}: page entry keeps the previous visit's checked ids")
    with tarfile.open(TAR) as tf:
        task = tf.extractfile(PREFIX + "views/system/task/index.html")
        batch = tf.extractfile(PREFIX + "views/site/site/update_form.html")
        task_text = "" if task is None else task.read().decode("utf-8", "replace")
        if "window.__veikorSystemTaskListCheckedMap = {};\n              table.reload('test-table-toolbar')" not in task_text or "window.__veikorSystemTaskListCheckedMap = {};\n      table.reload('test-table-toolbar')" not in task_text:
            fail("task list reload keeps checks that the refresh cleared on screen")
        if batch is None or "window.__veikorSiteListCheckedMap = {};\n            layui.table.reload('test-table-toolbar')" not in batch.read().decode("utf-8", "replace"):
            fail("batch site update reloads the list without dropping the previous checks")
        for rel in (
            "views/site/site/index.html",
            "views/site/cert/cert.html",
            "views/stream/stream/index.html",
            "views/package/sold/index.html",
        ):
            member = tf.extractfile(PREFIX + rel)
            body = "" if member is None else member.read().decode("utf-8", "replace")
            if 'closest("form").find("button.search").first().trigger("click")' not in body:
                fail(rel + ": reset clears the form and leaves the previous filter on the list")
        line_page = tf.extractfile(PREFIX + "views/node/group/line.html")
        line_text = "" if line_page is None else line_page.read().decode("utf-8", "replace")
        if "encodeURIComponent(search == null ? '' : search)" not in line_text:
            fail("line search puts the typed text into the query without encoding")


def scan_shared_table_map():
    if not os.path.isfile(TAR):
        return
    name = PREFIX + "lib/veikor-local-batch.js"
    with tarfile.open(TAR) as tf:
        member = tf.extractfile(name)
        if member is None:
            fail("veikor-local-batch.js missing from master package")
            return
        text = member.read().decode("utf-8", "replace")
    if "maps[tableId] = maps[tableId] || {}" in text:
        fail("veikor-local-batch keeps another page's checks on a reused table id")
    if "maps[tableId] = {}" not in text:
        fail("veikor-local-batch does not reset checks when a page installs the table")
    if "bound[tableId].alive" not in text:
        fail("veikor-local-batch checkbox listener does not follow the current page")
    if re.search(r"if \(bound\[tableId\]\) \{[\s\S]{0,80}?return;", text):
        fail("veikor-local-batch does not re-register after another page takes the checkbox event")
    if "var rawReload = table.reload;" not in text or "maps[tableId] = {}" not in text.split("var rawReload = table.reload;", 1)[-1]:
        fail("reloading a client table keeps checks that are no longer shown")
    if "#idx:" in text or "#tc:" in text or "#uri:" in text or "#addr:" in text or "#nv:" in text:
        fail("client row checks use a partial key that collides across rows")
    if "tableId + '#row:'" not in text:
        fail("client row checks do not use the full row")


SEARCH_PAGES = (
    "views/node/node/index.html",
    "views/node/group/index.html",
    "views/system/user/index.html",
    "views/site/acl/index.html",
    "views/site/cert/cert.html",
)


def scan_layui_keeps_handlers():
    """Tab switch does not re-run the view script. layui 2.5.5 used to keep only the last callback."""
    if not os.path.isfile(TAR):
        return
    layui_name = "cdnfly-master-v5.1.13/master/panel/console/layui/layui.js"
    with tarfile.open(TAR) as tf:
        member = tf.extractfile(layui_name)
        if member is None:
            fail("layui.js missing from master package")
            return
        js = member.read().decode("utf-8", "replace")
        for rel in SEARCH_PAGES:
            page = tf.extractfile(PREFIX + rel)
            if page is None:
                fail(f"{rel}: missing from master package")
                continue
            text = page.read().decode("utf-8", "replace")
            if "function search (" in text:
                fail(f"{rel}: search() replaces the other pages' search")
            if "__veikorPageSearch" not in text:
                fail(f"{rel}: search is not registered for tab switch")
    if "o.event[l][s]=[r]" in js:
        fail("layui keeps only the last table/form callback, so switching tabs drops the page's handlers")
    if "a[i].toString()===s" not in js:
        fail("layui does not keep a distinct callback per page")


def scan_filter_clears():
    if not os.path.isfile(TAR):
        return
    with tarfile.open(TAR) as tf:
        for rel, marker in FILTER_CLEARS.items():
            name = PREFIX + rel
            member = tf.extractfile(name)
            if member is None:
                fail(f"{rel}: missing from master package")
                continue
            text = member.read().decode("utf-8", "replace")
            if marker not in text:
                fail(f"{rel}: filter reload does not clear cross-page selection")
                continue
            for m in re.finditer(r"table\.reload\(\s*['\"]test-table-toolbar['\"][\s\S]{0,220}?where\s*:", text):
                before = text[max(0, m.start() - 220) : m.start()]
                if marker not in before:
                    line = text[: m.start()].count("\n") + 1
                    fail(f"{rel}:{line}: filtered reload keeps the previous checked ids")


def scan_tar_drift():
    if not os.path.isfile(TAR) or not os.path.isdir(PANEL):
        return
    drift = 0
    with tarfile.open(TAR) as tf:
        for member in tf.getmembers():
            if not member.name.startswith(PREFIX) or member.isdir():
                continue
            rel = member.name[len(PREFIX) :]
            local = os.path.join(PANEL, rel)
            if not os.path.isfile(local):
                continue
            tb = tf.extractfile(member).read()
            lb = open(local, "rb").read()
            if tb != lb:
                drift += 1
    if drift:
        fail(f"published tar: {drift} panel file(s) differ from .veikor-build (run sync-panel-to-master-tar.sh)")


def main():
    if os.path.isdir(VIEWS) and os.path.isfile(os.path.join(PANEL, "index.js")):
        scan_views()
        scan_index_preload()
    else:
        print("panel tree absent, skipped local view scan")
    import subprocess

    for script_name in (
        "audit-panel-res-data-shape.py",
        "audit-panel-req-response.py",
        "audit-panel-fail-guards.py",
        "audit-panel-toolbar-guards.py",
    ):
        script = os.path.join(os.path.dirname(__file__), script_name)
        if not os.path.isfile(script):
            continue
        r = subprocess.run([sys.executable, script], capture_output=True, text=True)
        print(r.stdout.rstrip())
        if r.returncode != 0:
            if r.stderr:
                print(r.stderr.rstrip())
            fail(script_name)
    scan_map_reset_on_entry()
    scan_shared_table_map()
    scan_layui_keeps_handlers()
    scan_filter_clears()
    scan_tar_drift()
    if FAILURES:
        print("=== batch regression FAILED ===")
        for f in FAILURES:
            print(f)
        print(f"total {len(FAILURES)}")
        sys.exit(1)
    print("=== batch regression OK ===")


if __name__ == "__main__":
    main()