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
        $keyword = $this->reelData['keyword'] ?? null;
        if (!$keyword) return;

        // Search the DB for the best match
        $dialogue = MovieDialogue::with('movie')
            ->where('text', 'LIKE', '%' . $keyword . '%')
            ->orderBy('id', 'desc')
            ->first();

        if (!$dialogue) {
            Notification::make()->title('No clips found for this keyword')->danger()->send();
            return;
        }

        $this->isGenerating = true;
        Notification::make()->title('Starting FFmpeg Generator')->body('Clipping video from YouTube...')->info()->send();

        // Calculate duration
        $startSec = $this->timeToSeconds($dialogue->start_time);
        $endSec = $this->timeToSeconds($dialogue->end_time);
        $duration = max(3, ceil($endSec - $startSec)); // at least 3 seconds

        try {
            $outputFilename = 'reel_' . uniqid() . '.mp4';
            
            $response = Http::timeout(120)->post('http://ai_api:8001/api/generate_reel', [
                'source_url' => $dialogue->movie->youtube_url,
                'start_time' => $dialogue->start_time,
                'duration' => $duration,
                'output_filename' => $outputFilename,
                'english_text' => $dialogue->text,
                'bengali_text' => $dialogue->translated_text ?? 'An AI thesis project.'
            ]);

            if ($response->successful()) {
                $data = $response->json();
                $this->generatedReelUrl = $data['data']['output_path'];
                Notification::make()->title('Reel Generated!')->success()->send();
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
