<?php

namespace App\Filament\Resources\GeneratedReels\Pages;

use App\Filament\Resources\GeneratedReels\GeneratedReelResource;
use Filament\Actions\CreateAction;
use Filament\Resources\Pages\ListRecords;

class ListGeneratedReels extends ListRecords
{
    protected static string $resource = GeneratedReelResource::class;

    protected function getHeaderActions(): array
    {
        return [
            CreateAction::make(),
        ];
    }
}
