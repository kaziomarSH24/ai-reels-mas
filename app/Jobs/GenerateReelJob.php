<?php

namespace App\Jobs;

use App\Models\GeneratedReel;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Queue\Queueable;
use Illuminate\Queue\InteractsWithQueue;
use Illuminate\Queue\SerializesModels;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;

class GenerateReelJob implements ShouldQueue
{
    use Queueable, InteractsWithQueue, SerializesModels;

    public int $tries = 3;
    public int $timeout = 900; // 15 mins for heavy rendering

    public function __construct(
        public readonly GeneratedReel $generatedReel,
        public readonly array $clipsToProcess
    ) {}

    public function handle(): void
    {
        Log::info("[GenerateReelJob] Starting rendering job for Reel ID: {$this->generatedReel->id}");

        $this->generatedReel->update(['status' => 'processing']);

        try {
            $outputFilename = 'reel_export_' . uniqid() . '.mp4';
            $clips = $this->clipsToProcess;
            
            // 1. Fetch unified translation from Gemini via Python API
            if (!empty($clips)) {
                $targetWord = $clips[0]['expression'];
                Log::info("[GenerateReelJob] Fetching fresh translation for '{$targetWord}'...");
                $transResponse = Http::timeout(60)->post('http://ai_api:8001/api/translate_word', [
                    'word' => $targetWord
                ]);
                
                if ($transResponse->successful()) {
                    $transData = $transResponse->json()['data'] ?? null;
                    if ($transData && isset($transData['casual_meaning'])) {
                        // Apply unified meaning to all clips
                        foreach ($clips as &$clip) {
                            $clip['casual_meaning'] = $transData['casual_meaning'];
                            $clip['easy_example'] = $transData['easy_example'] ?? '';
                            $clip['example_translation'] = $transData['example_translation'] ?? '';
                        }
                        Log::info("[GenerateReelJob] Applied fresh unified translation.");
                    }
                } else {
                    Log::warning("[GenerateReelJob] Failed to fetch translation. Using original DB meanings. Error: " . $transResponse->body());
                }
            }

            // 2. Render compilation
            $response = Http::timeout(900)->post('http://ai_api:8001/api/generate_compilation', [
                'clips'           => $clips,
                'output_filename' => $outputFilename
            ]);

            if (!$response->successful()) {
                throw new \Exception("Python API returned HTTP {$response->status()}: {$response->body()}");
            }

            $data = $response->json();
            $generatedReelUrl = $data['data']['output_path'];

            $this->generatedReel->update([
                'status'    => 'completed',
                'file_path' => $generatedReelUrl,
            ]);

            Log::info("[GenerateReelJob] Completed Reel ID: {$this->generatedReel->id}");

        } catch (\Exception $e) {
            Log::error("[GenerateReelJob] Failed for Reel ID {$this->generatedReel->id}: {$e->getMessage()}");
            $this->generatedReel->update([
                'status'    => 'failed',
                'error_log' => $e->getMessage(),
            ]);
            throw $e;
        }
    }

    public function failed(\Throwable $exception): void
    {
        Log::critical("[GenerateReelJob] Permanently failed for Reel ID {$this->generatedReel->id}. Error: {$exception->getMessage()}");
        $this->generatedReel->update([
            'status'    => 'failed',
            'error_log' => "Permanently failed after {$this->tries} tries: {$exception->getMessage()}",
        ]);
    }
}
