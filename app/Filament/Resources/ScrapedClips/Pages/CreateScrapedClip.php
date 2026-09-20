<?php

namespace App\Filament\Resources\ScrapedClips\Pages;

use App\Filament\Resources\ScrapedClips\ScrapedClipResource;
use Filament\Resources\Pages\CreateRecord;

class CreateScrapedClip extends CreateRecord
{
    protected static string $resource = ScrapedClipResource::class;
}
