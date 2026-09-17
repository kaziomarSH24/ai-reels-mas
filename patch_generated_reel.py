import re

with open("app/Models/GeneratedReel.php", "r") as f:
    content = f.read()

new_model = """
class GeneratedReel extends Model
{
    protected $fillable = [
        'target_word',
        'file_path',
        'is_posted_to_fb',
    ];
}
"""

content = re.sub(r"class GeneratedReel extends Model\s*\{\s*//\s*\}", new_model.strip(), content)

with open("app/Models/GeneratedReel.php", "w") as f:
    f.write(content)

with open("app/Filament/Resources/GeneratedReels/GeneratedReelResource.php", "r") as f:
    resource_content = f.read()

can_create_code = """
    public static function canCreate(): bool
    {
        return false;
    }
"""

if "public static function canCreate" not in resource_content:
    resource_content = resource_content.replace("    public static function getRelations(): array", can_create_code + "\n    public static function getRelations(): array")

with open("app/Filament/Resources/GeneratedReels/GeneratedReelResource.php", "w") as f:
    f.write(resource_content)
