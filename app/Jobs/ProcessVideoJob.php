<?php

namespace App\Jobs;

use App\Models\Video;
use App\Models\VideoJob;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Queue\Queueable;
use Illuminate\Queue\InteractsWithQueue;
use Illuminate\Queue\SerializesModels;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;

class ProcessVideoJob implements ShouldQueue
{
    use Queueable, InteractsWithQueue, SerializesModels;

    /**
     * Max number of attempts before marking as failed.
     * This covers transient errors. 429 quota errors are handled separately.
     */
    public int $tries = 3;

    /**
     * Max execution time in seconds (1 hour).
     * A long video with a lot of clips over a slow connection can take time.
     */
    public int $timeout = 3600;

    /**
     * Create a new job instance.
     */
    public function __construct(
        public readonly VideoJob $videoJob
    ) {}

    /**
     * Execute the job.
     */
    public function handle(): void
    {
        Log::info("[ProcessVideoJob] Starting job for URL: {$this->videoJob->youtube_url}");

        // 1. Mark as processing
        $this->videoJob->update(['status' => 'processing']);

        try {
            // 2. Call Python API to analyze the video (now supports any source)
            $response = Http::timeout(3500)->post('http://ai_api:8001/api/analyze_video', [
                'youtube_url' => $this->videoJob->youtube_url, // Used as generic URL
                'source_type' => $this->videoJob->source_type,
            ]);

            // 3. Handle Gemini quota exceeded (HTTP 429) - Release back to queue after 60s
            if ($response->status() === 429) {
                Log::warning("[ProcessVideoJob] Gemini quota exceeded. Releasing job in 60 seconds.");
                $this->videoJob->update([
                    'status'      => 'pending',
                    'error_log'   => 'Gemini quota exceeded (429). Retrying in 60s.',
                    'retry_count' => $this->videoJob->retry_count + 1,
                ]);
                // Release back to the queue after 60 seconds
                $this->release(60);
                return;
            }

            if (!$response->successful()) {
                throw new \Exception("Python API returned HTTP {$response->status()}: {$response->body()}");
            }

            // 4. Process the successful response
            $data       = $response->json();
            $clipsData  = $data['data']['extracted_clips'] ?? [];

            if (count($clipsData) === 0) {
                Log::warning("[ProcessVideoJob] No relevant clips found for: {$this->videoJob->youtube_url}");
                $this->videoJob->update(['status' => 'completed', 'error_log' => 'No relevant clips extracted.']);
                return;
            }

            // 5. Extract thumbnail (Only applies if it's YouTube)
            $thumbnailUrl = null;
            if ($this->videoJob->source_type === 'youtube') {
                $youtubeId = $this->extractYoutubeId($this->videoJob->youtube_url);
                $thumbnailUrl = $youtubeId ? "https://img.youtube.com/vi/{$youtubeId}/hqdefault.jpg" : null;
            }

            // 6. Persist the video and its extracted clips
            $video = Video::create([
                'title'         => 'Imported from Queue: ' . now()->format('Y-m-d H:i'),
                'youtube_url'   => $this->videoJob->source_type === 'youtube' ? $this->videoJob->youtube_url : null,
                'source_url'    => $this->videoJob->source_type !== 'youtube' ? $this->videoJob->youtube_url : null,
                'source_type'   => $this->videoJob->source_type,
                'thumbnail_url' => $thumbnailUrl,
                'is_processed'  => true,
            ]);

            $insertData = [];
            $seenExpressions = [];

            foreach ($clipsData as $item) {
                $expression = strtolower(trim($item['expression'] ?? ''));
                $startTime = (float) ($item['rough_start'] ?? 0);
                
                if (empty($expression)) continue;
                
                $isDuplicateTime = false;
                if (isset($seenExpressions[$expression])) {
                    foreach ($seenExpressions[$expression] as $seenTime) {
                        if (abs($seenTime - $startTime) <= 30) {
                            $isDuplicateTime = true;
                            break;
                        }
                    }
                }
                
                if ($isDuplicateTime) {
                    continue; // Skip because it's the exact same word at almost the same timestamp
                }
                
                $seenExpressions[$expression][] = $startTime;

                $insertData[] = [
                    'video_id'             => $video->id,
                    'expression'           => $item['expression'] ?? '',
                    'whisper_target'       => $item['whisper_target'] ?? ($item['expression'] ?? ''),
                    'category'             => $item['category'] ?? 'DAILY_PHRASE',
                    'casual_meaning'       => $item['casual_meaning'] ?? '',
                    'original_sentence'    => $item['original_sentence'] ?? '',
                    'original_translation' => $item['original_translation'] ?? '',
                    'easy_example'         => $item['easy_example'] ?? '',
                    'example_translation'  => $item['example_translation'] ?? '',
                    'start_time'           => strval($item['rough_start'] ?? '0'),
                    'end_time'             => strval($item['rough_end'] ?? '0'),
                    'created_at'           => now(),
                    'updated_at'           => now(),
                ];
            }

            \App\Models\VideoClip::insert($insertData);

            // 7. Mark the job as completed
            $this->videoJob->update(['status' => 'completed']);
            Log::info("[ProcessVideoJob] Completed. Extracted {$video->clips()->count()} clips for: {$this->videoJob->youtube_url}");

            // 8. Anti-YouTube-Ban: Random sleep between 45-90 seconds before the next job
            // This mimics human browsing behavior and prevents IP flagging.
            $sleepSeconds = rand(45, 90);
            Log::info("[ProcessVideoJob] Anti-ban sleep: {$sleepSeconds} seconds before releasing queue.");
            sleep($sleepSeconds);

        } catch (\Exception $e) {
            Log::error("[ProcessVideoJob] Failed for {$this->videoJob->youtube_url}: {$e->getMessage()}");
            $this->videoJob->update([
                'status'    => 'failed',
                'error_log' => $e->getMessage(),
            ]);
            // Re-throw so Horizon marks the job as failed and can retry
            throw $e;
        }
    }

    /**
     * Extract YouTube video ID from a URL.
     */
    private function extractYoutubeId(string $url): ?string
    {
        preg_match('/(?:v=|youtu\.be\/|embed\/)([a-zA-Z0-9_-]{11})/', $url, $matches);
        return $matches[1] ?? null;
    }

    /**
     * Handle a job that has failed after all retries are exhausted.
     */
    public function failed(\Throwable $exception): void
    {
        Log::critical("[ProcessVideoJob] Job permanently failed for: {$this->videoJob->youtube_url}. Error: {$exception->getMessage()}");
        $this->videoJob->update([
            'status'    => 'failed',
            'error_log' => "Permanently failed after {$this->tries} tries: {$exception->getMessage()}",
        ]);
    }
}
