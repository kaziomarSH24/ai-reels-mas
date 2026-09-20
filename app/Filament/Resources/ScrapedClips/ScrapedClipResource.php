<?php

namespace App\Filament\Resources\ScrapedClips;

use App\Filament\Resources\ScrapedClips\Pages\CreateScrapedClip;
use App\Filament\Resources\ScrapedClips\Pages\EditScrapedClip;
use App\Filament\Resources\ScrapedClips\Pages\ListScrapedClips;
use App\Filament\Resources\ScrapedClips\Schemas\ScrapedClipForm;
use App\Filament\Resources\ScrapedClips\Tables\ScrapedClipsTable;
use App\Models\ScrapedClip;
use BackedEnum;
use Filament\Resources\Resource;
use Filament\Schemas\Schema;
use Filament\Support\Icons\Heroicon;
use Filament\Tables\Table;

class ScrapedClipResource extends Resource
{
    protected static ?string $model = ScrapedClip::class;

    protected static string|BackedEnum|null $navigationIcon = Heroicon::OutlinedRectangleStack;

    public static function form(Schema $schema): Schema
    {
        return ScrapedClipForm::configure($schema);
    }

    public static function table(Table $table): Table
    {
        return ScrapedClipsTable::configure($table);
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
            'index' => ListScrapedClips::route('/'),
            'create' => CreateScrapedClip::route('/create'),
            'edit' => EditScrapedClip::route('/{record}/edit'),
        ];
    }
}
