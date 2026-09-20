<?php

namespace App\Filament\Resources\ScrapedClips\Pages;

use App\Filament\Resources\ScrapedClips\ScrapedClipResource;
use Filament\Actions\DeleteAction;
use Filament\Resources\Pages\EditRecord;

class EditScrapedClip extends EditRecord
{
    protected static string $resource = ScrapedClipResource::class;

    protected function getHeaderActions(): array
    {
        return [
            DeleteAction::make(),
        ];
    }
}
