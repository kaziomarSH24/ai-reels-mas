import re

with open("app/Filament/Resources/MovieDialogues/Tables/MovieDialoguesTable.php", "r") as f:
    content = f.read()

# Make sure we have the MovieDialogue model imported
if "use App\Models\MovieDialogue;" not in content:
    content = content.replace("use Filament\Tables\Table;", "use Filament\Tables\Table;\nuse App\Models\MovieDialogue;")

new_columns = """
                TextColumn::make('movie_id')
                    ->numeric()
                    ->sortable()
                    ->toggleable(isToggledHiddenByDefault: true),
                TextColumn::make('start_time')
                    ->label('Time')
                    ->badge()
                    ->color('gray')
                    ->searchable(),
                TextColumn::make('text')
                    ->label('Original Dialogue')
                    ->wrap()
                    ->searchable(),
                TextColumn::make('target_word')
                    ->label('Target Word')
                    ->badge()
                    ->color('warning')
                    ->searchable(),
                TextColumn::make('emotion')
                    ->label('Emotion')
                    ->badge()
                    ->color(fn (?string $state): string => match ($state) {
                        'JOY' => 'success',
                        'ANGER' => 'danger',
                        'SADNESS' => 'warning',
                        'FEAR' => 'danger',
                        'SURPRISE' => 'info',
                        'LOVE' => 'pink',
                        default => 'gray',
                    })
                    ->description(fn (MovieDialogue $record): string => $record->emotion_confidence ? $record->emotion_confidence . '%' : '')
                    ->searchable(),
                TextColumn::make('translated_text')
                    ->label('Translation')
                    ->wrap()
                    ->searchable(),
                TextColumn::make('cefr_level')
                    ->label('CEFR Level')
                    ->badge()
                    ->color(fn (?string $state): string => match ($state) {
                        'A1', 'A2' => 'gray',
                        'B1' => 'info',
                        'B2', 'C1', 'C2' => 'success',
                        default => 'gray',
                    })
                    ->description(fn (MovieDialogue $record): string => $record->cefr_confidence ? $record->cefr_confidence . '%' : '')
                    ->searchable(),
"""

# Replace the columns array
content = re.sub(
    r"TextColumn::make\('movie_id'\)[\s\S]*?TextColumn::make\('cefr_level'\)[\s\S]*?->searchable\(\),",
    new_columns.strip(),
    content
)

with open("app/Filament/Resources/MovieDialogues/Tables/MovieDialoguesTable.php", "w") as f:
    f.write(content)
