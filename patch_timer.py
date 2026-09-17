with open("resources/views/filament/pages/ai-studio-native.blade.php", "r") as f:
    content = f.read()

old_timer = """<div x-data="{ seconds: 0, interval: null }"
                 x-init="interval = setInterval(() => seconds++, 1000)"
                 style="position: absolute; top: 1.5rem; right: 1.5rem; background-color: rgba(0,0,0,0.5); padding: 0.5rem 1rem; border-radius: 0.5rem; border: 1px solid rgba(16, 185, 129, 0.3); color: #10b981; font-family: monospace; font-size: 1.25rem; font-weight: bold; display: flex; align-items: center; gap: 0.5rem;">"""

new_timer = """<div x-data="{ seconds: 0 }"
                 x-init="setInterval(() => { if ($el.offsetWidth > 0) { seconds++; } else { seconds = 0; } }, 1000)"
                 style="position: absolute; top: 1.5rem; right: 1.5rem; background-color: rgba(0,0,0,0.5); padding: 0.5rem 1rem; border-radius: 0.5rem; border: 1px solid rgba(16, 185, 129, 0.3); color: #10b981; font-family: monospace; font-size: 1.25rem; font-weight: bold; display: flex; align-items: center; gap: 0.5rem;">"""

content = content.replace(old_timer, new_timer)

with open("resources/views/filament/pages/ai-studio-native.blade.php", "w") as f:
    f.write(content)
