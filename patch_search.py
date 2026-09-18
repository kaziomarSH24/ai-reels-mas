import re
filepath = 'app/Filament/Pages/ReelGenerator.php'
with open(filepath, 'r') as f:
    content = f.read()

# Add the keyword translation logic right before returning results
target = '''$results = [];
        $results = [];
        foreach ($dialogues as $d) {'''

replacement = '''
        // Fetch keyword dictionary meaning
        $keywordMeaning = "";
        try {
            $meaningPrompt = "What is the Bengali dictionary meaning of the English word/idiom: '{$keyword}'? Return ONLY 2-3 words. No English.";
            $meaningResponse = Http::timeout(5)->post("https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent?key={$apiKey}", [
                'contents' => [['parts' => [['text' => $meaningPrompt]]]],
                'generationConfig' => ['temperature' => 0.1]
            ]);
            if ($meaningResponse->successful()) {
                $data = $meaningResponse->json();
                $meaning = trim($data['candidates'][0]['content']['parts'][0]['text'] ?? '');
                $meaning = str_replace(["\\n", "\\r", "*", "\""], "", $meaning);
                if (!empty($meaning)) {
                    $keywordMeaning = " <br><span style='color: #9ca3af; font-size: 0.85em;'>(অর্থ: " . $meaning . ")</span>";
                }
            }
        } catch (\Exception $e) {}

        $results = [];
        foreach ($dialogues as $d) {
            $displayTarget = ($keyword ?? $d->target_word) . $keywordMeaning;'''

content = content.replace(target, replacement)

# Replace the target_word usage in the array assignment
target2 = '''                'target_word' => $keyword ?? $d->target_word,'''
replacement2 = '''                'target_word' => $displayTarget,'''

content = content.replace(target2, replacement2)

with open(filepath, 'w') as f:
    f.write(content)
print("Keyword Meaning Patch applied!")
