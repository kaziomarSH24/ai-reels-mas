<?php

namespace App\Filament\Resources\VideoClips\Tables;

use Filament\Tables\Table;
use App\Models\VideoClip;
use Filament\Actions\BulkActionGroup;
use Filament\Actions\DeleteBulkAction;
use Filament\Actions\EditAction;
use Filament\Actions\ViewAction;
use Filament\Infolists\Components\TextEntry;
use Filament\Infolists\Components\Section;
use Filament\Infolists\Components\Grid;
use Filament\Infolists\Components\Split;
use Filament\Infolists\Components\Group;
use Filament\Tables\Columns\TextColumn;
use Filament\Tables\Filters\SelectFilter;




class VideoClipsTable
{
    public static function configure(Table $table): Table
    {
        return $table
            ->columns([
                TextColumn::make('video.title')
                    ->label('Video Source')
                    ->searchable()
                    ->sortable()
                    ->toggleable(isToggledHiddenByDefault: true),
                
                TextColumn::make('time_range')
                    ->label('Time (Start - End)')
                    ->state(function (VideoClip $record): string {
                        return number_format((float)$record->start_time, 1) . 's - ' . number_format((float)$record->end_time, 1) . 's';
                    })
                    ->badge()
                    ->color('gray'),

                TextColumn::make('category')
                    ->label('Category')
                    ->badge()
                    ->color(fn (?string $state): string => match ($state) {
                        'IDIOM' => 'danger',
                        'DAILY_PHRASE' => 'success',
                        'ADVANCED_WORD' => 'info',
                        default => 'gray',
                    })
                    ->searchable(),

                TextColumn::make('expression')
                    ->label('Expression / Phrase')
                    ->badge()
                    ->color('primary')
                    ->searchable()
                    ->sortable(),

                TextColumn::make('original_sentence')
                    ->label('Original Sentence')
                    ->wrap()
                    ->searchable()
                    ->toggleable(isToggledHiddenByDefault: true),
                    
                TextColumn::make('whisper_target')
                    ->label('Whisper Target')
                    ->color('warning')
                    ->searchable()
                    ->toggleable(isToggledHiddenByDefault: true),

                TextColumn::make('casual_meaning')
                    ->label('Casual Meaning')
                    ->wrap()
                    ->searchable(),

                TextColumn::make('easy_example')
                    ->label('Easy Example')
                    ->wrap()
                    ->searchable(),

                TextColumn::make('created_at')
                    ->dateTime()
                    ->sortable()
                    ->toggleable(isToggledHiddenByDefault: true),
            ])
            ->filters([
                SelectFilter::make('category')
                    ->options([
                        'IDIOM' => 'Idiom',
                        'DAILY_PHRASE' => 'Daily Phrase',
                        'ADVANCED_WORD' => 'Advanced Word',
                    ]),
            ])
            ->recordActions([
                ViewAction::make()
                    ->modalHeading('Clip Details')
                    ->modalWidth('4xl')
                    ->infolist([
                        Section::make('Core AI Extraction')
                            ->icon('heroicon-o-sparkles')
                            ->schema([
                                Split::make([
                                    Group::make([
                                        TextEntry::make('expression')
                                            ->label('Target Expression')
                                            ->size('text-2xl')
                                            ->weight('bold')
                                            ->color('primary'),
                                        TextEntry::make('category')
                                            ->badge()
                                            ->color(fn (?string $state): string => match ($state) {
                                                'IDIOM' => 'danger',
                                                'DAILY_PHRASE' => 'success',
                                                'ADVANCED_WORD' => 'info',
                                                default => 'gray',
                                            }),
                                    ]),
                                    Group::make([
                                        TextEntry::make('casual_meaning')
                                            ->label('Bengali Meaning')
                                            ->size('text-lg')
                                            ->color('success'),
                                        TextEntry::make('whisper_target')
                                            ->label('Whisper Alignment Target')
                                            ->color('warning')
                                            ->icon('heroicon-m-microphone'),
                                    ]),
                                ]),
                            ]),
                            
                        Grid::make(2)
                            ->schema([
                                Section::make('Original Source')
                                    ->columnSpan(1)
                                    ->icon('heroicon-o-video-camera')
                                    ->schema([
                                        TextEntry::make('original_sentence')
                                            ->label('Spoken Dialogue'),
                                        TextEntry::make('original_translation')
                                            ->label('Translation')
                                            ->color('gray'),
                                        TextEntry::make('time_range')
                                            ->label('Timestamps')
                                            ->state(function ($record) {
                                                return $record->start_time . 's  —  ' . $record->end_time . 's';
                                            })
                                            ->fontFamily('mono')
                                            ->icon('heroicon-m-clock'),
                                    ]),

                                Section::make('Generated Reel UI')
                                    ->columnSpan(1)
                                    ->icon('heroicon-o-film')
                                    ->schema([
                                        TextEntry::make('easy_example')
                                            ->label('Easy Example'),
                                        TextEntry::make('example_translation')
                                            ->label('Bengali Translation')
                                            ->color('gray'),
                                    ]),
                            ]),
                    ]),
                EditAction::make(),
            ])
            ->toolbarActions([
                BulkActionGroup::make([
                    DeleteBulkAction::make(),
                ]),
            ])
            ->paginated([50, 100, 500, 'all'])
            ->defaultPaginationPageOption(100);
    }
}
