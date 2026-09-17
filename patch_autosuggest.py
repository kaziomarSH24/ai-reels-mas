import re

with open("app/Filament/Pages/ReelGenerator.php", "r") as f:
    content = f.read()

new_input = r"""
                        \Filament\Forms\Components\TextInput::make('keyword')
                            ->label('Target Keyword')
                            ->placeholder('e.g., Destiny, Boss, Love')
                            ->datalist(function () {
                                return \App\Models\MovieDialogue::whereNotNull('target_word')
                                    ->where('target_word', '!=', 'None')
                                    ->select('target_word')
                                    ->distinct()
                                    ->limit(100)
                                    ->pluck('target_word')
                                    ->toArray();
                            })
                            ->required(),
"""

content = re.sub(
    r"TextInput::make\('keyword'\)[\s\S]*?->required\(\),",
    new_input.strip().replace("\\", "\\\\"),
    content
)

with open("app/Filament/Pages/ReelGenerator.php", "w") as f:
    f.write(content)
