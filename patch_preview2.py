filepath = 'resources/views/filament/pages/ai-studio-native.blade.php'
with open(filepath, 'r') as f:
    content = f.read()

target = '<div class="w-full">\n        {{ $this->analyzerForm }}\n    </div>'

replacement = '''<div class="w-full">
        {{ $this->analyzerForm }}
    </div>

    <!-- Dynamic YouTube Preview -->
    <div x-data="{ 
            url: @entangle('analyzerData.youtubeUrl').live,
            videoId() {
                if (!this.url) return null;
                const regExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|\&v=)([^#\&\?]*).*/;
                const match = this.url.match(regExp);
                return (match && match[2].length === 11) ? match[2] : null;
            }
        }"
        x-show="videoId()"
        style="display: none; margin-top: 1rem; padding: 1.5rem; background-color: rgba(17, 24, 39, 0.9); border-radius: 0.75rem; border: 1px solid rgba(16, 185, 129, 0.4); align-items: flex-start; gap: 1.5rem;"
        :style="videoId() ? 'display: flex;' : 'display: none;'">
        
        <div style="position: relative; width: 240px; border-radius: 0.5rem; overflow: hidden; border: 1px solid rgba(255,255,255,0.1); flex-shrink: 0;">
            <img :src="'https://img.youtube.com/vi/' + videoId() + '/hqdefault.jpg'" style="width: 100%; height: auto; object-fit: cover; aspect-ratio: 16/9;">
            <div style="position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; background-color: rgba(0,0,0,0.2);">
                <svg style="width: 3rem; height: 3rem; color: white; opacity: 0.8;" fill="currentColor" viewBox="0 0 24 24"><path d="M19.615 3.184c-3.604-.246-11.631-.245-15.23 0-3.897.266-4.356 2.62-4.385 8.816.029 6.185.484 8.549 4.385 8.816 3.6.245 11.626.246 15.23 0 3.897-.266 4.356-2.62 4.385-8.816-.029-6.185-.484-8.549-4.385-8.816zm-10.615 12.816v-8l8 3.993-8 4.007z"/></svg>
            </div>
        </div>
        
        <div>
            <h3 style="font-size: 1.125rem; font-weight: 700; color: #10b981; display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                <svg style="width: 1.25rem; height: 1.25rem;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                Video Ready for Analysis
            </h3>
            <p style="color: #9ca3af; font-size: 0.875rem; line-height: 1.5; max-width: 32rem;">
                Our AI Engine will download the subtitles, clean the text, and run the NLP Classification pipelines to extract targeted vocabulary.
            </p>
        </div>
    </div>'''

if target in content:
    content = content.replace(target, replacement)
    with open(filepath, 'w') as f:
        f.write(content)
    print("Preview Patch applied successfully!")
else:
    print("Target not found.")
