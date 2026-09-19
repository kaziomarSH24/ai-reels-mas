<?php

namespace App\Filament\Resources\VideoClips\Tables;

use Filament\Actions\BulkActionGroup;
use Filament\Actions\DeleteBulkAction;
use Filament\Actions\EditAction;
use Filament\Tables\Columns\TextColumn;
use Filament\Tables\Table;
use App\Models\VideoClip;

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
                        return number_format((float)$record->start_time, 1) . 's - ' . number_format((float)$record->end_time, 1) . 's';
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
                \Filament\Tables\Filters\SelectFilter::make('category')
                    ->options([
                        'IDIOM' => 'Idiom',
                        'DAILY_PHRASE' => 'Daily Phrase',
                        'ADVANCED_WORD' => 'Advanced Word',
                    ]),
            ])
            ->recordActions([
                EditAction::make(),
            ])
            ->toolbarActions([
                BulkActionGroup::make([
                    DeleteBulkAction::make(),
                ]),
            ])
            ->paginated([50, 100, 500, 'all'])
            ->defaultPaginationPageOption(100);
    }
}
