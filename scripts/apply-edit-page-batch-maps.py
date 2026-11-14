#!/usr/bin/env python3
"""Cross-page bulk for edit/wizard embedded tables + small list pages."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1] / ".veikor-build/cdnfly-master-v5.1.13/master/panel/src/views"

LIMITS = ",limits: [10,20,50,100,200,500]"

SERVER_FILES = [
    ("site/cert/dnsapi.html", "__veikorDnsApiListCheckedMap", "DnsApiList", "dnsApiPageAlive", "reloadDnsApiTable"),
]

LOCAL_FILES = [
    ("site/site/edit.html", "siteEditAlive", ["backend", "url-ratelimit", "cache", "req_header", "resp_header", "url_rewrite"], "['admin', 'table','form', 'veikorLocalBatch']", "function siteEditAlive"),
    ("site/site/update_form.html", "function() { return !!document.getElementById('LAY-popup-site-update'); }", ["batch-cache", "api-protect", "batch-req-header", "batch-url-rewrite", "batch-resp-header"], "['admin', 'veikorLocalBatch']", "function renderSiteUpdatePopupForms"),
    ("stream/stream/edit.html", "streamEditAlive", ["backend", "acllist"], "['admin', 'table','form', 'veikorLocalBatch']", "function streamEditAlive"),
    ("config/default/index.html", "defaultCacheStillHere", ["cache"], "['admin', 'table','form', 'veikorLocalBatch']", "function defaultCacheStillHere"),
]

POPUP_TABLE_FILES = [
    ("site/acl/acl-add.html", "acllist", "function() { return !!(document.getElementById('acllist') && document.getElementById('acllist').closest('.layui-table-view')); }"),
    ("site/cc/rule-add.html", "rulelist", "function() { return !!document.getElementById('rulelist'); }"),
    ("site/cc/match-add.html", "matchlist", "function() { return !!document.getElementById('matchlist'); }"),
]

ROW_PICKER_FILES = [
    ("system/update/index.html", "masterUpgradeAlive", "test-table-toolbar", "['admin', 'table', 'veikorLocalBatch']", "function masterUpgradeAlive"),
    ("site/monitor/blackip.html", "blackipAlive", "test-table-toolbar", "['admin', 'table', 'veikorLocalBatch']", "function blackipAlive"),
]

HELPER_SERVER = """
    var VEIKOR_LIST_TABLE_ID = 'test-table-toolbar';
    window.{map_key} = window.{map_key} || {{}};

    table.on('checkbox(' + VEIKOR_LIST_TABLE_ID + ')', function(obj) {{
      if (!{alive}()) return;
      var map = window.{map_key};
      if (obj.type === 'all') {{
        var cache = table.cache[VEIKOR_LIST_TABLE_ID] || [];
        for (var ci = 0; ci < cache.length; ci++) {{
          var row = cache[ci];
          if (!row || row.id == null) continue;
          if (obj.checked) map[row.id] = 1;
          else delete map[row.id];
        }}
        return;
      }}
      var id = obj.data && obj.data.id;
      if (id == null) return;
      if (obj.checked) map[id] = 1;
      else delete map[id];
    }});

    function collectChecked{prefix}Ids(fallbackRows) {{
      var data = fallbackRows;
      if (!data || !data.length) {{
        data = (table.checkStatus(VEIKOR_LIST_TABLE_ID).data) || [];
      }}
      var map = window.{map_key} || {{}};
      var ids = [];
      var seen = {{}};
      for (var i = 0; i < data.length; i++) {{
        if (data[i] && data[i].id != null) {{
          ids.push(data[i].id);
          seen[data[i].id] = 1;
        }}
      }}
      for (var k in map) {{
        if (!Object.prototype.hasOwnProperty.call(map, k)) continue;
        if (!seen[k]) ids.push(isNaN(+k) ? k : +k);
      }}
      return ids;
    }}

    function assign{prefix}IdsForBatch(checkStatus) {{
      return collectChecked{prefix}Ids(checkStatus && checkStatus.data);
    }}

