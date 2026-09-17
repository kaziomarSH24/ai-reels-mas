import re

with open("app/Filament/Resources/MovieDialogues/Tables/MovieDialoguesTable.php", "r") as f:
    content = f.read()

filters_code = """
                \Filament\Tables\Filters\SelectFilter::make('emotion')
                    ->options([
                        'JOY' => 'Joy',
                        'ANGER' => 'Anger',
                        'SADNESS' => 'Sadness',
                        'FEAR' => 'Fear',
                        'SURPRISE' => 'Surprise',
                        'LOVE' => 'Love',
                    ]),
                \Filament\Tables\Filters\SelectFilter::make('cefr_level')
                    ->options([
                        'A1' => 'A1 (Beginner)',
                        'A2' => 'A2 (Elementary)',
                        'B1' => 'B1 (Intermediate)',
                        'B2' => 'B2 (Upper Intermediate)',
                        'C1' => 'C1 (Advanced)',
                        'C2' => 'C2 (Mastery)',
                    ]),
"""

content = content.replace("->filters([\n                //\n            ])", "->filters([" + filters_code + "            ])")

with open("app/Filament/Resources/MovieDialogues/Tables/MovieDialoguesTable.php", "w") as f:
    f.write(content)
