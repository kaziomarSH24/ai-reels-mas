<?php

namespace App\Filament\Pages;

use Filament\Pages\Page;
use Filament\Forms\Concerns\InteractsWithForms;
use Filament\Forms\Contracts\HasForms;
use Filament\Schemas\Schema;
use Filament\Forms\Components\TextInput;
use Filament\Tables\Concerns\InteractsWithTable;
use Filament\Tables\Contracts\HasTable;
use Filament\Tables\Table;
use Filament\Tables\Columns\TextColumn;
use Filament\Notifications\Notification;
use Illuminate\Support\Facades\Http;
use App\Models\Movie;
use App\Models\MovieDialogue;
use Illuminate\Support\Facades\Log;
use Livewire\Attributes\On;
use BackedEnum;
use Filament\Actions\Action;
use Filament\Schemas\Components\Section;

class AiStudio extends Page implements HasForms, HasTable
{
    use InteractsWithForms, InteractsWithTable;

    protected string $view = 'filament.pages.ai-studio-native';

    public static function getNavigationIcon(): string|BackedEnum|null
    {
        return 'heroicon-o-sparkles';
    }

    public static function getNavigationLabel(): string
    {
        return 'AI Studio';
    }

    public static function getNavigationSort(): ?int
    {
        return 1;
    }

    public ?array $analyzerData = [];
    public ?array $generatorData = [];

    // Live Processing State
    public ?int $currentMovieId = null;
    public int $totalDialogues = 0;
    public int $processedDialogues = 0;
    public bool $isProcessing = false;
    public int $progressPercentage = 0;

    public function mount(): void
    {
        $this->analyzerForm->fill();
    }

    protected function getForms(): array
    {
        return [
            'analyzerForm',
        ];
    }

    public function analyzerForm(Schema $form): Schema
    {
        return $form
            ->schema([
                Section::make('1. The Analyzer (Input)')
                    ->description('Paste a YouTube URL. Our AI will fetch subtitles, detect emotions, and save timestamps.')
                    ->icon('heroicon-m-bolt')
                    ->schema([
                        TextInput::make('youtubeUrl')
                            ->label('YouTube URL')
                            ->placeholder('https://youtube.com/watch?v=...')
                            ->url()
                            ->required()
                            ->prefixIcon('heroicon-m-link'),
                    ])
                    ->headerActions([
                        Action::make('analyze')
                            ->label('Extract & Analyze')
                            ->color('success')
                            ->icon('heroicon-m-cpu-chip')
                            ->action('analyzeVideo')
                    ]),
            ])
            ->statePath('analyzerData');
    }

    public function table(Table $table): Table
    {
        return $table
            ->query(
                MovieDialogue::query()
                    ->where('movie_id', $this->currentMovieId)
                    ->orderBy('id', 'asc')
            )
            ->poll($this->isProcessing ? '2s' : null) // Auto-refresh table every 2s during processing!
            ->columns([
                TextColumn::make('start_time')
                    ->label('Time')
                    ->badge()
                    ->color('gray'),
                TextColumn::make('text')
                    ->label('Original Text')
                    ->wrap()
                    ->searchable(),
                TextColumn::make('emotion')
                    ->label('Emotion AI')
                    ->badge()
                    ->color(fn (string $state): string => match ($state) {
                        'JOY' => 'success',
                        'ANGER' => 'danger',
                        'SADNESS' => 'warning',
                        'FEAR' => 'danger',
                        'SURPRISE' => 'info',
                        'LOVE' => 'pink',
                        default => 'gray',
                    })
                    ->placeholder('Analyzing...'),
                TextColumn::make('translated_text')
                    ->label('Bangla Translation')
                    ->wrap()
                    ->placeholder('Analyzing...'),
                TextColumn::make('cefr_level')
                    ->label('Difficulty')
                    ->badge()
                    ->placeholder('Analyzing...'),
            ])
            ->paginated([5, 10, 25, 50, 'all'])
            ->defaultPaginationPageOption(10);
    }

    public function analyzeVideo()
    {
        $url = $this->analyzerData['youtubeUrl'] ?? null;

        if (empty($url)) {
            Notification::make()->title('Please enter a YouTube URL')->danger()->send();
            return;
        }

        // Check if the video is already in the database
        $existingMovie = Movie::where('youtube_url', $url)->first();
        if ($existingMovie) {
            if ($existingMovie->is_processed) {
                Notification::make()
                    ->title('Already Analyzed')
                    ->body('This video has already been processed and is in the database.')
                    ->info()
                    ->send();
                
                $this->currentMovieId = $existingMovie->id;
                $this->isProcessing = false;
                $this->progressPercentage = 100;
                $this->analyzerForm->fill();
                return;
            } else {
                $existingMovie->delete();
            }
        }

        Notification::make()->title('AI Extraction Started')->body('Fetching subtitles and running CEFR Filter (This may take a minute)...')->info()->send();

        try {
            // Increased timeout because Python is now processing everything
            $response = Http::timeout(300)->post('http://ai_api:8001/api/analyze_video', [
                'youtube_url' => $url
            ]);

            if ($response->successful()) {
                $data = $response->json();
                $accepted = $data['data']['accepted'] ?? [];
                $stats = $data['data']['stats'] ?? [];

                if (count($accepted) === 0) {
                    Notification::make()->title('No advanced B2/C1 vocabulary found')->warning()->send();
                    return;
                }

                $movie = Movie::create([
                    'title' => 'YouTube Video ' . uniqid(),
                    'youtube_url' => $url,
                    'is_processed' => true,
                ]);

                $insertData = [];
                foreach ($accepted as $dialogue) {
                    $insertData[] = [
                        'movie_id' => $movie->id,
                        'start_time' => $dialogue['start_time'],
                        'end_time' => $dialogue['end_time'],
                        'text' => $dialogue['text'],
                        'emotion' => $dialogue['analysis']['emotion'] ?? null,
                        'cefr_level' => $dialogue['analysis']['cefr_level'] ?? null,
                        'translated_text' => $dialogue['analysis']['translation'] ?? null,
                        'created_at' => now(),
                        'updated_at' => now(),
                    ];
                }

                foreach (array_chunk($insertData, 500) as $chunk) {
                    MovieDialogue::insert($chunk);
                }

                $this->currentMovieId = $movie->id;
                $this->isProcessing = false;
                $this->progressPercentage = 100;
                $this->analyzerForm->fill(); // Clear input
                
                // Show impressive stats to the Sirs
                Notification::make()
                    ->title('AI Analysis Complete! 🎯')
                    ->body("Scanned: {$stats['total_scanned']} lines. Rejected (Easy): {$stats['rejected_count']}. Saved (Advanced): {$stats['accepted_count']}.")
                    ->success()
                    ->duration(10000)
                    ->send();

            } else {
                $errorData = $response->json();
                $error = $errorData['errors'] ?? $errorData['message'] ?? 'Unknown error';
                Notification::make()->title('API Error')->body($error)->danger()->send();
            }
        } catch (\Exception $e) {
            \Illuminate\Support\Facades\Log::error('Python API Error: ' . $e->getMessage());
            Notification::make()->title('System Error')->body('Failed to connect to AI Engine.')->danger()->send();
        }
    }
}