"""


def add_limits(text):
    return re.sub(
        r",page: true\n(\s*)(\}\);)",
        lambda m: ",page: true\n      " + LIMITS + "\n" + m.group(1) + m.group(2)
        if "limits:" not in m.group(0)
        else m.group(0),
        text,
    )


def patch_local(rel, alive_expr, table_ids, use_list, insert_anchor):
    path = ROOT / rel
    text = path.read_text(encoding="utf-8")
    if "veikorLocalBatch.install" in text:
        print("skip local", rel)
        return

    text = re.sub(
        r"layui\.use\(\[[^\]]+\],\s*function\(\)",
        f"layui.use({use_list}, function()",
        text,
        count=1,
    )

    install_block = "    var veikorLocalBatch = layui.veikorLocalBatch;\n"
    for tid in table_ids:
        install_block += f"    veikorLocalBatch.install('{tid}', {alive_expr});\n"

    idx = text.find(insert_anchor)
    if idx == -1:
        print("no anchor", rel, insert_anchor)
        return
    text = text[:idx] + install_block + text[idx:]

    text = re.sub(
        r"var data = checkStatus\.data;\s*\n\s*if \(data\.length == 0\)",
        "if (!layui.veikorLocalBatch.hasSelection(obj.config.id, checkStatus))",
        text,
    )
    text = re.sub(
        r"var site_data = checkStatus\.data;\s*\n\s*if \(site_data\.length == 0\)",
        "if (!layui.veikorLocalBatch.hasSelection(obj.config.id, checkStatus))",
        text,
    )
    text = re.sub(
        r"var (\w+) = \[\]\s*\n\s*for \(i in table_data\) \{\s*\n\s*if \(!table_data\[i\]\['LAY_CHECKED'\]\) \{\s*\n\s*\1\.push\(table_data\[i\]\)\s*\n\s*\}\s*\n\s*\}",
        r"var \1 = layui.veikorLocalBatch.filterKeepingUnselected(obj.config.id, table_data, checkStatus)",
        text,
    )
    text = add_limits(text)
    path.write_text(text, encoding="utf-8")
    print("patched local", rel)


def patch_row_picker(rel, alive_expr, table_id, use_list, insert_anchor):
    path = ROOT / rel
    text = path.read_text(encoding="utf-8")
    if "veikorLocalBatch.install" in text:
        print("skip row", rel)
        return

    if "layui.use" in text:
        text = re.sub(
            r"layui\.use\(\[[^\]]+\],\s*function\(\)",
            f"layui.use({use_list}, function()",
            text,
            count=1,
        )
    else:
        text = text.replace("<script>", "<script>\nlayui.use(" + use_list + ", function(){", 1)

    install = (
        f"    var veikorLocalBatch = layui.veikorLocalBatch;\n"
        f"    veikorLocalBatch.install('{table_id}', {alive_expr});\n"
    )
    idx = text.find(insert_anchor)
    if idx == -1:
        print("no anchor row", rel)
        return
    text = text[:idx] + install + text[idx:]

  if rel == "site/monitor/blackip.html":
        text = re.sub(
            r"var site_data = checkStatus\.data;\s*\n\s*if \(site_data\.length == 0\)",
            "var site_data = layui.veikorLocalBatch.collectSelectedRows('{table_id}', obj.config.data, checkStatus);\n          if (site_data.length == 0)".format(table_id=table_id),
            text,
        )
    else:
        text = re.sub(
            r"var (site_)?data = checkStatus\.data;\s*\n\s*if \(\1?data\.length == 0\)",
            "var data = layui.veikorLocalBatch.collectSelectedRows('{table_id}', obj.config.data, checkStatus);\n      if (data.length == 0)".format(table_id=table_id),
            text,
        )

    text = add_limits(text)
    path.write_text(text, encoding="utf-8")
    print("patched row", rel)


def patch_server(rel, map_key, prefix, alive, reload_fn):
    path = ROOT / rel
    text = path.read_text(encoding="utf-8")
    if map_key in text:
        print("skip server", rel)
        return

    block = HELPER_SERVER.format(map_key=map_key, alive=alive, prefix=prefix)
    m = re.search(r"\n(\s*)var access_token = layui\.data", text)
    if not m:
        print("no insert", rel)
        return
    text = text[: m.start()] + "\n" + block + text[m.start() :]

    if reload_fn:
        text = text.replace(
            f"function {reload_fn}() {{\n      if (!{alive}()) return;\n      layui.table.reload('test-table-toolbar');",
            f"function {reload_fn}() {{\n      if (!{alive}()) return;\n      window.{map_key} = {{}};\n      layui.table.reload('test-table-toolbar');",
            1,
        )

    delete_block = (
        r"(case 'delete':\s*\n)"
        r"\s*var data = checkStatus\.data;\s*\n"
        r"\s*if \(data\.length == 0\) \{\s*\n"
        r"\s*layer\.alert\('([^']+)'\);\s*\n"
        r"\s*return\s*\n"
        r"\s*\}\s*\n"
        r"\s*req_data = \[\]\s*\n"
        r"\s*for \(i in data\) \{\s*\n"
        r"\s*req_data\.push\(data\[i\]\['id'\]\)\s*\n"
        r"\s*\}\s*\n"
        r"\s*var ids = req_data\.join\(\",\"\)\s*\n"
        r"\s*layer\.confirm\('将删除\('\+ids\+'\)([^']+)，是否继续'"
    )

    def fix_del(m):
        return (
            m.group(1)
            + f"          var batchIds = assign{prefix}IdsForBatch(checkStatus);\n"
            + "          if (batchIds.length == 0) {\n"
            + f"            layer.alert('{m.group(2)}');   \n"
            + "            return\n"
            + "          }\n"
            + '          var idParam = batchIds.join(",")\n'
            + "          var confirmIds = idParam\n"
            + "          if (batchIds.length > 20) {\n"
            + "            confirmIds = '共 ' + batchIds.length + ' 个（' + batchIds.slice(0, 20).join(',') + '…）'\n"
            + "          }\n"
            + f"          layer.confirm('将删除('+confirmIds+'){m.group(3)}，是否继续'"
        )

    text = re.sub(delete_block, fix_del, text)
    text = text.replace("url: '/dnsapis/'+ids", "url: '/dnsapis/'+idParam")
    text = add_limits(text)
    path.write_text(text, encoding="utf-8")
    print("patched server", rel)


def patch_popup_table(rel, table_id, alive_expr):
    path = ROOT / rel
    text = path.read_text(encoding="utf-8")
    if "veikorLocalBatch.install" in text:
        print("skip popup", rel)
        return
    insert = (
        f"  var veikorLocalBatch = layui.veikorLocalBatch;\n"
        f"  veikorLocalBatch.install('{table_id}', {alive_expr});\n\n"
    )
    anchor = "  table.render({"
    idx = text.find(anchor)
    if idx == -1:
        print("no popup anchor", rel)
        return
    text = text[:idx] + insert + text[idx:]
    text = re.sub(
        r"var data = checkStatus\.data;\s*\n\s*if \(data\.length == 0\)",
        "if (!layui.veikorLocalBatch.hasSelection(obj.config.id, checkStatus))",
        text,
    )
    text = re.sub(
        r"var (\w+) = \[\]\s*\n\s*for \(i in table_data\) \{\s*\n\s*if \(!table_data\[i\]\['LAY_CHECKED'\]\) \{\s*\n\s*\1\.push\(table_data\[i\]\)\s*\n\s*\}\s*\n\s*\}",
        r"var \1 = layui.veikorLocalBatch.filterKeepingUnselected(obj.config.id, table_data, checkStatus)",
        text,
    )
    text = add_limits(text)
    path.write_text(text, encoding="utf-8")
    print("patched popup", rel)


def main():
    for rel, alive, tids, use_list, anchor in LOCAL_FILES:
        patch_local(rel, alive, tids, use_list, anchor)
    for rel, alive, tid, use_list, anchor in ROW_PICKER_FILES:
        patch_row_picker(rel, alive, tid, use_list, anchor)
    for rel, tid, alive in POPUP_TABLE_FILES:
        patch_popup_table(rel, tid, alive)
    for rel, map_key, prefix, alive, reload in SERVER_FILES:
        patch_server(rel, map_key, prefix, alive, reload)


if __name__ == "__main__":
    main()