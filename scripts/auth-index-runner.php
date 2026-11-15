<?php
$_GET = json_decode(getenv('TEST_GET'), true);
if (!is_array($_GET)) {
    $_GET = array();
}
$_SERVER['REQUEST_URI'] = getenv('TEST_URI');
$_SERVER['REQUEST_METHOD'] = getenv('TEST_METHOD');
$_SERVER['REMOTE_ADDR'] = '127.0.0.1';
$index = getenv('TEST_INDEX');
chdir(dirname($index));
require $index;
