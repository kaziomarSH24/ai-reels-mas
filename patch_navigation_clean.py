import re
import os

def set_nav(filepath, group, sort):
    if not os.path.exists(filepath):
        return
        
    with open(filepath, "r") as f:
        content = f.read()
        
    # First remove any existing nav group/sort
    content = re.sub(r"^[ \t]*protected static \?int \$navigationSort.*?\n", "", content, flags=re.MULTILINE)
    content = re.sub(r"^[ \t]*protected static (\?string|string\|\s*\\?UnitEnum\s*\|null)\s*\$navigationGroup.*?\n", "", content, flags=re.MULTILINE)
    
    # Simple PHP injection code
    nav_code = f"    protected static string|\\UnitEnum|null $navigationGroup = '{group}';\n    protected static ?int $navigationSort = {sort};\n"
        
    # Just put it inside class
    content = re.sub(r"(class \w+ extends [A-Za-z0-9_\\]+(?:\s+implements [A-Za-z0-9_\\,\s]+)?\s*{)", r"\1\n" + nav_code.replace("\\", "\\\\"), content, count=1)
        
    with open(filepath, "w") as f:
        f.write(content)

# Apply settings
set_nav("app/Filament/Resources/Movies/MovieResource.php", "Data Management", 1)
set_nav("app/Filament/Resources/MovieDialogues/MovieDialogueResource.php", "Data Management", 2)

set_nav("app/Filament/Pages/ContentStrategy.php", "AI & Automation", 1)
set_nav("app/Filament/Pages/ReelGenerator.php", "AI & Automation", 2)
set_nav("app/Filament/Resources/GeneratedReels/GeneratedReelResource.php", "AI & Automation", 3)
set_nav("app/Filament/Pages/AiStudio.php", "AI & Automation", 4)
set_nav("app/Filament/Pages/AiAnalytics.php", "AI & Automation", 5)

