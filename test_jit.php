<?php
require __DIR__.'/vendor/autoload.php';
$app = require_once __DIR__.'/bootstrap/app.php';
$kernel = $app->make(Illuminate\Contracts\Console\Kernel::class);
$kernel->bootstrap();

$apiKey = env('GEMINI_API_KEY');
$prompt = "Translate hello to Bengali";
$url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent?key={$apiKey}";

$response = Illuminate\Support\Facades\Http::post($url, [
    'contents' => [['parts' => [['text' => $prompt]]]]
]);

echo "Status Code: " . $response->status() . "\n";
echo "Response: " . substr($response->body(), 0, 500) . "\n";
