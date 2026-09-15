<?php

namespace App\Filament\Resources\MovieDialogues\Schemas;

use Filament\Forms\Components\TextInput;
use Filament\Forms\Components\Textarea;
use Filament\Schemas\Schema;

class MovieDialogueForm
{
    public static function configure(Schema $schema): Schema
    {
        return $schema
            ->components([
                TextInput::make('movie_id')
                    ->required()
                    ->numeric(),
                Textarea::make('text')
                    ->required()
                    ->columnSpanFull(),
                TextInput::make('start_time')
                    ->required(),
                TextInput::make('end_time')
                    ->required(),
                TextInput::make('emotion'),
                Textarea::make('translated_text')
                    ->columnSpanFull(),
                TextInput::make('cefr_level'),
            ]);
    }
}
