<?php

namespace App\Filament\Resources\VideoJobs\Pages;

use App\Filament\Resources\VideoJobs\VideoJobResource;
use App\Jobs\ProcessVideoJob;
use App\Models\VideoJob;
use Filament\Actions\Action;
use Filament\Forms\Components\Textarea;
use Filament\Notifications\Notification;
use Filament\Resources\Pages\ListRecords;
use Filament\Forms\Concerns\InteractsWithForms;

class ListVideoJobs extends ListRecords
{
    protected static string $resource = VideoJobResource::class;

    protected function getHeaderActions(): array
    {
        return [
            // Single URL
            Action::make('add_single')
                ->label('Add Single URL')
                ->icon('heroicon-o-plus')
                ->color('primary')
                ->form([
                    Textarea::make('youtube_url')
                        ->label('YouTube URL')
                        ->placeholder('https://www.youtube.com/watch?v=...')
                        ->required()
                        ->rows(2),
                ])
                ->action(function (array $data): void {
                    $url = trim($data['youtube_url']);
                    
                    // Detect source type
                    if (str_contains($url, 'youtube.com') || str_contains($url, 'youtu.be')) {
                        $sourceType = 'youtube';
                    } elseif (str_contains($url, 'drive.google.com') || str_contains($url, 'drive.usercontent.google.com')) {
                        $sourceType = 'gdrive';
                    } else {
                        $sourceType = 'direct';
                    }

                    $job = VideoJob::create([
                        'youtube_url' => $url,
                        'source_type' => $sourceType,
                        'status'      => 'pending',
                    ]);
                    ProcessVideoJob::dispatch($job);
                    Notification::make()->title('Added to queue!')->success()->send();
                }),

            // Bulk URLs (one per line)
            Action::make('add_bulk')
                ->label('Bulk Import')
                ->icon('heroicon-o-document-text')
                ->color('info')
                ->form([
                    Textarea::make('youtube_urls')
                        ->label('Video URLs (one per line)')
                        ->placeholder("https://youtu.be/abc123\nhttps://drive.google.com/file/d/...")
                        ->required()
                        ->rows(10),
                ])
                ->action(function (array $data): void {
                    $urls  = array_filter(array_map('trim', explode("\n", $data['youtube_urls'])));
                    $count = 0;

                    foreach ($urls as $url) {
                        if (filter_var($url, FILTER_VALIDATE_URL)) {
                            // Detect source type
                            if (str_contains($url, 'youtube.com') || str_contains($url, 'youtu.be')) {
                                $sourceType = 'youtube';
                            } elseif (str_contains($url, 'drive.google.com') || str_contains($url, 'drive.usercontent.google.com')) {
                                $sourceType = 'gdrive';
                            } else {
                                $sourceType = 'direct';
                            }

                            $job = VideoJob::create([
                                'youtube_url' => $url, // reusing this column for any URL
                                'source_type' => $sourceType,
                                'status'      => 'pending',
                            ]);
                            ProcessVideoJob::dispatch($job);
                            $count++;
                        }
                    }

                    Notification::make()
                        ->title("{$count} URLs added to queue!")
                        ->body('Horizon will process them in the background with anti-ban delays.')
                        ->success()
                        ->send();
                }),
        ];
    }
}
