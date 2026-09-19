<?php

namespace App\Filament\Widgets;

use Filament\Widgets\StatsOverviewWidget;
use Filament\Widgets\StatsOverviewWidget\Stat;

class AiStatsWidget extends StatsOverviewWidget
{
    protected function getStats(): array
    {
        $totalVideos = \App\Models\Video::count();
        $totalDialogues = \App\Models\VideoClip::count();
        $analyzed = \App\Models\VideoClip::whereNotNull('emotion')->count();

        return [
            Stat::make('Total Videos Processed', $totalVideos)
                ->description('YouTube URLs extracted')
                ->descriptionIcon('heroicon-m-video-camera')
                ->color('primary'),
                
            Stat::make('Total Dialogues', $totalDialogues)
                ->description('Lines of text saved')
                ->descriptionIcon('heroicon-m-document-text')
                ->color('info'),
                
            Stat::make('AI Analyzed Lines', $analyzed)
                ->description('Processed by DistilBERT & BanglaT5')
                ->descriptionIcon('heroicon-m-cpu-chip')
                ->color('success')
                ->chart([7, 2, 10, 3, 15, 4, 17]),
        ];
    }
}
