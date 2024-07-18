<center>

<?php

function gpt_who($s){
    $calltext="Extract user information (in JSON format) from the following string: ".$s;

    $calltext.='\n\nEXAMPLE OUTPUT:{\"Age\":\"22\",\"Sex\":\"Female\",\"Skin Tone\":\"Olive\",\"Skin Type\":\"Oily\"}';

    $ccall="curl https://api.openai.com/v1/chat/completions  -H \"Content-Type: application/json\"  -H \"Authorization: Bearer {KEY REDACTED}\"   -d '{   \"model\": \"gpt-4o\",  \"messages\": [{\"role\": \"system\", \"content\": \"You are a personal beauty advisor! Ignore grammar errors. If fields are missing, do not include.\"},{\"role\": \"user\", \"content\": \"".$calltext."\"}],   \"temperature\": 0.4   }'";

    exec($ccall,$d);
    $res=implode(" ",$d);

    $ret=json_decode($res);
    $output=$ret->choices[0]->message->content;

    return $output;
    /*
    if (strpos($output,"```")!==false)
    {
    $finout=explode("```",$output);
    $finout2=explode("json",$finout[1]);
    $output=$finout2[1];
    }

    $cleanoutput_1=explode("[",$output);
    $cleanoutput_2=explode("]",$cleanoutput_1[1]);

    return json_decode("[".$cleanoutput_2[0]."]");

    */

}

function gpt_what($s){
    $calltext="Extract user information (in JSON format) from the following string: ".$s;

    $calltext.='\n\nEXAMPLE OUTPUT:{\"Products\":\"Foundation\",\"Price\":\"Under $100\",\"Brand\":\"Dior\"}';

    $ccall="curl https://api.openai.com/v1/chat/completions  -H \"Content-Type: application/json\"  -H \"Authorization: Bearer {KEY REDACTED}\"   -d '{   \"model\": \"gpt-3.5-turbo\",  \"messages\": [{\"role\": \"system\", \"content\": \"You are a personal beauty advisor! Ignore grammar errors. If fields are missing, do not include.\"},{\"role\": \"user\", \"content\": \"".$calltext."\"}],   \"temperature\": 0.4   }'";

    exec($ccall,$d);
    $res=implode(" ",$d);

    $ret=json_decode($res);
    $output=$ret->choices[0]->message->content;

    return $output;

}

// Call gpt functions to get user input for who and what
if (isset($_REQUEST['who'])){
    $who_input=gpt_who($_REQUEST['who']);
}

if (isset($_REQUEST['what'])){
    $what_input=gpt_what($_REQUEST['what']);
} 

// Handle each input (who and what) and convert to proper json format

// echo $who_input;
// echo $what_input;


$startPos = strpos($who_input, '{');
$endPos = strrpos($who_input, '}');
$who_input_cut = substr($who_input, $startPos, $endPos - $startPos + 1);
$data = json_decode($who_input_cut, true);
$who_input_json = json_encode($data);

$what_input = str_replace('$', '', $what_input);
$startPos = strpos($what_input, '{');
$endPos = strrpos($what_input, '}');
$what_input_cut = substr($what_input, $startPos, $endPos - $startPos + 1);
$data = json_decode($what_input_cut, true);
$what_input_json = json_encode($data);

// echo $who_input_json;
// echo $what_input_json;

// Call Python script to map user input to products
$output = shell_exec("python3 map_user_to_product.py  .$who_input_json .$what_input_json");

$output_split = explode('"', $output);

$output_split = array_values(array_filter(array_map('trim', $output_split)));

$brands = [];
$names = [];
$images = [];

for($x = 0; $x < count($output_split); $x++) {
    $remainder = fmod($x, 3);
    switch($remainder) {
        case 0:
            array_push($brands, $output_split[$x]);
            break;
        case 1:
            array_push($names, $output_split[$x]);
            break;
        case 2:
            array_push($images, $output_split[$x]);
            break;
        }
}

function displayImages($images, $names){
    for ($i=0; $i<count($images); $i++) {
        echo "<img src=\"".$images[$i] . "\"><br>";
        echo "<label>".$names[$i] . "</label><br>";
    }
}

 //print_r($brands);

//echo $output_split[0];

?>

<body>
    <main id ="main">
      <form id="pics" action="output.php" method="get">
        <!-- <label> test </label>  -->
        <?php echo displayImages($images, $names);?>
      </form>
    </main>
  </body>

