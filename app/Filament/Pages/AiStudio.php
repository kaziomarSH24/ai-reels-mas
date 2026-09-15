<?php

namespace App\Filament\Pages;

use Filament\Pages\Page;
use BackedEnum;

class AiStudio extends Page
{
    protected string $view = 'filament.pages.ai-studio';

    public static function getNavigationIcon(): string|BackedEnum|null
    {
        return 'heroicon-o-sparkles';
    }

    public static function getNavigationLabel(): string
    {
        return 'AI Studio';
    }

    public static function getNavigationSort(): ?int
    {
        return 1;
    }
}
