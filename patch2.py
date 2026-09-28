import re

file_path = "/Users/kaziomar/University/SEMESTER 07/AI/Lab-project/app/Filament/Pages/PlaylistImporter.php"
with open(file_path, "r") as f:
    content = f.read()

content = content.replace("use Filament\Forms\Form;", "use Filament\Schemas\Schema;\nuse Filament\Schemas\Components\Section;")
content = content.replace("use Filament\Forms\Components\Section;\n", "")
content = content.replace("public function form(Form $form): Form", "public function form(Schema $form): Schema")
content = content.replace("->schema([", "->components([")

with open(file_path, "w") as f:
    f.write(content)

print("Patched.")
