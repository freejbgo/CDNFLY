<?php

//执行全部监控
function node_monitor_all($targets){
    global $monitor_config;
    $result = [];
    if(!is_array($targets)) return $result;
    $target_group_1 = [];
    $target_group_2 = [];
    foreach($targets as $target){
        if(!is_array($target)) continue;
        if(isset($target['node_group']) && strval($target['node_group']) === '2') $target_group_2[] = $target;
        else $target_group_1[] = $target;
    }
    if(isset($monitor_config['group_1']) && count($monitor_config['group_1']) > 0 && count($target_group_1) > 0){
        foreach($monitor_config['group_1'] as $node){
            if($node['type'] == 'local'){
                foreach($target_group_1 as $target){
                    $result[] = node_monitor_local($node['node_id'], $target);
                }
            }elseif($node['type'] == 'remote'){
                $result = array_merge($result, node_monitor_remote($node['node_id'], $node['api'], $target_group_1));
            }
        }
    }
    if(isset($monitor_config['group_2']) && count($monitor_config['group_2']) > 0 && count($target_group_2) > 0){
        foreach($monitor_config['group_2'] as $node){
            if($node['type'] == 'local'){
                foreach($target_group_2 as $target){
                    $result[] = node_monitor_local($node['node_id'], $target);
                }
            }elseif($node['type'] == 'remote'){
                $result = array_merge($result, node_monitor_remote($node['node_id'], $node['api'], $target_group_2));
            }
        }
    }
    return $result;
}

//批量执行远程监控
function node_monitor_remote($node_id, $apiurl, $targets){
    if(!is_string($apiurl) || !preg_match('#^https?://#', $apiurl)) return [];
    $json = json_encode($targets);
    $data = send_request($apiurl, $json);
    $arr = json_decode($data, true);
    if(!$arr || !isset($arr['msg']) || !is_array($arr['msg'])) return [];
    $result = [];
    foreach($arr['msg'] as $target){
        if(!is_array($target)) continue;
        $target['node_id'] = $node_id;
        $result[] = $target;
    }
    return $result;
}

//单个执行本地监控
function node_monitor_local($node_id, $target){
    $status = false;
    $shown = '';
    if(is_array($target) && isset($target['type'], $target['target'])){
        $shown = $target['target'];
        $port = isset($target['port']) ? $target['port'] : 0;
        $timeout = isset($target['timeout']) ? $target['timeout'] : 3;
        if($target['type'] == 'http'){
            $path = isset($target['path']) ? $target['path'] : '/';
            $host = isset($target['host']) ? $target['host'] : '';
            $status = check_http($target['target'], $port, $path, $host, $timeout);
        }elseif($target['type'] == 'ping'){
            $status = check_ping($target['target'], $port, $timeout);
        }else{ //tcp
            $status = check_tcp($target['target'], $port, $timeout);
        }
    }
    return ['node_id'=>$node_id, 'success'=>$status?1:0, 'target'=>$shown];
}

function monitor_timeout($timeout, $cap){
    $timeout = intval($timeout);
    if($timeout < 1) $timeout = 1;
    if($timeout > $cap) $timeout = $cap;
    return $timeout;
}

function monitor_port($port, $fallback){
    $port = intval($port);
    if($port < 1 || $port > 65535) return intval($fallback);
    return $port;
}

function monitor_host_ok($target){
    if(!is_string($target) || $target === '') return false;
    if(filter_var($target, FILTER_VALIDATE_IP)) return true;
    return (bool)preg_match('/^[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)*$/', $target);
}

function monitor_header_host_ok($host){
    if($host === '' || $host === null) return true;
    if(!is_string($host) || strpbrk($host, "\r\n\0") !== false) return false;
    if(monitor_host_ok($host)) return true;
    return (bool)preg_match('/^[A-Za-z0-9.-]+:[0-9]{1,5}$/', $host);
}

function monitor_http_url($target, $port, $path){
    $port = monitor_port($port, 80);
    if(!is_string($path) || $path === '') $path = '/';
    if($path[0] !== '/') $path = '/'.$path;
    if(strpbrk($path, "\r\n\0") !== false) return '';
    $scheme = ($port === 443) ? 'https' : 'http';
    if($port === 80 || $port === 443) return $scheme.'://'.$target.$path;
    return $scheme.'://'.$target.':'.$port.$path;
}

function check_http($target, $port, $path, $host = '', $timeout = 3){
    $timeout = monitor_timeout($timeout, 3);
    if(!monitor_host_ok($target) || !monitor_header_host_ok($host)) return false;
    $url = monitor_http_url($target, $port, $path);
    if($url === '') return false;
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
    curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, false);
    $httpheader = [];
    $httpheader[] = "Accept: */*";
    $httpheader[] = "Accept-Language: zh-CN,zh;q=0.8";
    $httpheader[] = "Connection: close";
    if(!empty($host)){
        $httpheader[] = "Host: ".$host;
    }
    curl_setopt($ch, CURLOPT_HTTPHEADER, $httpheader);
    curl_setopt($ch, CURLOPT_USERAGENT, "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36");
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
    curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, $timeout);
    curl_setopt($ch, CURLOPT_TIMEOUT, $timeout);
    curl_exec($ch);
    $errno = curl_errno($ch);
    if($errno) {
        curl_close($ch);
        return false;
    }
    $httpcode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);
    if($httpcode>=200 && $httpcode<400){
        return true;
    }
    return false;
}

function check_tcp($target, $port, $timeout = 3){
    $timeout = monitor_timeout($timeout, 3);
    $port = monitor_port($port, 80);
    if(!monitor_host_ok($target)) return false;
    $domain = AF_INET;
    if(filter_var($target, FILTER_VALIDATE_IP, FILTER_FLAG_IPV6)) $domain = AF_INET6;
    $sock = @socket_create($domain, SOCK_STREAM, SOL_TCP);
    if($sock === false) return false;
    @socket_set_nonblock($sock);
    @socket_connect($sock, $target, $port);
    @socket_set_block($sock);
    $read = null;
    $write = [$sock];
    $except = [$sock];
    $n = @socket_select($read, $write, $except, $timeout);
    $ok = false;
    if($n > 0){
        $err = @socket_get_option($sock, SOL_SOCKET, SO_ERROR);
        $ok = ($err === 0);
    }
    @socket_close($sock);
    return $ok;
}

function check_ping($target, $port, $timeout = 2){
    if(!function_exists('exec') || PHP_OS == 'WINNT') return check_tcp($target, $port, $timeout);
    $timeout = monitor_timeout($timeout, 2);
    if(!monitor_host_ok($target)) return false;
    $bin = 'ping';
    if(filter_var($target, FILTER_VALIDATE_IP, FILTER_FLAG_IPV6)) $bin = 'ping6';
    $cmd = $bin.' -c 1 -w '.intval($timeout).' '.escapeshellarg($target).' > /dev/null 2>&1';
    exec($cmd, $output, $return_var);
    return $return_var === 0;
}

function send_request($url, $json){
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
    curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, false);
    curl_setopt($ch, CURLOPT_USERAGENT, "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36");
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
    curl_setopt($ch, CURLOPT_POST, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, $json);
    curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/json; charset=utf-8']);
    curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 3);
    curl_setopt($ch, CURLOPT_TIMEOUT, 10);
    $ret = curl_exec($ch);
    curl_close($ch);
    return $ret;
}
