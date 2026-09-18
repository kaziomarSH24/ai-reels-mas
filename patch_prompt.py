filepath = 'app/Filament/Pages/ReelGenerator.php'
with open(filepath, 'r') as f:
    content = f.read()

target = '''$meaningPrompt = "What is the Bengali dictionary meaning of the English word/idiom: '{$keyword}'? Return ONLY 2-3 words. No English.";'''
replacement = '''$meaningPrompt = "What are the top 2-3 possible Bengali dictionary meanings of the English word/idiom: '{$keyword}'? Return them as a comma-separated list. No English words.";'''

content = content.replace(target, replacement)

with open(filepath, 'w') as f:
    f.write(content)
print("Prompt updated!")
