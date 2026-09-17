import re

with open("app/Filament/Pages/AiStudio.php", "r") as f:
    content = f.read()

# Remove the getHeaderActions method completely
content = re.sub(r"protected function getHeaderActions\(\): array\s*\{[\s\S]*?\}\s*protected function getForms", "protected function getForms", content)

new_schema = r"""
                        TextInput::make('youtubeUrl')
                            ->label('YouTube URL')
                            ->placeholder('https://youtube.com/watch?v=...')
                            ->url()
                            ->prefixIcon('heroicon-m-link'),
                            
                        \Filament\Forms\Components\FileUpload::make('cookie_file')
                            ->label('Upload cookies.txt (Optional)')
                            ->helperText('Upload this file and click "Extract & Analyze" to save it permanently.')
                            ->acceptedFileTypes(['text/plain'])
                            ->disk('public'),
"""

# Replace the TextInput block correctly
content = re.sub(
    r"TextInput::make\('youtubeUrl'\)[\s\S]*?->prefixIcon\('heroicon-m-link'\),",
    new_schema.strip().replace("\\", "\\\\"),
    content
)

analyze_start = r"""
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

content = re.sub(
    r"public function analyzeVideo\(\)\s*\{\s*set_time_limit\(0\);[\s\S]*?if \(empty\(\$url\)\) \{[\s\S]*?return;\s*\}",
    analyze_start.strip().replace("\\", "\\\\"),
    content
)

with open("app/Filament/Pages/AiStudio.php", "w") as f:
    f.write(content)
