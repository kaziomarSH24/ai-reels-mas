import re
filepath = 'app/Filament/Pages/ReelGenerator.php'
with open(filepath, 'r') as f:
    content = f.read()

pattern = r'\$untranslated = \$dialogues->filter\(fn\(\$d\) => empty\(\$d->translated_text\)\);'
replacement = r'$untranslated = $dialogues->filter(fn($d) => empty($d->translated_text) || str_contains($d->translated_text, "Will translate"));'

content = re.sub(pattern, replacement, content)

with open(filepath, 'w') as f:
    f.write(content)
print("JIT Patch applied!")
