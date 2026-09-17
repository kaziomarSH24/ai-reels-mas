import re

with open("app/Filament/Pages/AiStudio.php", "r") as f:
    content = f.read()

# Replace the action logic
old_action = r"""
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
"""

new_action = r"""
                ->action(function (array $data) {
                    // In Filament 3, default disk might be 'private' or 'public'
                    $disk = \Illuminate\Support\Facades\Storage::disk();
                    if (\Illuminate\Support\Facades\Storage::disk('private')->exists($data['cookie_file'])) {
                         $disk = \Illuminate\Support\Facades\Storage::disk('private');
                    } elseif (\Illuminate\Support\Facades\Storage::disk('public')->exists($data['cookie_file'])) {
                         $disk = \Illuminate\Support\Facades\Storage::disk('public');
                    } elseif (\Illuminate\Support\Facades\Storage::disk('local')->exists($data['cookie_file'])) {
                         $disk = \Illuminate\Support\Facades\Storage::disk('local');
                    }
                    
                    $path = $disk->path($data['cookie_file']);
                    
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
                    } else {
                        \Filament\Notifications\Notification::make()->title('Error: File path not found ('.$path.')')->danger()->send();
                    }
                }),
"""

content = content.replace(old_action.strip(), new_action.strip())

with open("app/Filament/Pages/AiStudio.php", "w") as f:
    f.write(content)

