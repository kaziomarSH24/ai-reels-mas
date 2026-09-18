import re
filepath = 'resources/views/filament/pages/reel-generator.blade.php'
with open(filepath, 'r') as f:
    content = f.read()

target = '''<x-filament::button tag="a" href="{{ $generatedReelUrl }}" download color="success" size="lg" icon="heroicon-m-arrow-down-tray">'''
replacement = '''<x-filament::button tag="a" href="{{ $generatedReelUrl }}" download="AI_Reel_{{ str_replace([' ', '.'], '_', $reelData['keyword'] ?? 'Compilation') }}.mp4" color="success" size="lg" icon="heroicon-m-arrow-down-tray">'''

content = content.replace(target, replacement)
with open(filepath, 'w') as f:
    f.write(content)
print("Download attribute updated!")
