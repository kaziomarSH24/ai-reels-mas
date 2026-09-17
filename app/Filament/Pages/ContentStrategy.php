<?php

namespace App\Filament\Pages;

use Filament\Pages\Page;
use App\Models\MovieDialogue;
use Illuminate\Support\Facades\Http;
use Filament\Actions\Action;

class ContentStrategy extends Page
{
    protected static ?string $navigationIcon = 'heroicon-o-light-bulb';
    protected static ?string $navigationLabel = 'AI Strategy';
    protected static ?string $title = 'AI Content Strategy';
    protected static ?int $navigationSort = 3;

    protected static string $view = 'filament.pages.content-strategy';

    public ?string $aiRecommendation = null;
    public bool $isLoading = false;

    protected function getHeaderActions(): array
    {
        return [
            Action::make('generate_strategy')
                ->label('Ask Gemini for Today\'s Best Reels')
                ->icon('heroicon-o-sparkles')
                ->color('primary')
                ->action('generateStrategy')
                ->requiresConfirmation()
                ->modalHeading('Generate AI Strategy')
                ->modalDescription('Gemini will analyze your database words and recommend the best ones for today. This may take a few seconds.'),
        ];
    }

    public function generateStrategy()
    {
        $this->isLoading = true;
        
        try {
            // Get unique target words from the database
            $words = MovieDialogue::whereNotNull('target_word')
                ->where('target_word', '!=', '')
                ->distinct()
                ->pluck('target_word')
                ->toArray();
                
            if (empty($words)) {
                $this->aiRecommendation = "No target words found in the database. Please add some videos first.";
                $this->isLoading = false;
                return;
            }

            // Shuffle and take max 200 words to avoid hitting Gemini token limits unnecessarily
            shuffle($words);
            $wordsToAnalyze = array_slice($words, 0, 200);
            $wordsList = implode(", ", $wordsToAnalyze);

            $apiKey = env('GEMINI_API_KEY');
            if (!$apiKey) {
                $this->aiRecommendation = "Error: GEMINI_API_KEY is missing in your .env file.";
                $this->isLoading = false;
                return;
            }

            $prompt = "You are an expert Social Media Strategist and English Teacher for a Bengali audience on TikTok/YouTube Shorts. " .
                      "Here is a list of English vocabulary words available in my database right now: [ $wordsList ]. " .
                      "Please analyze these words and recommend the TOP 5 best words for me to make video reels on TODAY. " .
                      "Pick words that are trendy, emotionally impactful, or highly useful in daily conversation. " .
                      "For each word, provide: 1) The Word, 2) The Bengali Meaning, 3) Why it makes a great viral video reel. " .
                      "Format your response in beautiful Markdown, using bold text, bullet points, and emojis. Respond in Bengali.";

            $response = Http::timeout(30)->post("https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={$apiKey}", [
                'contents' => [
                    ['parts' => [['text' => $prompt]]]
                ],
                'generationConfig' => [
                    'temperature' => 0.7,
                ]
            ]);

            if ($response->successful()) {
                $data = $response->json();
                if (isset($data['candidates'][0]['content']['parts'][0]['text'])) {
                    $this->aiRecommendation = $data['candidates'][0]['content']['parts'][0]['text'];
                } else {
                    $this->aiRecommendation = "Received an unexpected response from Gemini.";
                }
            } else {
                $this->aiRecommendation = "Error communicating with Gemini API: " . $response->body();
            }
        } catch (\Exception $e) {
            $this->aiRecommendation = "An error occurred: " . $e->getMessage();
        }

        $this->isLoading = false;
    }
}
