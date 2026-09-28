<?php

namespace App\Filament\Pages;

use Filament\Pages\Page;
use Filament\Notifications\Notification;
use Symfony\Component\Process\Process;
use App\Models\VideoJob;
use App\Jobs\ProcessVideoJob;
use Illuminate\Support\Facades\Log;
use BackedEnum;
use UnitEnum;
use Filament\Forms\Concerns\InteractsWithForms;
use Filament\Forms\Contracts\HasForms;
use Filament\Schemas\Schema;
use Filament\Schemas\Components\Section;
use Filament\Forms\Components\TextInput;
use Filament\Forms\Components\Textarea;

class PlaylistImporter extends Page implements HasForms
{
    use InteractsWithForms;

    protected static string | BackedEnum | null $navigationIcon = 'heroicon-o-queue-list';
    protected static string | UnitEnum | null $navigationGroup = 'Tools';
    protected static ?string $navigationLabel = 'Playlist Importer';
    protected static ?string $title = 'YouTube Playlist Bulk Importer';

    protected string $view = 'filament.pages.playlist-importer';

    public ?array $data = [];
    public $extracted_links = '';
    public $is_loading = false;

    public function mount(): void
    {
        $this->form->fill();
    }

    public function form(Schema $form): Schema
    {
        return $form
            ->components([
                Section::make('Extract Links')
                    ->description('Enter a YouTube playlist URL to extract all video links.')
                    ->components([
                        TextInput::make('playlist_url')
                            ->label('Playlist URL')
                            ->placeholder('https://www.youtube.com/playlist?list=...')
                            ->required()
                            ->url(),
                    ]),
            ])
            ->statePath('data');
    }

    public function fetchLinks()
    {
        $data = $this->form->getState();
        $this->is_loading = true;
        $this->extracted_links = '';

        try {
            $url = escapeshellarg($data['playlist_url']);
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
        $this->form->fill();
    }
}
