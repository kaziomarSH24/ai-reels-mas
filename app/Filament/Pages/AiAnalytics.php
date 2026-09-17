<?php

namespace App\Filament\Pages;

use Filament\Pages\Page;

class AiAnalytics extends Page
{
    protected static string|\UnitEnum|null $navigationGroup = 'AI & Automation';
    protected static ?int $navigationSort = 5;

    public static function getNavigationIcon(): string|\BackedEnum|null
    {
        return 'heroicon-o-chart-pie';
    }

    public static function getNavigationLabel(): string
    {
        return 'AI Analytics';
    }

    public function getTitle(): string|\Illuminate\Contracts\Support\Htmlable
    {
        return 'AI Model Analytics';
    }

    public static function getNavigationSort(): ?int
    {
        return 3;
    }

    protected string $view = 'filament.pages.ai-analytics';

    protected function getHeaderWidgets(): array
    {
        return [
            \App\Filament\Widgets\AiStatsWidget::class,
            \App\Filament\Widgets\EmotionPieChart::class,
            \App\Filament\Widgets\CefrBarChart::class,
        ];
    }
}
