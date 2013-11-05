<?php
session_start();
require_once("twitteroauth/twitteroauth.php"); //Path to twitteroauth library
 
$twitteruser = "gobarnacle"; //Enter your twitter username
$notweets = 4;
$consumerkey = "eSdLTYTrltusULbDvoU0A"; //Enter Consumer key
$consumersecret = "P1vCmdiHJ2fMZUdSrTB8VoSYxsPzI6fePOl35KwrLU"; //Enter Consumer secret
$accesstoken = "1698640628-6YKNvQZKslGrIHLsM5tWQYrqNjpXQczAVkfQPZH"; //Enter Access token
$accesstokensecret = "mtjDvYZqFPcKlmeZv9R29xntNWmLJYV6aNMRMeTy8Mese"; //Enter Access token secret
 
function getConnectionWithAccessToken($cons_key, $cons_secret, $oauth_token, $oauth_token_secret) {
  $connection = new TwitterOAuth($cons_key, $cons_secret, $oauth_token, $oauth_token_secret);
  return $connection;
}
  
$connection = getConnectionWithAccessToken($consumerkey, $consumersecret, $accesstoken, $accesstokensecret);
 
$tweets = $connection->get("https://api.twitter.com/1.1/statuses/user_timeline.json?screen_name=".$twitteruser."&count=".$notweets);
 
echo json_encode($tweets);
?>