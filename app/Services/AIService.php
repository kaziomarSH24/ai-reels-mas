<?php

namespace App\Services;

use Illuminate\Support\Facades\Http;
use Exception;

class AIService
{
    /**
     * Send text to the Python Microservice for analysis.
     *
     * @param string $text
     * @return array
     * @throws Exception
     */
    public function analyze(string $text): array
    {
        $response = Http::timeout(5)->post('http://ai_api:8001/api/analyze', [
            'text' => $text
        ]);

        if ($response->successful()) {
            return $response->json('data');
        }

        throw new Exception('AI Server returned an error: ' . $response->body());
    }
}
