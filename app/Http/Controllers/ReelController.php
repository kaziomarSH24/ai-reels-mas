<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\MovieDialogue;
use App\Models\Movie;
use Illuminate\Support\Facades\Http;
use Inertia\Inertia;

class ReelController extends Controller
{
    /**
     * Show the Studio page for generating reels.
     */
    public function studio()
    {
        return Inertia::render('Studio');
    }

    /**
     * Search dialogues via Full-Text Search or simple LIKE query.
     */
    public function search(Request $request)
    {
        $query = $request->input('query');
        
        if (!$query) {
            return response()->json([]);
        }

        // Full-Text Search on dialogue_text
        $dialogues = MovieDialogue::with('movie')
            ->whereRaw('MATCH(dialogue_text) AGAINST(? IN BOOLEAN MODE)', [$query])
            ->orWhere('dialogue_text', 'LIKE', '%' . $query . '%')
            ->orWhere('emotion', 'LIKE', '%' . $query . '%')
            ->limit(10)
            ->get();

        return response()->json($dialogues);
    }

    /**
     * Communicate with the Python Engine to generate the video reel.
     */
    public function generate(Request $request)
    {
        $request->validate([
            'dialogue_id' => 'required|exists:movie_dialogues,id',
        ]);

        $dialogue = MovieDialogue::with('movie')->findOrFail($request->dialogue_id);

        // Convert duration logic (e.g. 00:00:15 - 00:00:10 = 5 seconds)
        // For simplicity, hardcode 10 seconds for reels if not exact
        $duration = 10; 
        
        $payload = [
            'source_url' => $dialogue->movie->video_url ?? 'https://test-videos.co.uk/vids/bigbuckbunny/mp4/h264/720/Big_Buck_Bunny_720_10s_1MB.mp4',
            'start_time' => '00:00:00', // Hardcoded for testing with the 10s clip
            'duration' => 5, // Cut 5 seconds
            'output_filename' => 'reel_' . $dialogue->id . '_' . time() . '.mp4'
        ];

        // Call the internal Python Microservice running on port 8001
        try {
            $response = Http::post('http://ai_api:8001/api/generate_reel', $payload);
            
            if ($response->successful()) {
                return response()->json([
                    'success' => true,
                    'reel_url' => '/reels/' . $payload['output_filename'],
                    'message' => 'Reel generated successfully!'
                ]);
            }

            return response()->json(['success' => false, 'message' => 'Python Engine Error: ' . $response->body()], 500);

        } catch (\Exception $e) {
            return response()->json(['success' => false, 'message' => 'Failed to connect to AI Engine: ' . $e->getMessage()], 500);
        }
    }
}
