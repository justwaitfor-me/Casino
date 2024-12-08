<?php

$api_url = 'http://127.0.0.1:5000/get-data';  // Flask API URL

// The 'index' you want to retrieve
$key = "version";

// Append the index as a query parameter to the URL
$api_url .= '?key=' . urlencode($key);

// Initialize cURL session
$ch = curl_init($api_url);

// Set cURL options
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_HTTPGET, true);  // Use GET request

// Execute the request
$response = curl_exec($ch);

// Handle errors
if (curl_errno($ch)) {
    echo 'Error:' . curl_error($ch);
} else {
    echo 'Response: ' . $response;
}

// Close the cURL session
curl_close($ch);
?>
