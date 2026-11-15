#!/usr/bin/env bash
# Checks that do not need a CentOS install: argument forwarding, crontab line, package contents.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
fail=0
ok() { echo "[OK] $*"; }
bad() { echo "[FAIL] $*"; fail=$((fail + 1)); }

bash -n "$ROOT/master.sh"
bash -n "$ROOT/agent.sh"
bash -n "$ROOT/50113.sh"
ok "wrapper syntax"

line="$(grep -v '^#' "$ROOT/scripts/ntp-crontab-canonical.txt" | grep -v '^$' | head -1)"
grep -qF "$line" "$ROOT/master.sh" && ok "master.sh ntp line" || bad "master.sh ntp line drifted"
grep -qF "$line" "$ROOT/agent.sh" && ok "agent.sh ntp line" || bad "agent.sh ntp line drifted"
if grep -q '/usr/bin/date' "$ROOT/master.sh" "$ROOT/agent.sh"; then
  bad "wrapper still falls back to the local clock"
else
  ok "wrapper does not rewrite the clock from local date"
fi

# cron 只把 \% 还原成 %。\$ 留给 shell，在双引号里就是正则的结尾。
ntp_re='^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}$'
grep -qF 'grep -Eq "^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}\$"' <<<"$line" \
  && ok "ntp regex is in the crontab line" || bad "ntp regex missing from crontab line"
printf '%s' '2026-11-15 10:09:00' | grep -Eq "$ntp_re" \
  && ok "ntp regex accepts a timestamp" || bad "ntp regex rejected a valid timestamp"
if printf '%s' '2026-11-15 10:09:00; reboot' | grep -Eq "$ntp_re"; then
  bad "ntp regex accepted extra shell text"
else
  ok "ntp regex rejects extra shell text"
fi

help_out="$(bash "$ROOT/master.sh" --help)"
grep -q '用法' <<<"$help_out" && ok "master --help" || bad "master --help"
help_out="$(bash "$ROOT/agent.sh" --es-pwd first --help)"
grep -q '用法' <<<"$help_out" && ok "agent --help in any position" || bad "agent --help in any position"

extract_fn() {
  local file="$1" kind="$2"
  awk -v kind="$kind" '
    $0 ~ ("# --- parse-install-args " kind " ---") {grab=1; next}
    $0 ~ /# --- parse-install-args end ---/ {grab=0}
    grab {print}
  ' "$file"
}

master_fn="$(extract_fn "$ROOT/master.sh" master)"
agent_fn="$(extract_fn "$ROOT/agent.sh" agent)"
[[ -n "$master_fn" && -n "$agent_fn" ]] && ok "extracted argument parsers" || bad "argument parser markers missing"

eval "$master_fn"
parse_install_args --es-dir /home/es --ver v5.1.13
[[ "$VER" == "v5.1.13" ]] && ok "master --ver after other flags" || bad "master dropped --ver, got ${VER:-empty}"
[[ "${FORWARD[0]}" == "--es-dir" && "${FORWARD[1]}" == "/home/es" && "${#FORWARD[@]}" -eq 2 ]] \
  && ok "master forwards es-dir only" || bad "master forward array: ${FORWARD[*]:-empty}"

eval "$agent_fn"
parse_install_args --es-pwd 'a b$c"d' --master-ver v5.1.13 --master-ip 1.2.3.4
[[ "$MASTER_VER" == "v5.1.13" ]] && ok "agent --master-ver after password" || bad "agent dropped --master-ver"
[[ "${FORWARD[0]}" == "--es-pwd" && "${FORWARD[1]}" == 'a b$c"d' && "${FORWARD[2]}" == "--master-ip" && "${FORWARD[3]}" == "1.2.3.4" ]] \
  && ok "agent keeps password and forwards install flags" || bad "agent forward array mismatch"

if [[ ! -x "$(command -v php)" ]]; then
  bad "php is required for auth/monitor checks"
else
  php "$ROOT/scripts/test-auth-monitor.php"
fi

web_unpack="$(mktemp -d)"
tar -xzf "$ROOT/web/web.tar.gz" -C "$web_unpack"
web_ok=1
for f in api.php config.php index.php monitor.php update.php version.json .htaccess 'nginx伪静态.txt'; do
  if cmp -s "$ROOT/web/$f" "$web_unpack/$f"; then
    :
  else
    bad "web.tar.gz $f differs from web/$f"
    web_ok=0
  fi
