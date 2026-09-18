import re
filepath = 'app/Filament/Pages/ReelGenerator.php'
with open(filepath, 'r') as f:
    content = f.read()

# Add a public property for fetchedMeaning
target_prop = 'public bool $hasSearched = false;'
replacement_prop = 'public bool $hasSearched = false;\n    public ?string $fetchedMeaning = null;'
if 'public ?string $fetchedMeaning' not in content:
    content = content.replace(target_prop, replacement_prop)

# Update the Gemini prompt and save to the property
target_prompt = '''$meaningPrompt = "What are the top 2-3 possible Bengali dictionary meanings of the English word/idiom: '{$keyword}'? Return them as a comma-separated list. No English words.";'''
replacement_prompt = '''$meaningPrompt = "What are the top 2-3 possible Bengali dictionary meanings of the English word/idiom: '{$keyword}'? Return them separated by slashes (/). Example: লজ্জায় পড়া / অপদস্থ হওয়া / বোকা বনে যাওয়া. No English words.";'''
content = content.replace(target_prompt, replacement_prompt)

target_meaning = '''if (!empty($meaning)) {
                    $keywordMeaning = " <br><span style='color: #9ca3af; font-size: 0.85em;'>(অর্থ: " . $meaning . ")</span>";
                }'''
replacement_meaning = '''if (!empty($meaning)) {
                    $this->fetchedMeaning = $meaning;
                    $keywordMeaning = " <br><span style='color: #9ca3af; font-size: 0.85em;'>(অর্থ: " . $meaning . ")</span>";
                }'''
content = content.replace(target_meaning, replacement_meaning)

# Pass it to Python
target_payload = ''''target_word' => $keyword ?? $dialogue['target_word']
                ];'''
replacement_payload = ''''target_word' => $keyword ?? $dialogue['target_word'],
                    'dictionary_meaning' => $this->fetchedMeaning
                ];'''
content = content.replace(target_payload, replacement_payload)

with open(filepath, 'w') as f:
    f.write(content)
print("PHP Payload updated!")
