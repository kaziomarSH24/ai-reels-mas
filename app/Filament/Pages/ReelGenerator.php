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
use App\Models\MovieDialogue;

class ReelGenerator extends Page implements HasForms
{
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

    public static function getNavigationSort(): ?int
    {
        return 2;
    }

    protected string $view = 'filament.pages.reel-generator';

    public ?array $reelData = [];
    public ?string $generatedReelUrl = null;
    public bool $isGenerating = false;

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
                Section::make('Search and Generate')
                    ->description('Type a keyword to find the most powerful AI-analyzed dialogue and convert it into a 9:16 Reel.')
                    ->schema([
                        TextInput::make('keyword')
                            ->label('Target Keyword')
                            ->placeholder('e.g., Destiny, Boss, Love')
                            ->required(),
                    ])
            ])
            ->statePath('reelData');
    }

    public function generateReelAction(): void
    {
        set_time_limit(0); // Prevent PHP from timing out during heavy FFmpeg processing
        
        $keyword = $this->reelData['keyword'] ?? null;
        if (!$keyword) return;

        // Search the DB for ALL matches (limit to 3 for a nice 15-second reel)
        // We will search by target_word exactly, or text LIKE if target_word doesn't match
        $dialogues = MovieDialogue::with('movie')
            ->where('target_word', 'LIKE', '%' . $keyword . '%')
            ->orWhere('text', 'LIKE', '%' . $keyword . '%')
            ->inRandomOrder()
            ->limit(3)
            ->get();

        if ($dialogues->isEmpty()) {
            Notification::make()->title('No clips found for this keyword')->danger()->send();
            return;
        }

        $this->isGenerating = true;
        Notification::make()->title('Compilation Reel Started')->body('Fetching ' . $dialogues->count() . ' clips from YouTube...')->info()->send();

        try {
            $outputFilename = 'reel_compilation_' . uniqid() . '.mp4';
            
            $clips = [];
            foreach ($dialogues as $dialogue) {
                $startSec = $this->timeToSeconds($dialogue->start_time);
                $endSec = $this->timeToSeconds($dialogue->end_time);
                $duration = max(3, ceil($endSec - $startSec));
                
                $clips[] = [
                    'source_url' => $dialogue->movie->youtube_url,
                    'start_time' => $dialogue->start_time,
                    'duration' => $duration,
                    'english_text' => $dialogue->text,
                    'bengali_text' => $dialogue->translated_text ?? 'An AI thesis project.',
                    'target_word' => $dialogue->target_word ?? $keyword
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
                    'target_word' => $targetWord,
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
