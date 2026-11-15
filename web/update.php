<?php
// version.json 是本发行版的授权站数据，不能从官方更新站覆盖。
// 官方接口不认 query，拉下来会把下载地址改回第三方升级脚本。

error_reporting(0);
header('Content-Type: text/plain; charset=UTF-8');
echo "未修改 version.json。本发行版的版本信息以仓库里的 web/version.json 为准，请直接编辑该文件。\n";
