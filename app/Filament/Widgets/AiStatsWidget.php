<?php

namespace App\Filament\Widgets;

use Filament\Widgets\StatsOverviewWidget;
use Filament\Widgets\StatsOverviewWidget\Stat;
use App\Models\Video;
use App\Models\VideoClip;
use App\Models\GeneratedReel;

class AiStatsWidget extends StatsOverviewWidget
{
    protected static ?int $sort = 1;

    protected function getStats(): array
    {
        $totalVideos = Video::count();
        $totalPhrases = VideoClip::count();
        $totalReels = GeneratedReel::count();

        return [
            Stat::make('Total YouTube Videos Processed', $totalVideos)
                ->description('URLs successfully extracted')
                ->descriptionIcon('heroicon-m-video-camera')
                ->color('primary'),
                
            Stat::make('Premium Phrases Extracted', $totalPhrases)
                ->description('Idioms, Phrases, and Vocabulary')
                ->descriptionIcon('heroicon-m-sparkles')
                ->color('success')
                ->chart([3, 5, 10, 15, 20, 30, $totalPhrases]),
                
            Stat::make('Viral Reels Generated', $totalReels)
                ->description('Fully rendered compilation videos')
                ->descriptionIcon('heroicon-m-film')
                ->color('warning')
                ->chart([1, 2, 3, 5, 8, 12, $totalReels]),
        ];
    }
}
