<?php

namespace App\Filament\Resources\MovieDialogues\Pages;

use App\Filament\Resources\MovieDialogues\MovieDialogueResource;
use Filament\Actions\DeleteAction;
use Filament\Resources\Pages\EditRecord;

class EditMovieDialogue extends EditRecord
{
    protected static string $resource = MovieDialogueResource::class;

    protected function getHeaderActions(): array
    {
        return [
            DeleteAction::make(),
        ];
    }
}
