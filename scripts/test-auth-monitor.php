<?php
error_reporting(E_ALL);

$root = dirname(__DIR__);
$web = $root . '/web';
require $web . '/monitor.php';

$fail = 0;
function check($name, $cond) {
    global $fail;
    if ($cond) {
        echo "[OK] $name\n";
        return;
    }
    echo "[FAIL] $name\n";
    $fail++;
}

check('http url keeps scheme for 80', monitor_http_url('example.com', 80, 'health') === 'http://example.com/health');
check('http url uses https on 443', monitor_http_url('example.com', 443, '/health') === 'https://example.com/health');
check('http url keeps custom port', monitor_http_url('example.com', 8080, '') === 'http://example.com:8080/');
check('http url rejects header injection', monitor_http_url('example.com', 80, "/ok\r\nX-Test: 1") === '');
check('host header rejects newline', monitor_header_host_ok("example.com\nX") === false);
check('host accepts a name', monitor_host_ok('cdn.example.com') === true);
check('host rejects shell metacharacters', monitor_host_ok('127.0.0.1;touch /tmp/pwned') === false);

$marker = sys_get_temp_dir() . '/cdnfly-monitor-pwn-' . getmypid();
@unlink($marker);
$evil = '127.0.0.1; touch ' . $marker;
check('ping rejects injected command', check_ping($evil, 80, 1) === false && !file_exists($marker));
check('tcp rejects injected target', check_tcp($evil, 80, 1) === false);
check('http rejects injected target', check_http($evil, 80, '/', '', 1) === false);
@unlink($marker);

$errno = 0;
$errstr = '';
$srv = stream_socket_server('tcp://127.0.0.1:0', $errno, $errstr);
check('local listener opened', is_resource($srv));
if (is_resource($srv)) {
    $name = stream_socket_get_name($srv, false);
    $port = (int)substr(strrchr($name, ':'), 1);
    check('tcp open port succeeds', check_tcp('127.0.0.1', $port, 2) === true);
    fclose($srv);
}
check('tcp closed port fails', check_tcp('127.0.0.1', 1, 1) === false);

$bad = node_monitor_all(null);
check('monitor all rejects non-array', $bad === array());
$one = node_monitor_local('9', array('type' => 'tcp', 'target' => 'not a host', 'port' => 80, 'timeout' => 1));
check('local monitor reports failure', $one['success'] === 0 && $one['node_id'] === '9');

function run_index($uri, $method, $get) {
    global $web;
    $cmd = 'php ' . escapeshellarg($web . '/../scripts/auth-index-runner.php');
    $desc = array(1 => array('pipe', 'w'), 2 => array('pipe', 'w'));
    $env = array(
        'TEST_URI' => $uri,
        'TEST_METHOD' => $method,
        'TEST_GET' => json_encode($get),
        'TEST_INDEX' => $web . '/index.php',
        'PATH' => getenv('PATH'),
    );
    $proc = proc_open($cmd, $desc, $pipes, $web, $env);
    $out = stream_get_contents($pipes[1]);
    $err = stream_get_contents($pipes[2]);
    fclose($pipes[1]);
    fclose($pipes[2]);
    $code = proc_close($proc);
    return array($code, $out, $err);
}

list($code, $out, $err) = run_index('/common/datetime?x=/auth', 'GET', array());
$out = trim($out);
check('datetime is echoed', $code === 0 && preg_match('/^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}$/', $out) === 1);
if ($err !== '') {
    echo $err;
}

list($code, $out, $err) = run_index('/master/upgrades?version_num=50113&op=>&limit=0', 'GET', array('version_num' => '50113', 'op' => '>'));
$parsed = json_decode($out, true);
check('current master version is not offered again', is_array($parsed) && isset($parsed['data']) && $parsed['data'] === array());

list($code, $out, $err) = run_index('/master/upgrades?latest=1', 'GET', array('latest' => '1'));
$parsed = json_decode($out, true);
check('latest upgrade still returns version.json', is_array($parsed) && isset($parsed['data'][0]['version_name']) && $parsed['data'][0]['version_name'] === 'v5.1.13');

list($code, $out, $err) = run_index('/agent/upgrades?version_num=50116&op=>', 'GET', array('version_num' => '50116', 'op' => '>'));
$parsed = json_decode($out, true);
check('agent upgrade list is empty', is_array($parsed) && isset($parsed['data']) && $parsed['data'] === array());

if ($fail) {
    echo "--- $fail failed ---\n";
    exit(1);
}
echo "--- auth/monitor checks passed ---\n";
