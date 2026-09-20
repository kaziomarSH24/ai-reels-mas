<?php

namespace App\Filament\Pages;

use Filament\Pages\Page;
use Filament\Forms\Concerns\InteractsWithForms;
use Filament\Forms\Contracts\HasForms;
use Filament\Schemas\Schema;
use Filament\Forms\Components\Textarea;
use Filament\Actions\Action;
use Filament\Notifications\Notification;

class BulkWordIngest extends Page implements HasForms
{
    use InteractsWithForms;

    protected string $view = 'filament.pages.bulk-word-ingest';

    public static function getNavigationIcon(): ?string
    {
        return 'heroicon-o-document-text';
    }

    public static function getNavigationGroup(): ?string
    {
        return 'AI Tools';
    }

    public function getTitle(): string 
    {
        return 'Bulk Word Bot';
    }

    public static function getNavigationLabel(): string
    {
        return 'Bulk Word Bot';
    }

    public ?array $data = [];

    public function mount(): void
    {
        $this->form->fill();
    }

    public function form(Schema $schema): Schema
    {
        return $schema
            ->components([
                Textarea::make('words_list')
                    ->label('Paste Words/Phrases (One per line)')
                    ->placeholder("I'm broke\nHold your horses\nIt rings a bell")
                    ->rows(15)
                    ->required(),
            ])
            ->statePath('data');
    }

    public function getFormActions(): array
    {
        return [
            Action::make('start_bot')
                ->label('Start Bot in Background')
                ->submit('start_bot')
                ->color('primary')
        ];
    }

    public function start_bot(): void
    {
        $data = $this->form->getState();
        $words = explode("\n", str_replace("\r", "", $data['words_list']));
        $words = array_filter(array_map('trim', $words));
        
        $count = count($words);
        
        foreach ($words as $word) {
            \App\Jobs\ScrapeWordJob::dispatch($word);
        }
        
        Notification::make()
            ->title('Bot Started!')
            ->body("Bot is now searching for clips for {$count} words in the background.")
            ->success()
            ->send();
            
        $this->form->fill();
    }
}
