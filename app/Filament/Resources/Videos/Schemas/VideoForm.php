<?php

namespace App\Filament\Resources\Videos\Schemas;

use Filament\Forms\Components\FileUpload;
use Filament\Forms\Components\Select;
use Filament\Forms\Components\TextInput;
use Filament\Forms\Components\Toggle;
use Filament\Schemas\Schema;

class VideoForm
{
    public static function configure(Schema $schema): Schema
    {
        return $schema
            ->components([
                TextInput::make('title')
                    ->label('Movie / Video Title')
                    ->placeholder('e.g. Pathaan (2023)')
                    ->required(),

                Select::make('source_type')
                    ->label('Source Type')
                    ->options([
                        'youtube' => '▶️ YouTube',
                        'gdrive'  => '📁 Google Drive',
                        'direct'  => '🔗 Direct URL (R2, S3, etc.)',
                    ])
                    ->default('youtube')
                    ->required(),

                TextInput::make('youtube_url')
                    ->label('YouTube URL')
                    ->url()
                    ->placeholder('https://www.youtube.com/watch?v=...')
                    ->helperText('Only required if Source Type is YouTube'),

                TextInput::make('source_url')
                    ->label('Source URL (Google Drive / Direct Link)')
                    ->url()
                    ->placeholder('https://drive.google.com/file/d/... or https://r2.dev/...')
                    ->helperText('Only required if Source Type is Google Drive or Direct URL'),

                FileUpload::make('subtitle_path')
                    ->label('Subtitle File (.srt)')
                    ->helperText('Upload the English SRT subtitle file for this video. The system will index all dialogues automatically.')
                    ->acceptedFileTypes(['text/plain', 'application/octet-stream'])
                    ->directory('subtitles')
                    ->disk('public'),

                TextInput::make('thumbnail_url')
                    ->label('Thumbnail URL (optional)')
                    ->url(),

                Toggle::make('is_processed')
                    ->label('Is Indexed / Processed')
                    ->helperText('Will be set automatically after subtitle indexing'),
            ]);
    }
}
