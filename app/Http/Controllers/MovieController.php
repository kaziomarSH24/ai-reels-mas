<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\Movie;
use App\Models\MovieDialogue;
use Inertia\Inertia;
use Illuminate\Support\Facades\Http;

class MovieController extends Controller
{
    public function index()
    {
        return Inertia::render('Upload');
    }

    public function store(Request $request)
    {
        $request->validate([
            'title' => 'required|string|max:255',
            'genre' => 'nullable|string',
            'video_url' => 'required|url',
            'srt_url' => 'required|url'
        ]);

        try {
            // 1. Create the Movie record
            $movie = Movie::create([
                'title' => $request->title,
                'genre' => $request->genre,
                'source_url' => 'manual',
                'video_url' => $request->video_url,
                'subtitle_url' => $request->srt_url,
                'is_processed' => true,
            ]);

            // 2. Fetch the SRT file from the URL
            $response = Http::get($request->srt_url);
            if (!$response->successful()) {
                throw new \Exception("Could not fetch the SRT file from the provided URL.");
            }

            $srtContent = $response->body();

            // 3. Parse the SRT and save to movie_dialogues
            $this->parseAndSaveSRT($movie->id, $srtContent);

            return response()->json(['success' => true, 'message' => 'Movie and subtitles imported successfully!']);
            
        } catch (\Exception $e) {
            return response()->json(['success' => false, 'message' => $e->getMessage()], 500);
        }
    }

    private function parseAndSaveSRT($movieId, $srtContent)
    {
        // Normalize line endings
        $srtContent = str_replace("\r\n", "\n", $srtContent);
        $blocks = explode("\n\n", $srtContent);

        $dialogues = [];
        foreach ($blocks as $block) {
            $lines = explode("\n", trim($block));
            if (count($lines) >= 3) {
                // $lines[0] is the index
                // $lines[1] is the timestamp like 00:01:10,000 --> 00:01:15,000
                $times = explode(" --> ", $lines[1]);
                if (count($times) == 2) {
                    // Convert 00:01:10,000 to 00:01:10
                    $startTime = explode(',', $times[0])[0];
                    $endTime = explode(',', $times[1])[0];
                    
                    // The rest is the dialogue text
                    $text = implode(" ", array_slice($lines, 2));
                    
                    // Clean HTML tags if any (like <i> or <b>)
                    $text = strip_tags($text);

                    $dialogues[] = [
                        'movie_id' => $movieId,
                        'start_time' => $startTime,
                        'end_time' => $endTime,
                        'dialogue_text' => $text,
                        'emotion' => 'neutral',
                        'cefr_level' => 'B1',
                        'created_at' => now(),
                        'updated_at' => now(),
                    ];
                }
            }
        }

        // Chunk insert for performance
        $chunks = array_chunk($dialogues, 500);
        foreach ($chunks as $chunk) {
            MovieDialogue::insert($chunk);
        }
    }
}
