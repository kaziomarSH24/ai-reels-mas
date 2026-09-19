<?php

namespace App\Filament\Pages;

use Filament\Pages\Page;
use Filament\Notifications\Notification;
use Illuminate\Support\Facades\Http;
use App\Models\Video;
use App\Models\VideoClip;
use App\Models\GeneratedReel;
use Illuminate\Support\Facades\Log;

/**
 * SnapClipStudio acts as the primary user interface for the AI Video pipeline.
 * It manages the lifecycle of video extraction (Phase 1) and compilation (Phase 2).
 */
class SnapClipStudio extends Page
{
    protected string $view = 'filament.pages.snap-clip-studio';
    protected static ?int $navigationSort = 1;

    // Component State
    public string $youtubeUrl = '';
    public bool $isAnalyzing = false;
    public bool $isGenerating = false;
    
    public ?int $currentVideoId = null;
    public array $extractedClips = [];
    public array $selectedClipIds = [];
    
    public ?string $generatedReelUrl = null;

    /**
     * Define the navigation icon for the Filament sidebar.
     */
    public static function getNavigationIcon(): string|\BackedEnum|null
    {
        return 'heroicon-o-sparkles';
    }

    /**
     * Define the label displayed in the Filament sidebar navigation.
     */
    public static function getNavigationLabel(): string
    {
        return 'SnapClip Studio';
    }

    /**
     * Define the page title.
     */
    public function getTitle(): string|\Illuminate\Contracts\Support\Htmlable
    {
        return 'SnapClip Studio';
    }

    /**
     * Initiates the Phase 1 extraction process.
     * Sends the YouTube URL to the Python AI engine for dialogue extraction.
     */
    public function analyzeVideo(): void
    {
        if (empty($this->youtubeUrl)) {
            Notification::make()->title('Please enter a valid YouTube URL.')->danger()->send();
            return;
        }

        $this->isAnalyzing = true;
        Notification::make()->title('Analysis Started')->body('Processing video content...')->info()->send();

        try {
            $response = Http::timeout(300)->post('http://ai_api:8001/api/analyze_video', [
                'youtube_url' => $this->youtubeUrl
            ]);

            if ($response->successful()) {
                $data = $response->json();
                $clipsData = $data['data']['extracted_clips'] ?? [];

                if (count($clipsData) === 0) {
                    Notification::make()->title('No relevant segments found.')->warning()->send();
                    $this->isAnalyzing = false;
                    return;
                }

                // Persist the parsed video session
                $video = Video::create([
                    'title' => 'Video Processed: ' . now()->format('Y-m-d H:i'),
                    'youtube_url' => $this->youtubeUrl,
                    'is_processed' => true,
                ]);

                $this->currentVideoId = $video->id;
                $insertData = [];
                
                // Format the AI payload for database insertion
                foreach ($clipsData as $item) {
                    $insertData[] = [
                        'video_id' => $video->id,
                        'expression' => $item['expression'] ?? '',
                        'whisper_target' => $item['whisper_target'] ?? null,
                        'category' => $item['category'] ?? null,
                        'casual_meaning' => $item['casual_meaning'] ?? null,
                        'original_sentence' => $item['original_sentence'] ?? '',
                        'original_translation' => $item['original_translation'] ?? null,
                        'easy_example' => $item['easy_example'] ?? null,
                        'example_translation' => $item['example_translation'] ?? null,
                        'start_time' => strval($item['rough_start'] ?? '0'),
                        'end_time' => strval($item['rough_end'] ?? '0'),
                        'created_at' => now(),
                        'updated_at' => now(),
                    ];
                }

                VideoClip::insert($insertData);
                
                // Refresh component state with newly inserted records
                $this->extractedClips = VideoClip::where('video_id', $video->id)->get()->toArray();
                $this->selectedClipIds = [];
                $this->generatedReelUrl = null;

                Notification::make()
                    ->title('Analysis Complete')
                    ->body('Successfully extracted ' . count($clipsData) . ' segments.')
                    ->success()
                    ->send();
            } else {
                Notification::make()->title('Processing Error')->body('Unable to analyze video.')->danger()->send();
            }
        } catch (\Exception $e) {
            Log::error('SnapClip Studio Error: ' . $e->getMessage());
            Notification::make()->title('System Error')->body('Connection to processing engine failed.')->danger()->send();
        }

        $this->isAnalyzing = false;
    }

