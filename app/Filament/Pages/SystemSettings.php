<?php

namespace App\Filament\Pages;

use Filament\Forms\Components\FileUpload;
use Filament\Forms\Concerns\InteractsWithForms;
use Filament\Forms\Contracts\HasForms;
use Filament\Schemas\Schema;
use Filament\Pages\Page;
use Illuminate\Support\Facades\Storage;
use Livewire\Features\SupportFileUploads\TemporaryUploadedFile;
use Filament\Notifications\Notification;

class SystemSettings extends Page implements HasForms
{
    use InteractsWithForms;

    protected string $view = 'filament.pages.system-settings';

    public ?array $data = [];

    public static function getNavigationIcon(): ?string
    {
        return 'heroicon-o-cog-6-tooth';
    }

    public static function getNavigationGroup(): ?string
    {
        return 'Settings';
    }

    public static function getNavigationLabel(): string
    {
        return 'System Settings';
    }

    public function getTitle(): string | \Illuminate\Contracts\Support\Htmlable
    {
        return 'System Settings';
    }

    public function mount(): void
    {
        $this->form->fill();
    }

    public function form(Schema $schema): Schema
    {
        return $schema
            ->components([
                FileUpload::make('cookie_file')
                    ->label('Upload cookies.txt for yt-dlp')
                    ->disk('local')
                    ->directory('temp_cookies')
                    ->acceptedFileTypes(['text/plain'])
                    ->helperText('Upload your browser cookies to bypass YouTube bot protection.')
                    ->required(),
            ])
            ->statePath('data');
    }

    public function save(): void
    {
        $data = $this->form->getState();
        
        if (!empty($data['cookie_file'])) {
            // Get the uploaded file path
            $uploadedPath = is_array($data['cookie_file']) ? array_values($data['cookie_file'])[0] : $data['cookie_file'];
            
            // Move and overwrite as exactly cookies.txt in the root of local disk (storage/app)
            if (Storage::disk('local')->exists($uploadedPath)) {
                $content = Storage::disk('local')->get($uploadedPath);
                Storage::disk('local')->put('cookies.txt', $content);
                
                // Cleanup temp
                Storage::disk('local')->delete($uploadedPath);
            }
        }
        
        Notification::make()
            ->title('Cookies saved successfully')
            ->success()
            ->send();
    }
}
