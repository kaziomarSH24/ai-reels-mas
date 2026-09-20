<?php

namespace App\Filament\Resources\VideoClips\Tables;

use Filament\Tables\Table;
use App\Models\VideoClip;
use Filament\Actions\BulkActionGroup;
use Filament\Actions\DeleteBulkAction;
use Filament\Actions\EditAction;
use Filament\Actions\ViewAction;
use Filament\Actions\BulkAction;
use Illuminate\Database\Eloquent\Collection;
use Illuminate\Support\Facades\Http;
use Filament\Notifications\Notification;
use App\Models\GeneratedReel;
use App\Jobs\GenerateReelJob;
use Illuminate\Support\Facades\Log;
use Filament\Infolists\Components\TextEntry;
use Filament\Schemas\Components\Section;
use Filament\Schemas\Components\Grid;
use Filament\Schemas\Components\Group;
use Filament\Tables\Columns\TextColumn;
use Filament\Tables\Filters\SelectFilter;






class VideoClipsTable
{
    public static function configure(Table $table): Table
    {
        return $table
            ->columns([
                TextColumn::make('video.title')
                    ->label('Video Source')
                    ->searchable()
                    ->sortable()
                    ->toggleable(isToggledHiddenByDefault: true),
                
                TextColumn::make('time_range')
                    ->label('Time (Start - End)')
                    ->state(function (VideoClip $record): string {
                        $formatTime = function ($seconds) {
                            $sec = (int) $seconds;
                            return $sec >= 3600 ? gmdate("H:i:s", $sec) : gmdate("i:s", $sec);
                        };
                        $start = $formatTime($record->start_time);
                        $end = $formatTime($record->end_time);
                        return "{$start} - {$end}";
                    })
                    ->badge()
                    ->color('gray'),

                TextColumn::make('category')
                    ->label('Category')
                    ->badge()
                    ->color(fn (?string $state): string => match ($state) {
                        'IDIOM' => 'danger',
                        'DAILY_PHRASE' => 'success',
                        'ADVANCED_WORD' => 'info',
                        default => 'gray',
                    })
                    ->searchable(),

                TextColumn::make('expression')
                    ->label('Expression / Phrase')
                    ->badge()
                    ->color('primary')
                    ->searchable()
                    ->sortable(),

                TextColumn::make('original_sentence')
                    ->label('Original Sentence')
                    ->wrap()
                    ->searchable()
                    ->toggleable(isToggledHiddenByDefault: true),
                    
                TextColumn::make('whisper_target')
                    ->label('Whisper Target')
                    ->color('warning')
                    ->searchable()
                    ->toggleable(isToggledHiddenByDefault: true),

                TextColumn::make('casual_meaning')
                    ->label('Casual Meaning')
                    ->wrap()
                    ->searchable(),

                TextColumn::make('easy_example')
                    ->label('Easy Example')
                    ->wrap()
                    ->searchable(),

                TextColumn::make('created_at')
                    ->dateTime()
                    ->sortable()
                    ->toggleable(isToggledHiddenByDefault: true),
            ])
            ->filters([
                SelectFilter::make('category')
                    ->options([
                        'IDIOM' => 'Idiom',
                        'DAILY_PHRASE' => 'Daily Phrase',
                        'ADVANCED_WORD' => 'Advanced Word',
                    ]),
            ])
            ->recordActions([
                ViewAction::make()
                    ->modalHeading('Clip Details')
                    ->modalWidth('4xl')
                    ->infolist([
                        Section::make('Core AI Extraction')
                            ->icon('heroicon-o-sparkles')
                            ->schema([
                                Grid::make(2)->schema([
                                    Group::make([
                                        TextEntry::make('expression')
                                            ->label('Target Expression')
                                            ->size('text-2xl')
                                            ->weight('bold')
                                            ->color('primary'),
                                        TextEntry::make('category')
                                            ->badge()
                                            ->color(fn (?string $state): string => match ($state) {
                                                'IDIOM' => 'danger',
                                                'DAILY_PHRASE' => 'success',
                                                'ADVANCED_WORD' => 'info',
                                                default => 'gray',
                                            }),
                                    ]),
                                    Group::make([
                                        TextEntry::make('casual_meaning')
                                            ->label('Bengali Meaning')
                                            ->size('text-lg')
                                            ->color('success'),
                                        TextEntry::make('whisper_target')
                                            ->label('Whisper Alignment Target')
                                            ->color('warning')
                                            ->icon('heroicon-m-microphone'),
                                    ]),
                                ]),
                            ]),
                            
                        Grid::make(2)
                            ->schema([
                                Section::make('Original Source')
                                    ->columnSpan(1)
                                    ->icon('heroicon-o-video-camera')
                                    ->schema([
                                        TextEntry::make('original_sentence')
                                            ->label('Spoken Dialogue'),
                                        TextEntry::make('original_translation')
                                            ->label('Translation')
                                            ->color('gray'),
                                        TextEntry::make('time_range')
                                            ->label('Timestamps')
                                            ->state(function ($record) {
                                                $formatTime = function ($seconds) {
                                                    $sec = (int) $seconds;
                                                    return $sec >= 3600 ? gmdate("H:i:s", $sec) : gmdate("i:s", $sec);
                                                };
                                                $start = $formatTime($record->start_time);
                                                $end = $formatTime($record->end_time);
                                                return "{$start}  —  {$end}   (" . number_format((float)$record->start_time, 1) . "s to " . number_format((float)$record->end_time, 1) . "s)";
                                            })
                                            ->fontFamily('mono')
                                            ->icon('heroicon-m-clock'),
                                    ]),

                                Section::make('Generated Reel UI')
                                    ->columnSpan(1)
                                    ->icon('heroicon-o-film')
                                    ->schema([
                                        TextEntry::make('easy_example')
                                            ->label('Easy Example'),
                                        TextEntry::make('example_translation')
                                            ->label('Bengali Translation')
                                            ->color('gray'),
                                    ]),
                            ]),
                    ]),
                EditAction::make(),
            ])
            ->toolbarActions([
                BulkActionGroup::make([
                    BulkAction::make('generate_reel')
                        ->label('Generate Reel')
                        ->icon('heroicon-o-film')
                        ->color('success')
                        ->requiresConfirmation()
                        ->modalHeading('Generate AI Reel')
                        ->modalDescription('Are you sure you want to combine the selected clips into a final video reel? This will trigger the AI rendering engine.')
                        ->modalSubmitActionLabel('Yes, Generate Reel')
                        ->action(function (Collection $records) {
                            $clipsToProcess = [];
                            
                            foreach ($records as $clip) {
                                $timeToSeconds = function($timeStr) {
                                    if (is_numeric($timeStr)) return (float) $timeStr;
                                    $parts = explode(':', $timeStr);
                                    if (count($parts) === 3) return ($parts[0] * 3600) + ($parts[1] * 60) + (float)$parts[2];
                                    return 0.0;
                                };

                                $startSec = $timeToSeconds($clip->start_time);
                                $endSec = $timeToSeconds($clip->end_time);
                                $duration = max(3, ceil($endSec - $startSec));
                                
                                $clipsToProcess[] = [
                                    'source_url' => $clip->video->youtube_url ?? '',
                                    'start_time' => $clip->start_time,
                                    'end_time' => $clip->end_time,
                                    'duration' => $duration,
                                    'expression' => $clip->expression,
                                    'whisper_target' => $clip->whisper_target,
                                    'casual_meaning' => $clip->casual_meaning,
                                    'easy_example' => $clip->easy_example,
                                    'example_translation' => $clip->example_translation,
                                ];
                            }
                            
                            if (empty($clipsToProcess)) {
                                Notification::make()->title('No valid clips selected')->warning()->send();
                                return;
                            }

                            try {
                                // Use first clip's video_id as reference
                                $videoId = $records->first()->video_id ?? null;
                                
                                $expressionsTitle = $records->pluck('expression')->unique()->take(3)->implode(', ');
                                if ($records->count() > 3) $expressionsTitle .= '...';

                                $generatedReel = GeneratedReel::create([
                                    'video_id' => $videoId,
                                    'target_word' => $expressionsTitle,
                                    'status' => 'pending',
                                    'file_path' => null,
                                    'is_posted_to_fb' => false,
                                ]);
                                
                                GenerateReelJob::dispatch($generatedReel, $clipsToProcess);
                                
                                Notification::make()
                                    ->title('Rendering Started!')
                                    ->body('Your reel generation has been queued. You can track its progress in the Generated Reels page.')
                                    ->success()
                                    ->send();
                            } catch (\Exception $e) {
                                Log::error('Generation Error (BulkAction): ' . $e->getMessage());
                                Notification::make()->title('System Error')->body('Failed to queue job. Check logs for details.')->danger()->send();
                            }
                        })
                        ->deselectRecordsAfterCompletion(),
                    DeleteBulkAction::make(),
                ]),
            ])
            ->paginated([50, 100, 500, 'all'])
            ->defaultPaginationPageOption(100);
    }
}
