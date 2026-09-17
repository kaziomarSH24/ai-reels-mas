with open("app/Filament/Pages/AiStudio.php", "r") as f:
    content = f.read()

# Add target_word to DB insert logic
insert_accepted_old = """'cefr_confidence' => $dialogue['analysis']['cefr_confidence'] ?? null,
                        'translated_text' => $dialogue['analysis']['translation'] ?? null,"""
insert_accepted_new = """'cefr_confidence' => $dialogue['analysis']['cefr_confidence'] ?? null,
                        'target_word' => $dialogue['analysis']['target_word'] ?? null,
                        'translated_text' => $dialogue['analysis']['translation'] ?? null,"""
content = content.replace(insert_accepted_old, insert_accepted_new)

# Add target_word to Filament UI Table
ui_old = """                TextColumn::make('cefr_level')
                    ->label('Difficulty')"""
ui_new = """                TextColumn::make('target_word')
                    ->label('Target Word')
                    ->badge()
                    ->color('warning')
                    ->searchable(),
                TextColumn::make('cefr_level')
                    ->label('Difficulty')"""
content = content.replace(ui_old, ui_new)

with open("app/Filament/Pages/AiStudio.php", "w") as f:
    f.write(content)
