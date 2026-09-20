<?php

namespace App\Filament\Resources\VideoJobs\Pages;

use App\Filament\Resources\VideoJobs\VideoJobResource;
use Filament\Actions\DeleteAction;
use Filament\Resources\Pages\EditRecord;

class EditVideoJob extends EditRecord
{
    protected static string $resource = VideoJobResource::class;

    protected function getHeaderActions(): array
    {
        return [
            DeleteAction::make(),
        ];
    }
}
