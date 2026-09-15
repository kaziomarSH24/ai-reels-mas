<?php

namespace App\Filament\Resources\Movies\Schemas;

use Filament\Forms\Components\TextInput;
use Filament\Forms\Components\Textarea;
use Filament\Forms\Components\Toggle;
use Filament\Schemas\Schema;

class MovieForm
{
    public static function configure(Schema $schema): Schema
    {
        return $schema
            ->components([
                TextInput::make('title')
                    ->required(),
                TextInput::make('genre'),
                TextInput::make('imdb_rating')
                    ->numeric(),
                TextInput::make('source_url')
                    ->url(),
                Textarea::make('video_url')
                    ->columnSpanFull(),
                Textarea::make('subtitle_url')
                    ->columnSpanFull(),
                Toggle::make('is_processed')
                    ->required(),
            ]);
    }
}
