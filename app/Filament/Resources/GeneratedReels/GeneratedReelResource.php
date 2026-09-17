<?php

namespace App\Filament\Resources\GeneratedReels;

use App\Filament\Resources\GeneratedReels\Pages;
use App\Models\GeneratedReel;
use Filament\Forms\Components\TextInput;
use Filament\Forms\Components\Toggle;
use Filament\Resources\Resource;
use Filament\Schemas\Schema;
use Filament\Tables\Columns\TextColumn;
use Filament\Tables\Columns\IconColumn;
use Filament\Actions\EditAction;
use Filament\Actions\DeleteAction;
use Filament\Actions\BulkActionGroup;
use Filament\Actions\DeleteBulkAction;
use Filament\Tables\Table;
use BackedEnum;

class GeneratedReelResource extends Resource
{
    protected static ?string $model = GeneratedReel::class;

    protected static string|BackedEnum|null $navigationIcon = 'heroicon-o-video-camera';
    protected static ?string $navigationLabel = 'Generated Reels';
    protected static ?int $navigationSort = 4;

    public static function form(Schema $schema): Schema
    {
        return $schema
            ->components([
                TextInput::make('target_word')
                    ->maxLength(255),
                TextInput::make('file_path')
                    ->required()
                    ->maxLength(255),
                Toggle::make('is_posted_to_fb')
                    ->required(),
            ]);
    }

    public static function table(Table $table): Table
    {
        return $table
            ->columns([
                TextColumn::make('target_word')
                    ->searchable()
                    ->sortable()
                    ->label('Target Word'),
                TextColumn::make('file_path')
                    ->formatStateUsing(fn ($state) => "<a href='{$state}' target='_blank' class='text-primary-600 underline'>Watch Video</a>")
                    ->html()
                    ->label('Reel Link'),
                IconColumn::make('is_posted_to_fb')
                    ->boolean()
                    ->label('Posted to FB'),
                TextColumn::make('created_at')
                    ->dateTime()
                    ->sortable()
                    ->toggleable(isToggledHiddenByDefault: false),
            ])
            ->filters([
                //
            ])
            ->recordActions([
                EditAction::make(),
                DeleteAction::make(),
            ])
            ->toolbarActions([
                BulkActionGroup::make([
                    DeleteBulkAction::make(),
                ]),
            ])
            ->defaultSort('created_at', 'desc');
    }

    public static function getRelations(): array
    {
        return [
            //
        ];
    }

    public static function getPages(): array
    {
        return [
            'index' => Pages\ListGeneratedReels::route('/'),
        ];
    }
}
