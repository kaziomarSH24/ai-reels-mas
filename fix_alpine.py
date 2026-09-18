filepath = 'resources/views/filament/pages/ai-studio-native.blade.php'
with open(filepath, 'r') as f:
    content = f.read()

target1 = '''if(!interval) startProgress();'''
target2 = '''if(interval) { clearInterval(interval); interval = null; }'''

replacement1 = '''if(!this.interval) this.startProgress();'''
replacement2 = '''if(this.interval) { clearInterval(this.interval); this.interval = null; }'''

content = content.replace(target1, replacement1)
content = content.replace(target2, replacement2)

# Also fix the initial call
target3 = '''if ($el.style.display !== 'none') startProgress();'''
replacement3 = '''if ($el.style.display !== 'none') this.startProgress();'''
content = content.replace(target3, replacement3)

with open(filepath, 'w') as f:
    f.write(content)
print("Alpine bug fixed!")
