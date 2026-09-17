import re

with open("app/Filament/Resources/GeneratedReels/GeneratedReelResource.php", "r") as f:
    content = f.read()

# Fix imports (using proper escapes or raw strings)
content = content.replace(r"use Filament\Tables\Actions\EditAction;", r"use Filament\Actions\EditAction;")
content = content.replace(r"use Filament\Tables\Actions\DeleteAction;", r"use Filament\Actions\DeleteAction;")
content = content.replace(r"use Filament\Tables\Actions\BulkActionGroup;", r"use Filament\Actions\BulkActionGroup;")
content = content.replace(r"use Filament\Tables\Actions\DeleteBulkAction;", r"use Filament\Actions\DeleteBulkAction;")

# Fix method names
content = content.replace("->actions([", "->recordActions([")
content = content.replace("->bulkActions([", "->toolbarActions([")

with open("app/Filament/Resources/GeneratedReels/GeneratedReelResource.php", "w") as f:
    f.write(content)
