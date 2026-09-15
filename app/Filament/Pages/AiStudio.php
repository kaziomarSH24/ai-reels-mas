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
                // If it was stuck in processing, let's delete the old data and start fresh
                $existingMovie->delete();
            }
        }

        Notification::make()->title('Extraction Started')->body('Fetching subtitles from YouTube...')->info()->send();

        try {
            $response = Http::timeout(60)->post('http://ai_api:8001/api/analyze_video', [
                'youtube_url' => $url
            ]);

            if ($response->successful()) {
                $data = $response->json();
                $dialogues = $data['data']['dialogues'] ?? [];

                if (count($dialogues) === 0) {
                    Notification::make()->title('No English subtitles found for this video')->danger()->send();
                    return;
                }

                $movie = Movie::create([
                    'title' => 'YouTube Video ' . uniqid(),
                    'youtube_url' => $url,
                    'is_processed' => false,
                ]);

                $insertData = [];
                foreach ($dialogues as $dialogue) {
                    $insertData[] = [
                        'movie_id' => $movie->id,
                        'start_time' => $dialogue['start_time'],
                        'end_time' => $dialogue['end_time'],
                        'text' => $dialogue['text'],
                        'created_at' => now(),
                        'updated_at' => now(),
                    ];
                }

                foreach (array_chunk($insertData, 500) as $chunk) {
                    MovieDialogue::insert($chunk);
                }

                // Initialize Progress State
                $this->currentMovieId = $movie->id;
                $this->totalDialogues = count($dialogues);
                $this->processedDialogues = 0;
                $this->progressPercentage = 0;
                $this->isProcessing = true;

                Notification::make()
                    ->title('Extraction Complete')
                    ->body('Extracted ' . $this->totalDialogues . ' lines. Starting AI Analysis...')
                    ->success()
                    ->send();
                    
                $this->analyzerForm->fill(); // Clear input
                
                // Trigger the background processing loop
                $this->dispatch('processNextBatch');

            } else {
                $errorData = $response->json();
                $error = $errorData['errors'] ?? $errorData['message'] ?? 'Unknown error';
                Notification::make()->title('API Error')->body($error)->danger()->send();
            }
        } catch (\Exception $e) {
            Log::error('Python API Error: ' . $e->getMessage());
            Notification::make()->title('System Error')->body('Failed to connect to AI Engine.')->danger()->send();
        }
    }

    #[On('processNextBatch')]
    public function processNextBatch()
    {
        if (!$this->isProcessing || !$this->currentMovieId) {
            return;
        }

        // Get next 5 unprocessed dialogues
        $pendingDialogues = MovieDialogue::where('movie_id', $this->currentMovieId)
            ->whereNull('emotion')
            ->orderBy('id', 'asc')
            ->limit(5)
            ->get();

        if ($pendingDialogues->isEmpty()) {
            // Processing is complete!
            $this->isProcessing = false;
            $this->progressPercentage = 100;
            Movie::where('id', $this->currentMovieId)->update(['is_processed' => true]);
            
            Notification::make()
                ->title('AI Analysis Complete! 🎉')
                ->body('All dialogues have been processed successfully.')
                ->success()
                ->send();
            return;
        }

        // Prepare batch request for Python
        $textsToAnalyze = $pendingDialogues->pluck('text')->toArray();

        try {
            $response = Http::timeout(30)->post('http://ai_api:8001/api/analyze_batch', [
                'texts' => $textsToAnalyze
            ]);

            if ($response->successful()) {
                $results = $response->json()['data']['results'] ?? [];

                // Update DB with results
                foreach ($pendingDialogues as $index => $dialogue) {
                    $analysis = $results[$index]['analysis'] ?? null;
                    if ($analysis) {
                        $dialogue->update([
                            'emotion' => $analysis['emotion'] ?? null,
                            'cefr_level' => $analysis['cefr_level'] ?? null,
                            'translated_text' => $analysis['translation'] ?? null,
                        ]);
                    } else {
                        // Mark as processed even if AI failed so it doesn't loop forever
                        $dialogue->update(['emotion' => 'UNKNOWN']); 
                    }
                }

                // Update progress
                $this->processedDialogues = MovieDialogue::where('movie_id', $this->currentMovieId)
                    ->whereNotNull('emotion')
                    ->count();
                
                $this->progressPercentage = min(100, round(($this->processedDialogues / $this->totalDialogues) * 100));

                // Dispatch the event to process the next batch (creates a loop)
                $this->dispatch('processNextBatch');
            } else {
                Log::error('Batch Analysis API Error: ' . $response->body());
                $this->isProcessing = false; // Stop loop on error
            }
        } catch (\Exception $e) {
            Log::error('Batch Analysis Exception: ' . $e->getMessage());
            $this->isProcessing = false; // Stop loop on error
        }
    }

}
