<?php

namespace App\Filament\Resources\MovieDialogues\Pages;

use App\Filament\Resources\MovieDialogues\MovieDialogueResource;
use Filament\Actions\CreateAction;
use Filament\Resources\Pages\ListRecords;

class ListMovieDialogues extends ListRecords
{
    protected static string $resource = MovieDialogueResource::class;

    protected function getHeaderActions(): array
    {
        return [
            CreateAction::make(),
        ];
    }
}
