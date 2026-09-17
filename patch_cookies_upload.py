import re

with open("app/Filament/Pages/AiStudio.php", "r") as f:
    content = f.read()

header_actions = r"""
    protected function getHeaderActions(): array
    {
        return [
            \Filament\Actions\Action::make('uploadCookies')
                ->label('Upload YouTube Cookies')
                ->icon('heroicon-o-key')
                ->color('warning')
                ->form([
                    \Filament\Forms\Components\FileUpload::make('cookie_file')
                        ->label('cookies.txt File')
                        ->acceptedFileTypes(['text/plain'])
                        ->required()
                        ->helperText('Upload your YouTube cookies.txt to bypass IP Blocks.'),
                ])
                ->action(function (array $data) {
                    $path = storage_path('app/public/' . $data['cookie_file']);
                    if (file_exists($path)) {
                        copy($path, base_path('python_engine/cookies.txt'));
                        copy($path, base_path('cookies.txt'));
                        \Filament\Notifications\Notification::make()->title('Cookies updated successfully! YouTube Block is now bypassed!')->success()->send();
                    } else {
                        \Filament\Notifications\Notification::make()->title('File not found!')->danger()->send();
                    }
                }),
        ];
    }
"""

if "protected function getHeaderActions" not in content:
    content = content.replace("    protected function getForms(): array", header_actions + "\n    protected function getForms(): array")

with open("app/Filament/Pages/AiStudio.php", "w") as f:
    f.write(content)
