<?php

namespace App\Filament\Resources\ScrapedClips\Tables;

use Filament\Actions\BulkActionGroup;
use Filament\Actions\DeleteBulkAction;
use Filament\Actions\EditAction;
use Filament\Tables\Columns\IconColumn;
use Filament\Tables\Columns\TextColumn;
use Filament\Tables\Table;

class ScrapedClipsTable
{
    public static function configure(Table $table): Table
    {
        return $table
            ->columns([
                TextColumn::make('target_word')
                    ->searchable(),
                TextColumn::make('file_path')
                    ->label('Preview')
                    ->html()
                    ->formatStateUsing(fn ($state) => '<video src="'.asset($state).'" controls style="height: 80px; border-radius: 8px; background: #000;"></video>'),
                TextColumn::make('source')
                    ->searchable(),
                IconColumn::make('is_used')
                    ->boolean(),
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
                //
            ])
            ->recordActions([
                EditAction::make(),
            ])
            ->toolbarActions([
                BulkActionGroup::make([
                    DeleteBulkAction::make(),
                ]),
            ]);
    }
}
