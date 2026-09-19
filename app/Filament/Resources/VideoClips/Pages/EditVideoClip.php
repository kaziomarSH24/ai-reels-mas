<?php

namespace App\Filament\Resources\VideoClips\Pages;

use App\Filament\Resources\VideoClips\VideoClipResource;
use Filament\Actions\DeleteAction;
use Filament\Resources\Pages\EditRecord;

class EditVideoClip extends EditRecord
{
    protected static string $resource = VideoClipResource::class;

    protected function getHeaderActions(): array
    {
        return [
            DeleteAction::make(),
        ];
    }
}
