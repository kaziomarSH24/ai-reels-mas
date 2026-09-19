<?php

namespace App\Filament\Pages;

use Filament\Pages\Page;
use Filament\Notifications\Notification;
use Illuminate\Support\Facades\Http;
use App\Models\Video;
use App\Models\VideoClip;
use App\Models\GeneratedReel;

class SnapClipStudio extends Page
{
    protected static ?string $navigationIcon = 'heroicon-o-sparkles';
    protected static ?string $navigationLabel = 'SnapClip Studio';
    protected static ?string $title = 'AI Video Studio';
    protected static ?int $navigationSort = 1;

    protected static string $view = 'filament.pages.snap-clip-studio';

    // State Variables
    public $youtubeUrl = '';
    public $isAnalyzing = false;
    public $isGenerating = false;
    
    public $currentVideoId = null;
    public $extractedClips = [];
    public $selectedClipIds = [];
    
    public $generatedReelUrl = null;

    public function analyzeVideo()
    {
        if (empty($this->youtubeUrl)) {
            Notification::make()->title('Please enter a YouTube URL.')->danger()->send();
            return;
        }

        $this->isAnalyzing = true;
        Notification::make()->title('AI Extraction Started')->body('Fetching subtitles and analyzing via Gemini (This will take a minute)...')->info()->send();

        try {
            // Phase 1 API Call
            $response = Http::timeout(300)->post('http://ai_api:8001/api/analyze_video', [
                'youtube_url' => $this->youtubeUrl
            ]);

            if ($response->successful()) {
                $data = $response->json();
                $clipsData = $data['data']['extracted_clips'] ?? [];

                if (count($clipsData) === 0) {
                    Notification::make()->title('No smart phrases found.')->warning()->send();
                    $this->isAnalyzing = false;
                    return;
                }

                // Database Storage
                $video = Video::create([
                    'title' => 'YouTube Extraction ' . uniqid(),
                    'youtube_url' => $this->youtubeUrl,
                    'is_processed' => true,
                ]);

                $this->currentVideoId = $video->id;
                $insertData = [];
                
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
                
                // Load clips to state
                $this->extractedClips = VideoClip::where('video_id', $video->id)->get()->toArray();
                $this->selectedClipIds = [];
                $this->generatedReelUrl = null;

                Notification::make()
                    ->title('AI Analysis Complete! 🎯')
                    ->body("Extracted " . count($clipsData) . " premium phrases.")
                    ->success()
                    ->send();
            } else {
                Notification::make()->title('Python API Error')->body('Check the Python logs.')->danger()->send();
            }
        } catch (\Exception $e) {
            \Illuminate\Support\Facades\Log::error('AI Studio Error: ' . $e->getMessage());
            Notification::make()->title('System Error')->body('Failed to connect to AI Engine.')->danger()->send();
        }

        $this->isAnalyzing = false;
    }

    public function toggleClipSelection($clipId)
    {
        if (in_array($clipId, $this->selectedClipIds)) {
            $this->selectedClipIds = array_diff($this->selectedClipIds, [$clipId]);
        } else {
            $this->selectedClipIds[] = $clipId;
        }
    }

    public function generateReel()
    {
        if (empty($this->selectedClipIds)) {
            Notification::make()->title('Please select at least one clip.')->warning()->send();
            return;
        }

        $this->isGenerating = true;
        Notification::make()->title('Reel Generation Started')->body('Fetching chunks and rendering via FFmpeg/Whisper...')->info()->send();

        try {
            $clipsToProcess = [];
            
            // Build the payload for Python
            foreach ($this->selectedClipIds as $id) {
                $clip = collect($this->extractedClips)->firstWhere('id', $id);
                if ($clip) {
                    $startSec = $this->timeToSeconds($clip['start_time']);
                    $endSec = $this->timeToSeconds($clip['end_time']);
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

            $outputFilename = 'viral_reel_' . uniqid() . '.mp4';
            
            // Phase 2 API Call
            $response = Http::timeout(300)->post('http://ai_api:8001/api/generate_compilation', [
                'clips' => $clipsToProcess,
                'output_filename' => $outputFilename
            ]);

            if ($response->successful()) {
                $data = $response->json();
                $this->generatedReelUrl = $data['data']['output_path'];
                
                // Save to DB
                GeneratedReel::create([
                    'video_id' => $this->currentVideoId,
                    'target_word' => 'Custom Compilation',
                    'file_path' => $this->generatedReelUrl,
                    'is_posted_to_fb' => false,
                ]);
                
                Notification::make()->title('Reel Generated Successfully! 🎉')->success()->send();
            } else {
                $errorData = $response->json();
                Notification::make()->title('Generation Error')->body($errorData['message'] ?? 'Unknown Error')->danger()->send();
            }
        } catch (\Exception $e) {
            \Illuminate\Support\Facades\Log::error('Generation Error: ' . $e->getMessage());
            Notification::make()->title('System Error')->body('FFmpeg rendering failed.')->danger()->send();
        }

        $this->isGenerating = false;
    }

    private function timeToSeconds($timeStr)
    {
        // Handle standard formats or floats passed straight from Python
        if (is_numeric($timeStr)) {
            return (float) $timeStr;
        }
        
        $parts = explode(':', $timeStr);
        if (count($parts) === 3) {
            return ($parts[0] * 3600) + ($parts[1] * 60) + (float)$parts[2];
        }
        return 0;
    }
}
