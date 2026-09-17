import re

with open("app/Filament/Pages/ReelGenerator.php", "r") as f:
    content = f.read()

search_code = """
        // Fetch more results to allow for deduplication
        $rawDialogues = MovieDialogue::with('movie')
            ->where('target_word', 'LIKE', '%' . $keyword . '%')
            ->orWhere('text', 'LIKE', '%' . $keyword . '%')
            ->inRandomOrder()
            ->limit(20)
            ->get();

        // Filter out duplicate text to prevent the same sentence from appearing 3 times
        $dialogues = $rawDialogues->unique('text')->take(3);
"""

# Replace the old query
content = re.sub(
    r"\$dialogues = MovieDialogue::with\('movie'\)[\s\S]*?->get\(\);", 
    search_code.strip(), 
    content
)

with open("app/Filament/Pages/ReelGenerator.php", "w") as f:
    f.write(content)
