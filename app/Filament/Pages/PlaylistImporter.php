<?php

namespace App\Filament\Pages;

use Filament\Pages\Page;
use Filament\Notifications\Notification;
use Symfony\Component\Process\Process;
use App\Models\VideoJob;
use App\Jobs\ProcessVideoJob;
use Illuminate\Support\Facades\Log;

class PlaylistImporter extends Page
{
    public static function getNavigationIcon(): ?string { return 'heroicon-o-queue-list'; }
    public static function getNavigationGroup(): ?string { return 'Tools'; }
    public static function getNavigationLabel(): string { return 'Playlist Importer'; }
    public function getTitle(): string|\Illuminate\Contracts\Support\Htmlable { return 'YouTube Playlist Bulk Importer'; }

    protected string $view = 'filament.pages.playlist-importer';

    public $playlist_url = '';
    public $extracted_links = '';
    public $is_loading = false;

    public function fetchLinks()
    {
        $this->validate([
            'playlist_url' => 'required|url'
        ]);

        $this->is_loading = true;
        $this->extracted_links = '';

        try {
            $url = escapeshellarg($this->playlist_url);
            $process = Process::fromShellCommandline("yt-dlp --flat-playlist --print 'https://www.youtube.com/watch?v=%(id)s' {$url}");
            $process->setTimeout(120);
            $process->run();

            if (!$process->isSuccessful()) {
                Notification::make()
                    ->title('Failed to fetch playlist')
                    ->body($process->getErrorOutput())
                    ->danger()
                    ->send();
                $this->is_loading = false;
                return;
            }

            $this->extracted_links = trim($process->getOutput());
            
            $count = count(array_filter(explode("\n", $this->extracted_links)));
            Notification::make()
                ->title("Successfully extracted {$count} links!")
                ->success()
                ->send();

        } catch (\Exception $e) {
            Notification::make()
                ->title('Error')
                ->body($e->getMessage())
                ->danger()
                ->send();
        }

        $this->is_loading = false;
    }

    public function addToQueue()
    {
        if (empty(trim($this->extracted_links))) {
            Notification::make()->title('No links to add!')->warning()->send();
            return;
        }

        $urls = array_filter(array_map('trim', explode("\n", $this->extracted_links)));
        $count = 0;

        foreach ($urls as $url) {
            if (filter_var($url, FILTER_VALIDATE_URL)) {
                $job = VideoJob::create([
                    'youtube_url' => $url,
                    'source_type' => 'youtube',
                    'status'      => 'pending',
                ]);
                ProcessVideoJob::dispatch($job);
                $count++;
            }
        }

        Notification::make()
            ->title("{$count} videos added to Job Queue!")
            ->success()
            ->send();
            
        $this->extracted_links = '';
        $this->playlist_url = '';
    }
}
