<?php

namespace App\Filament\Resources\VideoClips\Schemas;

use Filament\Forms\Components\TextInput;
use Filament\Forms\Components\Textarea;
use Filament\Forms\Components\Select;
use Filament\Schemas\Components\Grid;
use Filament\Schemas\Components\Section;
use Filament\Schemas\Schema;

class VideoClipForm
{
    public static function configure(Schema $schema): Schema
    {
        return $schema
            ->components([
                Section::make('Extraction Data')
                    ->description('Core NLP data extracted by Gemini')
                    ->icon('heroicon-o-sparkles')
                    ->schema([
                        Grid::make(2)->schema([
                            TextInput::make('expression')
                                ->label('Expression / Phrase')
                                ->required(),
                            Select::make('category')
                                ->label('Category')
                                ->options([
                                    'IDIOM' => 'Idiom',
                                    'DAILY_PHRASE' => 'Daily Phrase',
                                    'ADVANCED_WORD' => 'Advanced Word',
                                ])
                                ->required(),
                            TextInput::make('whisper_target')
                                ->label('Exact Whisper Target')
                                ->required(),
                            TextInput::make('casual_meaning')
                                ->label('Casual Bengali Meaning')
                                ->required(),
                        ]),
                    ]),
                    
                Section::make('Source Context')
                    ->description('The original dialogue spoken in the video')
                    ->icon('heroicon-o-chat-bubble-left-right')
                    ->schema([
                        Grid::make(2)->schema([
                            Textarea::make('original_sentence')
                                ->label('Original Dialogue (Spoken)')
                                ->rows(3)
                                ->required(),
                            Textarea::make('original_translation')
                                ->label('Full Translation')
                                ->rows(3),
                        ]),
                    ]),

                Section::make('Generated Content')
                    ->description('AI generated example usage for the reel')
                    ->icon('heroicon-o-pencil-square')
                    ->schema([
                        Grid::make(2)->schema([
                            Textarea::make('easy_example')
                                ->label('Easy Example Sentence')
                                ->rows(2)
                                ->required(),
                            Textarea::make('example_translation')
                                ->label('Example Translation')
                                ->rows(2),
                        ]),
                    ]),
                    
                Section::make('Timestamps')
                    ->icon('heroicon-o-clock')
                    ->schema([
                        Grid::make(2)->schema([
                            TextInput::make('start_time')
                                ->label('Start Time (seconds)')
                                ->numeric()
                                ->required(),
                            TextInput::make('end_time')
                                ->label('End Time (seconds)')
                                ->numeric()
                                ->required(),
                        ]),
                    ]),
            ]);
    }
}
