<?php

namespace App\Filament\Resources\VideoClips;

use App\Filament\Resources\VideoClips\Pages\CreateVideoClip;
use App\Filament\Resources\VideoClips\Pages\EditVideoClip;
use App\Filament\Resources\VideoClips\Pages\ListVideoClips;
use App\Filament\Resources\VideoClips\Schemas\VideoClipForm;
use App\Filament\Resources\VideoClips\Tables\VideoClipsTable;
use App\Models\VideoClip;
use BackedEnum;
use Filament\Resources\Resource;
use Filament\Schemas\Schema;
use Filament\Support\Icons\Heroicon;
use Filament\Tables\Table;

class VideoClipResource extends Resource
{
    protected static string|\UnitEnum|null $navigationGroup = 'Data Management';
    protected static ?int $navigationSort = 2;

    protected static ?string $model = VideoClip::class;

    protected static string|BackedEnum|null $navigationIcon = Heroicon::OutlinedRectangleStack;

    public static function form(Schema $schema): Schema
    {
        return VideoClipForm::configure($schema);
    }

    public static function table(Table $table): Table
    {
        return VideoClipsTable::configure($table);
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
            'index' => ListVideoClips::route('/'),
            'create' => CreateVideoClip::route('/create'),
            'edit' => EditVideoClip::route('/{record}/edit'),
        ];
    }
}
