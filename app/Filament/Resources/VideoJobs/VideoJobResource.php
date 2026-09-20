<?php

namespace App\Filament\Resources\VideoJobs;

use App\Filament\Resources\VideoJobs\Pages;
use App\Jobs\ProcessVideoJob;
use App\Models\VideoJob;
use BackedEnum;
use Filament\Actions\Action;
use Filament\Actions\BulkActionGroup;
use Filament\Actions\DeleteAction;
use Filament\Actions\DeleteBulkAction;
use Filament\Forms\Components\Textarea;
use Filament\Notifications\Notification;
use Filament\Resources\Resource;
use Filament\Schemas\Schema;
use Filament\Tables\Columns\TextColumn;
use Filament\Tables\Filters\SelectFilter;
use Filament\Tables\Table;

class VideoJobResource extends Resource
{
    protected static ?string $model = VideoJob::class;
    protected static string|BackedEnum|null $navigationIcon = 'heroicon-o-queue-list';
    protected static ?string $navigationLabel = 'Job Queue';
    protected static string|\UnitEnum|null $navigationGroup = 'AI & Automation';
    protected static ?int $navigationSort = 2;

    public static function form(Schema $schema): Schema
    {
        return $schema->components([
            Textarea::make('youtube_url')
                ->label('YouTube URL')
                ->required()
                ->columnSpanFull(),
        ]);
    }

    public static function table(Table $table): Table
    {
        return $table
            ->columns([
                TextColumn::make('id')
                    ->label('ID')
                    ->sortable()
                    ->width('60px'),

                TextColumn::make('youtube_url')
                    ->label('YouTube URL')
                    ->limit(60)
                    ->tooltip(fn ($record) => $record->youtube_url)
                    ->searchable(),

                TextColumn::make('status')
                    ->label('Status')
                    ->badge()
                    ->color(fn (string $state): string => match ($state) {
                        'pending'    => 'gray',
                        'processing' => 'warning',
                        'completed'  => 'success',
                        'failed'     => 'danger',
                        default      => 'gray',
                    })
                    ->icon(fn (string $state): string => match ($state) {
                        'pending'    => 'heroicon-o-clock',
                        'processing' => 'heroicon-o-arrow-path',
                        'completed'  => 'heroicon-o-check-circle',
                        'failed'     => 'heroicon-o-x-circle',
                        default      => 'heroicon-o-question-mark-circle',
                    })
                    ->sortable(),

                TextColumn::make('retry_count')
                    ->label('Retries')
                    ->sortable()
                    ->alignCenter(),

                TextColumn::make('error_log')
                    ->label('Last Error')
                    ->limit(50)
                    ->tooltip(fn ($record) => $record->error_log)
                    ->color('danger')
                    ->placeholder('—'),

                TextColumn::make('created_at')
                    ->label('Added')
                    ->since()
                    ->sortable(),

                TextColumn::make('updated_at')
                    ->label('Updated')
                    ->since()
                    ->sortable(),
            ])
            ->defaultSort('id', 'desc')
            ->filters([
                SelectFilter::make('status')
                    ->options([
                        'pending'    => 'Pending',
                        'processing' => 'Processing',
                        'completed'  => 'Completed',
                        'failed'     => 'Failed',
                    ]),
            ])
            ->actions([
                // Manually retry a failed job
                Action::make('retry')
                    ->label('Retry')
                    ->icon('heroicon-o-arrow-path')
                    ->color('warning')
                    ->visible(fn (VideoJob $record): bool => $record->status === 'failed')
                    ->action(function (VideoJob $record): void {
                        $record->update(['status' => 'pending', 'error_log' => null, 'retry_count' => 0]);
                        ProcessVideoJob::dispatch($record);
                        Notification::make()->title('Job re-queued successfully!')->success()->send();
                    }),
                
                Action::make('view_log')
                    ->label('View Details')
                    ->icon('heroicon-o-eye')
                    ->color('info')
                    ->modalHeading('Job Details')
                    ->modalDescription(function (VideoJob $record) {
                        if ($record->status === 'failed' || $record->status === 'pending' || $record->status === 'processing') {
                            return $record->error_log ?: 'Job is currently ' . $record->status . '. No errors logged yet.';
                        }
                        
                        // If completed, fetch the video and its clips
                        $video = \App\Models\Video::where('youtube_url', $record->youtube_url)->latest()->first();
                        if (!$video) {
                            return 'Video processed, but no record found in database. ' . ($record->error_log ?: '');
                        }
                        
                        $count = $video->clips()->count();
                        if ($count === 0) {
                            return 'Job completed, but no relevant clips were found to extract. ' . ($record->error_log ?: '');
                        }
                        
                        $expressions = $video->clips()->pluck('expression')->implode(', ');
                        return "Successfully extracted {$count} expressions!\n\nWords/Phrases: {$expressions}";
                    })
                    ->modalSubmitAction(false)
                    ->modalCancelActionLabel('Close'),

                DeleteAction::make(),
            ])
            ->bulkActions([
                BulkActionGroup::make([
                    DeleteBulkAction::make(),
                ]),
            ])
            ->poll('10s'); // Auto-refresh every 10 seconds to show live status
    }

    public static function getRelationsManagers(): array
    {
        return [];
    }

    public static function getPages(): array
    {
        return [
            'index' => Pages\ListVideoJobs::route('/'),
        ];
    }
}
