import re

with open("app/Filament/Pages/ContentStrategy.php", "r") as f:
    content = f.read()

# Replace the problematic properties with methods or correct types
old_props = """    protected static ?string $navigationIcon = 'heroicon-o-light-bulb';
    protected static ?string $navigationLabel = 'AI Strategy';
    protected static ?string $title = 'AI Content Strategy';
    protected static ?int $navigationSort = 3;"""

new_props = """    protected static string | \BackedEnum | null $navigationIcon = 'heroicon-o-light-bulb';
    protected static ?string $navigationLabel = 'AI Strategy';
    protected static ?string $title = 'AI Content Strategy';
    protected static ?int $navigationSort = 3;"""

content = content.replace(old_props, new_props)

with open("app/Filament/Pages/ContentStrategy.php", "w") as f:
    f.write(content)
