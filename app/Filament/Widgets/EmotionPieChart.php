<?php

namespace App\Filament\Widgets;

use Filament\Widgets\ChartWidget;

class EmotionPieChart extends ChartWidget
{
    protected ?string $heading = 'DistilBERT Emotion Breakdown';
    protected static ?int $sort = 1;

    protected function getData(): array
    {
        $data = \App\Models\MovieDialogue::whereNotNull('emotion')
            ->selectRaw('emotion, count(*) as count')
            ->groupBy('emotion')
            ->pluck('count', 'emotion')
            ->toArray();

        return [
            'datasets' => [
                [
                    'label' => 'Emotions',
                    'data' => array_values($data),
                    'backgroundColor' => [
                        '#10b981', // JOY (Green)
                        '#ef4444', // ANGER (Red)
                        '#f59e0b', // SADNESS (Orange/Yellow)
                        '#6366f1', // FEAR (Indigo)
                        '#3b82f6', // SURPRISE (Blue)
                        '#ec4899', // LOVE (Pink)
                        '#6b7280', // NEUTRAL
                    ],
                ],
            ],
            'labels' => array_keys($data),
        ];
    }

    protected function getType(): string
    {
        return 'doughnut';
    }
}
