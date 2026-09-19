<?php

namespace App\Filament\Pages;

use Filament\Pages\Page;
use Filament\Forms\Concerns\InteractsWithForms;
use Filament\Forms\Contracts\HasForms;
use Filament\Forms\Components\TextInput;
use Filament\Schemas\Components\Actions\Action;
use Filament\Notifications\Notification;
use Filament\Schemas\Components\Section;
use Illuminate\Support\Facades\Http;
use App\Models\VideoClip;

class ReelGenerator extends Page implements HasForms
{
    protected static string|\UnitEnum|null $navigationGroup = 'AI & Automation';
    protected static ?int $navigationSort = 2;

    use InteractsWithForms;

    public static function getNavigationIcon(): string|\BackedEnum|null
    {
        return 'heroicon-o-video-camera';
    }

    public static function getNavigationLabel(): string
    {
        return 'Reel Generator';
    }

    public function getTitle(): string|\Illuminate\Contracts\Support\Htmlable
    {
        return 'Reel Generator (Phase 2)';
    }

    protected string $view = 'filament.pages.reel-generator';

    public ?array $reelData = [];
    public ?string $generatedReelUrl = null;
    public bool $isGenerating = false;
    
    // New properties for search results
    public array $searchResults = [];
    public bool $hasSearched = false;
    public ?string $fetchedMeaning = null;

    public function mount(): void
    {
        $this->generatorForm->fill();
    }

    protected function getForms(): array
    {
        return [
            'generatorForm',
        ];
    }

    public function generatorForm(\Filament\Schemas\Schema $schema): \Filament\Schemas\Schema
    {
        return $schema
            ->schema([
                Section::make('Search and Preview')
                    ->description('Type a keyword to find the most powerful AI-analyzed dialogues. You can preview the clips before generating.')
                    ->schema([
                        \Filament\Forms\Components\TextInput::make('keyword')
                            ->label('Target Keyword')
                            ->placeholder('e.g., Destiny, Boss, Love')
                            ->datalist(function () {
                                return \App\Models\VideoClip::whereNotNull('target_word')
                                    ->where('target_word', '!=', 'None')
                                    ->select('target_word')
                                    ->distinct()
                                    ->limit(100)
                                    ->pluck('target_word')
                                    ->toArray();
                            })
                            ->required(),
                    ])
            ])
            ->statePath('reelData');
    }

    public function searchClipsAction(): void
    {
        $keyword = $this->reelData['keyword'] ?? null;
        if (!$keyword) return;

        // Search the DB for ALL matches (limit to 3 for a nice 15-second compilation reel)
        // Fetch more results to allow for deduplication
        $rawDialogues = VideoClip::with('video')
            ->where('target_word', 'LIKE', '%' . $keyword . '%')
            ->orWhere('text', 'LIKE', '%' . $keyword . '%')
            ->inRandomOrder()
            ->limit(20)
            ->get();


        // Filter out duplicate text to prevent the same sentence from appearing 3 times
        $dialogues = $rawDialogues->unique('text')->take(3);

        if ($dialogues->isEmpty()) {
            Notification::make()->title('No clips found for this keyword')->danger()->send();
            $this->searchResults = [];
            $this->hasSearched = true;
            return;
        }

        // ==========================================
        // JUST-IN-TIME (JIT) AI TRANSLATION
        // ==========================================
        $untranslated = $dialogues->filter(fn($d) => empty($d->translated_text) || str_contains($d->translated_text, "Will translate"));
        
        

        $results = [];
        foreach ($dialogues as $d) {
            $results[] = [
                'id' => $d->id,
                'video_id' => $d->video_id,
                'start_time' => $d->start_time,
                'end_time' => $d->end_time,
                'youtube_url' => $d->video->youtube_url,
                'expression' => $d->expression,
                'whisper_target' => $d->whisper_target,
                'casual_meaning' => $d->casual_meaning,
                'easy_example' => $d->easy_example,
                'example_translation' => $d->example_translation,
            ];
        }

        $this->searchResults = $results;
        $this->hasSearched = true;
        $this->generatedReelUrl = null; // reset if searching again
        
        Notification::make()->title('Clips Found!')->body('Found ' . count($results) . ' matching clips. Preview them below before generating.')->success()->send();
    }

    public function generateReelAction(): void
    {
        set_time_limit(0); 
        
        $keyword = $this->reelData['keyword'] ?? null;
        if (empty($this->searchResults)) {
            Notification::make()->title('Please search for clips first.')->danger()->send();
            return;
        }

        $this->isGenerating = true;
        Notification::make()->title('Compilation Reel Started')->body('Fetching clips from YouTube and generating reel...')->info()->send();

        try {
            $outputFilename = 'reel_compilation_' . uniqid() . '.mp4';
            
            $clips = [];
            foreach ($this->searchResults as $dialogue) {
                $startSec = $this->timeToSeconds($dialogue['start_time']);
                $endSec = $this->timeToSeconds($dialogue['end_time']);
                $duration = max(3, ceil($endSec - $startSec));
                
                $clips[] = [
                    'source_url' => $dialogue['youtube_url'],
                    'start_time' => $dialogue['start_time'],
                    'end_time' => $dialogue['end_time'],
                    'duration' => $duration,
                    'expression' => $dialogue['expression'],
                    'whisper_target' => $dialogue['whisper_target'],
                    'casual_meaning' => $dialogue['casual_meaning'],
                    'easy_example' => $dialogue['easy_example'],
                    'example_translation' => $dialogue['example_translation'],
                ];
            }
            
            $response = Http::timeout(300)->post('http://ai_api:8001/api/generate_compilation', [
                'clips' => $clips,
                'output_filename' => $outputFilename
            ]);

            if ($response->successful()) {
                $data = $response->json();
                $this->generatedReelUrl = $data['data']['output_path'];
                
                // Save to database
                \App\Models\GeneratedReel::create([
                    'target_word' => $keyword ?? 'Compilation',
                    'file_path' => $this->generatedReelUrl,
                    'is_posted_to_fb' => false,
                ]);
                
                Notification::make()->title('Reel Generated & Saved!')->success()->send();
            } else {
                $errorData = $response->json();
                $error = $errorData['errors'] ?? $errorData['message'] ?? 'Unknown error';
                Notification::make()->title('FFmpeg Error')->body($error)->danger()->send();
            }
        } catch (\Exception $e) {
            Notification::make()->title('System Error')->body($e->getMessage())->danger()->send();
        }

        $this->isGenerating = false;
    }

    private function timeToSeconds($timeStr)
    {
        $parts = explode(':', $timeStr);
        if (count($parts) === 3) {
            return ($parts[0] * 3600) + ($parts[1] * 60) + (float)$parts[2];
        }
        return 0;
    }
}
