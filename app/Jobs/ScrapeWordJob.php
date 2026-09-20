<?php

namespace App\Jobs;

use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Queue\Queueable;
use Illuminate\Foundation\Bus\Dispatchable;
use Illuminate\Queue\InteractsWithQueue;
use Illuminate\Queue\SerializesModels;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;
use App\Models\ScrapedClip;

class ScrapeWordJob implements ShouldQueue
{
    use Dispatchable, InteractsWithQueue, Queueable, SerializesModels;

    public $timeout = 600; // 10 minutes timeout per word

    protected string $targetWord;

    public function __construct(string $targetWord)
    {
        $this->targetWord = $targetWord;
    }

    public function handle(): void
    {
        Log::info("Starting scrape job for word: " . $this->targetWord);

        try {
            $response = Http::timeout(600)->post('http://python_api:8001/api/scrape_clips', [
                'target_word' => $this->targetWord,
                'max_clips' => 5
            ]);

            if ($response->successful()) {
                $paths = $response->json('data.paths') ?? [];
                
                foreach ($paths as $path) {
                    ScrapedClip::create([
                        'target_word' => $this->targetWord,
                        'file_path' => $path,
                        'source' => 'getyarn.io'
                    ]);
                }
                Log::info("Successfully scraped and saved " . count($paths) . " clips for: " . $this->targetWord);
            } else {
                Log::error("Failed to scrape word: " . $this->targetWord, ['response' => $response->body()]);
                throw new \Exception("Python API returned error");
            }
        } catch (\Exception $e) {
            Log::error("Exception in ScrapeWordJob for " . $this->targetWord . ": " . $e->getMessage());
            // Retry later
            $this->release(60);
        }
    }
}
