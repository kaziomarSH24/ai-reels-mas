filepath = 'app/Filament/Pages/ReelGenerator.php'
with open(filepath, 'r') as f:
    content = f.read()

target = '''$meaning = str_replace(["\\n", "\\r", "*", """], "", $meaning);'''
replacement = '''$meaning = str_replace(["\\n", "\\r", "*", "\\""], "", $meaning);'''

content = content.replace(target, replacement)

with open(filepath, 'w') as f:
    f.write(content)
print("Syntax Error Fixed!")
