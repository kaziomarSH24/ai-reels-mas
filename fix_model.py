filepath = 'app/Filament/Pages/ReelGenerator.php'
with open(filepath, 'r') as f:
    content = f.read()

content = content.replace('gemini-1.5-flash', 'gemini-3.5-flash')

with open(filepath, 'w') as f:
    f.write(content)
print("Gemini model name reverted!")
