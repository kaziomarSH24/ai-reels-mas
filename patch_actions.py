import re

with open("app/Filament/Resources/GeneratedReels/GeneratedReelResource.php", "r") as f:
    content = f.read()

content = content.replace("use Filament\Tables\Actions\EditAction;", "use Filament\Actions\EditAction;")
content = content.replace("use Filament\Tables\Actions\DeleteAction;", "use Filament\Actions\DeleteAction;")
content = content.replace("use Filament\Tables\Actions\BulkActionGroup;", "use Filament\Actions\BulkActionGroup;")
content = content.replace("use Filament\Tables\Actions\DeleteBulkAction;", "use Filament\Actions\DeleteBulkAction;")

# Wait, the action methods in Table class are `actions()` and `bulkActions()` 
# Wait, let's look at MoviesTable again
# It used `recordActions` instead of `actions`?
