import re

# 1. Update the Blade View
with open("resources/views/filament/pages/ai-studio-native.blade.php", "r") as f:
    blade = f.read()

if "<x-filament-actions::modals />" not in blade:
    blade = blade.replace("</x-filament-panels::page>", "    <x-filament-actions::modals />\n</x-filament-panels::page>")

with open("resources/views/filament/pages/ai-studio-native.blade.php", "w") as f:
    f.write(blade)

# 2. Update the PHP Class
with open("app/Filament/Pages/AiStudio.php", "r") as f:
    content = f.read()

# Add getHeaderActions
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
                        ->helperText('Upload your new YouTube cookies.txt. This will replace the old one.'),
                ])
                ->action(function (array $data) {
                    $path = storage_path('app/public/' . $data['cookie_file']);
                    if (file_exists($path)) {
                        if (file_exists(base_path('python_engine/cookies.txt'))) {
                            @unlink(base_path('python_engine/cookies.txt'));
                        }
                        if (file_exists(base_path('cookies.txt'))) {
                            @unlink(base_path('cookies.txt'));
                        }
                        copy($path, base_path('python_engine/cookies.txt'));
                        copy($path, base_path('cookies.txt'));
                        \Filament\Notifications\Notification::make()->title('Cookies successfully updated!')->success()->send();
                    }
                }),
        ];
    }
"""

if "protected function getHeaderActions" not in content:
    content = content.replace("    protected function getForms(): array", header_actions + "\n    protected function getForms(): array")

# Instead of complex regex, let's just do targeted replacements
# Remove the FileUpload
upload_field = r"""
                        \Filament\Forms\Components\FileUpload::make('cookie_file')
                            ->label('Upload cookies.txt (Optional)')
                            ->helperText('Upload this file and click "Extract & Analyze" to save it permanently.')
                            ->acceptedFileTypes(['text/plain'])
                            ->disk('public'),
"""
content = content.replace(upload_field, "")

# Restore analyzeVideo
old_analyze = r"""
    public function analyzeVideo()
    {
        set_time_limit(0); 
        
        $url = $this->analyzerData['youtubeUrl'] ?? null;
        $cookieFile = $this->analyzerData['cookie_file'] ?? null;

        if ($cookieFile) {
            $path = storage_path('app/public/' . $cookieFile);
            if (file_exists($path)) {
                copy($path, base_path('python_engine/cookies.txt'));
                copy($path, base_path('cookies.txt'));
                \Filament\Notifications\Notification::make()->title('Cookies Saved Successfully!')->success()->send();
                $this->analyzerData['cookie_file'] = null;
            }
        }

        if (empty($url)) {
            if ($cookieFile) return; 
            \Filament\Notifications\Notification::make()->title('Please enter a YouTube URL')->danger()->send();
            return;
        }
"""
new_analyze = r"""
    public function analyzeVideo()
    {
        set_time_limit(0); 
        
        $url = $this->analyzerData['youtubeUrl'] ?? null;

        if (empty($url)) {
            \Filament\Notifications\Notification::make()->title('Please enter a YouTube URL')->danger()->send();
            return;
        }
"""
content = content.replace(old_analyze.strip(), new_analyze.strip())

with open("app/Filament/Pages/AiStudio.php", "w") as f:
    f.write(content)
