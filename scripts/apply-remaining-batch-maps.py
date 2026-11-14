#!/usr/bin/env python3
"""Add CheckedMap batch helpers to remaining panel list pages."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1] / ".veikor-build/cdnfly-master-v5.1.13/master/panel/src/views"

HELPER = """
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
      var ids = collectChecked{prefix}Ids(checkStatus && checkStatus.data);
      return ids;
    }}

"""

LIMITS = ",limits: [10,20,50,100,200,500]"

FILES = [
    ("node/node/index.html", "__veikorNodeListCheckedMap", "NodeList", "nodeListAlive", "reloadNodeList"),
    ("package/upgrade/index.html", "__veikorPackageUpgradeListCheckedMap", "PackageUpgrade", "packageUpgradeAlive", "reloadPackageUpgradeTable"),
    ("site/group/index.html", "__veikorSiteGroupListCheckedMap", "SiteGroup", "siteGroupAlive", "reloadSiteGroupTable"),
    ("stream/group/index.html", "__veikorStreamGroupListCheckedMap", "StreamGroup", "streamGroupAlive", "reloadStreamGroupTable"),
    ("package/group/index.html", "__veikorPackageGroupListCheckedMap", "PackageGroup", "packageGroupAlive", "reloadPackageGroupTable"),
    ("node/region/index.html", "__veikorNodeRegionListCheckedMap", "NodeRegion", "regionPageAlive", "reloadRegionTable"),
    ("node/group/index.html", "__veikorNodeGroupListCheckedMap", "NodeGroupList", "nodeGroupAlive", "reloadNodeGroupTable"),
    ("system/task/index.html", "__veikorSystemTaskListCheckedMap", "SystemTask", "taskPageAlive", None),
    ("system/user/index.html", "__veikorSystemUserListCheckedMap", "SystemUser", "userListAlive", "reloadUserTable"),
    ("system/announcement/index.html", "__veikorAnnouncementListCheckedMap", "Announcement", "announcementAlive", "reloadAnnouncementTable"),
]


def patch_file(rel, map_key, prefix, alive, reload_fn):
    path = ROOT / rel
    text = path.read_text(encoding="utf-8")
    if map_key in text:
        print("skip (already)", rel)
        return

    block = HELPER.format(map_key=map_key, alive=alive, prefix=prefix)
    # insert before access_token line before first table.render in layui.use
    m = re.search(r"\n(\s*)var access_token = layui\.data", text)
    if not m:
        m = re.search(r"\n(\s*)table\.render\(\{", text)
    if not m:
        print("no insert point", rel)
        return
    text = text[: m.start()] + "\n" + block + text[m.start() :]

    if reload_fn:
        text = text.replace(
            f"function {reload_fn}() {{\n      if (!{alive}()) return;\n      layui.table.reload('test-table-toolbar');",
            f"function {reload_fn}() {{\n      if (!{alive}()) return;\n      window.{map_key} = {{}};\n      layui.table.reload('test-table-toolbar');",
            1,
        )
    elif rel == "system/task/index.html":
        text = text.replace(
            "function taskPageAlive() {",
            f"function reloadTaskTable() {{\n      if (!taskPageAlive()) return;\n      window.{map_key} = {{}};\n      layui.table.reload('test-table-toolbar');\n    }}\n\n    function taskPageAlive() {{",
            1,
        )
        text = text.replace(
            "if (!taskPageAlive()) return;\n              layui.table.reload('test-table-toolbar'); //重载表格",
            "reloadTaskTable();",
        )

    if rel == "node/node/index.html":
        text = text.replace(
            "function reloadNodeList() {\n    if (!nodeListAlive()) return;\n    layui.table.reload('test-table-toolbar');",
            f"function reloadNodeList() {{\n    if (!nodeListAlive()) return;\n    window.{map_key} = {{}};\n    layui.table.reload('test-table-toolbar');",
            1,
        )

    # limits on page:true tables (first occurrences only - add to all page:true before });
    def add_limits(match):
        chunk = match.group(0)
        if "limits:" in chunk:
            return chunk
        return chunk.replace(",page: true", ",page: true\n      " + LIMITS.strip())

    text = re.sub(r",page: true\n(\s*),defaultToolbar", ",page: true\n      " + LIMITS + "\n\\1,defaultToolbar", text, count=1)
    text = re.sub(
        r",page: true\n(\s*)\}\);",
        lambda m: ",page: true\n      " + LIMITS + "\n" + m.group(1) + "});",
        text,
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

    def fix_delete_block(m):
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

    text = re.sub(delete_block, fix_delete_block, text)

    # bulk replace enable/disable loops
    text = re.sub(
        r"var data = checkStatus\.data;\s*\n\s*if \(data\.length == 0\)",
        f"var batchIds = assign{prefix}IdsForBatch(checkStatus);\n          if (batchIds.length == 0)",
        text,
    )
    text = re.sub(
        r"var check_data = checkStatus\.data;\s*\n\s*if \(check_data\.length == 0\)",
        f"var batchIds = assign{prefix}IdsForBatch(checkStatus);\n          window.__veikorNodeMonitorBatchIds = batchIds.slice();\n          if (batchIds.length == 0)",
        text,
        count=1,
    )
    text = text.replace(
        'for (i in data) {\n            req_data.push({"id":data[i][\'id\'],"enable":1})',
        'for (i in batchIds) {\n            req_data.push({"id":batchIds[i],"enable":1})',
    )
    text = text.replace(
        'for (i in data) {\n            req_data.push({"id":data[i][\'id\'],"enable":0})',
        'for (i in batchIds) {\n            req_data.push({"id":batchIds[i],"enable":0})',
    )
    text = text.replace(
        'for (i in data) {\n            req_data.push({"id":data[i][\'id\'],"enable":0,"disable_by":"admin"})',
        'for (i in batchIds) {\n            req_data.push({"id":batchIds[i],"enable":0,"disable_by":"admin"})',
    )
    text = text.replace(
        'for (i in data) {\n            req_data.push({"id":data[i][\'id\'],"enable":1,"target":"node"})',
        'for (i in batchIds) {\n            req_data.push({"id":batchIds[i],"enable":1,"target":"node"})',
    )
    text = text.replace(
        'for (i in data) {\n            req_data.push({"id":data[i][\'id\'],"enable":0,"target":"node","disable_by":"admin"})',
        'for (i in batchIds) {\n            req_data.push({"id":batchIds[i],"enable":0,"target":"node","disable_by":"admin"})',
    )
    text = text.replace(
        'for (i in data) {\n            req_data.push({"id":data[i][\'id\'],"is_mgmt":1})',
        'for (i in batchIds) {\n            req_data.push({"id":batchIds[i],"is_mgmt":1})',
    )
    text = text.replace(
        'for (i in data) {\n            req_data.push({"id":data[i][\'id\'],"is_mgmt":0})',
        'for (i in batchIds) {\n            req_data.push({"id":batchIds[i],"is_mgmt":0})',
    )
    text = text.replace(
        'for (i in check_data) {\n                      req_data.push({"id":check_data[i][\'id\'],',
        'var monitorIds = window.__veikorNodeMonitorBatchIds || batchIds;\n                    for (i in monitorIds) {\n                      req_data.push({"id":monitorIds[i],',
    )
    text = text.replace(
        'for (i in data) {\n            req_data.push({"id":data[i][\'id\'],"enable":0})',
        'for (i in batchIds) {\n            req_data.push({"id":batchIds[i],"enable":0})',
    )
    text = text.replace(
        'for (i in data) {\n            req_data.push({"id":data[i][\'id\'],"enable":0})\n          }',
        'for (i in batchIds) {\n            req_data.push({"id":batchIds[i],"enable":0})\n          }',
    )

    # task cancel
    text = text.replace(
        'for (i in data) {\n            req_data.push({"id":data[i][\'id\'],"enable":0})',
        'for (i in batchIds) {\n            req_data.push({"id":batchIds[i],"enable":0})',
    )

    # node delete url
    text = text.replace("url: '/nodes/'+ids ", "url: '/nodes/'+idParam ")

    # fix delete URLs still using ids variable
    for old_url in [
        ("'/site-groups/'+ids", "'/site-groups/'+idParam"),
        ("'/stream-groups/'+ids", "'/stream-groups/'+idParam"),
        ("'/package-groups/'+ids", "'/package-groups/'+idParam"),
        ("'/regions/'+ids", "'/regions/'+idParam"),
        ("'/node-groups/'+ids", "'/node-groups/'+idParam"),
        ("'/package-ups/'+ids", "'/package-ups/'+idParam"),
        ("'/users/'+ids", "'/users/'+idParam"),
        ("'/messages/'+ids", "'/messages/'+idParam"),
    ]:
        text = text.replace(old_url[0], old_url[1])

    path.write_text(text, encoding="utf-8")
    print("patched", rel)


def main():
    for rel, map_key, prefix, alive, reload_fn in FILES:
        patch_file(rel, map_key, prefix, alive, reload_fn)


if __name__ == "__main__":
    main()