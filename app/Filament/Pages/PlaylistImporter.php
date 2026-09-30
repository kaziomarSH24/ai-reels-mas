<?php

namespace App\Filament\Pages;

use Filament\Pages\Page;
use Filament\Notifications\Notification;
use Symfony\Component\Process\Process;
use App\Models\VideoJob;
use App\Jobs\ProcessVideoJob;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\Http;
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
        $apiKey = env('YOUTUBE_API_KEY');

        if (empty($apiKey)) {
            Notification::make()->title('API Key Missing')->body('Please set YOUTUBE_API_KEY in your .env file')->danger()->send();
            $this->is_loading = false;
            return;
        }

        try {
            $url = $data['playlist_url'];
            parse_str(parse_url($url, PHP_URL_QUERY), $queryParams);
            $playlistId = $queryParams['list'] ?? null;

            if (!$playlistId) {
                Notification::make()->title('Invalid URL')->body('Could not find a valid playlist ID in the URL.')->danger()->send();
                $this->is_loading = false;
                return;
            }

            $pageToken = '';
            $extractedUrls = [];
            
            do {
                $response = Http::get("https://www.googleapis.com/youtube/v3/playlistItems", [
                    'part' => 'snippet',
                    'maxResults' => 50,
                    'playlistId' => $playlistId,
                    'key' => $apiKey,
                    'pageToken' => $pageToken,
                ]);

                if ($response->failed()) {
                    Notification::make()
                        ->title('YouTube API Error')
                        ->body($response->json('error.message', 'Failed to fetch playlist data.'))
                        ->danger()
                        ->send();
                    $this->is_loading = false;
                    return;
                }

                $items = $response->json('items', []);
                foreach ($items as $item) {
                    $videoId = data_get($item, 'snippet.resourceId.videoId');
                    if ($videoId) {
                        $extractedUrls[] = "https://www.youtube.com/watch?v={$videoId}";
                    }
                }

                $pageToken = $response->json('nextPageToken');
            } while ($pageToken);

            $this->extracted_links = implode("\n", $extractedUrls);
            $count = count($extractedUrls);
            
            Notification::make()
                ->title("Successfully extracted {$count} links using Official API!")
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