done
if [[ "$web_ok" -eq 1 ]]; then
  ok "web.tar.gz matches the web directory"
fi
rm -rf "$web_unpack"

python3 - "$ROOT" <<'PY'
import io, json, os, tarfile, sys, tempfile, textwrap, shutil
root = sys.argv[1]
failures = []

def bad(msg):
    failures.append(msg)
    print("[FAIL]", msg)

def ok(msg):
    print("[OK]", msg)

def member_text(tar, name):
    f = tar.extractfile(name)
    return f.read().decode("utf-8", "replace")

master_tar = os.path.join(root, "cdnfly", "cdnfly-master-v5.1.13-centos-7.tar.gz")
agent_tar = os.path.join(root, "cdnfly", "cdnfly-agent-v5.1.16-centos-7.tar.gz")
with tarfile.open(master_tar) as tar:
    install = member_text(tar, "cdnfly-master-v5.1.13/master/install.sh")
    upgrade = member_text(tar, "cdnfly-master-v5.1.13/master/tasks/upgrade.py")
    up_sh = member_text(tar, "cdnfly-master-v5.1.13/master/upgrade_script/50113.sh")
    packaged_master = member_text(tar, "cdnfly-master-v5.1.13/master/master.sh")
    db_sql = member_text(tar, "cdnfly-master-v5.1.13/master/conf/db.sql")
with tarfile.open(agent_tar) as tar:
    agent_install = member_text(tar, "cdnfly-agent-v5.1.16/agent/install.sh")
    agent_up = member_text(tar, "cdnfly-agent-v5.1.16/agent/upgrade.py")
    packaged_agent = member_text(tar, "cdnfly-agent-v5.1.16/agent/agent.sh")

canon = open(os.path.join(root, "scripts", "ntp-crontab-canonical.txt"), encoding="utf-8").read()
line = [ln for ln in canon.splitlines() if ln and not ln.startswith("#")][0]
if line not in install or line not in agent_install:
    bad("packaged install.sh ntp line drifted")
else:
    ok("packaged install.sh ntp line")
if "/usr/bin/date" in install or "/usr/bin/date" in agent_install:
    bad("packaged install.sh still uses local date fallback")
else:
    ok("packaged install.sh has no local date fallback")
if "dl2.cdnfly.cn" in upgrade or "us.centos.bz" in upgrade or "dl2.cdnfly.cn" in agent_up:
    bad("upgrade.py still downloads scripts from a third-party host")
else:
    ok("upgrade.py does not call third-party script hosts")
if "script_url" not in upgrade or "script_url" not in agent_up:
    bad("upgrade.py does not require the url field")
else:
    ok("upgrade.py requires an explicit script url")
if "supervisorctl -c /opt/cdnfly/master/conf/supervisord.conf restart all" not in up_sh:
    bad("bundled 50113.sh does not restart the master supervisord")
else:
    ok("bundled 50113.sh restarts the master supervisord")
if "ignore-ntp" not in install.split("getopt", 1)[1][:400]:
    bad("master install.sh getopt still rejects --ignore-ntp")
else:
    ok("master install.sh accepts --ignore-ntp")
if "if ! grep -q 65535 /etc/security/limits.conf" not in install:
    bad("kernel_tune still treats grep -q as a string test")
else:
    ok("kernel_tune checks limits.conf by exit status")
if 'echo "目前只支持 CentOS 7' not in install or "exit 1" not in install.split("need_sys()", 1)[1][:500]:
    bad("master install.sh does not stop on a non-CentOS system")
else:
    ok("master install.sh requires CentOS 7")
if 'echo "目前只支持 CentOS 7' not in agent_install or "exit 1" not in agent_install.split("need_sys()", 1)[1][:500]:
    bad("agent install.sh does not stop on a non-CentOS system")
else:
    ok("agent install.sh requires CentOS 7")
repo_master = open(os.path.join(root, "master.sh"), encoding="utf-8").read()
repo_agent = open(os.path.join(root, "agent.sh"), encoding="utf-8").read()
if packaged_master != repo_master:
    bad("packaged master.sh differs from the repo installer")
