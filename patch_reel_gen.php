<?php
$content = file_get_contents("app/Filament/Pages/ReelGenerator.php");

$old_logic = <<<'OLD'
        // Search the DB for the best match
        $dialogue = MovieDialogue::with('movie')
            ->where('text', 'LIKE', '%' . $keyword . '%')
            ->orderBy('id', 'desc')
            ->first();

        if (!$dialogue) {
            Notification::make()->title('No clips found for this keyword')->danger()->send();
            return;
        }

        $this->isGenerating = true;
        Notification::make()->title('Starting FFmpeg Generator')->body('Clipping video from YouTube...')->info()->send();

        // Calculate duration
        $startSec = $this->timeToSeconds($dialogue->start_time);
        $endSec = $this->timeToSeconds($dialogue->end_time);
        $duration = max(3, ceil($endSec - $startSec)); // at least 3 seconds

        try {
            $outputFilename = 'reel_' . uniqid() . '.mp4';
            
            $response = Http::timeout(120)->post('http://ai_api:8001/api/generate_reel', [
                'source_url' => $dialogue->movie->youtube_url,
                'start_time' => $dialogue->start_time,
                'duration' => $duration,
                'output_filename' => $outputFilename,
                'english_text' => $dialogue->text,
                'bengali_text' => $dialogue->translated_text ?? 'An AI thesis project.'
            ]);
OLD;

$new_logic = <<<'NEW'
        // Search the DB for ALL matches (limit to 3 for a nice 15-second reel)
        // We will search by target_word exactly, or text LIKE if target_word doesn't match
        $dialogues = MovieDialogue::with('movie')
            ->where('target_word', 'LIKE', '%' . $keyword . '%')
            ->orWhere('text', 'LIKE', '%' . $keyword . '%')
            ->inRandomOrder()
            ->limit(3)
            ->get();

        if ($dialogues->isEmpty()) {
            Notification::make()->title('No clips found for this keyword')->danger()->send();
            return;
        }

        $this->isGenerating = true;
        Notification::make()->title('Compilation Reel Started')->body('Fetching ' . $dialogues->count() . ' clips from YouTube...')->info()->send();

        try {
            $outputFilename = 'reel_compilation_' . uniqid() . '.mp4';
            
            $clips = [];
            foreach ($dialogues as $dialogue) {
                $startSec = $this->timeToSeconds($dialogue->start_time);
                $endSec = $this->timeToSeconds($dialogue->end_time);
                $duration = max(3, ceil($endSec - $startSec));
                
                $clips[] = [
                    'source_url' => $dialogue->movie->youtube_url,
                    'start_time' => $dialogue->start_time,
                    'duration' => $duration,
                    'english_text' => $dialogue->text,
                    'bengali_text' => $dialogue->translated_text ?? 'An AI thesis project.',
                    'target_word' => $dialogue->target_word ?? $keyword
                ];
            }
            
            $response = Http::timeout(300)->post('http://ai_api:8001/api/generate_compilation', [
                'clips' => $clips,
                'output_filename' => $outputFilename
            ]);
NEW;

$content = str_replace($old_logic, $new_logic, $content);
file_put_contents("app/Filament/Pages/ReelGenerator.php", $content);
