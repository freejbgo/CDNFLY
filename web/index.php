<?php
error_reporting(0);
date_default_timezone_set("PRC");
header('Content-Type: application/json; charset=UTF-8');
define('AES_KEY','L6DYHZ3NEb2QUL6D');
define('AES_KEY2','kQ3vaLGnZ8sgyd5T');
define('KEY_APPEND', 'rbkgp46j53');

if (function_exists("set_time_limit"))
{
	@set_time_limit(0);
}

$uri = isset($_SERVER['REQUEST_URI']) ? $_SERVER['REQUEST_URI'] : '';
$qpos = strpos($uri, '?');
if($qpos !== false) $uri = substr($uri, 0, $qpos);
$method = isset($_SERVER['REQUEST_METHOD']) ? $_SERVER['REQUEST_METHOD'] : 'GET';

if(strpos($uri, '/common/timestamp2') !== false && $method=='POST'){
    $param = require_param(parse_input2());
    $data = ['now'=>time(), 'rnd'=>isset($param['rnd']) ? $param['rnd'] : ''];
    echo generate_output2($data);
}
elseif(strpos($uri, '/auth2') !== false && $method=='POST'){
    $param = require_param(parse_input2());
    $data = ['nodes'=>10000, 'machine_code'=>isset($param['machine_code']) ? $param['machine_code'] : '', 'end_at'=>time()+3600*24*36500];
    echo generate_output2($data);
}
elseif(strpos($uri, '/common/timestamp') !== false && $method=='POST'){
    $param = require_param(parse_input());
    $data = ['now'=>time(), 'rnd'=>isset($param['rnd']) ? $param['rnd'] : ''];
    echo generate_output($data);
}
elseif(strpos($uri, '/auth') !== false && $method=='POST'){
    $param = require_param(parse_input());
    $data = ['nodes'=>10000, 'machine_code'=>isset($param['machine_code']) ? $param['machine_code'] : '', 'end_at'=>time()+3600*24*36500];
    echo generate_output($data);
}
elseif(strpos($uri, '/check') !== false && $method=='POST'){
    require 'config.php';
    require 'monitor.php';
    $post = file_get_contents('php://input');
    $param = json_decode($post, true);
    $result = node_monitor_all($param);
    $data = ['msg'=>$result];
    echo json_encode($data);
}
elseif(strpos($uri, '/common/datetime') !== false && $method=='GET'){
    header('Content-Type: text/plain; charset=UTF-8');
    echo date('Y-m-d H:i:s');
}
elseif(strpos($uri, '/agent/upgrades') !== false){
    $client_ip = isset($_SERVER['REMOTE_ADDR']) ? $_SERVER['REMOTE_ADDR'] : '';
    echo json_encode(['code'=>0, 'count'=>0, 'data'=>[], 'ip'=>$client_ip]);
}
elseif(strpos($uri, '/master/upgrades') !== false){
    $version_data = file_get_contents('version.json');
    $client_ip = isset($_SERVER['REMOTE_ADDR']) ? $_SERVER['REMOTE_ADDR'] : '';
    if(!$version_data) exit(json_encode(['code'=>-1, 'data'=>[], 'ip'=>$client_ip, 'msg'=>'版本信息文件不存在']));
    $version_info = json_decode($version_data, true);
    if(!$version_info) exit(json_encode(['code'=>-1, 'data'=>[], 'ip'=>$client_ip, 'msg'=>'解析版本信息文件失败']));
    $rows = upgrade_rows($version_info);
    $data = ['code'=>0, 'count'=>count($rows), 'data'=>$rows, 'ip'=>$client_ip];
    echo json_encode($data);
}


function require_param($param){
    return is_array($param) ? $param : [];
}
function upgrade_rows($info){
    $rows = [$info];
    if(!isset($_GET['version_num']) || $_GET['version_num'] === '') return $rows;
    $cur = intval($_GET['version_num']);
    $ver = intval(isset($info['version_num']) ? $info['version_num'] : 0);
    $op = isset($_GET['op']) ? $_GET['op'] : '=';
    if($op === '>') $keep = $ver > $cur;
    elseif($op === '>=') $keep = $ver >= $cur;
    elseif($op === '<') $keep = $ver < $cur;
    elseif($op === '<=') $keep = $ver <= $cur;
    else $keep = ($ver === $cur);
    if(!$keep) return [];
    return $rows;
}
function parse_input2(){
    $post = file_get_contents('php://input');
    $de_text = text_decrypt($post, get_aes_key());
    $param = json_decode($de_text, true);
    return $param;
}
function generate_output2($data){
    $json = json_encode($data);
    $cipher = text_encrypt($json, get_aes_key());
    $data = ['code'=>0, 'data'=>$cipher, 'msg'=>''];
    return json_encode($data);
}
function get_aes_key(){
    $key = isset($_GET['key']) ? trim($_GET['key']) : '';
    $aes_key = substr(md5($key.KEY_APPEND), 0, 16);
    return $aes_key;
}
function parse_input(){
    $post = file_get_contents('php://input');
    $param = json_decode(text_decrypt($post, AES_KEY), true);
    return $param;
}
function generate_output($data){
    $cipher = text_encrypt(json_encode($data), AES_KEY);
    $data = ['code'=>0, 'data'=>$cipher, 'msg'=>''];
    return json_encode($data);
}
function text_encrypt($data, $key){
    return openssl_encrypt($data, 'aes-128-cbc', $key, 0, $key);
}
function text_decrypt($data, $key){
    return openssl_decrypt($data, 'aes-128-cbc', $key, 0, $key);
}