else:
    ok("packaged master.sh matches the repo installer")
if packaged_agent != repo_agent:
    bad("packaged agent.sh differs from the repo installer")
else:
    ok("packaged agent.sh matches the repo installer")
if '"key":"__OPENRESTY_KEY__"' not in db_sql or "QWOBRGt35Y" in db_sql:
    bad("db.sql does not leave the openresty key for install.sh to replace")
elif 's/__OPENRESTY_KEY__/' not in install:
    bad("install.sh no longer substitutes __OPENRESTY_KEY__")
else:
    ok("install.sh substitutes a fresh openresty key")
if "wait_for_elasticsearch" not in install:
    bad("elasticsearch setup still continues after a fixed 5 second sleep")
else:
    ok("elasticsearch setup waits until it answers")
if "下载失败" not in install or "下载失败" not in agent_install:
    bad("download() still ignores a failed wget")
else:
    ok("download() fails when the file is empty")

def run_embedded(install_text, start, paths):
    begin = install_text.index(start)
    body = install_text[begin:]
    py_at = body.index("<<'PY'\n") + len("<<'PY'\n")
    script = body[py_at:body.index("\nPY\n", py_at)]
    for old, new in paths.items():
        script = script.replace(old, new)
    ns = {}
    # Execute as a program via subprocess to keep argv handling.
    return script

def exec_script(script, args, cwd):
    path = os.path.join(cwd, "run.py")
    open(path, "w", encoding="utf-8").write(script)
    import subprocess
    proc = subprocess.run([sys.executable, path] + args, cwd=cwd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr or proc.stdout)
    return proc

work = tempfile.mkdtemp(prefix="cdnfly-secret-")
try:
    master_conf = os.path.join(work, "master-config.py")
    with tarfile.open(master_tar) as tar:
        data = tar.extractfile("cdnfly-master-v5.1.13/master/conf/config.py").read()
    open(master_conf, "wb").write(data)
    script = run_embedded(install, "write_master_config()", {})
    script = script.replace('"/opt/cdnfly/master/conf/config.py"', json.dumps(master_conf))
    pwd = 'p#a&s s$("x")'
    exec_script(script, ["127.0.0.1", "10.1.2.3", pwd], work)
    written = open(master_conf, encoding="utf-8").read()
    if 'LOG_PWD=' + json.dumps(pwd) not in written:
        bad("master config password was not escaped")
    elif 'LOG_IP=' + json.dumps("10.1.2.3") not in written:
        bad("master config es ip was not written")
    else:
        ok("master config escapes a password with shell metacharacters")

    agent_conf = os.path.join(work, "agent-config.py")
    fb = os.path.join(work, "filebeat.yml")
    with tarfile.open(agent_tar) as tar:
        open(agent_conf, "wb").write(tar.extractfile("cdnfly-agent-v5.1.16/agent/conf/config.py").read())
        open(fb, "wb").write(tar.extractfile("cdnfly-agent-v5.1.16/agent/conf/filebeat.yml").read())
    script = run_embedded(agent_install, "write_agent_secrets()", {
        '"/opt/cdnfly/agent/conf/config.py"': json.dumps(agent_conf),
        '"/opt/cdnfly/agent/conf/filebeat.yml"': json.dumps(fb),
    })
    exec_script(script, [pwd, "10.9.8.7", "10.0.0.8"], work)
    cfg = open(agent_conf, encoding="utf-8").read()
    yml = open(fb, encoding="utf-8").read()
    if 'ES_PWD = ' + json.dumps(pwd) not in cfg:
        bad("agent config password was not escaped")
    elif yml.count(json.dumps(pwd)) < 2:
        bad("filebeat did not replace every password placeholder")
    elif '10.9.8.7:9200' not in yml or '192.168.0.30' in yml:
        bad("filebeat es host was not replaced")
    else:
        ok("agent config and filebeat escape a password with shell metacharacters")
finally:
    shutil.rmtree(work)

if failures:
    print("---", len(failures), "package checks failed ---")
    sys.exit(1)
print("--- package checks passed ---")
PY

[[ "$fail" -eq 0 ]] && echo "--- deep audit checks passed ---" || { echo "--- $fail failed ---"; exit 1; }
