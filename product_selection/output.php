<center>

<?php

function gpt_what($s){
    $calltext="Give an rgb colour value for the shade specified by user: ".$s;

    $calltext.='\n\nEXAMPLE OUTPUT:{\"Under 255\",\"Under 255\",\"Under 255\"}';

    $ccall="curl https://api.openai.com/v1/chat/completions  -H \"Content-Type: application/json\"  -H \"Authorization: Bearer {}\"   -d '{   \"model\": \"gpt-3.5-turbo\",  \"messages\": [{\"role\": \"system\", \"content\": \"Give RGB values separated by commas like (r, g, b).\"},{\"role\": \"user\", \"content\": \"".$calltext."\"}],   \"temperature\": 0.4   }'";

    exec($ccall,$d);
    $res=implode(" ",$d);

    $ret=json_decode($res);
    $output=$ret->choices[0]->message->content;

    return $output;

}

if (isset($_REQUEST['what'])){
    $what_input=gpt_what($_REQUEST['what']);
} 

$what_input = str_replace('$', '', $what_input);
$startPos = strpos($what_input, '{');
$endPos = strrpos($what_input, '}');
$what_input_cut = substr($what_input, $startPos, $endPos - $startPos + 1);
$data = json_decode($what_input_cut, true);
$what_input_json = json_encode($data);

$output = shell_exec("python3 user_shaderequest.py .$what_input_json");

?>
