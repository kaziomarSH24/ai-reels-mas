<?php

namespace App\Filament\Resources\ScrapedClips\Schemas;

use Filament\Forms\Components\TextInput;
use Filament\Forms\Components\Toggle;
use Filament\Schemas\Schema;

class ScrapedClipForm
{
    public static function configure(Schema $schema): Schema
    {
        return $schema
            ->components([
                TextInput::make('target_word')
                    ->required(),
                TextInput::make('file_path')
                    ->required(),
                TextInput::make('source')
                    ->default('playphrase'),
                Toggle::make('is_used')
                    ->required(),
            ]);
    }
}
