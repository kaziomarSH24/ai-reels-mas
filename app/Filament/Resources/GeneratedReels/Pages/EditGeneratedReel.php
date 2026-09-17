<?php

namespace App\Filament\Resources\GeneratedReels\Pages;

use App\Filament\Resources\GeneratedReels\GeneratedReelResource;
use Filament\Actions\DeleteAction;
use Filament\Resources\Pages\EditRecord;

class EditGeneratedReel extends EditRecord
{
    protected static string $resource = GeneratedReelResource::class;

    protected function getHeaderActions(): array
    {
        return [
            DeleteAction::make(),
        ];
    }
}
