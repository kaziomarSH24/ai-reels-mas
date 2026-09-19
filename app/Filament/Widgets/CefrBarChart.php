<?php

namespace App\Filament\Widgets;

use Filament\Widgets\ChartWidget;

class CefrBarChart extends ChartWidget
{
    protected ?string $heading = 'CEFR Difficulty Level Breakdown';
    protected static ?int $sort = 2;

    protected function getData(): array
    {
        $data = \App\Models\VideoClip::whereNotNull('cefr_level')
            ->selectRaw('cefr_level, count(*) as count')
            ->groupBy('cefr_level')
            ->orderBy('cefr_level')
            ->pluck('count', 'cefr_level')
            ->toArray();

        return [
            'datasets' => [
                [
                    'label' => 'Total Dialogues',
                    'data' => array_values($data),
                    'backgroundColor' => '#3b82f6',
                ],
            ],
            'labels' => array_keys($data),
        ];
    }

    protected function getType(): string
    {
        return 'bar';
    }
}
