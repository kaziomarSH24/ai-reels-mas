import re

with open("app/Filament/Resources/GeneratedReels/GeneratedReelResource.php", "r") as f:
    content = f.read()

# Remove the Create action from the List page
# Wait, I need to check how ListGeneratedReels is defined or I can just override canCreate() in the Resource
can_create_code = """
    public static function canCreate(): bool
    {
        return false;
    }
"""

if "public static function canCreate" not in content:
    # Insert it before getRelations
    content = content.replace("    public static function getRelations(): array", can_create_code + "\n    public static function getRelations(): array")

with open("app/Filament/Resources/GeneratedReels/GeneratedReelResource.php", "w") as f:
    f.write(content)
