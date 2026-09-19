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
                TextColumn::make('video_id')
                    ->numeric()
                    ->sortable()
                    ->toggleable(isToggledHiddenByDefault: true),
                TextColumn::make('start_time')
                    ->label('Time')
                    ->badge()
                    ->color('gray')
                    ->searchable(),
                TextColumn::make('text')
                    ->label('Original Dialogue')
                    ->wrap()
                    ->searchable(),
                TextColumn::make('target_word')
                    ->label('Target Word')
                    ->badge()
                    ->color('warning')
                    ->searchable(),
                TextColumn::make('emotion')
                    ->label('Emotion')
                    ->badge()
                    ->color(fn (?string $state): string => match ($state) {
                        'JOY' => 'success',
                        'ANGER' => 'danger',
                        'SADNESS' => 'warning',
                        'FEAR' => 'danger',
                        'SURPRISE' => 'info',
                        'LOVE' => 'pink',
                        default => 'gray',
                    })
                    ->description(fn (VideoClip $record): string => $record->emotion_confidence ? $record->emotion_confidence . '%' : '')
                    ->searchable(),
                TextColumn::make('translated_text')
                    ->label('Translation')
                    ->wrap()
                    ->searchable(),
                TextColumn::make('cefr_level')
                    ->label('CEFR Level')
                    ->badge()
                    ->color(fn (?string $state): string => match ($state) {
                        'A1', 'A2' => 'gray',
                        'B1' => 'info',
                        'B2', 'C1', 'C2' => 'success',
                        default => 'gray',
                    })
                    ->description(fn (VideoClip $record): string => $record->cefr_confidence ? $record->cefr_confidence . '%' : '')
                    ->searchable(),
                TextColumn::make('created_at')
                    ->dateTime()
                    ->sortable()
                    ->toggleable(isToggledHiddenByDefault: true),
                TextColumn::make('updated_at')
                    ->dateTime()
                    ->sortable()
                    ->toggleable(isToggledHiddenByDefault: true),
            ])
            ->filters([
                \Filament\Tables\Filters\SelectFilter::make('emotion')
                    ->options([
                        'JOY' => 'Joy',
                        'ANGER' => 'Anger',
                        'SADNESS' => 'Sadness',
                        'FEAR' => 'Fear',
                        'SURPRISE' => 'Surprise',
                        'LOVE' => 'Love',
                    ]),
                \Filament\Tables\Filters\SelectFilter::make('cefr_level')
                    ->options([
                        'A1' => 'A1 (Beginner)',
                        'A2' => 'A2 (Elementary)',
                        'B1' => 'B1 (Intermediate)',
                        'B2' => 'B2 (Upper Intermediate)',
                        'C1' => 'C1 (Advanced)',
                        'C2' => 'C2 (Mastery)',
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
