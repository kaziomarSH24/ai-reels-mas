import re

path = '/Users/kaziomar/University/SEMESTER 07/AI/Lab-project/app/Filament/Pages/PlaylistImporter.php'
with open(path, 'r') as f:
    content = f.read()

# Replace the problematic properties with methods to avoid PHP 8.4 strict property type errors
old_props = """    protected static ?string $navigationIcon = 'heroicon-o-queue-list';
    protected static ?string $navigationGroup = 'Tools';
    protected static ?string $navigationLabel = 'Playlist Importer';
    protected static ?string $title = 'YouTube Playlist Bulk Importer';"""

new_methods = """    public static function getNavigationIcon(): ?string { return 'heroicon-o-queue-list'; }
    public static function getNavigationGroup(): ?string { return 'Tools'; }
    public static function getNavigationLabel(): string { return 'Playlist Importer'; }
    public function getTitle(): string|\Illuminate\Contracts\Support\Htmlable { return 'YouTube Playlist Bulk Importer'; }"""

content = content.replace(old_props, new_methods)

with open(path, 'w') as f:
    f.write(content)
