<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Services\AIService;
use App\Models\AnalysisHistory;
use Exception;
use Inertia\Inertia;

class EmotionController extends Controller
{
    protected $aiService;

    public function __construct(AIService $aiService)
    {
        $this->aiService = $aiService;
    }

    /**
     * Display the dashboard with history.
     */
    public function index()
    {
        $history = AnalysisHistory::where('user_id', auth()->id())
            ->latest()
            ->take(10)
            ->get();

        return Inertia::render('Dashboard', [
            'history' => $history
        ]);
    }

    /**
     * Process the emotion detection and save to database.
     */
    public function detect(Request $request)
    {
        $request->validate([
            'sentence' => 'required|string|max:1000'
        ]);

        $sentence = $request->input('sentence');

        try {
            $data = $this->aiService->analyze($sentence);

            // Save to Database
            AnalysisHistory::create([
                'user_id' => auth()->id(),
                'sentence' => $sentence,
                'emotion' => $data['emotion'],
                'confidence' => $data['confidence'],
                'cefr_level' => $data['cefr_level'],
                'translation' => $data['translation'],
            ]);

            $result = $data;
        } catch (Exception $e) {
            $result = ['error' => 'Failed to connect to AI Microservice: ' . $e->getMessage()];
        }

        return back()->with('result', $result)->with('sentence', $sentence);
    }
}
