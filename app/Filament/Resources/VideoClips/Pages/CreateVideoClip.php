<?php

namespace App\Filament\Resources\VideoClips\Pages;

use App\Filament\Resources\VideoClips\VideoClipResource;
use Filament\Resources\Pages\CreateRecord;

class CreateVideoClip extends CreateRecord
{
    protected static string $resource = VideoClipResource::class;
}
