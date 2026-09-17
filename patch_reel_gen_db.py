import re

with open("app/Filament/Pages/ReelGenerator.php", "r") as f:
    content = f.read()

old_code = """            if ($response->successful()) {
                $data = $response->json();
                $this->generatedReelUrl = $data['data']['output_path'];
                Notification::make()->title('Reel Generated!')->success()->send();
            }"""

new_code = """            if ($response->successful()) {
                $data = $response->json();
                $this->generatedReelUrl = $data['data']['output_path'];
                
                // Save to database
                \App\Models\GeneratedReel::create([
                    'target_word' => $targetWord,
                    'file_path' => $this->generatedReelUrl,
                    'is_posted_to_fb' => false,
                ]);
                
                Notification::make()->title('Reel Generated & Saved!')->success()->send();
            }"""

content = content.replace(old_code, new_code)

with open("app/Filament/Pages/ReelGenerator.php", "w") as f:
    f.write(content)
