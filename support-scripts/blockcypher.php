<?php

$postdata = file_get_contents("php://input");
$js = json_decode($postdata);
if (!$js) return;

$json = array(
 'mode'=>'heightupdate',
 'data'=>$js
);


$fp = fopen("/tmp/TBC-INTERRUPT.txt","w");
fwrite($fp, json_encode($json));
fclose($fp);
copy("/tmp/TBC-INTERRUPT.txt", "/tmp/latestBlockheight.txt");

system("/opt/ThexBerryClock/interruptsudo.sh");