    /**
     * Toggles the selection state of a specific clip for final generation.
     */
    public function toggleClipSelection(int $clipId): void
    {
        if (in_array($clipId, $this->selectedClipIds)) {
            $this->selectedClipIds = array_diff($this->selectedClipIds, [$clipId]);
        } else {
            $this->selectedClipIds[] = $clipId;
        }
    }

    /**
     * Initiates the Phase 2 video generation pipeline.
     * Submits the curated clip metadata to the Python engine for FFmpeg rendering.
     */
    public function generateReel(): void
    {
        if (empty($this->selectedClipIds)) {
            Notification::make()->title('Selection Required')->body('Please select at least one segment.')->warning()->send();
            return;
        }

        $this->isGenerating = true;
        Notification::make()->title('Generation Started')->body('Rendering final video output...')->info()->send();

        try {
            $clipsToProcess = [];
            
            // Map the selected database records into the API payload structure
            foreach ($this->selectedClipIds as $id) {
                $clip = collect($this->extractedClips)->firstWhere('id', $id);
                if ($clip) {
                    $startSec = $this->timeToSeconds($clip['start_time']);
                    $endSec = $this->timeToSeconds($clip['end_time']);
                    
                    // Enforce a minimum 3-second duration for better viewing experience
                    $duration = max(3, ceil($endSec - $startSec));
                    
                    $clipsToProcess[] = [
                        'source_url' => $this->youtubeUrl,
                        'start_time' => $clip['start_time'],
                        'end_time' => $clip['end_time'],
                        'duration' => $duration,
                        'expression' => $clip['expression'],
                        'whisper_target' => $clip['whisper_target'],
                        'casual_meaning' => $clip['casual_meaning'],
                        'easy_example' => $clip['easy_example'],
                        'example_translation' => $clip['example_translation'],
                    ];
                }
            }

            $outputFilename = 'reel_export_' . uniqid() . '.mp4';
            
            $response = Http::timeout(300)->post('http://ai_api:8001/api/generate_compilation', [
                'clips' => $clipsToProcess,
                'output_filename' => $outputFilename
            ]);

            if ($response->successful()) {
                $data = $response->json();
                $this->generatedReelUrl = $data['data']['output_path'];
                
                GeneratedReel::create([
                    'video_id' => $this->currentVideoId,
                    'target_word' => 'Export: ' . count($clipsToProcess) . ' Clips',
                    'file_path' => $this->generatedReelUrl,
                    'is_posted_to_fb' => false,
                ]);
                
                Notification::make()->title('Export Ready')->success()->send();
            } else {
                $errorData = $response->json();
                Notification::make()->title('Rendering Failed')->body($errorData['message'] ?? 'Unknown Error')->danger()->send();
            }
        } catch (\Exception $e) {
            Log::error('Generation Error: ' . $e->getMessage());
            Notification::make()->title('System Error')->body('FFmpeg rendering service is unreachable.')->danger()->send();
        }

        $this->isGenerating = false;
    }

    /**
     * Converts a timestamp string (e.g., "00:01:23.450" or "83.45") into total seconds.
     */
    private function timeToSeconds(string $timeStr): float
    {
        if (is_numeric($timeStr)) {
            return (float) $timeStr;
        }
        
        $parts = explode(':', $timeStr);
        if (count($parts) === 3) {
            return ($parts[0] * 3600) + ($parts[1] * 60) + (float)$parts[2];
        }
        
        return 0.0;
    }
}
