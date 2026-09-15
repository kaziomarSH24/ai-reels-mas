<?php

namespace App\Filament\Resources\MovieDialogues;

use App\Filament\Resources\MovieDialogues\Pages\CreateMovieDialogue;
use App\Filament\Resources\MovieDialogues\Pages\EditMovieDialogue;
use App\Filament\Resources\MovieDialogues\Pages\ListMovieDialogues;
use App\Filament\Resources\MovieDialogues\Schemas\MovieDialogueForm;
use App\Filament\Resources\MovieDialogues\Tables\MovieDialoguesTable;
use App\Models\MovieDialogue;
use BackedEnum;
use Filament\Resources\Resource;
use Filament\Schemas\Schema;
use Filament\Support\Icons\Heroicon;
use Filament\Tables\Table;

class MovieDialogueResource extends Resource
{
    protected static ?string $model = MovieDialogue::class;

    protected static string|BackedEnum|null $navigationIcon = Heroicon::OutlinedRectangleStack;

    public static function form(Schema $schema): Schema
    {
        return MovieDialogueForm::configure($schema);
    }

    public static function table(Table $table): Table
    {
        return MovieDialoguesTable::configure($table);
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
            'index' => ListMovieDialogues::route('/'),
            'create' => CreateMovieDialogue::route('/create'),
            'edit' => EditMovieDialogue::route('/{record}/edit'),
        ];
    }
}
