<?php

namespace App\Filament\Resources\ScrapedClips\Pages;

use App\Filament\Resources\ScrapedClips\ScrapedClipResource;
use Filament\Actions\CreateAction;
use Filament\Resources\Pages\ListRecords;

class ListScrapedClips extends ListRecords
{
    protected static string $resource = ScrapedClipResource::class;

    protected function getHeaderActions(): array
    {
        return [
            CreateAction::make(),
        ];
    }
}
