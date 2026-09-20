<?php

namespace App\Filament\Resources\VideoJobs\Schemas;

use Filament\Forms\Components\Select;
use Filament\Forms\Components\TextInput;
use Filament\Forms\Components\Textarea;
use Filament\Schemas\Schema;

class VideoJobForm
{
    public static function configure(Schema $schema): Schema
    {
        return $schema
            ->components([
                TextInput::make('youtube_url')
                    ->url()
                    ->required(),
                Select::make('status')
                    ->options([
            'pending' => 'Pending',
            'processing' => 'Processing',
            'completed' => 'Completed',
            'failed' => 'Failed',
        ])
                    ->default('pending')
                    ->required(),
                TextInput::make('retry_count')
                    ->required()
                    ->numeric()
                    ->default(0),
                Textarea::make('error_log')
                    ->columnSpanFull(),
            ]);
    }
}
