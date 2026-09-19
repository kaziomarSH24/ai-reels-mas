<?php

namespace App\Filament\Resources\VideoClips\Pages;

use App\Filament\Resources\VideoClips\VideoClipResource;
use Filament\Actions\CreateAction;
use Filament\Resources\Pages\ListRecords;

class ListVideoClips extends ListRecords
{
    protected static string $resource = VideoClipResource::class;

    protected function getHeaderActions(): array
    {
        return [
            CreateAction::make(),
        ];
    }
}
