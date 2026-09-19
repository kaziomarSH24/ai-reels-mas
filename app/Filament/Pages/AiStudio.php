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
use App\Models\Video;
use App\Models\VideoClip;
use Illuminate\Support\Facades\Log;
use Livewire\Attributes\On;
use BackedEnum;
use Filament\Actions\Action;
use Filament\Schemas\Components\Section;

class AiStudio extends Page implements HasForms, HasTable
{
    protected static string|\UnitEnum|null $navigationGroup = 'AI & Automation';
    protected static ?int $navigationSort = 4;

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
    public ?int $currentVideoId = null;
    public int $totalDialogues = 0;
    public int $processedDialogues = 0;
    public bool $isProcessing = false;
    public int $progressPercentage = 0;

    public function mount(): void
    {
        $this->analyzerForm->fill();
    }



    protected function getHeaderActions(): array
    {
        return [
            \Filament\Actions\Action::make('uploadCookies')
                ->label('Upload YouTube Cookies')
                ->icon('heroicon-o-key')
                ->color('warning')
                ->form([
                    \Filament\Forms\Components\FileUpload::make('cookie_file')
                        ->label('cookies.txt File')
                        ->acceptedFileTypes(['text/plain'])
                        ->required()
                        ->disk('public')
                        ->helperText('Upload your new YouTube cookies.txt. This will replace the old one.'),
                ])
                ->action(function (array $data) {
                    $disk = \Illuminate\Support\Facades\Storage::disk('public');
                    $path = $disk->path($data['cookie_file']);
                    
                    if (file_exists($path)) {
                        if (file_exists(base_path('python_engine/cookies.txt'))) {
                            @unlink(base_path('python_engine/cookies.txt'));
                        }
                        if (file_exists(base_path('cookies.txt'))) {
                            @unlink(base_path('cookies.txt'));
                        }
                        copy($path, base_path('python_engine/cookies.txt'));
                        copy($path, base_path('cookies.txt'));
                        \Filament\Notifications\Notification::make()->title('Cookies successfully updated!')->success()->send();
                    } else {
                        \Filament\Notifications\Notification::make()->title('Error: File path not found ('.$path.')')->danger()->send();
                    }
                }),
        ];
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
                VideoClip::query()
                     
                    ->latest('id')
            )
            ->poll($this->isProcessing ? '2s' : null) // Auto-refresh table every 2s during processing!
            ->columns([
                TextColumn::make('start_time')
                    ->label('Time')
                    ->badge()
                    ->color('gray'),
                TextColumn::make('original_sentence')
                    ->label('Original Text')
                    ->wrap()
                    ->searchable(),
                
                TextColumn::make('original_translation')
                    ->label('Bangla Translation')
                    ->wrap()
                    ->placeholder('Analyzing...'),
                TextColumn::make('expression')
                    ->label('Target Word')
                    ->badge()
                    ->color('warning')
                    ->searchable(),
                TextColumn::make('category')
                    ->label('Type')
                    ->color(fn (string $state): string => match ($state) { 'IDIOM' => 'danger', 'HARD_WORD' => 'warning', default => 'gray' })
                    ->badge()
                    
                    ->placeholder('Analyzing...'),
            ])
            ->paginated([5, 10, 25, 50, 'all'])
            ->defaultPaginationPageOption(10);
    }

    public function getTabs(): array
    {
        return [
            'all' => \Filament\Tables\Components\Tab::make('All Dialogues'),
            'accepted' => \Filament\Tables\Components\Tab::make('Extracted Vocabulary')
                ->modifyQueryUsing(fn ($query) => $query->whereNotNull('category')),
            
                        'end_time' => $dialogue['end_time'],
                        'text' => $dialogue['text'],
                        'emotion' => $dialogue['analysis']['emotion'] ?? null,
                        'emotion_confidence' => $dialogue['analysis']['emotion_confidence'] ?? null,
                        'cefr_level' => $dialogue['analysis']['cefr_level'] ?? null,
                        'cefr_confidence' => $dialogue['analysis']['cefr_confidence'] ?? null,
                        'target_word' => $dialogue['analysis']['target_word'] ?? null,
                        'translated_text' => $dialogue['analysis']['translation'] ?? null,
                        'created_at' => now(),
                        'updated_at' => now(),
                    ];
                }
                
                // Save Rejected (A1, A2, B1) so the Sir can see them
                foreach ($rejected as $dialogue) {
                    $insertData[] = [
                        'video_id' => $video->id,
                        'start_time' => $dialogue['start_time'],
                        'end_time' => $dialogue['end_time'],
                        'text' => $dialogue['text'],
                        'emotion' => $dialogue['analysis']['emotion'] ?? null,
                        'emotion_confidence' => $dialogue['analysis']['emotion_confidence'] ?? null,
                        'cefr_level' => $dialogue['analysis']['cefr_level'] ?? null,
                        'cefr_confidence' => $dialogue['analysis']['cefr_confidence'] ?? null,
                        'target_word' => $dialogue['analysis']['target_word'] ?? null,
                        'translated_text' => $dialogue['analysis']['translation'] ?? null,
                        'created_at' => now(),
                        'updated_at' => now(),
                    ];
                }

                foreach (array_chunk($insertData, 500) as $chunk) {
                    VideoClip::insert($chunk);
                }

                $this->currentVideoId = $video->id;
                $this->isProcessing = false;
                $this->progressPercentage = 100;
                $this->analyzerForm->fill(); // Clear input
                
                // Show impressive stats to the Sirs
                Notification::make()
                    ->title('AI Analysis Complete! 🎯')
                    ->body("Scanned: {$stats['total_scanned']} lines. Extracted: {$stats['extracted_count']} smart phrases.")
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
