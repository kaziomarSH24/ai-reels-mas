<?php

namespace App\Filament\Resources\MovieDialogues\Tables;

use Filament\Actions\BulkActionGroup;
use Filament\Actions\DeleteBulkAction;
use Filament\Actions\EditAction;
use Filament\Tables\Columns\TextColumn;
use Filament\Tables\Table;

class MovieDialoguesTable
{
    public static function configure(Table $table): Table
    {
        return $table
            ->columns([
                TextColumn::make('movie_id')
                    ->numeric()
                    ->sortable(),
                TextColumn::make('start_time')
                    ->searchable(),
                TextColumn::make('end_time')
                    ->searchable(),
                TextColumn::make('text')
                    ->wrap()
                    ->searchable(),
                TextColumn::make('emotion')
                    ->searchable(),
                TextColumn::make('translated_text')
                    ->wrap()
                    ->searchable(),
                TextColumn::make('cefr_level')
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
                //
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
